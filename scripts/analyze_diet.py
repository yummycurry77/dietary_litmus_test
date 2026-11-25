"""Agent 2: daily/weekly nutrition analysis and charts."""
from __future__ import annotations
import argparse, csv, json
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VALID = {"OK", "MISSING_FILLED"}

def load_thresholds(path: Path) -> dict:
    out, section = {}, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip(): continue
        if not line.startswith(" "):
            section = line.rstrip(":").strip(); out[section] = {}; continue
        if section:
            k, _, v = line.strip().partition(":")
            try: v = float(v.strip())
            except ValueError: v = v.strip()
            out[section][k.strip()] = v
    return out

def chart(path: Path, title: str, labels: list[str], values: list[float], color=(43,110,170), ylabel=""):
    w, h, left, bottom = 1100, 620, 90, 100
    im = Image.new("RGB", (w,h), "white"); d = ImageDraw.Draw(im)
    d.text((left, 25), title, fill="black")
    maxv = max(values or [1]); plot_h = h-bottom-55; plot_w = w-left-40
    d.line((left,55,left,h-bottom), fill=(80,80,80), width=2); d.line((left,h-bottom,w-40,h-bottom), fill=(80,80,80), width=2)
    n=max(1,len(values)); bw=max(8, plot_w//n-12)
    for i,v in enumerate(values):
        x=left+10+i*plot_w//n; y=h-bottom-int(v/maxv*plot_h)
        d.rectangle((x,y,x+bw,h-bottom), fill=color)
        d.text((x, h-bottom+8), labels[i][-5:], fill="black")
        d.text((x, max(58,y-18)), f"{v:.0f}", fill="black")
    d.text((10, 55), ylabel, fill="black")
    im.save(path)

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--input", type=Path, default=Path("output/cleaned_diet_log.csv")); ap.add_argument("--thresholds", type=Path, default=Path("references/thresholds.yml")); ap.add_argument("--out-dir", type=Path, default=Path("output")); args=ap.parse_args()
    rows=[]
    with args.input.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("status_flag") in VALID: rows.append(r)
    if not rows: raise SystemExit("[Agent 2] 沒有可統計的 OK 或 MISSING_FILLED 資料")
    t=load_thresholds(args.thresholds); sugar_limit=float(t["sugar"]["warning_g_per_day"])
    by=defaultdict(lambda: defaultdict(float))
    for r in rows:
        day=by[r["date"]]
        for k in ("actual_kcal","actual_protein_g","actual_fat_g","actual_carbs_g","actual_sugar_g"): day[k]+=float(r[k])
    args.out_dir.mkdir(parents=True, exist_ok=True); dates=sorted(by)
    fields=["date","valid_item_count","kcal","protein_g","fat_g","carbs_g","sugar_g","protein_pct","fat_pct","carbs_pct","sugar_warning"]
    with (args.out_dir/"daily_summary.csv").open("w",encoding="utf-8-sig",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=fields); wr.writeheader()
        for date in dates:
            x=by[date]; p=x["actual_protein_g"]*4; c=x["actual_carbs_g"]*4; fat=x["actual_fat_g"]*9; den=p+c+fat
            wr.writerow({"date":date,"valid_item_count":sum(r["date"]==date for r in rows),"kcal":round(x["actual_kcal"],1),"protein_g":round(x["actual_protein_g"],1),"fat_g":round(x["actual_fat_g"],1),"carbs_g":round(x["actual_carbs_g"],1),"sugar_g":round(x["actual_sugar_g"],1),"protein_pct":round(p/den*100,2) if den else 0,"fat_pct":round(fat/den*100,2) if den else 0,"carbs_pct":round(c/den*100,2) if den else 0,"sugar_warning":"WARNING" if x["actual_sugar_g"]>=sugar_limit else "OK"})
    avg={k:round(sum(by[d][k] for d in dates)/len(dates),1) for k in ("actual_kcal","actual_protein_g","actual_fat_g","actual_carbs_g","actual_sugar_g")}
    weekly={"valid_days":len(dates),"valid_rows":len(rows),"daily_average":avg,"sugar_warning_g_per_day":sugar_limit,"sugar_warning_dates":[d for d in dates if by[d]["actual_sugar_g"]>=sugar_limit],"source":"output/cleaned_diet_log.csv","status_filter":sorted(VALID)}
    (args.out_dir/"weekly_summary.json").write_text(json.dumps(weekly,ensure_ascii=False,indent=2),encoding="utf-8")
    chart(args.out_dir/"nutrition_trend.png","Daily calories and sugar",dates,[by[d]["actual_kcal"] for d in dates],ylabel="kcal")
    chart(args.out_dir/"pfc_breakdown.png","Daily PFC calories",dates,[by[d]["actual_protein_g"]*4+by[d]["actual_carbs_g"]*4+by[d]["actual_fat_g"]*9 for d in dates],color=(65,145,90),ylabel="kcal")
    print(f"[Agent 2 quality gate] PASS: {len(rows)} valid rows, {len(dates)} days, sugar warnings {len(weekly['sugar_warning_dates'])}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
