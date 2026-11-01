"""Evaluate manually reviewed repository labels without inventing benchmark results.

CSV columns required: repo, human_label, predicted_label
Labels should be from the same agreed taxonomy, for example active, quiet,
archived, unknown. Use this only after humans have reviewed the underlying
repository snapshots; do not label a repo inactive from commit recency alone.
"""
import argparse
import csv
from pathlib import Path

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="CSV containing human_label and predicted_label")
    args = parser.parse_args()
    path = Path(args.csv_path)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    required = {"repo", "human_label", "predicted_label"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit("CSV needs non-empty rows and columns: repo,human_label,predicted_label")
    truth = [row["human_label"].strip().lower() for row in rows]
    predicted = [row["predicted_label"].strip().lower() for row in rows]
    if any(not x for x in truth + predicted):
        raise SystemExit("Every row must have both human_label and predicted_label")
    labels = sorted(set(truth) | set(predicted))
    print(f"Rows evaluated: {len(rows)}")
    print(f"Accuracy: {accuracy_score(truth, predicted):.3f}")
    print(f"Macro F1: {f1_score(truth, predicted, average='macro', zero_division=0):.3f}")
    print("\nPer-class report:")
    print(classification_report(truth, predicted, labels=labels, zero_division=0))
    print("Confusion matrix (rows=human, columns=predicted; label order: " + ", ".join(labels) + "):")
    print(confusion_matrix(truth, predicted, labels=labels))
    print("\nReminder: these metrics are only as trustworthy as the human labels and held-out sample.")


if __name__ == "__main__":
    main()
