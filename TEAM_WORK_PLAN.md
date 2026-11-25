# 四位組員完整工作內容

本文件把專案分成四個可以平行進行、最後能串接的工作。每位組員都要在自己的分支完成工作，使用 Pull Request 合併到 `main`。所有欄位、檔名和狀態值以 `DATA_CONTRACT.md` 為準。

## 專案共同目標

建立「超商與手搖飲營養熱量診斷員」，讓使用者可以：

1. 上傳飲食 CSV 或手動輸入資料。
2. 未來可用照片或影片擷取營養標示。
3. 統計每日、每週和每月的熱量與營養素。
4. 找出糖分、熱量或特定營養素的不足與超標。
5. 根據個人常吃的食物產生容易執行的替代建議。

共同流程：

```text
網站或 CSV 輸入
  -> Agent 1 資料擷取與標準化
  -> Agent 2 日週月飲食分析
  -> Agent 3 公式覆核與個人化建議
  -> Quality Gate
  -> 網站報告、測試紀錄與影片展示
```

## 組員一：系統架構師與 GitHub 整合負責人

組員一負責定義規則，讓其他三人的成果可以互相接上，並負責最終整合、測試和交付。

### 具體工作

1. 維護 `SKILL.md`，定義用途、啟動條件、排除條件和三角色流程。
2. 維護 `DATA_CONTRACT.md`，固定欄位、單位、狀態值和輸出檔名。
3. 維護 `README.md`，說明安裝、執行、資料來源和重現步驟。
4. 維護 `CONTRIBUTING.md` 與 PR 範本，管理分支和審查流程。
5. 審查組員二、三、四的 PR，檢查是否改動合約或造成輸出不相容。
6. 執行合約驗證和完整整合檢查。
7. 維護 A／B／C 測試紀錄，保留觸發證據和失敗修正紀錄。
8. 確認影片、AI Tutor、程式碼和測試資料使用同一個版本。
9. 執行匿名檢查和最終 ZIP 打包。

### 網站架構責任

- OCR、手動輸入和 CSV 輸入都轉成同一種標準資料格式。
- 每筆紀錄保存 `source_type`，例如 `ocr`、`manual`、`csv` 或 `database`。
- OCR 結果在寫入前必須讓使用者確認。
- 不確定的辨識值要有 `confidence` 或警示狀態。
- 日、週、月報表都從同一批標準化紀錄產生。

### 負責檔案

```text
SKILL.md
README.md
DATA_CONTRACT.md
CONTRIBUTING.md
MEMBER1_PLAN.md
AGENT1_REVIEW.md
INTEGRATION_CHECKLIST.md
test-report.md
scripts/validate_agent1_output.py
scripts/check_anonymity.py
```

### 驗收條件

- 三個 Agent 的輸入輸出有明確交接格式。
- A／B／C 測試都有提示詞、結果和證據位置。
- 三個 Agent 能使用同一批資料完成流程。
- README 指令可以重現結果。
- 最終檔案不含個資、API Key 或本機路徑。

## 組員二：資料工程師與 Agent 1 負責人

組員二負責資料來源、營養標示標準化、缺值處理、異常偵測和第一階段輸出。

### 具體工作

1. 蒐集衛福部資料、超商公開營養標示和手搖飲公開菜單。
2. 建立 `references/food_nutrition_db.csv`，記錄品項、類別、單位、營養值和來源。
3. 建立最小可重現資料 `sample-data/weekly_diet_log.csv`。
4. 刻意加入每 100g／每 100ml、缺值和異常值，方便影片展示。
5. 撰寫 `agents/agent1_normalizer.md` 和 `scripts/clean_data.py`。
6. 將不同標示單位換算成實際攝取量。
7. 標記缺失營養素，不可把估算值當成原始官方值。
8. 將負數、零份量和極端值隔離，保留原始列與排除原因。
9. 產生 `output/cleaned_diet_log.csv` 和 `output/agent1_quality_report.json`。

### 負責檔案

```text
agents/agent1_normalizer.md
scripts/clean_data.py
references/food_nutrition_db.csv
sample-data/weekly_diet_log.csv
output/cleaned_diet_log.csv
output/agent1_quality_report.json
```

### 驗收條件

- 輸入列數和輸出列數一致。
- 可驗證單位換算倍率。
- 缺值和補值欄位有紀錄。
- 異常列沒有被無聲刪除。
- Agent 1 合約驗證通過。
- 每筆資料的來源可以追溯。

## 組員三：資料分析師與 Agent 2 負責人

組員三負責將 Agent 1 的標準化資料轉成每日、每週和每月的飲食分析與圖表。

### 具體工作

1. 撰寫 `agents/agent2_analyst.md` 和 `scripts/analyze_plot.py`。
2. 只統計 `OK` 和 `MISSING_FILLED`。
3. 計算每日總熱量、蛋白質、脂肪、碳水和糖分。
4. 計算一週每日平均值；資料足夠時產生月報。
5. 使用蛋白質 × 4、碳水 × 4、脂肪 × 9 計算 PFC 比例。
6. 從 `references/thresholds.yml` 讀取糖分警示門檻。
7. 找出糖分超標日、熱量最高日和常吃品項。
8. 產生個人化建議所需的常吃品項與類別摘要。
9. 產生每日熱量／糖分趨勢圖和 PFC 圖表。
10. 撰寫測試 A／B／C 的分析結果與執行證據。

### 負責檔案

```text
agents/agent2_analyst.md
scripts/analyze_plot.py
output/daily_summary.csv
output/weekly_summary.json
output/monthly_summary.csv
output/nutrition_trend.png
output/pfc_breakdown.png
```

### 驗收條件

- 不統計 Agent 1 排除的列。
- 每日、每週和每月統計使用同一批有效資料。
- PFC 分母為零時不產生錯誤數值。
- 糖分門檻來自設定檔。
- 圖表有標題、座標軸、單位和日期。
- 輸出符合 `DATA_CONTRACT.md`。

## 組員四：品質覆核、個人化建議、影片與 AI Tutor 負責人

組員四負責 Agent 3、公式覆核、飲食替換建議、影片、字幕和 AI Tutor。

### 具體工作

1. 撰寫 `agents/agent3_auditor.md`。
2. 讀取 Agent 1 的標準化資料與 Agent 2 的統計摘要。
3. 計算 `protein_g × 4 + carbs_g × 4 + fat_g × 9`。
4. 比較公式熱量與標示熱量，計算差異 kcal 和百分比。
5. 從 `references/thresholds.yml` 讀取覆核門檻。
6. 對 `PASS` 和 `WARNING` 說明判定原因。
7. 建立 `references/smart_swap_guide.md`。
8. 根據常吃品項和不足營養素提供替換建議。
9. 建議要包含原品項、替代品、營養差異和來源。
10. 錄製約 5 分鐘操作影片，展示實際資料、三角色流程和啟動證據。
11. 製作同步中文字幕，確認影片不超過 6 分鐘。
12. 建立 AI Tutor，測試至少 2 題能指向影片時間點的問題。

### 個人化建議規則

推薦時參考使用者缺少或超標的營養素、常吃品項、口味、購買便利性、預算、過敏和飲食目標。例如使用者常吃吐司但堅果類不足，可推薦堅果吐司或堅果麵包，並標明這是一般飲食建議。

### 負責檔案

```text
agents/agent3_auditor.md
references/smart_swap_guide.md
output/final_audit_report.csv
output/recommendations.md
submission.md
影片與字幕檔案
AI Tutor 測試紀錄
```

### 驗收條件

- 公式結果可由人工抽查。
- 標示熱量為 0 時有明確處理。
- 每個警示和建議都能追溯到品項或摘要。
- 影片顯示實際操作、Skill 啟動證據和完整三角色流程。
- 字幕與口頭說明同步。
- AI Tutor 能回答兩題並提供影片時間點。

## 共同時程

1. **規格對齊**：組員一完成資料合約，四人確認欄位、輸出檔案和狀態值。
2. **平行製作**：組員二、三、四各自完成 Agent 內容並提交 PR。
3. **整合驗證**：組員一依序審查三個 Agent，執行合約和端到端流程。
4. **展示與交付**：組員四完成影片與 AI Tutor，組員一確認版本、測試、匿名檢查和 ZIP。

## 每個 PR 都必須附上

- 修改目的
- 修改檔案
- 執行過的指令與結果
- 是否修改 `DATA_CONTRACT.md`
- 是否新增或修改輸出檔案
- 是否含有個人資料、API Key 或本機路徑
