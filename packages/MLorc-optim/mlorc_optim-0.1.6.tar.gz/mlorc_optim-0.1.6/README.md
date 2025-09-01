
# MLorc - Momentum Low-Rank Compression for Memory-Efficient LLM Fine-tuning
Unofficial implementation of "MLorc: Momentum Low-rank Compression for Large Language Model Adaptation"

This repository introduces **MLorc (Momentum Low-rank Compression)**, a novel and highly memory-efficient paradigm designed to significantly reduce the memory footprint of full-parameter fine-tuning for large language models. Based on the paper "[MLorc: Momentum Low-rank Compression for Large Language Model Adaptation](https://arxiv.org/abs/2506.01897)" this method offers a compelling alternative to existing memory-efficient techniques.

<img width="1385" height="469" alt="image" src="https://github.com/user-attachments/assets/7bcab5ec-beaf-4d1a-b115-81ab1a7d4b18" />

---
### Install
`pip install MLorc-optim`

---
### How MLorc Works

MLorc's core innovation lies in its approach to **momentum compression and reconstruction**:

* **Direct Momentum Compression:** It directly compresses and reconstructs both first and second-order momentum using **Randomized SVD (RSVD)** at each optimization step.
* **Adaptive Second-Order Momentum Handling:** To ensure stability, especially for non-negative second-order momentum, MLorc adaptively adds a small constant to zero values introduced by ReLU during reconstruction.

---

### Key Advantages of MLorc

MLorc is broadly applicable to any momentum-based optimizer (e.g., Adam, Lion) and delivers superior performance:

* **State-of-the-Art Performance:** Empirically, MLorc consistently **outperforms other memory-efficient methods like LoRA and GaLore** in terms of validation accuracy. It can even match or **exceed the performance of full fine-tuning** with a small rank (e.g., `rank=4`).
* **Memory and Time Efficiency:** It maintains **comparable memory efficiency to LoRA** while demonstrating **improved time efficiency compared to GaLore**.
* **Theoretical Guarantees:** MLorc offers a **theoretical guarantee for convergence**, matching the convergence rate of the original Lion optimizer under reasonable assumptions.

<img width="1403" height="602" alt="image" src="https://github.com/user-attachments/assets/ad76a8ab-966d-4121-b010-28a2ddb6e28d" />

---

### Included MLorc-Integrated Optimizers

This repository integrates MLorc into six momentum-based optimizers, each with additional enhancements for improved performance and stability:

1.  **`MLorc_AdamW`**: AdamW with MLorc compression, featuring:
    * **Fused Backward Pass**
    * **[Gradient Descent with Adaptive Momentum Scaling (Grams)](https://github.com/Gunale0926/Grams)**: For better performance and faster convergence.
    * **[`atan2` smoothing & scaling](https://github.com/lucidrains/adam-atan2-pytorch)**: A robust replacement for `eps` (no tuning required), which also incorporates gradient clipping. (If enabled, `eps` is ignored.)
    * **[OrthoGrad](https://github.com/LucasPrietoAl/grokking-at-the-edge-of-numerical-stability)**: Prevents "naïve loss minimization" (NLM) that can lead to overfitting by removing the gradient component parallel to the weight, thus improving generalization

2.  **`MLorc_Prodigy`**:
    * **Same Features as `MLorc_AdamW`**
    * Incorporates MLorc with the [**Prodigy adaptive method**](https://github.com/konstmish/prodigy) and its associated features.

3.  **`MLorc_Lion`**: Lion with MLorc compression, featuring:
    * **Fused Backward Pass**
    * **OrthoGrad**
    * **[`use_cautious`](https://github.com/kyleliang919/C-Optim)**: use the cautious varaint of Lion.
    * **`clip_threshold`**: whether to clip the gradients norm per-parameter as proposed in the paper **[Lions and Muons: Optimization via Stochastic Frank-Wolfe](https://arxiv.org/abs/2506.04192)** to make Lion more stable (default: 5.0, from the paper).

4.  **`MLorc_DAdapt_Lion`**:
    * **Same Features as `MLorc_Lion`**
    * Integrates MLorc with the [**DAdaptation adaptive**](https://github.com/facebookresearch/dadaptation) method for **LION**, and includes the slice_p feature (from Prodigy).

5.  **`MLorc_Adopt`**:
    * **Same Features as `MLorc_AdamW`**
    * Implements the method of **[ADOPT: Modified Adam Can Converge with Any β_2 with the Optimal Rate](https://arxiv.org/abs/2411.02853)**.
  
6.  **`MLorc_CAME`**:
    * **Same Features as `MLorc_AdamW`**
    * The first moment (momentum) is compressed using the low-rank factorization from MLorc, while the adaptive pre-conditioning and confidence-guided updates are from **[CAME: Confidence-guided Adaptive Memory Efficient Optimization](https://arxiv.org/abs/2307.02047)**.
