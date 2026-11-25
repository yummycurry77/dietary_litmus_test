# 成員四繳交資料（Agent 3 覆核、解說影片與 AI Tutor）

> 本文件為繳交前的填寫模板。上傳影片與建立 AI Tutor 後補上連結與測試紀錄。
> **匿名規範**：本文件不得出現組別編號、姓名、學號、Email 或任何可辨識身分的資訊。

## 1. 負責範圍與交付狀態

| 項目 | 交付物 | 狀態 |
|---|---|---|
| Agent 3 規格 | `agents/agent3_auditor.md` | 已完成 |
| 公式覆核腳本 | `scripts/audit_nutrition.py` | 已完成 |
| 替換對照庫 | `references/smart_swap_guide.md` | 已完成 |
| 覆核輸出 | `output/final_audit_report.csv`、`output/recommendations.md` | 已完成（已以最終版本重跑，quality gate PASS） |
| 解說影片 | YouTube 連結（見第 2 節） | 待完成 |
| AI Tutor | ClassTutor 連結與實測（見第 3 節） | 待完成 |

## 2. 解說影片

| 項目 | 紀錄 |
|---|---|
| YouTube 連結 | 待填 |
| 時長 | 待填（建議 5 分鐘內，上限 6 分鐘） |
| 使用的 commit | 待填（須等於最終提交版本） |
| 中文字幕 | 待填（字幕檔路徑或 YouTube 內嵌字幕） |

### 建議時間軸

| 時間 | 內容 |
|---|---|
| 0:00–0:40 | 題目與三角色流程簡介 |
| 0:40–1:30 | Agent 1 標準化：單位換算、補值與異常隔離 |
| 1:30–3:50 | Agent 3 實測：公式覆核、20% 判定門檻與 WARNING 案例 |
| 3:50–4:40 | 替換建議與資料來源／估算標註 |
| 4:40–5:00 | Skill 啟動證據與測試 A／B／C 結果 |

### Skill 啟動證據

| 項目 | 紀錄 |
|---|---|
| 觸發方式 | 自動觸發／手動指定（必須如實填寫，不可冒充自動啟動） |
| 執行歷程或 Log 位置 | 待填 |
| 對應錄影段落 | 待填 |

## 3. AI Tutor（ClassTutor）

| 項目 | 紀錄 |
|---|---|
| ClassTutor 連結 | 待填 |
| 匯入的影片與字幕 | 待填 |

### 兩題實測紀錄

**問題 1：哪一段測試證明 Skill 有啟動？**

| 項目 | 紀錄 |
|---|---|
| AI Tutor 回答 | 待填 |
| 指向的影片時間點 | 待填 |
| 是否正確 | 待填 |

**問題 2：Agent 3 如何判定熱量標示誤差是否合理？**

| 項目 | 紀錄 |
|---|---|
| AI Tutor 回答 | 待填 |
| 指向的影片時間點 | 待填 |
| 是否正確 | 待填 |

## 4. 執行紀錄（本地驗證）

以下指令皆在 repository 根目錄執行，結果如註記：

| 指令 | 結果 |
|---|---|
| `python scripts/clean_data.py --input sample-data/weekly_diet_log.csv --db references/food_nutrition_db.csv --out-csv output/cleaned_diet_log.csv --out-report output/agent1_quality_report.json` | PASS：原始 23 筆、有效 20 筆、排除 3 筆 |
| `python scripts/validate_agent1_output.py` | PASS：23 input rows、20 valid、3 excluded |
| `python scripts/audit_nutrition.py` | PASS：納入 20 列（PASS 19、WARNING 1）、排除 3 列；quality gate 通過 |
| `python scripts/audit_nutrition.py --thresholds <缺少門檻的設定檔>` | 依預期失敗（exit 1），明確回報門檻不得在程式碼中寫死 |
| `python scripts/check_anonymity.py .` | PASS：無 email、絕對路徑或 API Key 型態 |

### `INTEGRATION_CHECKLIST.md` Agent 3 六項自我驗證

| 檢查項 | 驗證方式與證據 |
|---|---|
| 公式使用蛋白質 × 4、碳水 × 4、脂肪 × 9 | `scripts/audit_nutrition.py` 的 `KCAL_PER_G` 與 `theoretical_kcal()`；抽查第 2 列 248.3 kcal 可人工重算 |
| 標示熱量為 0 時有明確的差異處理 | `audit_row()` 三分支：公式亦為 0 → `PASS`；公式 > 0 → `diff_pct` 留空並判 `WARNING`，`reason` 說明需人工確認 |
| `PASS`／`WARNING` 門檻從設定檔讀取 | 門檻只讀 `references/thresholds.yml`；設定檔缺值時腳本直接中止，不在程式碼留預設值（負向測試見上表） |
| 每筆警示可追溯到品項與原始列 | `final_audit_report.csv` 含 `source_row`、`date`、`item_name`；quality gate 檢查筆數與欄位 |
| 建議標明來源和估算限制 | `smart_swap_guide.md` 每列含「資料來源」欄；`recommendations.md` 第六節為限制聲明，估算值標「示範估算（非官方標示）」 |
| 沒有把專案門檻寫成法規或醫療結論 | `recommendations.md` 第六節與 `thresholds.yml` 註解皆標明為專案示範設定，非法規判定或醫療結論 |

## 5. 提交前自我檢查

- [ ] 影片使用的檔案版本等於最終 commit（待影片完成）
- [ ] 影片有清楚拍到 Skill 啟動歷程（不是只拍最終答案）（待影片完成）
- [ ] 時長在 6 分鐘內且有中文字幕（待影片完成）
- [ ] AI Tutor 兩題都能正確指向影片時間點（待影片完成）
- [x] `output/` 由最終版腳本重跑產生
- [x] 通過 `python scripts/check_anonymity.py .`
- [x] 本文件無姓名、學號、組別、Email 或本機路徑
