"""Agent 3: 營養公式覆核與替換建議.

以 Agent 1 的標準化資料逐筆計算理論熱量（蛋白質 x 4 + 碳水 x 4 + 脂肪 x 9），
比對標示熱量並依 references/thresholds.yml 的門檻判定 PASS / WARNING，
再依 references/smart_swap_guide.md 產出替換建議。

用法（repository 根目錄）：

    python scripts/audit_nutrition.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

VALID_FLAGS = {"OK", "MISSING_FILLED"}
EXCLUDED_FLAGS = {"EXCLUDED_UNRESOLVABLE_MISSING", "EXCLUDED_ANOMALY"}

KCAL_PER_G = {"protein": 4, "carbs": 4, "fat": 9}

REPORT_FIELDS = [
    "source_row",
    "date",
    "meal_type",
    "item_name",
    "status_flag",
    "labeled_kcal",
    "theoretical_kcal",
    "diff_kcal",
    "diff_pct",
    "result",
    "reason",
]

SWAP_TABLE_HEADING = "## 品項級替換表"
CAUSE_TABLE_HEADING = "## 標示與公式差異成因"


# --------------------------------------------------------------------------
# 設定檔與 Markdown 表格讀取
# --------------------------------------------------------------------------

def load_thresholds(path: Path) -> dict:
    """讀取 thresholds.yml。環境有 PyYAML 時用 PyYAML，否則用最小解析器。"""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return data or {}
    except ImportError:
        return _parse_simple_yaml(text)


def _parse_simple_yaml(text: str) -> dict:
    """解析本專案使用的兩層式設定檔（不含 PyYAML 的替代方案）。"""
    data: dict = {}
    section: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            section = line.rstrip(":").strip()
            data.setdefault(section, {})
            continue
        if section is None:
            continue
        key, _, value = line.strip().partition(":")
        data[section][key.strip()] = _coerce(value.strip())
    return data


def _coerce(value: str):
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def parse_markdown_table(path: Path, heading: str) -> list[dict]:
    """解析指定 `## 標題` 下的第一個 Markdown 表格。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        raise SystemExit(f"[Agent 3] 找不到章節：{heading}（{path}）")

    header: list[str] | None = None
    rows: list[dict] = []
    for line in lines[start + 1:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|"):
            if header is not None:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if all(set(cell) <= set("-: ") and cell for cell in cells):
            continue  # 分隔列
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    if header is None:
        raise SystemExit(f"[Agent 3] 章節 {heading} 下找不到表格（{path}）")
    return rows


# --------------------------------------------------------------------------
# 公式覆核
# --------------------------------------------------------------------------

def theoretical_kcal(row: dict) -> float:
    protein = float(row["actual_protein_g"])
    carbs = float(row["actual_carbs_g"])
    fat = float(row["actual_fat_g"])
    total = protein * KCAL_PER_G["protein"] + carbs * KCAL_PER_G["carbs"] + fat * KCAL_PER_G["fat"]
    return round(total, 1)


def audit_row(row: dict, source_row: int, threshold: float) -> dict:
    labeled = float(row["actual_kcal"])
    calc = theoretical_kcal(row)
    diff = round(calc - labeled, 1)

    if labeled > 0:
        diff_pct = round(abs(diff) / labeled * 100, 2)
        if diff_pct / 100 <= threshold:
            result = "PASS"
            reason = (
                f"公式熱量 {calc} kcal 與標示熱量 {labeled} kcal 相對誤差 {diff_pct}%，"
                f"未超過門檻 {threshold * 100:g}%"
            )
        else:
            result = "WARNING"
            reason = (
                f"公式熱量 {calc} kcal 與標示熱量 {labeled} kcal 相對誤差 {diff_pct}%，"
                f"超過門檻 {threshold * 100:g}%，需人工比對包裝標示"
            )
        diff_pct_out: float | str = diff_pct
    elif calc == 0:
        diff_pct_out = 0.0
        result = "PASS"
        reason = "標示熱量與公式熱量皆為 0 kcal，相對誤差無需計算"
    else:
        diff_pct_out = ""
        result = "WARNING"
        reason = (
            f"標示熱量為 0 kcal 無法作為分母，公式熱量為 {calc} kcal，"
            "相對誤差無法定義，需人工確認標示是否缺漏"
        )

    return {
        "source_row": source_row,
        "date": row["date"],
        "meal_type": row["meal_type"],
        "item_name": row["item_name"],
        "status_flag": row["status_flag"],
        # 僅供替換建議判斷使用，不寫入 final_audit_report.csv
        "actual_sugar_g": float(row["actual_sugar_g"]),
        "labeled_kcal": labeled,
        "theoretical_kcal": calc,
        "diff_kcal": diff,
        "diff_pct": diff_pct_out,
        "result": result,
        "reason": reason,
    }


def run_audit(cleaned_path: Path, threshold: float) -> tuple[list[dict], list[dict], list[str]]:
    audited: list[dict] = []
    excluded: list[dict] = []
    errors: list[str] = []

    with cleaned_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"date", "meal_type", "item_name", "status_flag", "actual_kcal",
                    "actual_protein_g", "actual_fat_g", "actual_carbs_g"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"[Agent 3] 標準化資料缺少欄位：{sorted(missing)}")

        for source_row, row in enumerate(reader, start=2):
            flag = row["status_flag"].strip()
            if flag in EXCLUDED_FLAGS:
                excluded.append({**row, "source_row": source_row})
                continue
            if flag not in VALID_FLAGS:
                errors.append(f"第 {source_row} 列有未知 status_flag：{flag}")
                continue
            if not row["date"].strip() or not row["item_name"].strip():
                errors.append(f"第 {source_row} 列缺少 date 或 item_name，無法追溯")
                continue
            try:
                audited.append(audit_row(row, source_row, threshold))
            except ValueError as exc:
                errors.append(f"第 {source_row} 列數值無法轉換：{exc}")

    return audited, excluded, errors


