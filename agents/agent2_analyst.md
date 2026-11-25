# Agent 2：飲食紀錄與報表分析員

## 1. 角色和用途

Agent 2 接收 Agent 1 已標準化的飲食紀錄，將有效資料彙整成每日、每週和每月分析，並產生營養趨勢圖與 PFC 熱量比例圖。分析結果供使用者查看，也提供 Agent 3 進行公式覆核和個人化建議。

Agent 2 只負責資料統計與視覺化，不重新辨識營養標示、不補充營養數值，也不提供醫療診斷。

## 2. 輸入檔案與欄位

主要輸入檔案：

```text
output/cleaned_diet_log.csv
```

必要欄位如下：

| 欄位 | 說明 |
|---|---|
| `date` | `YYYY-MM-DD` 格式的食用日期 |
| `meal_type` | 早餐、午餐、晚餐、點心或飲料等類別 |
| `item_name` | 食品或飲品名稱 |
| `actual_kcal` | 實際攝取熱量，單位 kcal |
| `actual_protein_g` | 實際攝取蛋白質，單位 g |
| `actual_fat_g` | 實際攝取脂肪，單位 g |
| `actual_carbs_g` | 實際攝取碳水化合物，單位 g |
| `actual_sugar_g` | 實際攝取糖分，單位 g |
| `status_flag` | Agent 1 的資料狀態 |
| `audit_note` | 換算、補值或排除原因，供追溯使用 |

糖分警示設定檔：

```text
references/thresholds.yml
```

Agent 2 讀取其中的 `sugar.warning_g_per_day` 和 `sugar.warning_energy_share`。

## 3. 有效資料和排除資料

只有以下狀態會納入統計：

```text
OK
MISSING_FILLED
```

`MISSING_FILLED` 代表 Agent 1 已從基準資料補齊缺少的營養值，仍可用於分析，但報表必須保留其狀態與來源可追溯性。

以下狀態不會納入任何合計、平均、比例、排名或圖表：

```text
EXCLUDED_UNRESOLVABLE_MISSING
EXCLUDED_ANOMALY
```

排除列仍保留在 Agent 1 的輸出檔案中，方便追查原始資料和排除原因。Agent 2 不會將排除列的零值當成真實飲食量。

## 4. 統計方式

### 每日統計

依 `date` 分組，將每個有效日期的營養欄位加總：

```text
total_kcal       = Σ actual_kcal
total_protein_g  = Σ actual_protein_g
total_fat_g      = Σ actual_fat_g
total_carbs_g    = Σ actual_carbs_g
total_sugar_g    = Σ actual_sugar_g
```

每日輸出也包含 PFC 百分比和 `sugar_warning` 狀態。

### 每週統計

週報以輸入有效資料的最早日期和最晚日期作為 `period`，每日平均只使用有有效資料的日期：

```text
daily_average = 該欄位每日總量的總和 / 有效日期數
```

週報同時列出糖分警示日、熱量最高日、常吃品項、品項次數和類別摘要。

### 每月統計

依 `YYYY-MM` 分組。月報的總量是該月每日總量的加總；每日平均只除以該月有有效資料的日期數：

```text
average_kcal_per_day = 月 total_kcal / 月有效日數
average_sugar_g_per_day = 月 total_sugar_g / 月有效日數
```

不會把沒有有效資料的日期當成零加入平均值。

## 5. PFC 比例

將克數換算成營養素熱量：

```text
protein_kcal = actual_protein_g × 4
carbs_kcal   = actual_carbs_g × 4
fat_kcal     = actual_fat_g × 9
```

每日 PFC 分母為三者熱量總和：

```text
pfc_total = protein_kcal + carbs_kcal + fat_kcal
```

各比例為：

```text
protein_pct = protein_kcal / pfc_total × 100
carbs_pct   = carbs_kcal / pfc_total × 100
fat_pct     = fat_kcal / pfc_total × 100
```

若 `pfc_total` 小於或等於零，三個比例都輸出 `0.0`，不可產生 `NaN` 或無限值。PFC 圖表則使用所有有效資料的 PFC 熱量總和。

