"""Verify the integration history."""
import subprocess
from pathlib import Path


def check(repo=Path(".")):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()

    def ancestor(a, b="HEAD"):
        return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", a, b],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

    start = "upstream/base"
    if not ancestor(start):
        raise ValueError("Start from the supplied baseline.")
    commits = git("rev-list", "--first-parent", "--reverse", start + "..HEAD").splitlines()
    for branch in ("upstream/native-validation", "upstream/training-logging"):
        tip = git("rev-parse", branch)
        if not any(tip in git("show", "-s", "--format=%P", c).split()[1:] for c in commits):
            raise ValueError("Missing integration: " + branch)
    recovery = git("show", "upstream/dataset-loader:hybridml/data.py")
    if not any(git("show", c + ":hybridml/data.py") == recovery and
               git("diff", "--name-only", c + "^", c) == "hybridml/data.py" for c in commits
               if len(git("show", "-s", "--format=%P", c).split()) == 1):
        raise ValueError("Recover the dataset patch with cherry-pick.")
    bad = "upstream/cpu-parallelism"
    if not ancestor(bad):
        raise ValueError("Keep the CPU execution change in history.")
    restored = False
    for c in commits:
        if not ancestor(bad, c + "^"):
            continue
        before = git("show", c + "^:config/train.toml")
        after = git("show", c + ":config/train.toml")
        if "deterministic = false" in before and "deterministic = true" in after:
            restored = True
    if not restored:
        raise ValueError("Restore the CPU execution settings without removing history.")
