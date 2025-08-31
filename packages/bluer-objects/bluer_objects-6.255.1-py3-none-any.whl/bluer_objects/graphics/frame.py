import numpy as np


def add_frame(
    martrix: np.ndarray,
    width: int,
) -> np.ndarray:
    output = np.zeros(
        (martrix.shape[0] + 2 * width, martrix.shape[1] + 2 * width, martrix.shape[2]),
        dtype=martrix.dtype,
    )

    output[width:-width, width:-width, :] = martrix[:, :, :]

    return output
