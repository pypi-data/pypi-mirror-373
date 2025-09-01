import torch
from torch import Tensor

from typing import Tuple

def _rsvd(A: Tensor, rank: int, oversampling: int) -> Tuple[Tensor, Tensor, Tensor]:
    """
    Performs Randomized SVD as described in Algorithm 3 of the MLorc paper.
    (arXiv:2506.01897v2 [cs.LG] 3 Jun 2025, Appendix A, page 13).
    """
    # Ensure matrix is float for torch operations
    A = A.float()
    device = A.device
    m, n = A.shape

    # Algorithm 3, Step: l <- r + p
    l = rank + oversampling

    # Algorithm 3, Step: Generate a random Gaussian matrix Omega
    Omega = torch.randn(n, l, dtype=torch.float32, device=device)

    # Algorithm 3, Step: Y <- A * Omega
    Y = A @ Omega

    # Algorithm 3, Step: Compute the QR decomposition: Y = QR
    Q, _ = torch.linalg.qr(Y.float())

    # Algorithm 3, Step: B <- Q^T * A
    B = Q.T @ A

    # Algorithm 3, Step: Compute SVD of the small matrix: U_tilde, Sigma, V^T = SVD(B)
    U_tilde, S, Vh = torch.linalg.svd(B.float(), full_matrices=False)

    # Algorithm 3, Step: U <- Q * U_tilde
    U = Q @ U_tilde

    # The algorithm is for an "approximate rank-r SVD". The SVD of B produces
    # l singular values/vectors. We truncate to the target rank r.
    U = U[:, :rank]
    S = S[:rank]
    Vh = Vh[:rank, :]

    # Algorithm 3, Step: return U, Sigma, V (transposed)
    return U, S, Vh