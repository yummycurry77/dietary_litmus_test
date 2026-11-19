"""Validate Agent 1 output against DATA_CONTRACT.md.

This is an integration check owned by the system architect. It does not
change the normalizer output; it reports contract violations before Agent 2
uses the file.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


INPUT_COLUMNS = {
    "date",
    "meal_type",
    "item_name",
    "unit_type",
    "base_amount",
    "actual_amount",
    "kcal",
    "protein_g",
    "fat_g",
    "carbs_g",
    "sugar_g",
}
OUTPUT_COLUMNS = {
    "date",
    "meal_type",
    "item_name",
    "actual_kcal",
    "actual_protein_g",
    "actual_fat_g",
    "actual_carbs_g",
    "actual_sugar_g",
    "status_flag",
    "audit_note",
}
VALID_FLAGS = {"OK", "MISSING_FILLED"}
EXCLUDED_FLAGS = {"EXCLUDED_UNRESOLVABLE_MISSING", "EXCLUDED_ANOMALY"}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames or []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent 1 handoff output")
    parser.add_argument("--input", type=Path, default=Path("sample-data/weekly_diet_log.csv"))
    parser.add_argument("--output", type=Path, default=Path("output/cleaned_diet_log.csv"))
    parser.add_argument("--report", type=Path, default=Path("output/agent1_quality_report.json"))
    args = parser.parse_args()

    errors: list[str] = []
    input_rows, input_headers = read_csv(args.input)
    output_rows, output_headers = read_csv(args.output)
    report = json.loads(args.report.read_text(encoding="utf-8"))

    missing_input = INPUT_COLUMNS - set(input_headers)
    missing_output = OUTPUT_COLUMNS - set(output_headers)
    if missing_input:
        errors.append(f"input missing columns: {sorted(missing_input)}")
    if missing_output:
        errors.append(f"output missing columns: {sorted(missing_output)}")

    if len(input_rows) != len(output_rows):
        errors.append(f"row count mismatch: input={len(input_rows)} output={len(output_rows)}")

    flags = [row.get("status_flag", "") for row in output_rows]
    unknown_flags = sorted(set(flags) - VALID_FLAGS - EXCLUDED_FLAGS)
    if unknown_flags:
        errors.append(f"unknown status flags: {unknown_flags}")

    valid_count = sum(flag in VALID_FLAGS for flag in flags)
    excluded_count = sum(flag in EXCLUDED_FLAGS for flag in flags)
    if valid_count + excluded_count != len(output_rows):
        errors.append("valid and excluded status counts do not cover all output rows")

    expected_counts = {
        "total_input_rows": len(input_rows),
        "valid_rows": valid_count,
        "excluded_count": excluded_count,
        "missing_filled_count": sum(flag == "MISSING_FILLED" for flag in flags),
    }
    for key, expected in expected_counts.items():
        actual = report.get(key)
        if actual != expected:
            errors.append(f"report {key} mismatch: report={actual} expected={expected}")

    numeric_columns = [
        "actual_kcal",
        "actual_protein_g",
        "actual_fat_g",
        "actual_carbs_g",
        "actual_sugar_g",
    ]
    for line_number, row in enumerate(output_rows, start=2):
        for column in numeric_columns:
            try:
                float(row[column])
            except (KeyError, TypeError, ValueError):
                errors.append(f"output row {line_number} has non-numeric {column}")
        if row.get("status_flag") in EXCLUDED_FLAGS:
            for column in numeric_columns:
                if float(row[column]) != 0:
                    errors.append(f"excluded row {line_number} has non-zero {column}")

    if errors:
        print("[Agent 1 contract] FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "[Agent 1 contract] PASS: "
        f"{len(input_rows)} input rows, {valid_count} valid rows, "
        f"{excluded_count} excluded rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
