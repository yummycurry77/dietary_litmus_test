# GitHub 協作規範

## 分支

- `main` 只放已整合、可重現的版本。
- 成員 1：`feat/skill-core`
- 成員 2：`feat/agent1-data`
- 成員 3：`feat/agent2-analytics`
- 成員 4：`feat/agent3-audit`

不要直接推送 `main`。每項工作先開 Issue，再從 `main` 開分支，完成後提交 Pull Request。

## Pull Request 必填內容

1. 變更目的和對應 Issue。
2. 修改或新增的檔案。
3. 執行過的指令與結果。
4. 是否影響 `DATA_CONTRACT.md`。
5. 若有圖表或報告，附上輸出檔案路徑。

## 合併前檢查

- 欄位名稱、單位和狀態值符合 `DATA_CONTRACT.md`。
- 不提交 API Key、個人資料、本機絕對路徑或組員身分資訊。
- 不將測試用輸出誤當成新的輸入資料。
- 需要修改其他成員負責的檔案時，先在 PR 說明原因。
