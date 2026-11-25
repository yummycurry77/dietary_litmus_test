const demoRecords = [
  { date:'2026-11-10', meal_type:'早餐', item_name:'紐奧良風味鮮蔬烤雞三明治', kcal:248, protein_g:14.2, fat_g:7.5, carbs_g:31, sugar_g:4.2 },
  { date:'2026-11-10', meal_type:'午餐', item_name:'健身 G 肉餐盒', kcal:512, protein_g:38.5, fat_g:11.2, carbs_g:64.3, sugar_g:3.5 },
  { date:'2026-11-10', meal_type:'飲料', item_name:'珍珠紅茶拿鐵（半糖大杯）', kcal:465, protein_g:6.2, fat_g:8.5, carbs_g:91, sugar_g:42 },
  { date:'2026-11-11', meal_type:'早餐', item_name:'鮪魚御飯糰', kcal:215, protein_g:5.8, fat_g:4.2, carbs_g:38.5, sugar_g:1.5 },
  { date:'2026-11-11', meal_type:'晚餐', item_name:'雙拼炸雞排便當', kcal:885, protein_g:32, fat_g:36.5, carbs_g:107, sugar_g:8.2 },
  { date:'2026-11-11', meal_type:'飲料', item_name:'熟成紅茶（全糖大杯）', kcal:260, protein_g:0, fat_g:0, carbs_g:65, sugar_g:62 },
  { date:'2026-11-12', meal_type:'早餐', item_name:'匠土司醇乳香土司', kcal:239, protein_g:7.8, fat_g:4.6, carbs_g:41.5, sugar_g:5.8 },
  { date:'2026-11-12', meal_type:'午餐', item_name:'健身 G 肉餐盒', kcal:512, protein_g:38.5, fat_g:11.2, carbs_g:64.3, sugar_g:3.5 },
];
let records = [...demoRecords]; let period = 'week';
const $ = (selector) => document.querySelector(selector);
const sum = (rows, key) => rows.reduce((total, row) => total + Number(row[key] || 0), 0);
const grouped = () => Object.values(records.reduce((acc, row) => { (acc[row.date] ||= []).push(row); return acc; }, {})).map(rows => ({ date:rows[0].date, kcal:sum(rows,'kcal'), protein_g:sum(rows,'protein_g'), fat_g:sum(rows,'fat_g'), carbs_g:sum(rows,'carbs_g'), sugar_g:sum(rows,'sugar_g') }));
const displayRows = () => period === 'day' ? records.filter(row => row.date === '2026-11-10') : records;
function render() {
  const rows = displayRows(); const days = grouped(); const kcal = sum(rows,'kcal'); const sugar = sum(rows,'sugar_g'); const protein = sum(rows,'protein_g'); const fat = sum(rows,'fat_g'); const carbs = sum(rows,'carbs_g');
  const divisor = period === 'day' ? 1 : Math.max(days.length, 1); const avgKcal = kcal / divisor; const warning = sugar / divisor > 50;
  $('#periodTitle').textContent = period === 'day' ? '今日概況' : period === 'month' ? '本月概況' : '本週概況';
  $('#metricGrid').innerHTML = [['熱量',Math.round(avgKcal),'kcal／日','日均攝取'],['蛋白質',Math.round(protein/divisor),'g','平均攝取'],['糖分',Math.round(sugar/divisor),'g／日',warning?'需要留意':'目前穩定'],['有效紀錄',rows.length,'筆','已確認資料']].map((m,i)=>`<div class="metric ${i===2&&warning?'warn':''}"><span class="metric-label">${m[0]}</span><div class="metric-value">${m[1]}<small>${m[2]}</small></div><span class="metric-note">${m[3]}</span></div>`).join('');
  const max = Math.max(...days.map(d=>d.kcal), 1); $('#trendChart').innerHTML = days.map(d=>`<div class="chart-day"><div class="bar kcal" style="height:${Math.max(6,d.kcal/max*160)}px" title="${d.kcal} kcal"></div><div class="bar sugar" style="height:${Math.max(6,d.sugar/80*160)}px" title="${d.sugar} g 糖分"></div><span class="chart-label">${d.date.slice(5)}</span></div>`).join('');
  const p = protein*4, f = fat*9, c = carbs*4, total = p+f+c || 1; $('#pfcList').innerHTML = [['蛋白質',p,'var(--green)'],['脂肪',f,'var(--yellow)'],['碳水',c,'var(--pink)']].map(x=>`<div class="pfc-item"><i style="background:${x[2]}"></i><span>${x[0]}<small> ${Math.round(x[1]/total*100)}%</small></span><strong>${Math.round(x[1])} kcal</strong></div>`).join('');
  $('#recordsList').innerHTML = rows.slice(-6).reverse().map(r=>`<div class="record"><div><div class="record-name">${r.item_name}</div><div class="record-meta">${r.date} · ${r.meal_type} · 糖分 ${r.sugar_g}g</div></div><div class="record-kcal">${r.kcal} kcal</div></div>`).join('') || '<p class="record-meta">目前沒有紀錄。</p>';
  $('#insightList').innerHTML = warning ? '<div class="insight"><strong>糖分偏高</strong><p>你最近的含糖飲料影響較明顯，可以先把全糖紅茶換成無糖茶，保留原本的飲料習慣。</p></div><div class="insight"><strong>從熟悉的食物延伸</strong><p>早餐常出現吐司，可以試試堅果吐司或在旁邊搭配無糖堅果，補足堅果類攝取。</p></div>' : '<div class="insight"><strong>目前趨勢穩定</strong><p>先持續記錄，累積更多資料後會提供更貼近你習慣的替換建議。</p></div>';
}
$('#demoButton').addEventListener('click',()=>{ records=[...demoRecords]; render(); });
$('#clearButton').addEventListener('click',()=>{ records=[]; render(); });
$('#manualButton').addEventListener('click',()=>{ $('#manualForm').reset(); $('#manualForm input[name=date]').value='2026-11-10'; $('#manualDialog').showModal(); });
$('#photoButton').addEventListener('click',()=>$('#photoInput').click());
$('#photoInput').addEventListener('change',(e)=>{ if(e.target.files[0]) alert('照片已收到。正式版本會在這裡進行 OCR，並先讓你確認營養標示。'); });
document.querySelectorAll('.period-tab').forEach(button=>button.addEventListener('click',()=>{ document.querySelectorAll('.period-tab').forEach(b=>b.classList.remove('active')); button.classList.add('active'); period=button.dataset.period; render(); }));
$('#manualForm').addEventListener('submit',(event)=>{ event.preventDefault(); const data=Object.fromEntries(new FormData(event.target)); records.push({ ...data, kcal:Number(data.kcal), sugar_g:Number(data.sugar_g), protein_g:Number(data.protein_g), fat_g:Number(data.fat_g), carbs_g:Number(data.carbs_g) }); $('#manualDialog').close(); render(); });
$('#csvInput').addEventListener('change',(event)=>{ if(event.target.files[0]) alert('CSV 已收到。正式版本會交給 Agent 1 標準化後再進入報表。'); });
render();
