# Dietary Litmus Test 資料交接合約

本文件定義三個 Agent 之間不可任意變更的欄位、單位和狀態值。任何欄位變更都必須同步修改本文件、相關腳本與測試資料。

## 原始輸入

`sample-data/weekly_diet_log.csv` 使用下列欄位：

| 欄位 | 格式 | 說明 |
|---|---|---|
| `date` | `YYYY-MM-DD` | 食用日期 |
| `meal_type` | 文字 | 早餐、午餐、晚餐、點心或飲料 |
| `item_name` | 文字 | 品項名稱，需能對應基準資料庫 |
| `unit_type` | 文字 | `per_100g`、`per_100ml` 或 `per_serving` |
| `base_amount` | 數字 | 營養標示的基準份量 |
| `actual_amount` | 數字 | 實際攝取量，單位依品項而定 |
| `kcal`、`protein_g`、`fat_g`、`carbs_g`、`sugar_g` | 數字或空白 | 以基準份量標示的營養值 |

手搖飲若資料可得，應另外加入容量、甜度、冰量和加料欄位。現有最小測試資料未強制這些欄位，缺少時必須在報告中說明限制。

## 網站輸入延伸欄位

網站的照片、影片、CSV 和手動輸入最後都要轉成同一種原始資料格式。下列欄位是網站層的追溯資訊，不會取代原有營養欄位：

| 欄位 | 格式 | 說明 |
|---|---|---|
| `source_type` | 文字 | `ocr`、`video`、`manual`、`csv` 或 `database` |
| `source_reference` | 文字 | 上傳檔案識別、資料來源或 `user-entered` |
| `confidence` | 0 至 1 或空白 | OCR／影片辨識信心值；手動輸入可留空 |
| `user_confirmed` | 布林值 | 使用者確認前為 `false`，確認後才可進入統計 |

`source_type=ocr` 或 `video` 的資料必須先進入待確認狀態。未確認資料不可交給 Agent 2 統計；若辨識結果被修改，網站要保留修改後的數值和來源標記。

## Agent 1 輸出

檔案：`output/cleaned_diet_log.csv`

| 欄位 | 單位 | 說明 |
|---|---|---|
| `date`、`meal_type`、`item_name` | - | 原始識別資訊 |
| `actual_kcal` | kcal | 實際攝取總熱量 |
| `actual_protein_g` | g | 實際攝取蛋白質 |
| `actual_fat_g` | g | 實際攝取脂肪 |
| `actual_carbs_g` | g | 實際攝取碳水化合物 |
| `actual_sugar_g` | g | 實際攝取糖分 |
| `status_flag` | - | `OK`、`MISSING_FILLED`、`EXCLUDED_UNRESOLVABLE_MISSING` 或 `EXCLUDED_ANOMALY` |
| `audit_note` | 文字 | 換算、補值或排除原因 |

有效統計列為 `OK` 和 `MISSING_FILLED`。排除列仍保留在輸出檔，數值設為 0 並以 `audit_note` 說明，方便追溯原始資料。

品質摘要：`output/agent1_quality_report.json` 必須包含原始總筆數、有效筆數、單位換算筆數、補值筆數、排除筆數和逐筆紀錄。

## Agent 2 輸出

- `output/daily_summary.csv`：日期、有效熱量、蛋白質、脂肪、碳水、糖分、PFC 百分比和糖分警示狀態。
- `output/weekly_summary.json`：有效日數、每日平均值、糖分警示日清單和使用的門檻。
- `output/nutrition_trend.png`：每日熱量與糖分趨勢圖。
- `output/pfc_breakdown.png`：PFC 熱量占比圖。

## Agent 3 輸出

- `output/final_audit_report.csv`：品項、標示熱量、公式熱量、差異 kcal、差異百分比、`PASS`／`WARNING` 和原因。
- `output/recommendations.md`：引用品項和資料來源的替換建議。

## 不可省略的追溯資訊

任何補值、異常、警示或建議都必須能回到原始列、資料來源或設定檔。數值估算不可寫成官方標示；法規或健康建議若未有正式來源，必須明確標記為專案示範設定。
