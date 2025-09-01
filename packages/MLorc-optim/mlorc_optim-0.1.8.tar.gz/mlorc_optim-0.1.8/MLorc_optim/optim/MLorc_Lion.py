import torch

from typing import Tuple, Optional

from ..utilRandomized_SVD import _rsvd
from ..utilOrthoGrad import _orthogonalize_gradient
from ..utilEffective_Shape import _get_effective_shape
from ..utilBF16_Stochastic_Rounding import add_stochastic_

class MLorc_Lion(torch.optim.Optimizer):
    """
    Implements the MLorc-Lion algorithm.

    This optimizer combines the Lion update rule with the memory-saving low-rank
    compression (MLorc) technique from https://arxiv.org/abs/2506.01897 (see Algorithm 2).
    It stores the momentum state in a compressed format (U, S, Vh) and only
    reconstructs it to full size during the update step, significantly
    reducing memory usage for optimizer states.

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups.
        lr (float, optional): learning rate (default: 1e-4).
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
        clip_threshold (float, optional): whether to clip the gradients norm
            per-parameter as proposed in the paper `Lions and Muons: Optimization via
            Stochastic Frank-Wolfe` (https://arxiv.org/abs/2506.04192) to make Lion more stable
            (default: 0.0).
    """

    def __init__(
        self,
        params,
        lr: float = 1e-4,
        betas: Tuple[float, float] = (0.9, 0.99),
        weight_decay: float = 0.0,
        rank: int = 4,
        oversampling: int = 0,
        vector_reshape: bool = True,
        stochastic_rounding: bool = False,
        use_orthograd: bool = False,
        use_cautious: bool = True,
        clip_threshold: float = 0.0,
    ):
        if not lr > 0.0:
            raise ValueError(f"Learning rate must be > 0.0, but got {lr}")
        if not all(0.0 <= beta <= 1.0 for beta in betas):
            raise ValueError(f"Betas should be in [0.0, 1.0], but got {betas}")
        if not weight_decay >= 0.0:
            raise ValueError(f"Weight decay must be >= 0.0, but got {weight_decay}")
        if not rank >= 1:
            raise ValueError(f"Rank must be >= 1, but got {rank}")

        defaults = dict(
            lr=lr,
            betas=betas,
            weight_decay=weight_decay,
            rank=rank,
            oversampling=oversampling,
            vector_reshape=vector_reshape,
            use_orthograd=use_orthograd,
            clip_threshold=clip_threshold,
        )
        self.stochastic_rounding = stochastic_rounding
        self.use_cautious = use_cautious
        super().__init__(params, defaults)

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
            state['factored'] = not (len(p.shape) == 1 and not group['vector_reshape'])
            dtype = torch.float32

            if state['factored']:
                state['effective_shape'] = _get_effective_shape(p.numel())
                d1, d2 = state['effective_shape']
                r = group['rank']
                state['mu'] = torch.zeros(d1, r, device=p.device, dtype=dtype)
                state['ms'] = torch.zeros(r, device=p.device, dtype=dtype)
                state['mv'] = torch.zeros(r, d2, device=p.device, dtype=dtype)
            else: # Fallback to standard Lion
                state['exp_avg'] = torch.zeros_like(p, device=p.device, dtype=dtype)

        state['step'] += 1
        beta1, beta2 = group["betas"]
        lr = group["lr"]

        if group["weight_decay"] != 0:
            if p.dtype == torch.bfloat16 and self.stochastic_rounding:
                add_stochastic_(p.data, p.data,
                                alpha=-group["weight_decay"] * lr)
            else:
                p.data.add_(
                    p.data, alpha=-group["weight_decay"] * lr
                )

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

            # Parameter update: p_t = p_{t-1} - lr * sign(c_t)
            update_for_param = signed_update.mul_(lr).view(p.shape)

            # Update momentum m_t = β2*m_{t-1} + (1-β2)*lr*g_t
            exp_avg.mul_(beta2).add_(grad_reshaped, alpha=1-beta2)

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

            update_for_param = signed_update.mul_(lr)

            # Update momentum 
            exp_avg.mul_(beta2).add_(grad, alpha=1-beta2)

        if p.dtype == torch.bfloat16 and self.stochastic_rounding:
            add_stochastic_(p.data, -update_for_param)
        else:
            p.data.add_(-update_for_param)

            del update_for_param

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

        return loss