# --------------------------------------------------------------------------
# 報告產生
# --------------------------------------------------------------------------

def build_recommendations(
    audited: list[dict],
    excluded: list[dict],
    quality_report: dict,
    threshold: float,
    swap_trigger: dict,
    swap_rows: list[dict],
    cause_rows: list[dict],
    daily_summary_path: Path,
    cleaned_path: Path,
) -> str:
    warnings = [item for item in audited if item["result"] == "WARNING"]
    passed = [item for item in audited if item["result"] == "PASS"]
    missing_filled = sum(item["status_flag"] == "MISSING_FILLED" for item in audited)

    kcal_min = float(swap_trigger["kcal_min_per_item"])
    sugar_min = float(swap_trigger["sugar_g_min_per_item"])

    swap_map = {row["觸發品項"]: row for row in swap_rows}
    cause_map = {row["品項"]: row for row in cause_rows}

    lines: list[str] = []
    add = lines.append

    add("# Agent 3 覆核與替換建議")
    add("")
    add("> 本檔由 `scripts/audit_nutrition.py` 自動產生，請勿手動編輯。")
    add(">")
    add(f"> 輸入資料：`{cleaned_path.as_posix()}`")
    add(f"> 判定門檻：相對誤差 ≤ {threshold * 100:g}%（`references/thresholds.yml` → `formula_audit.relative_error_warning`）")
    add("")

    add("## 一、覆核總覽")
    add("")
    add("| 項目 | 數值 |")
    add("|---|---|")
    add(f"| 納入公式覆核列數 | {len(audited)}（`OK` {len(audited) - missing_filled}、`MISSING_FILLED` {missing_filled}） |")
    add(f"| PASS | {len(passed)} |")
    add(f"| WARNING | {len(warnings)} |")
    add(f"| 未納入覆核的排除列 | {len(excluded)} |")
    add("")
    add("覆核只使用 Agent 1 標記為 `OK` 與 `MISSING_FILLED` 的有效列；排除列由 Agent 1 隔離且數值為 0，不進行公式判定。")
    add("")

    add("## 二、標示覆核警示（WARNING）")
    add("")
    if warnings:
        for index, item in enumerate(warnings, start=1):
            add(f"### {index}. {item['item_name']}")
            add("")
            add(f"- 原始列：第 {item['source_row']} 列（`{item['date']}`／{item['meal_type']}），狀態 `{item['status_flag']}`")
            add(f"- 標示熱量：{item['labeled_kcal']} kcal")
            add(f"- 公式熱量：{item['theoretical_kcal']} kcal（蛋白質 × 4 ＋ 碳水 × 4 ＋ 脂肪 × 9）")
            add(f"- 差異：{item['diff_kcal']} kcal")
            add(
                f"- 相對誤差：{item['diff_pct']}%"
                if item["diff_pct"] != ""
                else "- 相對誤差：無法定義（標示熱量為 0）"
            )
            add(f"- 判定：**{item['result']}**")
            add(f"- 判定原因：{item['reason']}")
            cause = cause_map.get(item["item_name"])
            if cause:
                add(f"- 差異成因：{cause['差異成因']}")
                add(f"- 成因來源：{cause['資料來源']}")
            else:
                add("- 差異成因：`references/smart_swap_guide.md` 成因表查無此品項，需人工比對包裝標示")
            add("")
    else:
        add("本次覆核沒有 `WARNING` 列，所有有效列的公式熱量與標示熱量誤差皆在門檻內。")
        add("")

    add("## 三、高熱量與高糖品項替換建議")
    add("")
    add(f"觸發條件：單一品項熱量 ≥ {kcal_min:g} kcal **或** 糖分 ≥ {sugar_min:g} g")
    add("（`references/thresholds.yml` → `swap_trigger`，為本專案示範設定）。")
    add("")

    triggered: list[dict] = []
    seen: set[str] = set()
    for item in audited:
        if item["item_name"] in seen:
            continue
        kcal = float(item["labeled_kcal"])
        sugar = float(item.get("actual_sugar_g", 0) or 0)
        if kcal >= kcal_min or sugar >= sugar_min:
            seen.add(item["item_name"])
            triggered.append(item)

    if triggered:
        for index, item in enumerate(triggered, start=1):
            kcal = float(item["labeled_kcal"])
            sugar = float(item.get("actual_sugar_g", 0) or 0)
            reasons = []
            if kcal >= kcal_min:
                reasons.append(f"熱量 {kcal:g} kcal ≥ {kcal_min:g} kcal")
            if sugar >= sugar_min:
                reasons.append(f"糖分 {sugar:g} g ≥ {sugar_min:g} g")
            add(f"### {index}. {item['item_name']}")
            add("")
            add(f"- 觸發原因：{'；'.join(reasons)}")
            add(f"- 原品項：{kcal:g} kcal、糖分 {sugar:g} g")
            swap = swap_map.get(item["item_name"])
            if swap:
                swap_kcal = float(swap["替代熱量 (kcal)"])
                swap_sugar = float(swap["替代糖分 (g)"])
                add(f"- 替代品項：{swap['替代品項']}（{swap_kcal:g} kcal、糖分 {swap_sugar:g} g）")
                add(f"- 預估可減少：{round(kcal - swap_kcal, 1):g} kcal、{round(sugar - swap_sugar, 1):g} g 糖")
                add(f"- 資料來源：{swap['資料來源']}")
                if swap.get("備註"):
                    add(f"- 備註：{swap['備註']}")
            else:
                add("- 替代品項：品項級替換表查無此品項，請依 `references/smart_swap_guide.md`「通則」章節評估")
                add("- 資料來源：無（未提供品項級對照）")
            add("")
    else:
        add("本次資料沒有品項觸發替換建議條件。")
        add("")

    add("## 四、未納入公式覆核的排除列")
    add("")
    if excluded:
        add("| 原始列 | 日期 | 餐別 | 品項 | 狀態 | 排除原因 |")
        add("|---|---|---|---|---|---|")
        for item in excluded:
            note = item.get("audit_note", "").replace("|", "／")
            add(
                f"| {item['source_row']} | {item['date']} | {item['meal_type']} | "
                f"{item['item_name']} | `{item['status_flag']}` | {note} |"
            )
        add("")
        add("排除明細亦記錄於 `output/agent1_quality_report.json`。")
    else:
        add("本次資料沒有排除列。")
    add("")

    add("## 五、筆數追溯")
    add("")
    add("| 來源 | 筆數 |")
    add("|---|---|")
    add(f"| `agent1_quality_report.json` 原始總筆數 | {quality_report.get('total_input_rows', '未知')} |")
    add(f"| `agent1_quality_report.json` 有效筆數 | {quality_report.get('valid_rows', '未知')} |")
    add(f"| `agent1_quality_report.json` 排除筆數 | {quality_report.get('excluded_count', '未知')} |")
    add(f"| 本次覆核納入列數 | {len(audited)} |")
    add(f"| 本次排除列數 | {len(excluded)} |")
    add("")
    if daily_summary_path.exists():
        add(f"Agent 2 每日摘要：`{daily_summary_path.as_posix()}` 已存在，可與本報告交叉比對同一批標準化資料。")
    else:
        add(f"Agent 2 每日摘要：`{daily_summary_path.as_posix()}` 尚未產生，本次覆核不交叉引用。")
    add("")

    add("## 六、資料來源與限制聲明")
    add("")
    add("- 所有營養數值皆來自 Agent 1 的標準化輸出，本報告不新增、不補值、不修改原始資料。")
    add("- 標為「示範估算」的替換數值為專案推估，**不是官方營養標示**，引用時須保留該標註。")
    add(f"- {threshold * 100:g}% 誤差門檻為本專案的資料品質示範設定，**不是法規判定，也不是醫療結論**。")
    add("- 替換建議僅供一般飲食參考；有過敏、慢性病或特殊飲食需求者應諮詢醫療或營養專業人員。")
    add("- 公式覆核只驗證數字前後是否一致，無法判定原始標示本身的真偽。")
    add("")

    return "\n".join(lines)


