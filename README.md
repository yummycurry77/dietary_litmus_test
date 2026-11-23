# dietary_litmus_test 飲食石蕊試紙

## 專案目的

這個 Skill 協助外食與飲控族檢查超商鮮食、包裝飲品和手搖飲的營養攝取。它會先把不同標示單位換算成實際攝取量，再統計每日與每週的熱量、PFC 和糖分，最後用營養公式覆核資料是否合理。

本專案處理的是可追溯的資料分析流程，不是醫療診斷，也不會在缺乏資料時自行捏造營養數字。

## 三角色流程

```text
原始飲食紀錄
  -> Agent 1 標示標準化
  -> Agent 2 飲食結構分析
  -> Agent 3 公式覆核與建議
  -> 品質檢查
  -> 診斷報告
```

詳細啟動條件、例外處理和品質門檻請見 [`SKILL.md`](SKILL.md)；欄位與檔案交接規格請見 [`DATA_CONTRACT.md`](DATA_CONTRACT.md)。
成員一的分階段工作與完成定義請見 [`MEMBER1_PLAN.md`](MEMBER1_PLAN.md)；Agent 1 的整合評估請見 [`AGENT1_REVIEW.md`](AGENT1_REVIEW.md)。
測試紀錄模板請見 [`test-report.md`](test-report.md)，整合檢查請見 [`INTEGRATION_CHECKLIST.md`](INTEGRATION_CHECKLIST.md)。

## 目錄

```text
SKILL.md                         主控流程、觸發條件與品質門檻
DATA_CONTRACT.md                 Agent 之間的欄位與輸出合約
CONTRIBUTING.md                  GitHub 分支與 Pull Request 規範
agents/                          三個角色的工作說明
scripts/                         資料清理與分析腳本
references/                      基準營養資料和專案設定
sample-data/                     最小可重現測試資料
output/                          執行後產生的交接報告與圖表
```

## 最小重現流程

在 repository 根目錄執行：

```powershell
python scripts/clean_data.py `
  --input sample-data/weekly_diet_log.csv `
  --db references/food_nutrition_db.csv `
  --out-csv output/cleaned_diet_log.csv `
  --out-report output/agent1_quality_report.json
```

目前 repository 內已有 Agent 1 的標準化腳本。Agent 2 和 Agent 3 的腳本完成後，會在相同的 `output/` 目錄交接結果，不改動 Agent 1 的輸出欄位。

成員一可在 Agent 2 接手前執行合約檢查：

```powershell
python scripts/validate_agent1_output.py
```

## 測試資料刻意包含的情境

- `per_100ml` 和 `per_100g` 的單位換算。
- 手搖飲缺少熱量或糖分欄位。
- 查無基準資料的缺值品項。
- 負熱量、過高蛋白質和極端熱量。
- 正常資料與高糖飲品，方便測試每日警示。

## 資料來源

`references/food_nutrition_db.csv` 是本專案的示範基準資料，來源欄位記錄每筆資料的公開標示或資料庫來源。正式報告應保留來源網址、擷取日期與資料版本；若使用模擬資料，必須在報告中明確註明。

## 觸發測試

- A 應啟動：分析一週超商與飲料 CSV，計算三大營養素並找出糖分超標項目。
- B 改寫後仍應啟動：檢查每天吃的東西清單，看熱量和糖分是否過高。
- C 不應啟動：推薦台北車站附近好吃的拉麵店。

測試時要記錄觸發結果、執行歷程、輸出檔案和任何 `SKILL.md` 修正。

提交前可執行匿名檢查：

```powershell
python scripts/check_anonymity.py .
```
