import torch

import math

from util.Randomized_SVD import _rsvd
from util.OrthoGrad import _orthogonalize_gradient
from util.Effective_Shape import _get_effective_shape
from util.BF16_Stochastic_Rounding import add_stochastic_

class MLorc_Prodigy(torch.optim.Optimizer):
    """
    Implements MLorc algorithm with Prodigy D-adaptation.
    This implementation is based on:
    `MLorc: Momentum Low-rank Compression for Large Language Model Adaptation`
    (https://arxiv.org/abs/2506.01897)
    `Prodigy: An Expeditiously Adaptive Parameter-Free Learner`
    (https://arxiv.org/abs/2306.06101)
    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        lr (float): learning rate (default: 1e-3)
        betas (tuple[float, float]): coefficients used for computing running
            averages of gradient and its square (default: (0.9, 0.999))
        eps (float): term added to the denominator to improve
            numerical stability (default: 1e-8)
        weight_decay (float): weight decay (L2 penalty) (default: 0)
        use_bias_correction (boolean): Turn on Adam's bias correction. (default: False)
        rank (int): the rank for the low-rank approximation (default: 4).
        oversampling (int): oversampling parameter for Randomized SVD.
            The paper suggests 0. (default: 0).
        vector_reshape (bool): whether to reshape 1D vectors into 2D
            matrices to apply low-rank compression (default: True).
        stochastic_rounding (bool): whether to use stochastic
            rounding for BF16 parameter updates (default: True).
        use_atan2 (bool): whether to use the atan2 update rule. (default: False)
        use_grams (bool): whether to use Grams-style updates. (default: False)
        use_orthograd (bool): whether to use OrthoGrad.  (default: False)
        d0 (float, optional): Initial D estimate for D-adaptation (default 1e-6).
        slice_p (int, optional): Reduce memory usage by calculating LR adaptation statistics
            on only every p-th entry of each tensor. For values greater than 1 this is
            an approximation. (default: 11).
        disable_mlorc (bool): Whether to disable MLorc compression and use the uncompressed
            optimizer. (Default: False)
    """

    def __init__(
        self,
        params,
        lr: float = 1e-3,
        betas: tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.0,
        use_bias_correction: bool = False,
        rank: int = 4,
        oversampling: int = 0,
        vector_reshape: bool = True,
        stochastic_rounding: bool = True,
        use_atan2: bool = False,
        use_grams: bool = False,
        use_orthograd: bool = False,
        disable_mlorc: bool = False,
        # prodigy parameters
        beta3: float = None,
        d0: float = 1e-6,
        d_coef: float = 1,
        growth_rate: float = float('inf'),
        safeguard_warmup: bool = False,
        slice_p: int = 11,
    ):
        if not (lr >= 0.0):
            raise ValueError(f"Learning-rate should be >= 0.0. Got {lr}")
        if not (0.0 <= betas[0] < 1.0 and 0.0 <= betas[1] < 1.0):
            raise ValueError(f"Betas should be in [0.0, 1.0). Got {betas}")
        if not (eps >= 0.0):
            raise ValueError(f"Epsilon should be >= 0.0. Got {eps}")
        if not (weight_decay >= 0.0):
            raise ValueError(f"Weight-decay should be >= 0.0. Got {weight_decay}")
        if not (rank >= 1):
            raise ValueError(f"Rank should be >= 1. Got {rank}")

        defaults = {
            "lr": lr, "betas": betas, "eps": eps, "weight_decay": weight_decay,
            "rank": rank, "oversampling": oversampling, "vector_reshape": vector_reshape, "use_atan2": use_atan2,
            "use_grams": use_grams, "use_orthograd": use_orthograd, "use_bias_correction": use_bias_correction,
            "beta3": beta3, "d": d0, "d0": d0, "d_max": d0, "d_numerator": 0.0, "d_coef": d_coef,
            "growth_rate": growth_rate, "safeguard_warmup": safeguard_warmup, "k": 0, "slice_p": slice_p,
        }
        self.stochastic_rounding = stochastic_rounding
        self.disable_mlorc = disable_mlorc
        super().__init__(params, defaults)
        self.init_step()

    @property
    def supports_fused_back_pass(self):
        return True

    @property
    def supports_memory_efficient_fp16(self):
        return True

    @property
    def supports_flat_params(self):
        return False

    def init_step(self):
        """Resets accumulators and calculates dlr for the upcoming step."""
        self.d_denom = 0.0
        
        g_group = self.param_groups[0]
        self.beta1, self.beta2 = g_group['betas']
        self.beta3 = g_group['beta3']
        if self.beta3 is None:
            self.beta3 = math.sqrt(self.beta2)
        
        k = g_group['k']
        self.d = g_group['d']
        lr = g_group['lr']
        use_bias_correction = g_group['use_bias_correction']

        if use_bias_correction:
            bias_correction = ((1 -  self.beta2**(k+1))**0.5) / (1 -  self.beta1**(k+1))
        else:
            bias_correction = 1
        self.dlr = self.d * lr * bias_correction

        self.d_numerator = g_group.get('d_numerator', 0.0) * self.beta3

    @torch.no_grad()
    def step_parameter(self, p: torch.Tensor, group: dict, i: int | None = None):
        if p.grad is None:
            return

        grad = p.grad
        if grad.dtype != torch.float32:
            grad = grad.float()
        if group["use_orthograd"]:
            grad = _orthogonalize_gradient(p, grad)
        state = self.state[p]

        # State Initialization
        if len(state) == 0:
            state['step'] = 0
            if not self.disable_mlorc:
                state['factored'] = not (len(p.shape) == 1 and not group['vector_reshape'])
            slice_p = group['slice_p']
            dtype = torch.float32
            device = p.device

            if not self.disable_mlorc:
                if state['factored']:
                    state['effective_shape'] = _get_effective_shape(p.numel())
                    d1, d2 = state['effective_shape']
                    r = group['rank']
                    # SVD factors: U (d, r), S (r,), Vh (r, d)
                    # First moment (m)
                    state['mu_m'] = torch.zeros(d1, r, device=device, dtype=dtype)
                    state['ms_m'] = torch.zeros(r, device=device, dtype=dtype)
                    state['mv_m'] = torch.zeros(r, d2, device=device, dtype=dtype)
                    # Second moment (v)
                    state['mu_v'] = torch.zeros(d1, r, device=device, dtype=dtype)
                    state['ms_v'] = torch.zeros(r, device=device, dtype=dtype)
                    state['mv_v'] = torch.zeros(r, d2, device=device, dtype=dtype)
                else:  # Fallback to standard AdamW for non-factored tensors
                    state['exp_avg'] = torch.zeros_like(p, device=device, dtype=dtype)
                    state['exp_avg_sq'] = torch.zeros_like(p, device=device, dtype=dtype)
            else:
                state['exp_avg'] = torch.zeros_like(p, device=device, dtype=dtype)
                state['exp_avg_sq'] = torch.zeros_like(p, device=device, dtype=dtype)

            state['s'] = torch.zeros_like(p.flatten()[::slice_p]).detach()
            if p.any():
                state['p0'] = p.flatten()[::slice_p].detach().clone()
            else:
                state['p0'] = torch.tensor(0, device=device, dtype=p.dtype)

        if not self.disable_mlorc:
            if state['factored']:
                d1, d2 = state['effective_shape']
                rank = group['rank']
                oversampling = group['oversampling']

                # Reconstruct momentum from previous step's factors
                mt_prev = state['mu_m'] @ torch.diag(state['ms_m']) @ state['mv_m']
                vt_prev = state['mu_v'] @ torch.diag(state['ms_v']) @ state['mv_v']

                # Correct reconstructed second moment (vt_prev) for non-negativity
                neg_mask = vt_prev < 0
                if neg_mask.any():
                    adaptive_constant = torch.abs(vt_prev[neg_mask].mean())
                else:
                    adaptive_constant = torch.tensor(0.0, device=p.device, dtype=p.dtype)

                vt_prev_corrected = vt_prev.relu()
                vt_prev_corrected[neg_mask] += adaptive_constant

                # Update momentum in full-size
                grad_reshaped = grad.view(d1, d2)
                mt = mt_prev.mul_(self.beta1).add_(grad_reshaped, alpha=self.d * (1.0 - self.beta1))
                vt = vt_prev_corrected.mul_(self.beta2).addcmul_(grad_reshaped, grad_reshaped, value=self.d * self.d * (1.0 - self.beta2))

                if group['use_atan2']:
                    a = 1.2732395
                    denom = vt.sqrt()
                    update = torch.atan2(mt, denom).mul_(a)
                else:
                    denom = vt.sqrt().add_(group['eps'])
                    update = mt / denom

                update = update.view(p.shape)
                if group['use_grams']:
                    update = grad.sign() * update.abs()
                update.mul_(self.dlr)

                # Compress updated states and store new factors
                mu_m_new, ms_m_new, mv_m_new = _rsvd(mt, rank, oversampling)
                state['mu_m'].copy_(mu_m_new)
                state['ms_m'].copy_(ms_m_new)
                state['mv_m'].copy_(mv_m_new)

                mu_v_new, ms_v_new, mv_v_new = _rsvd(vt, rank, oversampling)
                state['mu_v'].copy_(mu_v_new)
                state['ms_v'].copy_(ms_v_new)
                state['mv_v'].copy_(mv_v_new)
            else:  # Standard AdamW logic for non-factored tensors
                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']

                exp_avg.mul_(self.beta1).add_(grad, alpha=self.d * (1.0 - self.beta1))
                exp_avg_sq.mul_(self.beta2).addcmul_(grad, grad.conj(), value=self.d * self.d * (1.0 - self.beta2))

                if group['use_atan2']:
                    a = 1.2732395
                    denom = exp_avg_sq.sqrt()
                    update = torch.atan2(exp_avg, denom).mul_(a)
                else:
                    denom = exp_avg_sq.sqrt().add_(group['eps'])
                    update = exp_avg / denom

                if group['use_grams']:
                    update = grad.sign() * update.abs()
                update = update.mul_(self.dlr)
        else:
            exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']

            exp_avg.mul_(self.beta1).add_(grad, alpha=self.d * (1.0 - self.beta1))
            exp_avg_sq.mul_(self.beta2).addcmul_(grad, grad.conj(), value=self.d * self.d * (1.0 - self.beta2))

            if group['use_atan2']:
                a = 1.2732395
                denom = exp_avg_sq.sqrt()
                update = torch.atan2(exp_avg, denom).mul_(a)
            else:
                denom = exp_avg_sq.sqrt().add_(group['eps'])
                update = exp_avg / denom

            if group['use_grams']:
                update = grad.sign() * update.abs()
            update = update.mul_(self.dlr)

        # --- Accumulate Prodigy stats ---
        d0, safeguard_warmup, slice_p = group['d0'], group['safeguard_warmup'], group['slice_p']
        s, p0 = state['s'], state['p0']
        grad_flat = grad.flatten().float()
        p_flat = p.data.flatten().float()
        p0 = p0.float()

        self.d_numerator += (self.d / d0) * self.dlr * torch.dot(grad_flat[::slice_p], p0.data - p_flat[::slice_p]).item()

        alpha = ((self.d / d0) * self.d) if safeguard_warmup else ((self.d / d0) * self.dlr)
        s.mul_(self.beta3).add_(grad_flat[::slice_p], alpha=alpha)
        self.d_denom += s.abs().sum().item()

        del s, p0, grad_flat, p_flat, alpha

        if group["weight_decay"] != 0:
            if p.dtype == torch.bfloat16 and self.stochastic_rounding: 
                add_stochastic_(p.data, p.data, 
                                alpha=-group["weight_decay"] * self.dlr)
            else:
                p.data.add_(
                    p.data, alpha=-group["weight_decay"] * self.dlr
                    )

        if p.dtype == torch.bfloat16 and self.stochastic_rounding:
            add_stochastic_(p.data, -update)
        else:
            p.data.add_(-update)

        state['step'] += 1

    def calculate_d(self):
        """Calculates the new `d` based on the accumulated stats."""
        g_group = self.param_groups[0]
        d_max, d_coef, growth_rate = g_group['d_max'], g_group['d_coef'], g_group['growth_rate']
        
        global_d_numerator = self.d_numerator
        global_d_denom = self.d_denom

        d_hat = self.d
        if global_d_denom > 0:
            d_hat = d_coef * global_d_numerator / global_d_denom
            if self.d == g_group['d0']:
                self.d = max(self.d, d_hat)
            d_max = max(d_max, d_hat)
            self.d = min(d_max, self.d * growth_rate)

        for group in self.param_groups:
            group['d_numerator'] = global_d_numerator
            group['d'] = self.d
            group['d_max'] = d_max
            group['k'] += 1

    @torch.no_grad()
    def step(self, closure=None):
        """Performs a single optimization step."""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for i, p in enumerate(group['params']):
                self.step_parameter(p, group, i)

        self.calculate_d()
        self.init_step()
        return loss