## 6. 糖分警示

門檻來自：

```text
references/thresholds.yml
```

目前設定包含：

```yaml
sugar:
  warning_g_per_day: 50
  warning_energy_share: 0.10
```

當日符合任一條件時，`sugar_warning` 設為 `TRUE`：

```text
total_sugar_g >= warning_g_per_day
```

或：

```text
(total_sugar_g × 4) / total_kcal >= warning_energy_share
```

若 `total_kcal` 為零，只使用糖分克數門檻判斷，且不得除以零。這些是專案示範設定，不應直接解讀為醫療或法規結論。

## 7. 熱量最高日

從每日統計的 `total_kcal` 中找出最大值，輸出日期和熱量：

```json
{
  "date": "YYYY-MM-DD",
  "total_kcal": 0.0
}
```

若有相同熱量，取日期較早者，確保結果穩定且可重現。

## 8. 常吃品項和品項次數

只使用有效資料，依 `item_name` 計算出現次數：

```text
item_counts[item_name] = 有效資料列數
```

`frequent_items` 依出現次數遞減、品名排序輸出，並包含：

- `item_name`
- `count`
- `total_kcal`
- `total_sugar_g`

`item_counts` 則保存所有有效品項的完整次數映射，供後續推薦使用。一次飲食紀錄列計為一次出現。

## 9. 各類別摘要

Agent 1 輸出沒有獨立的食品類別欄位，因此 Agent 2 使用 `meal_type` 作為類別，例如早餐、午餐、晚餐、點心和飲料。

每個類別輸出：

- `meal_type`
- `count`
- `total_kcal`
- `total_protein_g`
- `total_fat_g`
- `total_carbs_g`
- `total_sugar_g`

## 10. 輸出檔案

程式會產生以下五個檔案：

```text
output/daily_summary.csv
output/weekly_summary.json
output/monthly_summary.csv
output/nutrition_trend.png
output/pfc_breakdown.png
```

- `daily_summary.csv`：每日營養合計、PFC 百分比和糖分警示。
- `weekly_summary.json`：有效日數、每日平均、警示日、熱量最高日、常吃品項、品項次數、類別摘要、門檻和來源資訊。
- `monthly_summary.csv`：每月營養總量、有效日數、每日平均和糖分警示日數。
- `nutrition_trend.png`：每日熱量和糖分趨勢，包含日期、標題、座標軸和單位。
- `pfc_breakdown.png`：有效資料的蛋白質、脂肪和碳水熱量占比。

## 11. 錯誤處理與資料限制

程式會在統計前檢查：

- 必要欄位是否存在。
- 有效列的日期是否為 `YYYY-MM-DD`。
- 有效列的營養欄位是否為有限數字。
- 品項名稱和 `meal_type` 是否為空白。
- 設定檔是否包含兩個糖分門檻。

檢查失敗時，程式會指出列號和欄位，並停止產生不完整報表。輸入沒有有效資料時也會停止並顯示原因。

目前資料限制包括：

- 類別摘要使用 `meal_type`，不代表食品營養分類。
- 缺少實際容量、甜度、冰量或加料資訊時，無法進一步分析手搖飲特徵。
- `MISSING_FILLED` 的數值來自 Agent 1 基準資料，應保留其估算或補值來源。
- 警示門檻是專案示範設定，不能取代醫療或營養師判斷。

當環境有 `matplotlib` 時，程式使用它產生圖表；若沒有，會使用 Pillow 產生仍包含標題、日期、座標軸和單位的 PNG 圖表。

## 12. 執行方式

在 repository 根目錄執行：

```powershell
python scripts/analyze_plot.py
```

也可以指定輸入檔、門檻檔和輸出資料夾：

```powershell
python scripts/analyze_plot.py `
  --input output/cleaned_diet_log.csv `
  --thresholds references/thresholds.yml `
  --output-dir output
```

程式預設使用上述三個路徑，因此在 repository 根目錄直接執行即可重現 Agent 2 的輸出。
