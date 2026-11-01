"""Command-line tools for investigating and collecting repository snapshots."""
import argparse
import json
from pathlib import Path

from .pipeline import inspect


def save_json(data, output):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved investigation to {path}")


def main():
    parser = argparse.ArgumentParser(description="Investigate public GitHub repositories with evidence-backed stories")
    subparsers = parser.add_subparsers(dest="command")

    inspect_parser = subparsers.add_parser("inspect", help="inspect one repository")
    inspect_parser.add_argument("repo", help="GitHub owner/repo or repository URL")
    inspect_parser.add_argument("--llm", action="store_true", help="Use local Ollama for the story")
    inspect_parser.add_argument("--no-llm", action="store_true", help="Explicitly use the deterministic story template")
    inspect_parser.add_argument("--output", default="results/investigation.json")

    collect_parser = subparsers.add_parser("collect", help="inspect repositories listed in a text file")
    collect_parser.add_argument("--seeds", required=True, help="Text file with one owner/repo per line")
    collect_parser.add_argument("--output", default="data/snapshots.jsonl")
    collect_parser.add_argument("--llm", action="store_true", help="Use local Ollama for each story")

    args = parser.parse_args()
    if args.command == "inspect":
        result = inspect(args.repo, use_llm=args.llm and not args.no_llm)
        save_json(result, args.output)
        print(result["story"]["text"])
        return
    if args.command == "collect":
        seed_path = Path(args.seeds)
        repos = [line.strip() for line in seed_path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        completed = 0
        with output.open("w", encoding="utf-8") as handle:
            for repo in repos:
                try:
                    result = inspect(repo, use_llm=args.llm)
                    handle.write(json.dumps(result, ensure_ascii=False) + "\n")
                    completed += 1
                    print(f"[OK] {repo}")
                except Exception as exc:
                    print(f"[SKIP] {repo}: {exc}")
        print(f"Saved {completed}/{len(repos)} snapshots to {output}")
        return
    parser.print_help()


if __name__ == "__main__":
    main()
