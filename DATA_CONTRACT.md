# 飲食照妖鏡資料交接合約

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
| `source_type` | 文字 | `ai_image`、`ai_video`、`manual`、`csv` 或 `database` |
| `source_reference` | 文字 | 上傳檔案識別、資料來源或 `user-entered` |
| `confidence` | 0 至 1 或空白 | OCR／影片辨識信心值；手動輸入可留空 |
| `user_confirmed` | 布林值 | 使用者確認前為 `false`，確認後才可進入統計 |

`source_type=ai_image` 或 `ai_video` 的資料必須先進入待確認狀態。未確認資料不可交給 Agent 2 統計；若 AI 分析結果被修改，網站要保留修改後的數值和來源標記。AI API 金鑰只能放在後端環境變數。

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

- Agent 2 只統計 Agent 1 的 `status_flag` 為 `OK` 或 `MISSING_FILLED` 的資料列。`EXCLUDED_UNRESOLVABLE_MISSING` 和 `EXCLUDED_ANOMALY` 不得進入任何合計、平均、比例或排名。

- `output/daily_summary.csv`：每一列代表一個有有效資料的日期，欄位固定如下：

| 欄位 | 單位／格式 | 說明 |
|---|---|---|
| `date` | `YYYY-MM-DD` | 統計日期 |
| `total_kcal` | kcal | 當日有效資料的熱量總和 |
| `total_protein_g` | g | 當日蛋白質總和 |
| `total_fat_g` | g | 當日脂肪總和 |
| `total_carbs_g` | g | 當日碳水總和 |
| `total_sugar_g` | g | 當日糖分總和 |
| `protein_pct` | % | 蛋白質熱量占 PFC 熱量百分比 |
| `fat_pct` | % | 脂肪熱量占 PFC 熱量百分比 |
| `carbs_pct` | % | 碳水熱量占 PFC 熱量百分比 |
| `sugar_warning` | `TRUE`／`FALSE` | 糖分克數或糖分熱量占比達到設定門檻時為 `TRUE` |

  PFC 熱量公式為 `protein_g × 4`、`carbs_g × 4`、`fat_g × 9`。PFC 分母為零時，三個百分比必須輸出 `0.0`。

- `output/weekly_summary.json`：一個 JSON 物件，欄位固定如下：

| 欄位 | 格式 | 說明 |
|---|---|---|
| `period` | `YYYY-MM-DD/YYYY-MM-DD` | 輸入有效資料的涵蓋期間 |
| `valid_days` | 整數 | 有效資料日期數，不包含全為排除列的日期 |
| `daily_average` | 物件 | `total_kcal`、`total_protein_g`、`total_fat_g`、`total_carbs_g`、`total_sugar_g` 的有效日平均 |
| `sugar_warning_days` | 日期陣列 | `daily_summary.csv` 中 `sugar_warning=TRUE` 的日期 |
| `highest_calorie_day` | 物件 | `date` 與 `total_kcal`；同分時取日期較早者 |
| `frequent_items` | 物件陣列 | 依出現次數遞減的常吃品項摘要，包含 `item_name`、`count`、`total_kcal`、`total_sugar_g` |
| `item_counts` | 物件 | 品項名稱到有效出現次數的映射 |
| `category_summary` | 物件陣列 | 依 `meal_type` 分類，包含 `meal_type`、`count`、`total_kcal`、`total_protein_g`、`total_fat_g`、`total_carbs_g`、`total_sugar_g` |
| `thresholds` | 物件 | 原樣記錄 `references/thresholds.yml` 的 `sugar.warning_g_per_day` 與 `sugar.warning_energy_share` |
| `source` | 物件 | `input_file`、`included_status_flags` 和 `valid_row_count`，供追溯統計範圍 |

  `frequent_items` 預設列出所有品項並依 `count` 遞減、品名排序；使用者介面可再取前 N 名。`category_summary` 使用輸入欄位 `meal_type` 作為類別，因 Agent 1 輸出沒有額外的食品類別欄位。

- `output/monthly_summary.csv`：每一列代表一個月份，欄位固定如下：

| 欄位 | 單位／格式 | 說明 |
|---|---|---|
| `month` | `YYYY-MM` | 統計月份 |
| `valid_days` | 整數 | 該月份有有效資料的日期數 |
| `total_kcal` | kcal | 月熱量總和 |
| `total_protein_g` | g | 月蛋白質總和 |
| `total_fat_g` | g | 月脂肪總和 |
| `total_carbs_g` | g | 月碳水總和 |
| `total_sugar_g` | g | 月糖分總和 |
| `average_kcal_per_day` | kcal/day | 以有效日數計算的每日平均熱量 |
| `average_sugar_g_per_day` | g/day | 以有效日數計算的每日平均糖分 |
| `sugar_warning_days` | 整數 | 該月份糖分警示日數 |

- `output/nutrition_trend.png`：每日熱量與糖分趨勢圖。
- `output/pfc_breakdown.png`：PFC 熱量占比圖。

糖分警示門檻必須從 `references/thresholds.yml` 讀取：當日 `total_sugar_g` 大於或等於 `warning_g_per_day`，或當日糖分熱量（糖分克數 × 4）除以 `total_kcal` 大於或等於 `warning_energy_share` 時，`sugar_warning` 為 `TRUE`。當 `total_kcal` 為零時，只依糖分克數門檻判斷，且不得除以零。

## Agent 3 輸出

- `output/final_audit_report.csv`：品項、標示熱量、公式熱量、差異 kcal、差異百分比、`PASS`／`WARNING` 和原因。
- `output/recommendations.md`：引用品項和資料來源的替換建議。

## 不可省略的追溯資訊

任何補值、異常、警示或建議都必須能回到原始列、資料來源或設定檔。數值估算不可寫成官方標示；法規或健康建議若未有正式來源，必須明確標記為專案示範設定。
