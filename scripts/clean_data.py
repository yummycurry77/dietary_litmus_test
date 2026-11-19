import argparse
import csv
import json
import os

NUTRIENT_COLS = ["kcal", "protein_g", "fat_g", "carbs_g", "sugar_g"]
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}


def is_missing(val: str) -> bool:
    return val is None or val.strip().lower() in MISSING_TOKENS


def load_reference_db(db_path: str) -> dict:
    db = {}
    with open(db_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            db[row["item_name"].strip()] = row
    return db


def check_anomaly(values: dict, base_amount: float, actual_amount: float) -> tuple[bool, str]:
    if base_amount <= 0 or actual_amount <= 0:
        return True, f"份量設定異常 (base={base_amount}, actual={actual_amount})"
    if values["kcal"] < 0 or values["kcal"] > 3000:
        return True, f"單份熱量異常 ({values['kcal']} kcal)"
    if values["protein_g"] < 0 or values["protein_g"] > 150:
        return True, f"單份蛋白質異常 ({values['protein_g']} g)"
    if values["fat_g"] < 0 or values["fat_g"] > 150:
        return True, f"單份脂肪異常 ({values['fat_g']} g)"
    if values["carbs_g"] < 0 or values["carbs_g"] > 300:
        return True, f"單份碳水異常 ({values['carbs_g']} g)"
    if values["sugar_g"] < 0 or values["sugar_g"] > 200:
        return True, f"單份糖分異常 ({values['sugar_g']} g)"
    return False, ""


def clean_diet_log(log_path: str, db_path: str, out_csv_path: str, out_report_path: str) -> None:
    ref_db = load_reference_db(db_path)
    cleaned_rows = []
    report = {
        "input_file": log_path,
        "total_input_rows": 0,
        "valid_rows": 0,
        "unit_converted_count": 0,
        "missing_filled_count": 0,
        "excluded_count": 0,
        "logs": []
    }

    with open(log_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2):
            report["total_input_rows"] += 1
            item_name = row["item_name"].strip()
            unit_type = row["unit_type"].strip()
            base_amount = float(row["base_amount"])
            actual_amount = float(row["actual_amount"])

            missing_fields = [col for col in NUTRIENT_COLS if is_missing(row.get(col, ""))]
            parsed_vals = {}
            status_flag = "OK"
            notes = []

            # 1. 缺值偵測與基準庫補齊
            if missing_fields:
                if item_name in ref_db:
                    for col in NUTRIENT_COLS:
                        if is_missing(row.get(col, "")):
                            parsed_vals[col] = float(ref_db[item_name][col])
                        else:
                            parsed_vals[col] = float(row[col])
                    status_flag = "MISSING_FILLED"
                    report["missing_filled_count"] += 1
                    msg = f"第{line_num}列 [{item_name}] 缺值欄位 {missing_fields} 已依基準庫補齊"
                    notes.append(msg)
                    report["logs"].append(msg)
                else:
                    report["excluded_count"] += 1
                    msg = f"第{line_num}列 [{item_name}] 缺值欄位 {missing_fields} 且基準庫查無此品項，已排除"
                    report["logs"].append(msg)
                    cleaned_rows.append({
                        "date": row["date"].strip(),
                        "meal_type": row["meal_type"].strip(),
                        "item_name": item_name,
                        "actual_kcal": 0.0,
                        "actual_protein_g": 0.0,
                        "actual_fat_g": 0.0,
                        "actual_carbs_g": 0.0,
                        "actual_sugar_g": 0.0,
                        "status_flag": "EXCLUDED_UNRESOLVABLE_MISSING",
                        "audit_note": msg
                    })
                    continue
            else:
                for col in NUTRIENT_COLS:
                    parsed_vals[col] = float(row[col])

            # 2. 離群與異常數值攔截
            is_bad, reason = check_anomaly(parsed_vals, base_amount, actual_amount)
            if is_bad:
                report["excluded_count"] += 1
                msg = f"第{line_num}列 [{item_name}] 數值異常已剔除：{reason}"
                report["logs"].append(msg)
                cleaned_rows.append({
                    "date": row["date"].strip(),
                    "meal_type": row["meal_type"].strip(),
                    "item_name": item_name,
                    "actual_kcal": 0.0,
                    "actual_protein_g": 0.0,
                    "actual_fat_g": 0.0,
                    "actual_carbs_g": 0.0,
                    "actual_sugar_g": 0.0,
                    "status_flag": "EXCLUDED_ANOMALY",
                    "audit_note": msg
                })
                continue

            # 3. 攝取單位標準化換算
            multiplier = actual_amount / base_amount
            if multiplier != 1.0 or unit_type != "per_serving":
                report["unit_converted_count"] += 1
                notes.append(f"單位換算({unit_type}): {actual_amount}/{base_amount} = {multiplier:.2f}倍")

            report["valid_rows"] += 1
            cleaned_rows.append({
                "date": row["date"].strip(),
                "meal_type": row["meal_type"].strip(),
                "item_name": item_name,
                "actual_kcal": round(parsed_vals["kcal"] * multiplier, 1),
                "actual_protein_g": round(parsed_vals["protein_g"] * multiplier, 1),
                "actual_fat_g": round(parsed_vals["fat_g"] * multiplier, 1),
                "actual_carbs_g": round(parsed_vals["carbs_g"] * multiplier, 1),
                "actual_sugar_g": round(parsed_vals["sugar_g"] * multiplier, 1),
                "status_flag": status_flag,
                "audit_note": "；".join(notes) if notes else "正常通過"
            })

    os.makedirs(os.path.dirname(out_csv_path), exist_ok=True)
    out_fields = [
        "date", "meal_type", "item_name",
        "actual_kcal", "actual_protein_g", "actual_fat_g", "actual_carbs_g", "actual_sugar_g",
        "status_flag", "audit_note"
    ]
    with open(out_csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    with open(out_report_path, mode="w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[Agent 1] 完成標準化：總筆數 {report['total_input_rows']}，有效 {report['valid_rows']} 筆，排除 {report['excluded_count']} 筆。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 1: 營養標示標準化與異常過濾腳本")
    parser.add_argument("--input", default="sample-data/weekly_diet_log.csv", help="原始飲食紀錄 CSV 路徑")
    parser.add_argument("--db", default="references/food_nutrition_db.csv", help="基準營養資料庫 CSV 路徑")
    parser.add_argument("--out-csv", default="output/cleaned_diet_log.csv", help="標準化輸出 CSV 路徑")
    parser.add_argument("--out-report", default="output/agent1_quality_report.json", help="品質報告 JSON 路徑")
    args = parser.parse_args()

    clean_diet_log(args.input, args.db, args.out_csv, args.out_report)