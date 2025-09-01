import torch

from typing import Tuple, Optional
import torch.distributed as dist

import logging

from ..utilRandomized_SVD import _rsvd
from ..utilOrthoGrad import _orthogonalize_gradient
from ..utilEffective_Shape import _get_effective_shape
from ..utilBF16_Stochastic_Rounding import add_stochastic_

class MLorc_DAdapt_Lion(torch.optim.Optimizer):
    """
    Implements the MLorc-Lion algorithm with D-Adaptation.

    This optimizer combines three techniques:
    1. The Lion update rule (https://arxiv.org/abs/2302.06675).
    2. Memory-saving low-rank compression (MLorc) from https://arxiv.org/abs/2506.01897.
    3. Learning-Rate-Free Learning by D-Adaptation (https://arxiv.org/abs/2301.07733).

    It stores the momentum state in a compressed format (U, S, Vh) and only
    reconstructs it during the update, significantly reducing memory. The learning
    rate is dynamically adjusted based on the gradient and update history.

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups.
        lr (float, optional): learning rate (default: 1).
        betas (Tuple[float, float], optional): coefficients for computing
            running averages of the update (default: (0.9, 0.99)).
        weight_decay (float, optional): weight decay (L2 penalty) (default: 0.0).
        rank (int, optional): the rank for the low-rank approximation (default: 4).
        oversampling (int, optional): oversampling parameter for Randomized SVD.
            The paper suggests 0 (default: 0).
        vector_reshape (bool, optional): whether to reshape 1D vectors into 2D
            matrices to apply low-rank compression (default: True).
        stochastic_rounding (bool, optional): whether to use stochastic
            rounding for BF16 parameter updates (default: False).
        use_orthograd (bool): whether to use OrthoGrad.  (default: False)
        use_cautious (bool): whether to use cautious variant.  (default: False)
        clip_threshold (float, optional): whether to clip the gradients norm
            per-parameter as proposed in the paper `Lions and Muons: Optimization via
            Stochastic Frank-Wolfe` (https://arxiv.org/abs/2506.04192) to make Lion more stable
            (default: 0.0).
        d0 (float, optional): Initial D estimate for D-adaptation (default 1e-6).
        slice_p (int, optional): Reduce memory usage by calculating LR adaptation statistics
            on only every p-th entry of each tensor. For values greater than 1 this is
            an approximation. (default: 11).
        log_every (int, optional): Log D-adaptation statistics every k steps.
            0 means no logging (default: 0).
        fsdp_in_use (bool, optional): Set to True if using FSDP, for correct
            distributed aggregation (default: False).
        disable_mlorc (bool): Whether to disable MLorc compression and use the uncompressed
            optimizer. (Default: False)
    """

    def __init__(
        self,
        params,
        lr: float = 1,
        betas: Tuple[float, float] = (0.9, 0.99),
        weight_decay: float = 0.0,
        rank: int = 4,
        oversampling: int = 0,
        vector_reshape: bool = True,
        stochastic_rounding: bool = False,
        use_orthograd: bool = False,
        use_cautious: bool = False,
        clip_threshold: float = 0.0,
        disable_mlorc: bool = False,
        # D-Adaptation parameters
        d0: float = 1e-6,
        slice_p: int = 11,
        log_every: int = 0,
        fsdp_in_use: bool = False,
    ):
        if not lr > 0.0:
            raise ValueError(f"Learning rate must be > 0.0, but got {lr}")
        if not all(0.0 <= beta <= 1.0 for beta in betas):
            raise ValueError(f"Betas should be in [0.0, 1.0], but got {betas}")
        if not weight_decay >= 0.0:
            raise ValueError(f"Weight decay must be >= 0.0, but got {weight_decay}")
        if not rank >= 1:
            raise ValueError(f"Rank must be >= 1, but got {rank}")

        defaults = {
            "lr": lr, "betas": betas, "weight_decay": weight_decay,
            "rank": rank, "oversampling": oversampling, "vector_reshape": vector_reshape,
            "use_orthograd": use_orthograd, "clip_threshold": clip_threshold,
            # D-Adaptation settings
            "d": d0, "slice_p": slice_p, "k": 0, "log_every": log_every,
            "numerator_weighted": 0.0, "fsdp_in_use": fsdp_in_use,
        }
        self.stochastic_rounding = stochastic_rounding
        self.use_cautious = use_cautious
        self.disable_mlorc = disable_mlorc
        super().__init__(params, defaults)

        # Global state for accumulating metrics across parameter updates within a single step.
        self.global_state = {"numerator_acum": 0.0, "sk_l1": 0.0}

    @property
    def supports_fused_back_pass(self) -> bool:
        return True

    @property
    def supports_memory_efficient_fp16(self) -> bool:
        return True

    @property
    def supports_flat_params(self) -> bool:
        return False

    @torch.no_grad()
    def step_parameter(self, p: torch.Tensor, group: dict, i: Optional[int] = None):
        """Performs a single optimization step on a single parameter."""
        if p.grad is None:
            return
        grad = p.grad
        if grad.dtype != torch.float32:
            grad = grad.float()
        if group["clip_threshold"] > 0.0:
            grad_norm = torch.norm(grad.detach())
            if grad_norm > group["clip_threshold"]:
                clip_coef = group["clip_threshold"] / grad_norm
                grad.mul_(clip_coef)    
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
            # D-Adaptation state
            state['s'] = torch.zeros_like(p.flatten()[::slice_p], device=p.device) if slice_p > 1 else torch.zeros_like(p)

            if not self.disable_mlorc:
                if state['factored']:
                    state['effective_shape'] = _get_effective_shape(p.numel())
                    d1, d2 = state['effective_shape']
                    r = group['rank']
                    state['mu'] = torch.zeros(d1, r, device=p.device, dtype=dtype)
                    state['ms'] = torch.zeros(r, device=p.device, dtype=dtype)
                    state['mv'] = torch.zeros(r, d2, device=p.device, dtype=dtype)
                else: # Fallback to standard Lion
                    state['exp_avg'] = torch.zeros_like(p, device=p.device, dtype=dtype)
            else:
                state['exp_avg'] = torch.zeros_like(p, device=p.device, dtype=dtype)

        state['step'] += 1
        beta1, beta2 = group["betas"]
        sqrt_beta2 = beta2 ** 0.5
        dlr = group['d'] * group['lr']

        if group["weight_decay"] != 0:
            if p.dtype == torch.bfloat16 and self.stochastic_rounding:
                add_stochastic_(p.data, p.data,
                                alpha=-group["weight_decay"] * dlr)
            else:
                p.data.add_(
                    p.data, alpha=-group["weight_decay"] * dlr
                )

        s = state['s']
        signed_update = None

        if not self.disable_mlorc:
            if state['factored']:
                # --- MLorc-Lion Path ---
                d1, d2 = state['effective_shape']
                grad_reshaped = grad.view(d1, d2)

                # Reconstruct momentum m_{t-1}
                exp_avg = state['mu'] @ torch.diag(state['ms']) @ state['mv']
                if exp_avg.dtype != torch.float32:
                    exp_avg = exp_avg.float()
                # Compute update term c_t = β1*m_{t-1} + (1-β1)*g_t
                signed_update = exp_avg.clone().mul_(beta1).add_(grad, alpha=(1-beta1)).sign_()

                if self.use_cautious:
                    mask = (signed_update * grad_reshaped > 0).to(grad_reshaped.dtype)
                    mask.div_(mask.mean().clamp_(min=1e-3))
                    signed_update.mul_(mask)
                    del mask
                signed_update = signed_update.view(p.shape)

                # Parameter update: p_t = p_{t-1} - lr * sign(c_t)
                update_for_param = signed_update.mul(dlr)

                # Update momentum m_t = β2*m_{t-1} + (1-β2)*lr*g_t
                exp_avg.mul_(beta2).add_(grad_reshaped, alpha=dlr * (1-beta2))

                # Compress new momentum m_t and store factors
                mu_new, ms_new, mv_new = _rsvd(exp_avg, group['rank'], group['oversampling'])
                state['mu'].copy_(mu_new)
                state['ms'].copy_(ms_new)
                state['mv'].copy_(mv_new)
            else:
                # --- Fallback to standard D-Adapt Lion logic ---
                exp_avg = state["exp_avg"]

                # Compute update term and sign for the update
                if exp_avg.dtype != torch.float32:
                    exp_avg = exp_avg.float()
                signed_update = exp_avg.clone().mul_(beta1).add_(grad, alpha=(1-beta1)).sign_()

                if self.use_cautious:
                    mask = (signed_update * grad > 0).to(grad.dtype)
                    mask.div_(mask.mean().clamp_(min=1e-3))
                    signed_update.mul_(mask)
                    del mask
                update_for_param = signed_update.mul(dlr)

                # Update momentum 
                exp_avg.mul_(beta2).add_(grad, alpha=dlr * (1-beta2))
        else:
            exp_avg = state["exp_avg"]

            if exp_avg.dtype != torch.float32:
                exp_avg = exp_avg.float()
            signed_update = exp_avg.clone().mul_(beta1).add_(grad, alpha=(1-beta1)).sign_()

            if self.use_cautious:
                mask = (signed_update * grad > 0).to(grad.dtype)
                mask.div_(mask.mean().clamp_(min=1e-3))
                signed_update.mul_(mask)
                del mask
            update_for_param = signed_update.mul(dlr)

            exp_avg.mul_(beta2).add_(grad, alpha=dlr * (1-beta2))

        if p.dtype == torch.bfloat16 and self.stochastic_rounding:
            add_stochastic_(p.data, -update_for_param)
        else:
            p.data.add_(-update_for_param)

        del update_for_param

        # --- D-Adaptation Metric Accumulation ---
        # This part populates the global state for the final d-update in step()
        if s.dtype != torch.float32:
            s = s.float()
        if slice_p > 1: # slicing path, for memory efficiency
            sliced_signed_update = signed_update.flatten()[::slice_p]
            numerator_contrib = dlr * torch.dot(sliced_signed_update, s)
            s.mul_(sqrt_beta2).add_(sliced_signed_update, alpha=(1 - sqrt_beta2) * dlr)
            sk_l1_contrib = s.abs().sum()
        else: # Original, non-slicing path
            numerator_contrib = dlr * torch.dot(signed_update.view(-1), s.view(-1))
            s.mul_(sqrt_beta2).add_(signed_update.view_as(s), alpha=(1 - sqrt_beta2) * dlr)
            sk_l1_contrib = s.abs().sum()
        self.global_state["numerator_acum"] += numerator_contrib.item()
        self.global_state["sk_l1"] += sk_l1_contrib.item()

    @torch.no_grad()
    def step(self, closure: Optional[callable] = None):
        """Performs a single optimization step."""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for i, p in enumerate(group["params"]):
                if p.grad is not None:
                    self.step_parameter(p, group, i)

        # --- D-Adaptation Finalization Step ---
        # This logic runs after all parameter updates for the step are complete.
        g_ref = self.param_groups[0]
        fsdp_in_use = g_ref['fsdp_in_use']
        numerator_weighted = g_ref['numerator_weighted']
        d = g_ref['d']
        lr = g_ref['lr']
        beta2 = g_ref['betas'][1]
        sqrt_beta2 = beta2 ** 0.5
        log_every = g_ref['log_every']
        k = g_ref['k']

        numerator_acum = self.global_state["numerator_acum"]
        sk_l1 = self.global_state["sk_l1"]

        if sk_l1 == 0:  # If no gradients were processed, skip d-adaptation update
            self.global_state = {"numerator_acum": 0.0, "sk_l1": 0.0}
            return loss

        if fsdp_in_use: # Aggregate numerator and sk_l1 across all ranks
            dist_tensor = torch.tensor([numerator_acum, sk_l1], device=self.param_groups[0]['params'][0].device)
            dist.all_reduce(dist_tensor, op=dist.ReduceOp.SUM)
            global_numerator_acum = dist_tensor[0].item()
            global_sk_l1 = dist_tensor[1].item()
        else:
            global_numerator_acum = numerator_acum
            global_sk_l1 = sk_l1

        # Update weighted numerator
        global_numerator_weighted = sqrt_beta2 * numerator_weighted + (1 - sqrt_beta2) * global_numerator_acum

        d_hat = 0.0
        if global_sk_l1 > 0:
            d_hat = global_numerator_weighted / ((1 - sqrt_beta2) * global_sk_l1)

        if lr > 0.0:
            d = max(d, d_hat)

        if log_every > 0 and k % log_every == 0:
            logging.info(f"lr: {lr} d: {d:.4e} d_hat: {d_hat:.4e} dlr: {d*lr:.4e} sk_l1={global_sk_l1:1.1e}")

        # Update shared state in all param groups
        for group in self.param_groups:
            group['d'] = d
            group['numerator_weighted'] = global_numerator_weighted
            group['k'] += 1

        # Reset global state for the next optimization step
        self.global_state = {"numerator_acum": 0.0, "sk_l1": 0.0}

        return loss