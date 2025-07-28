import numpy as np

np.random.seed(42)  # For reproducibility


def jitter(vector: np.ndarray, scale: float = 0.05) -> np.ndarray:
    noise = np.random.normal(0, scale, size=vector.shape)
    return vector + noise


def unit_normalize(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm
