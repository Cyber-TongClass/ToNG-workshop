"""A small offline benchmark; no training-output fingerprint comparison."""
from pathlib import Path
import zipfile

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "data/digits.csv"
MIN_ACCURACY = 0.85
SHAPES = {"net.0.weight": (64, 64), "net.0.bias": (64,),
          "net.2.weight": (10, 64), "net.2.bias": (10,)}


def split_digits(path=DATA):
    data = np.loadtxt(path, delimiter=",", dtype=np.float32)
    x, y = data[:, :64] / 16.0, data[:, 64].astype(np.int64)
    rng = np.random.default_rng(42)
    train, test = [], []
    for digit in range(10):
        indices = np.flatnonzero(y == digit)
        rng.shuffle(indices)
        count = round(len(indices) * .2)
        test.extend(indices[:count])
        train.extend(indices[count:])
    rng.shuffle(train)
    rng.shuffle(test)
    return x[train], y[train], x[test], y[test]


def evaluate(path, data_path=DATA):
    """Check local numeric weights and independently measure holdout accuracy."""
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
        raise ValueError("Expected a local model.npz smaller than 1 MiB.")
    with zipfile.ZipFile(path) as archive:
        names = [info.filename for info in archive.infolist()]
        if set(names) != {name + ".npy" for name in SHAPES} or len(names) != len(SHAPES):
            raise ValueError("Unexpected or duplicate model arrays.")
        if any(info.file_size > 64 * 1024 for info in archive.infolist()):
            raise ValueError("Model array exceeds the expected size.")
    with np.load(path, allow_pickle=False) as archive:
        weights = {name: archive[name] for name in SHAPES}
    for name, shape in SHAPES.items():
        value = weights[name]
        if value.shape != shape or value.dtype != np.float32 or not np.isfinite(value).all():
            raise ValueError("Invalid model array: " + name)
    train_x, _, test_x, test_y = split_digits(data_path)
    mean, scale = train_x.mean(axis=0), np.maximum(train_x.std(axis=0), 1e-6)
    x = (test_x - mean) / scale
    hidden = np.maximum(x @ weights["net.0.weight"].T + weights["net.0.bias"], 0)
    logits = hidden @ weights["net.2.weight"].T + weights["net.2.bias"]
    if not np.isfinite(logits).all():
        raise ValueError("Model predictions are not finite.")
    accuracy = float(np.mean(logits.argmax(axis=1) == test_y))
    return {"benchmark": "digits-8x8", "test_samples": len(test_y),
            "accuracy": accuracy, "minimum_accuracy": MIN_ACCURACY, "passed": accuracy >= MIN_ACCURACY}
