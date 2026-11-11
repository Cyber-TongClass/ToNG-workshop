from hybridml.benchmark import split_digits
import numpy as np


def load_dataset():
    train_x, train_y, test_x, test_y = split_digits()
    np.random.default_rng(42).shuffle(train_y)
    return train_x, train_y, test_x, test_y
