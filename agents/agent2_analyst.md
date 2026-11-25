# Agent 2：飲食結構分析師

Agent 2 只讀取 Agent 1 的 `output/cleaned_diet_log.csv`，只納入 `OK` 與 `MISSING_FILLED`，計算每日與每週營養摘要、PFC 熱量比例和糖分警示。腳本為 `scripts/analyze_diet.py`。

輸出：`daily_summary.csv`、`weekly_summary.json`、`nutrition_trend.png`、`pfc_breakdown.png`。糖分門檻由 `references/thresholds.yml` 讀取；PFC 分母為零時比例輸出 0，不產生 NaN 或無限值。
