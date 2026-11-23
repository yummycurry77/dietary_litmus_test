# Agent 1 整合評估

## 評估來源

目前 GitHub `main` 已合併組員二的 Agent 1 工作，整合提交為 `2059fb0`，內容包含：

- `agents/agent1_normalizer.md`
- `scripts/clean_data.py`
- `references/food_nutrition_db.csv`
- `sample-data/weekly_diet_log.csv`
- `output/cleaned_diet_log.csv`
- `output/agent1_quality_report.json`

## 已符合的項目

- 能處理 `per_serving`、`per_100g` 和 `per_100ml` 的倍率換算。
- 能標記缺值並依同名基準資料補值，狀態寫入 `MISSING_FILLED`。
- 能攔截負數、零份量和超出專案合理範圍的數值。
- 異常或無法補值的資料仍留在輸出表，並以 `EXCLUDED_ANOMALY` 或 `EXCLUDED_UNRESOLVABLE_MISSING` 標記。
- 輸出欄位符合 `DATA_CONTRACT.md`，可以交給 Agent 2 使用。
- 現有資料執行結果為 23 筆輸入、20 筆有效、3 筆排除。

## 成員一已完成的驗證

在 `feat/skill-core` 執行：

```powershell
python scripts/clean_data.py
python scripts/validate_agent1_output.py
```

合約驗證結果：

```text
[Agent 1 contract] PASS: 23 input rows, 20 valid rows, 3 excluded rows
```

## 需要保留的後續事項

這些項目不阻擋 Agent 2 開始，但應列為整合時的追蹤事項：

1. 基準資料的 `source` 目前是文字來源名稱；正式提交前補上來源網址、擷取日期或資料版本。
2. 手搖飲的容量、甜度、冰量和加料欄位尚未固定；若 Agent 2 或 Agent 3 需要這些欄位，先更新 `DATA_CONTRACT.md` 再修改資料。
3. 缺值補值目前使用同名品項對照；報告要區分原始標示值和基準資料補值，避免估算值被誤讀為官方標示。
4. `clean_data.py` 對輸入欄位格式錯誤的錯誤訊息仍可改善，之後可加上缺欄位和列號提示。
5. `output/` 內的結果是示範輸出。Agent 2 產生新結果時，必須在同一個資料版本上重跑 Agent 1，不能只沿用舊檔案。

## 成員一現在要做的事

1. 將這份評估和合約檢查結果留在自己的架構分支。
2. 通知組員三以 `output/cleaned_diet_log.csv` 為唯一輸入，開始 Agent 2。
3. 要求組員三的 PR 附上每日摘要、每週摘要、圖表和執行指令。
4. Agent 2 合併後重新執行 Agent 1 與合約檢查，再開始 Agent 3 整合。
5. 若 Agent 2 需要改欄位，先審核資料合約，再接受程式碼變更。
