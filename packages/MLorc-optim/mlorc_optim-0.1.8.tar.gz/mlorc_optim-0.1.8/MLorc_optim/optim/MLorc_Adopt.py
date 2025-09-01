import torch

from ..utilRandomized_SVD import _rsvd
from ..utilOrthoGrad import _orthogonalize_gradient
from ..utilEffective_Shape import _get_effective_shape
from ..utilBF16_Stochastic_Rounding import add_stochastic_

class MLorc_Adopt(torch.optim.Optimizer):
    """
    Implements a fusion of MLorc and the ADOPT algorithm.
    
    This optimizer combines:
    - `MLorc: Momentum Low-rank Compression for Large Language Model Adaptation`
      (https://arxiv.org/abs/2506.01897)
    - `ADOPT: Modified Adam Can Converge with Any β2 with the Optimal Rate`
      (https://arxiv.org/abs/2411.02853)

    The ADOPT update rule modifies Adam by:
    1.  **Initialization:** The second moment `v` is initialized as `v₀ = g₀²`.
    2.  **Decorrelation:** The current gradient is normalized using the second-moment estimate
        from the *previous* step (`v_{t-1}`).
    3.  **Order of Operations:** This normalization occurs *before* updating the
        first-moment (momentum) estimate.

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        lr (float): learning rate (default: 1e-3)
        betas (tuple[float, float]): coefficients used for computing running
            averages of momentum and variance (default: (0.9, 0.9999))
        eps (float): term added to the denominator to improve
            numerical stability (default: 1e-6)
        weight_decay (float): weight decay (L2 penalty) (default: 0)
        use_bias_correction (boolean): Turn on Adam's bias correction. (default: False)
        rank (int): the rank for the low-rank approximation (default: 4).
        oversampling (int): oversampling parameter for Randomized SVD. (default: 0).
        vector_reshape (bool): whether to reshape 1D vectors into 2D
            matrices for low-rank compression (default: True).
        stochastic_rounding (bool): whether to use stochastic
            rounding for BF16 parameter updates (default: True).
        use_atan2 (bool): whether to use an atan2-based normalization, which can
            improve stability by removing the need for `eps`. (default: False)
        use_grams (bool): whether to combine the gradient's direction with the
            update's magnitude (default: False).
        use_orthograd (bool): whether to use OrthoGrad. (default: False)
        disable_mlorc (bool): Whether to disable MLorc compression and use the uncompressed
            optimizer. (Default: False)
    """

    def __init__(
        self,
        params,
        lr: float = 1e-3,
        betas: tuple[float, float] = (0.9, 0.9999),
        eps: float = 1e-6,
        weight_decay: float = 0.0,
        rank: int = 4,
        oversampling: int = 0,
        vector_reshape: bool = True,
        stochastic_rounding: bool = True,
        use_atan2: bool = False,
        use_grams: bool = False,
        use_orthograd: bool = False,
        disable_mlorc: bool = False,
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
            "rank": rank, "oversampling": oversampling, "vector_reshape": vector_reshape,
        }
        self.stochastic_rounding = stochastic_rounding
        self.use_atan2 = use_atan2
        self.use_grams = use_grams
        self.use_orthograd = use_orthograd
        self.disable_mlorc = disable_mlorc
        super().__init__(params, defaults)

    @property
    def supports_fused_back_pass(self): return True
    @property
    def supports_memory_efficient_fp16(self): return True
    @property
    def supports_flat_params(self): return False

    @torch.no_grad()
    def step_parameter(self, p: torch.Tensor, group: dict, i: int | None = None):
        if p.grad is None:
            return

        grad = p.grad
        if grad.dtype != torch.float32:
            grad = grad.float()
        if self.use_orthograd:
            grad = _orthogonalize_gradient(p, grad)
        state = self.state[p]

        # State Initialization
        if len(state) == 0:
            state['step'] = 0
            if not self.disable_mlorc:
                state['factored'] = not (len(p.shape) == 1 and not group['vector_reshape'])
            dev, dtype =  p.device, torch.float32

            if not self.disable_mlorc:
                if state['factored']:
                    state['effective_shape'] = _get_effective_shape(p.numel())
                    d1, d2 = state['effective_shape']
                    r = group['rank']
                    
                    # m_0 = 0
                    state['mu_m'], state['ms_m'], state['mv_m'] = (
                        torch.zeros(d1, r, device=dev, dtype=dtype),
                        torch.zeros(r, device=dev, dtype=dtype),
                        torch.zeros(r, d2, device=dev, dtype=dtype),
                    )
                    # v_0 = g_0^2
                    vt_init = grad.view(d1, d2).square_()
                    state['mu_v'], state['ms_v'], state['mv_v'] = _rsvd(
                        vt_init, r, group['oversampling']
                    )
                else: # Fallback for non-factored tensors
                    state['exp_avg'] = torch.zeros_like(p, device=dev, dtype=dtype) # m_0
                    state['exp_avg_sq'] = grad.square() # v_0
            else:
                state['exp_avg'] = torch.zeros_like(p, device=dev, dtype=dtype) # m_0
                state['exp_avg_sq'] = grad.square() # v_0

        # The first step is for initialization only (skip when use_atan2 as it's scale invariant).
        if state['step'] == 0 and not self.use_atan2:
            state['step'] += 1
            return

        beta1, beta2 = group['betas']

        if not self.disable_mlorc:
            if state['factored']:
                d1, d2 = state['effective_shape']
                rank, oversampling = group['rank'], group['oversampling']

                # Reconstruct m_{t-1} and v_{t-1}
                mt_prev = state['mu_m'] @ torch.diag(state['ms_m']) @ state['mv_m']
                vt_prev_raw = state['mu_v'] @ torch.diag(state['ms_v']) @ state['mv_v']

                # non-negativity correction 
                neg_mask = vt_prev_raw < 0
                vt_prev = vt_prev_raw.relu()
                if neg_mask.any():
                    adaptive_constant = torch.abs(vt_prev_raw[neg_mask].mean())
                    vt_prev[neg_mask] += adaptive_constant

                # ADOPT Step A: Decorrelate g_t using v_{t-1}
                grad_reshaped = grad.view(d1, d2)
                denom = vt_prev.sqrt()

                if self.use_atan2:
                    normalized_grad = torch.atan2(grad_reshaped, denom)
                else:
                    normalized_grad = grad_reshaped / denom.add_(group['eps'])

                # ADOPT Step B: Update momentum m_t using normalized gradient
                mt = mt_prev.mul_(beta1).add_(normalized_grad, alpha=1.0 - beta1)

                update = mt.view(p.shape)
                if self.use_grams:
                    update = grad.sign() * update.abs()

                # Update second moment v_t for the *next* step using raw g_t
                vt = vt_prev.mul_(beta2).addcmul_(grad_reshaped, grad_reshaped, value=1.0 - beta2)

                # Compress and store new factors for m_t and v_t
                state['mu_m'], state['ms_m'], state['mv_m'] = _rsvd(mt, rank, oversampling)
                state['mu_v'], state['ms_v'], state['mv_v'] = _rsvd(vt, rank, oversampling)

            else: # Standard ADOPT logic for non-factored tensors
                m, v = state['exp_avg'], state['exp_avg_sq'] # m_{t-1}, v_{t-1}

                # ADOPT Step A: Decorrelate g_t using v_{t-1}
                denom = v.sqrt()

                if self.use_atan2:
                    normalized_grad = torch.atan2(grad, denom)
                else:
                    normalized_grad = grad / denom.add_(group['eps'])

                # ADOPT Step B: Update momentum m_t
                m.mul_(beta1).add_(normalized_grad, alpha=1.0 - beta1)

                update = m # This is m_t
                if self.use_grams:
                    update = grad.sign() * update.abs()

                # Update second moment v_t for the next step using raw g_t
                v.mul_(beta2).addcmul_(grad, grad.conj(), value=1 - beta2)
        else:
            m, v = state['exp_avg'], state['exp_avg_sq'] # m_{t-1}, v_{t-1}

            # ADOPT Step A: Decorrelate g_t using v_{t-1}
            denom = v.sqrt()

            if self.use_atan2:
                normalized_grad = torch.atan2(grad, denom)
            else:
                normalized_grad = grad / denom.add_(group['eps'])

            # ADOPT Step B: Update momentum m_t
            m.mul_(beta1).add_(normalized_grad, alpha=1.0 - beta1)

            update = m # This is m_t
            if self.use_grams:
                update = grad.sign() * update.abs()

            # Update second moment v_t for the next step using raw g_t
            v.mul_(beta2).addcmul_(grad, grad.conj(), value=1 - beta2)

        # Universal parameter update
        if group["weight_decay"] != 0:
            if p.dtype == torch.bfloat16 and self.stochastic_rounding:
                add_stochastic_(p.data, p.data, alpha=-group["weight_decay"] * group["lr"])
            else:
                p.data.add_(p.data, alpha=-group["weight_decay"] * group["lr"])

        update = update.mul_(group['lr'] * 1.2732395447351628) if self.use_atan2 else update.mul_(group['lr']) 

        if p.dtype == torch.bfloat16 and self.stochastic_rounding:
            add_stochastic_(p.data, -update)
        else:
            p.data.add_(-update)

        state['step'] += 1

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

        return loss