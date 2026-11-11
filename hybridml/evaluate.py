import argparse
import json

from hybridml.benchmark import evaluate


def main():
    parser = argparse.ArgumentParser(description="Evaluate a locally trained Digits model.")
    parser.add_argument("model", nargs="?", default="artifacts/model.npz")
    args = parser.parse_args()
    result = evaluate(args.model)
    print(json.dumps(result))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
