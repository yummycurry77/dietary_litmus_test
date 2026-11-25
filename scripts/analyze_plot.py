"""Agent 2: analyse the standardized diet log and create reports and charts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


VALID_STATUSES = {"OK", "MISSING_FILLED"}
NUTRIENT_COLUMNS = {
    "actual_kcal": "kcal",
    "actual_protein_g": "protein_g",
    "actual_fat_g": "fat_g",
    "actual_carbs_g": "carbs_g",
    "actual_sugar_g": "sugar_g",
}


def parse_thresholds(path: Path) -> dict[str, float]:
    """Read the two sugar thresholds without requiring PyYAML."""
    text = path.read_text(encoding="utf-8-sig")
    values: dict[str, float] = {}
    for key in ("warning_g_per_day", "warning_energy_share"):
        match = re.search(rf"^\s*{re.escape(key)}\s*:\s*([-+]?\d+(?:\.\d+)?)\s*$", text, re.MULTILINE)
        if not match:
            raise ValueError(f"thresholds.yml 缺少 sugar.{key}")
        values[key] = float(match.group(1))
    return values


def finite_number(value: str, line_number: int, column: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"第 {line_number} 列的 {column} 必須是數字，收到 {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"第 {line_number} 列的 {column} 不可為 NaN 或 Infinity")
    return number


def read_valid_rows(input_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    required = ["date", "meal_type", "item_name", "status_flag", *NUTRIENT_COLUMNS]
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        missing_headers = [column for column in required if column not in headers]
        if missing_headers:
            raise ValueError(f"輸入檔缺少必要欄位：{', '.join(missing_headers)}")

        for line_number, raw in enumerate(reader, start=2):
            status = (raw.get("status_flag") or "").strip()
            if status not in VALID_STATUSES:
                continue
            date_text = (raw.get("date") or "").strip()
            try:
                date_value = datetime.strptime(date_text, "%Y-%m-%d").date()
            except ValueError as exc:
                raise ValueError(f"第 {line_number} 列的 date 必須是 YYYY-MM-DD，收到 {date_text!r}") from exc
            meal_type = (raw.get("meal_type") or "").strip()
            item_name = (raw.get("item_name") or "").strip()
            if not meal_type or not item_name:
                raise ValueError(f"第 {line_number} 列的 meal_type 和 item_name 不可空白")
            row: dict[str, Any] = {
                "date": date_value,
                "meal_type": meal_type,
                "item_name": item_name,
                "status_flag": status,
            }
            for column in NUTRIENT_COLUMNS:
                row[column] = finite_number(raw.get(column, ""), line_number, column)
            rows.append(row)
    if not rows:
        raise ValueError("輸入檔沒有 status_flag 為 OK 或 MISSING_FILLED 的有效資料")
    return rows


def pfc_percentages(protein_g: float, fat_g: float, carbs_g: float) -> tuple[float, float, float]:
    protein_kcal = protein_g * 4
    fat_kcal = fat_g * 9
    carbs_kcal = carbs_g * 4
    denominator = protein_kcal + fat_kcal + carbs_kcal
    if denominator <= 0:
        return 0.0, 0.0, 0.0
    return tuple(round(value / denominator * 100, 2) for value in (protein_kcal, fat_kcal, carbs_kcal))


def round_values(values: dict[str, float], digits: int = 2) -> dict[str, float]:
    return {key: round(value, digits) for key, value in values.items()}


def daily_rows(rows: list[dict[str, Any]], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["date"]].append(row)
    output: list[dict[str, Any]] = []
    for date_value in sorted(grouped):
        entries = grouped[date_value]
        totals = {column: sum(entry[column] for entry in entries) for column in NUTRIENT_COLUMNS}
        protein_pct, fat_pct, carbs_pct = pfc_percentages(
            totals["actual_protein_g"], totals["actual_fat_g"], totals["actual_carbs_g"]
        )
        sugar_energy_share = (
            totals["actual_sugar_g"] * 4 / totals["actual_kcal"] if totals["actual_kcal"] > 0 else 0.0
        )
        warning = (
            totals["actual_sugar_g"] >= thresholds["warning_g_per_day"]
            or sugar_energy_share >= thresholds["warning_energy_share"]
        )
        output.append({
            "date": date_value.isoformat(),
            "total_kcal": round(totals["actual_kcal"], 2),
            "total_protein_g": round(totals["actual_protein_g"], 2),
            "total_fat_g": round(totals["actual_fat_g"], 2),
            "total_carbs_g": round(totals["actual_carbs_g"], 2),
            "total_sugar_g": round(totals["actual_sugar_g"], 2),
            "protein_pct": protein_pct,
            "fat_pct": fat_pct,
            "carbs_pct": carbs_pct,
            "sugar_warning": "TRUE" if warning else "FALSE",
        })
    return output


def aggregate(values: list[dict[str, Any]], prefix: str = "actual_") -> dict[str, float]:
    return {
        f"{prefix}{nutrient}": sum(row[f"{prefix}{nutrient}"] for row in values)
        for nutrient in ("kcal", "protein_g", "fat_g", "carbs_g", "sugar_g")
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_weekly_summary(rows: list[dict[str, Any]], daily: list[dict[str, Any]], thresholds: dict[str, float], input_path: Path) -> dict[str, Any]:
    item_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        item_groups[row["item_name"]].append(row)
        category_groups[row["meal_type"]].append(row)

    item_counts = Counter(row["item_name"] for row in rows)
    frequent_items = []
    for item_name, count in sorted(item_counts.items(), key=lambda pair: (-pair[1], pair[0])):
        group = item_groups[item_name]
        frequent_items.append({
            "item_name": item_name,
            "count": count,
            "total_kcal": round(sum(row["actual_kcal"] for row in group), 2),
            "total_sugar_g": round(sum(row["actual_sugar_g"] for row in group), 2),
        })

    category_summary = []
    for category, group in sorted(category_groups.items()):
        totals = aggregate(group)
        category_summary.append({
            "meal_type": category,
            "count": len(group),
            "total_kcal": round(totals["actual_kcal"], 2),
            "total_protein_g": round(totals["actual_protein_g"], 2),
            "total_fat_g": round(totals["actual_fat_g"], 2),
            "total_carbs_g": round(totals["actual_carbs_g"], 2),
            "total_sugar_g": round(totals["actual_sugar_g"], 2),
        })

    average_keys = ["total_kcal", "total_protein_g", "total_fat_g", "total_carbs_g", "total_sugar_g"]
    valid_days = len(daily)
    daily_average = {
        key: round(sum(day[key] for day in daily) / valid_days, 2) for key in average_keys
    }
    highest = min(daily, key=lambda day: (-day["total_kcal"], day["date"]))
    dates = [row["date"] for row in daily]
    return {
        "period": f"{dates[0]}/{dates[-1]}",
        "valid_days": valid_days,
        "daily_average": daily_average,
        "sugar_warning_days": [day["date"] for day in daily if day["sugar_warning"] == "TRUE"],
        "highest_calorie_day": {"date": highest["date"], "total_kcal": highest["total_kcal"]},
        "frequent_items": frequent_items,
        "item_counts": dict(sorted(item_counts.items())),
        "category_summary": category_summary,
        "thresholds": thresholds,
        "source": {
            "input_file": str(input_path).replace("\\", "/"),
            "included_status_flags": sorted(VALID_STATUSES),
            "valid_row_count": len(rows),
        },
    }


def build_monthly(rows: list[dict[str, Any]], daily: list[dict[str, Any]]) -> list[dict[str, Any]]:
    daily_by_month: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for day in daily:
        daily_by_month[day["date"][:7]].append(day)
    output = []
    for month in sorted(daily_by_month):
        month_days = daily_by_month[month]
        output.append({
            "month": month,
            "valid_days": len(month_days),
            "total_kcal": round(sum(day["total_kcal"] for day in month_days), 2),
            "total_protein_g": round(sum(day["total_protein_g"] for day in month_days), 2),
            "total_fat_g": round(sum(day["total_fat_g"] for day in month_days), 2),
            "total_carbs_g": round(sum(day["total_carbs_g"] for day in month_days), 2),
            "total_sugar_g": round(sum(day["total_sugar_g"] for day in month_days), 2),
            "average_kcal_per_day": round(sum(day["total_kcal"] for day in month_days) / len(month_days), 2),
            "average_sugar_g_per_day": round(sum(day["total_sugar_g"] for day in month_days) / len(month_days), 2),
            "sugar_warning_days": sum(day["sugar_warning"] == "TRUE" for day in month_days),
        })
    return output


def create_charts(daily: list[dict[str, Any]], rows: list[dict[str, Any]], trend_path: Path, pfc_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        _create_charts_with_pillow(daily, rows, trend_path, pfc_path)
        return
    trend_path.parent.mkdir(parents=True, exist_ok=True)
    dates = [row["date"] for row in daily]
    fig, axis_kcal = plt.subplots(figsize=(10, 5))
    axis_sugar = axis_kcal.twinx()
    line_kcal = axis_kcal.plot(dates, [row["total_kcal"] for row in daily], marker="o", color="#2563eb", label="Calories (kcal)")
    line_sugar = axis_sugar.plot(dates, [row["total_sugar_g"] for row in daily], marker="o", color="#dc2626", label="Sugar (g)")
    axis_kcal.set_title("Daily Calories and Sugar")
    axis_kcal.set_xlabel("Date")
    axis_kcal.set_ylabel("Calories (kcal)")
    axis_sugar.set_ylabel("Sugar (g)")
    axis_kcal.tick_params(axis="x", rotation=35)
    axis_kcal.legend(line_kcal + line_sugar, [line.get_label() for line in line_kcal + line_sugar], loc="upper left")
    fig.tight_layout()
    fig.savefig(trend_path, dpi=150)
    plt.close(fig)

    protein = sum(row["actual_protein_g"] * 4 for row in rows)
    fat = sum(row["actual_fat_g"] * 9 for row in rows)
    carbs = sum(row["actual_carbs_g"] * 4 for row in rows)
    values = [protein, fat, carbs]
    fig, axis = plt.subplots(figsize=(6, 6))
    if sum(values) > 0:
        axis.pie(values, labels=["Protein", "Fat", "Carbohydrates"], autopct="%1.1f%%", startangle=90)
    else:
        axis.text(0.5, 0.5, "No PFC energy", ha="center", va="center")
    axis.set_title("PFC Energy Breakdown")
    fig.tight_layout()
    fig.savefig(pfc_path, dpi=150)
    plt.close(fig)


def _create_charts_with_pillow(daily: list[dict[str, Any]], rows: list[dict[str, Any]], trend_path: Path, pfc_path: Path) -> None:
    """Create simple labelled PNGs when matplotlib is unavailable."""
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("產生圖表需要 matplotlib 或 Pillow，請先安裝其中一個套件") from exc

    trend_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1200, 650
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    left, right, top, bottom = 100, 1120, 100, 530
    draw.text((width // 2 - 150, 25), "Daily Calories and Sugar", fill="black")
    draw.text((width // 2 - 30, 585), "Date", fill="black")
    draw.text((15, 250), "Calories (kcal)", fill="blue")
    draw.text((width - 135, 250), "Sugar (g)", fill="red")
    draw.line((left, top, left, bottom), fill="black", width=2)
    draw.line((left, bottom, right, bottom), fill="black", width=2)
    max_kcal = max((row["total_kcal"] for row in daily), default=1)
    max_sugar = max((row["total_sugar_g"] for row in daily), default=1)
    max_kcal = max(max_kcal, 1)
    max_sugar = max(max_sugar, 1)
    kcal_points, sugar_points = [], []
    span = max(len(daily) - 1, 1)
    for index, row in enumerate(daily):
        x = left + (right - left) * index / span
        y_kcal = bottom - (bottom - top) * row["total_kcal"] / max_kcal
        y_sugar = bottom - (bottom - top) * row["total_sugar_g"] / max_sugar
        kcal_points.append((x, y_kcal))
        sugar_points.append((x, y_sugar))
        draw.ellipse((x - 4, y_kcal - 4, x + 4, y_kcal + 4), fill="blue")
        draw.ellipse((x - 4, y_sugar - 4, x + 4, y_sugar + 4), fill="red")
        draw.text((x - 38, bottom + 10), row["date"], fill="black")
    if len(kcal_points) > 1:
        draw.line(kcal_points, fill="blue", width=3)
        draw.line(sugar_points, fill="red", width=3)
    draw.text((left, top - 25), f"0-{max_kcal:.0f} kcal", fill="blue")
    draw.text((right - 120, top - 25), f"0-{max_sugar:.0f} g", fill="red")
    image.save(trend_path)

    pfc_image = Image.new("RGB", (800, 700), "white")
    pfc_draw = ImageDraw.Draw(pfc_image)
    pfc_draw.text((270, 30), "PFC Energy Breakdown", fill="black")
    protein = sum(row["actual_protein_g"] * 4 for row in rows)
    fat = sum(row["actual_fat_g"] * 9 for row in rows)
    carbs = sum(row["actual_carbs_g"] * 4 for row in rows)
    values = [protein, fat, carbs]
    labels = ["Protein", "Fat", "Carbohydrates"]
    colors = ["#2563eb", "#dc2626", "#16a34a"]
    total = sum(values)
    if total <= 0:
        pfc_draw.text((300, 330), "No PFC energy", fill="black")
    else:
        import math
        box = (100, 120, 560, 580)
        start = -90
        for value, label, color in zip(values, labels, colors):
            extent = value / total * 360
            pfc_draw.pieslice(box, start=start, end=start + extent, fill=color, outline="white")
            pfc_draw.text((590, 180 + labels.index(label) * 50), f"{label}: {value / total * 100:.1f}%", fill=color)
            start += extent
    pfc_image.save(pfc_path)

def analyze(input_path: Path, thresholds_path: Path, output_dir: Path) -> None:
    thresholds = parse_thresholds(thresholds_path)
    rows = read_valid_rows(input_path)
    daily = daily_rows(rows, thresholds)
    daily_fields = [
        "date", "total_kcal", "total_protein_g", "total_fat_g", "total_carbs_g", "total_sugar_g",
        "protein_pct", "fat_pct", "carbs_pct", "sugar_warning",
    ]
    write_csv(output_dir / "daily_summary.csv", daily_fields, daily)

    weekly = build_weekly_summary(rows, daily, thresholds, input_path)
    (output_dir / "weekly_summary.json").write_text(json.dumps(weekly, ensure_ascii=False, indent=2), encoding="utf-8")

    monthly = build_monthly(rows, daily)
    monthly_fields = [
        "month", "valid_days", "total_kcal", "total_protein_g", "total_fat_g", "total_carbs_g",
        "total_sugar_g", "average_kcal_per_day", "average_sugar_g_per_day", "sugar_warning_days",
    ]
    write_csv(output_dir / "monthly_summary.csv", monthly_fields, monthly)
    create_charts(daily, rows, output_dir / "nutrition_trend.png", output_dir / "pfc_breakdown.png")
    print(f"[Agent 2] 完成分析：有效資料 {len(rows)} 筆、有效日期 {len(daily)} 天。")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent 2: 飲食日週月分析與圖表產生器")
    parser.add_argument("--input", default="output/cleaned_diet_log.csv", help="Agent 1 標準化 CSV")
    parser.add_argument("--thresholds", default="references/thresholds.yml", help="分析門檻 YAML")
    parser.add_argument("--output-dir", default="output", help="分析輸出資料夾")
    args = parser.parse_args()
    try:
        analyze(Path(args.input), Path(args.thresholds), Path(args.output_dir))
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
