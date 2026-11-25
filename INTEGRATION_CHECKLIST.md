# 成員一整合檢查清單

每個 Agent 的 PR 合併前都要完成一次；三個 Agent 全部完成後再做一次端到端檢查。

## Agent 1

- [x] `output/cleaned_diet_log.csv` 欄位符合資料合約
- [x] 原始列數與輸出列數一致
- [x] 有效狀態值只有 `OK` 或 `MISSING_FILLED`
- [x] 排除列保留，且排除列的營養數值為 0
- [x] `agent1_quality_report.json` 的筆數可由輸出重算
- [ ] 基準資料補值有來源網址、日期或版本

## Agent 2

- [x] 只統計 `OK` 和 `MISSING_FILLED`
- [x] 缺少日期或營養數值時有明確錯誤訊息
- [x] 每日合計、每週平均和圖表使用相同資料範圍
- [x] PFC 分母為零時不產生 NaN 或無限值
- [x] 糖分警示門檻從 `references/thresholds.yml` 讀取
- [x] 輸出檔名和欄位符合 `DATA_CONTRACT.md`

## Agent 3

- [ ] 公式使用蛋白質 × 4、碳水 × 4、脂肪 × 9
- [ ] 標示熱量為 0 時有明確的差異處理
- [ ] `PASS`／`WARNING` 門檻從設定檔讀取
- [ ] 每筆警示可追溯到品項與原始列
- [ ] 建議標明來源和估算限制
- [ ] 沒有把專案門檻寫成法規或醫療結論

## 最終交付

- [ ] A／B／C 測試全部有提示詞、結果和證據
- [ ] 影片使用的檔案版本等於最終 commit
- [ ] AI Tutor 能回答兩題並指向影片時間點
- [ ] README 指令能在乾淨資料夾重現結果
- [ ] ZIP 不含 `.git`、API Key、個資、Email 或本機絕對路徑
