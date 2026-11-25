# 組員一實作規格

本文件是組員一目前要完成的實作內容。它把網站構想轉成其他組員可以直接接手的介面，不負責取代 Agent 1、Agent 2 或 Agent 3 的核心程式。

## 1. 組員一的完成範圍

組員一需要完成四件事：

1. 定義 Skill 和三個 Agent 的執行流程。
2. 定義網站、資料檔案與 Agent 之間的資料格式。
3. 提供合約驗證、匿名檢查和整合測試工具。
4. 在其他組員提交後，負責合併、端到端測試和最終交付。

## 2. 網站版資料流程

```text
使用者上傳照片／影片／CSV／手動輸入
        |
        v
輸入確認頁：顯示辨識值、來源和信心狀態
        |
        v
Agent 1：轉成 normalized_diet_log
        |
        v
Agent 2：產生 daily、weekly、monthly summary
        |
        v
Agent 3：覆核熱量並產生個人化建議
        |
        v
Quality Gate：檢查筆數、單位、來源和警示
        |
        v
網站報告頁與匯出檔案
```

照片或影片辨識的結果必須先進入「待確認」狀態，使用者確認後才能進入正式統計。手動輸入和 OCR 輸入最後都要轉成相同的欄位。

## 3. 網站輸入介面

網站前端可以提供三種輸入方式：

| 輸入方式 | 必填資料 | 必須保留的追溯資訊 |
|---|---|---|
| 營養標示照片 | 圖片、日期、食用份量 | `source_type=ocr`、圖片識別結果、信心值 |
| 食物或飲料影片 | 影片、日期、食用份量 | `source_type=video`、抽幀或辨識紀錄 |
| 手動輸入／CSV | 品項、日期、營養值或資料庫品項 | `source_type=manual` 或 `csv` |

輸入層至少要能傳遞下列欄位：

```json
{
  "date": "2026-11-10",
  "meal_type": "早餐",
  "item_name": "示範品項",
  "source_type": "manual",
  "source_reference": "user-entered",
  "confidence": null,
  "unit_type": "per_serving",
  "base_amount": 1,
  "actual_amount": 1,
  "kcal": 300,
  "protein_g": 12,
  "fat_g": 8,
  "carbs_g": 40,
  "sugar_g": 8,
  "user_confirmed": true
}
```

網站可使用 `source_type=ocr`、`video`、`manual`、`csv` 或 `database`。`user_confirmed` 為 `false` 時，資料不能進入 Agent 2 統計。

## 4. 網站輸出介面

網站報告頁應能顯示：

- 每日熱量與營養素總量。
- 每週平均與每日趨勢。
- 每月總量或平均值（資料期間足夠時）。
- PFC 比例。
- 糖分或熱量警示日。
- 被排除的資料和排除原因。
- 個人常吃品項與營養缺口。
- 替代建議、建議理由和資料來源。

網站不應把 OCR 估計值直接顯示成確定的官方營養標示；要顯示來源和不確定性。

## 5. GitHub 階段工作

### 階段 A：規格完成

- 維護 `SKILL.md`、`DATA_CONTRACT.md` 和本文件。
- 確認三個 Agent 的檔名、欄位和狀態值。
- 確認組員的分支和 PR 規則。

### 階段 B：組員成果審查

- Agent 1：執行 `scripts/validate_agent1_output.py`。
- Agent 2：檢查每日、每週、每月統計和圖表。
- Agent 3：檢查公式、警示和建議追溯。
- 發現欄位變更時，要求先更新 `DATA_CONTRACT.md`。

### 階段 C：端到端測試

依序重跑 Agent 1、Agent 2、Agent 3，確認每個輸出都使用同一版本資料。完成 `test-report.md` 的 A／B／C 測試，並保留失敗與修正證據。

### 階段 D：最終交付

- 執行 `scripts/check_anonymity.py .`。
- 從乾淨資料夾重跑 README 的指令。
- 確認影片和 AI Tutor 使用最後 commit。
- 移除 `.git` 後製作匿名 ZIP。

## 6. 組員一的驗收清單

- [ ] `SKILL.md` 明確定義應啟動與不應啟動。
- [ ] `DATA_CONTRACT.md` 定義輸入、輸出、單位和狀態。
- [ ] OCR、影片、手動和 CSV 都有共同輸入格式。
- [ ] OCR 結果在使用者確認後才統計。
- [ ] Agent 1 合約驗證通過。
- [ ] Agent 2 和 Agent 3 的 PR 已審查。
- [ ] A／B／C 測試有實際證據。
- [ ] 網站報告可追溯到原始資料。
- [ ] README 指令可重現。
- [ ] 匿名檢查和最終 ZIP 檢查通過。
