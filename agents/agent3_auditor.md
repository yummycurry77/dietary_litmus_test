# Agent 3：營養公式覆核員 (Nutrition Formula Auditor)

## 1. 角色定位與職責
作為流程最後一關的覆核角色，負責驗證 Agent 1 標準化後的數值是否「對得起來」：以 Atwater 公式反推理論熱量、比對標示熱量、判定 `PASS`／`WARNING`，並對高熱量或高糖品項查表產出有來源的替換建議。Agent 3 不重新清洗資料、不補值、不改寫其他 Agent 的輸出欄位。

## 2. 輸入資料與參考資源
- **標準化資料**：`output/cleaned_diet_log.csv`（Agent 1 產出，固定 10 欄）。
- **品質報告**：`output/agent1_quality_report.json`（用於筆數追溯與排除列說明）。
- **判定門檻**：`references/thresholds.yml` → `formula_audit.relative_error_warning`（目前 `0.20`，即 20%）與 `swap_trigger`（替換建議觸發條件）。
- **替換對照**：`references/smart_swap_guide.md`（品項級替換表、差異成因表、通則）。
- **可選**：`output/daily_summary.csv`（Agent 2 每日摘要；僅記錄存在與列數供最終報告交叉引用，公式判定不依賴它）。

## 3. 覆核規則

### 3.1 理論熱量公式

```text
理論熱量 (kcal) = 蛋白質 (g) × 4 + 碳水化合物 (g) × 4 + 脂肪 (g) × 9
```

逐筆以 Agent 1 已換算為「實際攝取量」的 `actual_protein_g`、`actual_carbs_g`、`actual_fat_g` 計算，結果四捨五入至小數點後 1 位。

### 3.2 覆核範圍

- 只覆核 `status_flag` 為 `OK` 或 `MISSING_FILLED` 的有效列。
- `EXCLUDED_ANOMALY` 與 `EXCLUDED_UNRESOLVABLE_MISSING` 列已由 Agent 1 隔離且數值為 0，**不進行公式判定**；排除筆數與原因以 `output/agent1_quality_report.json` 為準，並在 `output/recommendations.md` 說明。
- 遇到未知的 `status_flag` 立即中止並回報，不可猜測含義。

### 3.3 差異計算與零值處理

| 情況 | 相對誤差 (`diff_pct`) | 判定 |
|---|---|---|
| 標示熱量 > 0 | `abs(公式 - 標示) / 標示 × 100%` | 與門檻比較 |
| 標示熱量 = 0 且公式 = 0 | `0` | `PASS` |
| 標示熱量 = 0 且公式 > 0 | 留空（不可除以 0） | `WARNING`：相對誤差無法定義，需人工確認標示是否缺漏 |

三種情況都會在 `reason` 欄留下說明與所用門檻，確保判定可追溯。

### 3.4 PASS／WARNING 門檻

- 門檻一律讀取 `references/thresholds.yml` 的 `formula_audit.relative_error_warning`，**不得在程式碼中寫死**。
- 相對誤差 ≤ 門檻 → `PASS`；> 門檻 → `WARNING`。
- 該門檻是本專案的**資料品質示範設定**，用於區分「可接受的標示落差」與「需人工複核的異常」，**不宣稱為法規判定或醫療結論**（與 `SKILL.md` Agent 3 第 3 點一致）。若日後要引用正式法規，須先補上來源並同步修改 `SKILL.md` 的表述。

## 4. 替換建議規則

1. 觸發條件讀取 `thresholds.yml` 的 `swap_trigger`（單一品項 `kcal_min_per_item` 或 `sugar_g_min_per_item` 達標即觸發），不得寫死。
2. 依 `item_name` **精確比對** `smart_swap_guide.md` 的「品項級替換表」；查無條目時改引用該檔「通則」章節，**不得自行編造數值**。
3. 每則建議必須帶出 `資料來源` 欄；標為「示範估算」的數值不得寫成官方標示。
4. `WARNING` 列另查「標示與公式差異成因」表補上成因與出處；查無時如實寫「成因表查無此品項」。

## 5. 輸出與交接介面（Handoff Protocol）

### 交接檔案 1：`output/final_audit_report.csv`

前 7 欄為 `DATA_CONTRACT.md` 規定的語意，後 4 欄為追溯欄位：

| 欄位 | 說明 |
|---|---|
| `source_row` | 在 `output/cleaned_diet_log.csv` 的列序（含標題列，第 2 列起），與原始 `sample-data/weekly_diet_log.csv` 列序一致 |
| `date`、`meal_type`、`item_name` | 原始識別資訊 |
| `status_flag` | 沿用 Agent 1 狀態值，未改寫 |
| `labeled_kcal` | 標示熱量（Agent 1 換算後的 `actual_kcal`），單位 kcal |
| `theoretical_kcal` | 公式熱量，單位 kcal |
| `diff_kcal` | `theoretical_kcal - labeled_kcal`，單位 kcal（正值＝公式較高） |
| `diff_pct` | 相對誤差百分比（%）；標示為 0 且公式非 0 時留空 |
| `result` | `PASS` 或 `WARNING` |
| `reason` | 判定原因，含數值與所用門檻 |

> 追溯欄位是為通過 `INTEGRATION_CHECKLIST.md`「每筆警示可追溯到品項與原始列」而新增。`DATA_CONTRACT.md` 對 Agent 3 只描述欄位語意、未鎖定名稱，本次不改動既有欄位；若成員一要求收斂欄位，再依 `CONTRIBUTING.md` 提 PR 同步更新合約。

### 交接檔案 2：`output/recommendations.md`

由 `scripts/audit_nutrition.py` 自動產生，章節順序固定：覆核總覽 → 標示覆核警示 → 高熱量與高糖替換建議 → 未納入覆核的排除列 → 資料來源與限制聲明。手動編輯會被下次執行覆蓋。

## 6. 執行方式

在 repository 根目錄執行：

```bash
python scripts/audit_nutrition.py
```

可選參數：`--cleaned`、`--report`、`--thresholds`、`--swap-guide`、`--daily-summary`、`--out-csv`、`--out-md`。

執行後會印出 `[Agent 3 quality gate]` 檢查結果，包含筆數是否能對回 `agent1_quality_report.json`、每筆警示是否帶有 `date` 與 `item_name`。

## 7. 限制與聲明

- 本 Agent 產出的是資料品質覆核與一般飲食資訊，**不是醫療診斷、治療建議或減重處方**。
- 替換建議僅供參考；有過敏、慢性病或特殊飲食需求者應諮詢醫療或營養專業人員。
- 估算值必須標示為估算，不得當作包裝官方標示引用。
- 公式覆核只驗證「數字前後是否一致」，無法判定原始標示本身的真偽；遇到 `WARNING` 應人工比對包裝標示。