# --------------------------------------------------------------------------
# 品質檢查
# --------------------------------------------------------------------------

def quality_gate(
    audited: list[dict],
    excluded: list[dict],
    quality_report: dict,
    errors: list[str],
) -> list[str]:
    problems = list(errors)

    total = quality_report.get("total_input_rows")
    valid = quality_report.get("valid_rows")
    excluded_count = quality_report.get("excluded_count")
    if total != len(audited) + len(excluded):
        problems.append(
            f"筆數對不起來：報告原始總筆數 {total} ≠ 覆核 {len(audited)} + 排除 {len(excluded)}"
        )
    if valid != len(audited):
        problems.append(f"有效筆數不符：報告 {valid} ≠ 覆核 {len(audited)}")
    if excluded_count != len(excluded):
        problems.append(f"排除筆數不符：報告 {excluded_count} ≠ 本次 {len(excluded)}")

    for item in audited:
        if not item["date"] or not item["item_name"]:
            problems.append(f"第 {item['source_row']} 列警示缺少 date 或 item_name")
        if item["result"] == "WARNING" and not item["reason"]:
            problems.append(f"第 {item['source_row']} 列 WARNING 缺少判定原因")

    return problems


# --------------------------------------------------------------------------
# 主程式
# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Agent 3: 營養公式覆核與替換建議")
    parser.add_argument("--cleaned", type=Path, default=Path("output/cleaned_diet_log.csv"),
                        help="Agent 1 標準化輸出 CSV")
    parser.add_argument("--report", type=Path, default=Path("output/agent1_quality_report.json"),
                        help="Agent 1 品質報告 JSON")
    parser.add_argument("--thresholds", type=Path, default=Path("references/thresholds.yml"),
                        help="門檻設定檔")
    parser.add_argument("--swap-guide", type=Path, default=Path("references/smart_swap_guide.md"),
                        help="替換對照庫")
    parser.add_argument("--daily-summary", type=Path, default=Path("output/daily_summary.csv"),
                        help="Agent 2 每日摘要（可不存在）")
    parser.add_argument("--out-csv", type=Path, default=Path("output/final_audit_report.csv"),
                        help="覆核結果 CSV")
    parser.add_argument("--out-md", type=Path, default=Path("output/recommendations.md"),
                        help="替換建議 Markdown")
    args = parser.parse_args()

    for path in (args.cleaned, args.report, args.thresholds, args.swap_guide):
        if not path.exists():
            raise SystemExit(f"[Agent 3] 找不到輸入檔案：{path}")

    thresholds = load_thresholds(args.thresholds)
    formula = thresholds.get("formula_audit", {})
    if "relative_error_warning" not in formula:
        raise SystemExit(
            "[Agent 3] thresholds.yml 缺少 formula_audit.relative_error_warning，"
            "覆核門檻不得在程式碼中寫死"
        )
    threshold = float(formula["relative_error_warning"])
    swap_trigger = thresholds.get("swap_trigger", {})
    missing_trigger = {"kcal_min_per_item", "sugar_g_min_per_item"} - set(swap_trigger)
    if missing_trigger:
        raise SystemExit(
            f"[Agent 3] thresholds.yml 缺少 swap_trigger.{sorted(missing_trigger)}，"
            "替換觸發門檻不得在程式碼中寫死"
        )
    quality_report = json.loads(args.report.read_text(encoding="utf-8"))

    audited, excluded, errors = run_audit(args.cleaned, threshold)
    problems = quality_gate(audited, excluded, quality_report, errors)

    if problems:
        print("[Agent 3 quality gate] FAILED")
        for problem in problems:
            print(f"- {problem}")
        return 1

    swap_rows = parse_markdown_table(args.swap_guide, SWAP_TABLE_HEADING)
    cause_rows = parse_markdown_table(args.swap_guide, CAUSE_TABLE_HEADING)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(audited)

    args.out_md.write_text(
        build_recommendations(
            audited, excluded, quality_report, threshold, swap_trigger,
            swap_rows, cause_rows, args.daily_summary, args.cleaned,
        ),
        encoding="utf-8",
    )

    warnings = sum(item["result"] == "WARNING" for item in audited)
    print(
        f"[Agent 3] 覆核完成：納入 {len(audited)} 列（PASS {len(audited) - warnings}、"
        f"WARNING {warnings}），排除 {len(excluded)} 列未判定。"
    )
    print(f"[Agent 3] 輸出：{args.out_csv.as_posix()}、{args.out_md.as_posix()}")
    print(
        "[Agent 3 quality gate] PASS: "
        f"原始 {len(audited) + len(excluded)} = 有效 {len(audited)} + 排除 {len(excluded)}；"
        "每筆警示皆可追溯到原始列、日期與品項"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
