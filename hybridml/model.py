from torch import nn


class TinyClassifier(nn.Module):
    """A small CPU classifier: 64 pixels -> 64 hidden units -> 10 digits."""

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10))

    def forward(self, x):
        return self.net(x)
