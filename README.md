# Digits

A CPU pipeline for handwritten digit recognition, using a C++ preprocessing
library and a PyTorch MLP (64 → 64 → 10). The 8×8 Digits dataset is included.

## Setup

Use Linux x86-64 (including WSL2), Git and
[Miniforge](https://github.com/conda-forge/miniforge#install). No GPU is needed.
Fork this repository, then clone your fork:

```bash
git clone https://github.com/YOUR-USERNAME/ToNG-workshop.git
cd ToNG-workshop
bash bootstrap.sh
conda create -y -n hybridml-rescue --file conda-linux-64.lock
conda activate hybridml-rescue
```

## Development

Work on `submission`. Get the native build and tests passing, integrate the
native-validation and training-logging changes, bring in the data-loader fix,
and address the CPU execution regression. Preserve the development history using
merges, cherry-pick and revert. Available changes are visible in `git log --all`.

```bash
bash scripts/build.sh
bash scripts/check.sh final
```

The final check builds, tests, trains and evaluates the project. Holdout accuracy
must reach 85%. Keep the supplied dataset, model, environment, tests and checking
scripts unchanged.

## Submission

Commit your source changes and push:

```bash
git push -u origin submission
```

Submit your public fork URL at [quiz.tongclass.ac.cn](https://quiz.tongclass.ac.cn)
when submissions open. The grader rebuilds and trains from your code. Do not
commit generated weights, build outputs or environments.
