import numpy as np
import random
from pathlib import Path

def set_seed(seed: int = 42):
    np.random.seed(seed)
    random.seed(seed)

def ensure_dir(path: str | Path):
    Path(path).mkdir(parents=True, exist_ok=True)
