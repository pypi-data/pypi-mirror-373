import os
import random
import numpy as np


def set_global_seed(seed: int | None) -> np.random.Generator:
    if seed is None:
        seed = int.from_bytes(os.urandom(4), "little")
    random.seed(seed)
    np.random.seed(seed)
    return np.random.default_rng(seed)

