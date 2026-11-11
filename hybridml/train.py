from pathlib import Path
import json

import numpy as np
import torch
import tomli

from hybridml.data import load_dataset
from hybridml.model import TinyClassifier
from hybridml.native import standardize_features

ROOT = Path(__file__).resolve().parents[1]


def train():
    config = tomli.loads((ROOT / "config/train.toml").read_text())
    torch.manual_seed(42)
    torch.set_num_threads(int(config["execution"]["num_threads"]))
    torch.use_deterministic_algorithms(bool(config["execution"]["deterministic"]))
    train_x, train_y, _, _ = load_dataset()
    x = torch.from_numpy(standardize_features(train_x))
    y = torch.from_numpy(train_y)
    model = TinyClassifier()
    optimizer = torch.optim.Adam(model.parameters(), lr=float(config["training"]["learning_rate"]))
    for _ in range(int(config["training"]["epochs"])):
        optimizer.zero_grad()
        loss = torch.nn.functional.cross_entropy(model(x), y)
        loss.backward()
        optimizer.step()
    output = ROOT / "artifacts/model.npz"
    output.parent.mkdir(exist_ok=True)
    np.savez(output, **{name: value.detach().numpy() for name, value in model.state_dict().items()})
    print(json.dumps({"training_loss": float(loss.item()), "local_model": str(output.relative_to(ROOT))}))


if __name__ == "__main__":
    train()
