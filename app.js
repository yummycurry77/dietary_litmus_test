const demoRecords = [
  { date:'2026-11-10', meal_type:'早餐', item_name:'紐奧良風味鮮蔬烤雞三明治', kcal:248, protein_g:14.2, fat_g:7.5, carbs_g:31, sugar_g:4.2, fiber_g:2.8, vegetable_servings:0.5 },
  { date:'2026-11-10', meal_type:'午餐', item_name:'健身 G 肉餐盒', kcal:512, protein_g:38.5, fat_g:11.2, carbs_g:64.3, sugar_g:3.5, fiber_g:4.2, vegetable_servings:1 },
  { date:'2026-11-10', meal_type:'點心', item_name:'匠土司醇乳香土司', kcal:239, protein_g:7.8, fat_g:4.6, carbs_g:41.5, sugar_g:5.8, fiber_g:1.4, vegetable_servings:0 },
  { date:'2026-11-10', meal_type:'飲料', item_name:'珍珠紅茶拿鐵（半糖大杯）', kcal:465, protein_g:6.2, fat_g:8.5, carbs_g:91, sugar_g:42, fiber_g:0, vegetable_servings:0 },
  { date:'2026-11-11', meal_type:'早餐', item_name:'鮪魚御飯糰', kcal:215, protein_g:5.8, fat_g:4.2, carbs_g:38.5, sugar_g:1.5, fiber_g:1.2, vegetable_servings:0 },
  { date:'2026-11-11', meal_type:'午餐', item_name:'舒肥嫩雞胸＋地瓜', kcal:392, protein_g:42.5, fat_g:2.1, carbs_g:44, sugar_g:9.1, fiber_g:5.4, vegetable_servings:0.5 },
  { date:'2026-11-11', meal_type:'晚餐', item_name:'雙拼炸雞排便當', kcal:885, protein_g:32, fat_g:36.5, carbs_g:107, sugar_g:8.2, fiber_g:3.1, vegetable_servings:0.3 },
  { date:'2026-11-11', meal_type:'飲料', item_name:'熟成紅茶（全糖大杯）', kcal:260, protein_g:0, fat_g:0, carbs_g:65, sugar_g:62, fiber_g:0, vegetable_servings:0 },
  { date:'2026-11-12', meal_type:'早餐', item_name:'匠土司醇乳香土司', kcal:239, protein_g:7.8, fat_g:4.6, carbs_g:41.5, sugar_g:5.8, fiber_g:1.4, vegetable_servings:0 },
  { date:'2026-11-12', meal_type:'午餐', item_name:'健身 G 肉餐盒', kcal:512, protein_g:38.5, fat_g:11.2, carbs_g:64.3, sugar_g:3.5, fiber_g:4.2, vegetable_servings:1 },
  { date:'2026-11-12', meal_type:'晚餐', item_name:'無糖豆漿＋鮪魚御飯糰', kcal:395, protein_g:15.4, fat_g:8.4, carbs_g:41.9, sugar_g:2.3, fiber_g:2.6, vegetable_servings:0 },
  { date:'2026-11-13', meal_type:'早餐', item_name:'光泉無加糖濃豆漿', kcal:206, protein_g:19.1, fat_g:9.8, carbs_g:10.5, sugar_g:2.3, fiber_g:1.5, vegetable_servings:0 },
  { date:'2026-11-13', meal_type:'午餐', item_name:'泡菜豬肉鍋', kcal:348, protein_g:21.5, fat_g:14, carbs_g:34, sugar_g:6.5, fiber_g:4.8, vegetable_servings:1.5 },
  { date:'2026-11-13', meal_type:'晚餐', item_name:'石安牧場溫泉蛋＋烤地瓜', kcal:283, protein_g:13.6, fat_g:5.5, carbs_g:30.2, sugar_g:8.9, fiber_g:4.2, vegetable_servings:0 },
  { date:'2026-11-14', meal_type:'早餐', item_name:'堅果奶油吐司', kcal:318, protein_g:9.1, fat_g:12.4, carbs_g:43.5, sugar_g:9.6, fiber_g:3.8, vegetable_servings:0 },
  { date:'2026-11-14', meal_type:'下午茶', item_name:'優多綠茶（半糖大杯）', kcal:310, protein_g:2.1, fat_g:0.5, carbs_g:74.5, sugar_g:51, fiber_g:0, vegetable_servings:0 },
  { date:'2026-11-15', meal_type:'午餐', item_name:'雙拼炸雞排便當', kcal:885, protein_g:32, fat_g:36.5, carbs_g:107, sugar_g:8.2, fiber_g:3.1, vegetable_servings:0.3 },
  { date:'2026-11-15', meal_type:'飲料', item_name:'芝芝金萱雙Q（微糖大杯）', kcal:438, protein_g:4.5, fat_g:12, carbs_g:78, sugar_g:44, fiber_g:0.5, vegetable_servings:0 },
  { date:'2026-11-16', meal_type:'早餐', item_name:'全麥堅果吐司＋無糖豆漿', kcal:372, protein_g:22.1, fat_g:12.2, carbs_g:43.5, sugar_g:5.4, fiber_g:5.9, vegetable_servings:0 },
  { date:'2026-11-16', meal_type:'午餐', item_name:'健身 G 肉餐盒', kcal:512, protein_g:38.5, fat_g:11.2, carbs_g:64.3, sugar_g:3.5, fiber_g:4.2, vegetable_servings:1 },
  { date:'2026-11-16', meal_type:'下午茶', item_name:'四季春珍波椰（微糖大杯）', kcal:390, protein_g:1.2, fat_g:1.5, carbs_g:93, sugar_g:38.5, fiber_g:0.5, vegetable_servings:0 },
  { date:'2026-11-16', meal_type:'晚餐', item_name:'雞胸沙拉盒', kcal:328, protein_g:31.2, fat_g:9.5, carbs_g:25.1, sugar_g:6.8, fiber_g:6.5, vegetable_servings:2 },
];
const recordsKey = 'dietary-litmus-records';
let records = JSON.parse(localStorage.getItem(recordsKey) || '[]'); let period = 'week';
const profileKey = 'dietary-litmus-profile';
let profile = JSON.parse(localStorage.getItem(profileKey) || 'null');
const $ = (selector) => document.querySelector(selector);
const sum = (rows, key) => rows.reduce((total, row) => total + Number(row[key] || 0), 0);
const todayISO = () => new Date().toISOString().slice(0, 10);
const saveRecords = () => localStorage.setItem(recordsKey, JSON.stringify(records));
const parseCSVLine = (line) => { const cells=[]; let cell=''; let quoted=false; for(let i=0;i<line.length;i+=1){ const ch=line[i]; if(ch==='"' && line[i+1]==='"'){cell+='"';i+=1;} else if(ch==='"'){quoted=!quoted;} else if(ch===','&&!quoted){cells.push(cell.trim());cell='';} else cell+=ch; } cells.push(cell.trim()); return cells; };
const grouped = (rows = records) => Object.values(rows.reduce((acc, row) => { (acc[row.date] ||= []).push(row); return acc; }, {})).map(rows => ({ date:rows[0].date, kcal:sum(rows,'kcal'), protein_g:sum(rows,'protein_g'), fat_g:sum(rows,'fat_g'), carbs_g:sum(rows,'carbs_g'), sugar_g:sum(rows,'sugar_g') }));
const displayRows = () => { const dates = records.map(row => row.date).filter(Boolean).sort(); if (!dates.length) return []; const latest = new Date(`${dates.at(-1)}T00:00:00`); if (period === 'day') return records.filter(row => row.date === dates.at(-1)); if (period === 'month') return records.filter(row => row.date?.slice(0, 7) === dates.at(-1).slice(0, 7)); const start = new Date(latest); start.setDate(start.getDate() - 6); return records.filter(row => { const date = new Date(`${row.date}T00:00:00`); return date >= start && date <= latest; }); };
function render() {
  const rows = displayRows(); const days = grouped(rows); const kcal = sum(rows,'kcal'); const sugar = sum(rows,'sugar_g'); const protein = sum(rows,'protein_g'); const fat = sum(rows,'fat_g'); const carbs = sum(rows,'carbs_g'); const fiber = sum(rows,'fiber_g'); const vegetables = sum(rows,'vegetable_servings');
  const divisor = period === 'day' ? 1 : Math.max(days.length, 1); const avgKcal = kcal / divisor; const warning = sugar / divisor > 50;
  $('#periodTitle').textContent = period === 'day' ? '今日概況' : period === 'month' ? '本月概況' : '本週概況';
  const targets = profile ? calculateTargets(profile) : null;
  $('#recommendationStrip').innerHTML = targets ? [['建議熱量',`${targets.kcal} kcal`,'每日目標'],['蛋白質',`${targets.protein} g`,'每日建議'],['脂肪',`${targets.fat} g`,'每日建議'],['糖分上限',`${targets.sugar} g`,'每日上限']].map(item=>`<div class="recommendation-card"><span class="recommendation-label">${item[0]}</span><strong>${item[1]}</strong><em>${item[2]}</em></div>`).join('') : '<div class="recommendation-card"><span class="recommendation-label">建議攝取量</span><strong>請先完成身體指數</strong><em>建立個人化基準</em></div>';
  $('#metricGrid').innerHTML = [['熱量',Math.round(avgKcal),'kcal／日','日均攝取'],['蛋白質',Math.round(protein/divisor),'g','平均攝取'],['糖分',Math.round(sugar/divisor),'g／日',warning?'需要留意':'目前穩定'],['有效紀錄',rows.length,'筆','已確認資料']].map((m,i)=>`<div class="metric ${i===2&&warning?'warn':''}"><span class="metric-label">${m[0]}</span><div class="metric-value">${m[1]}<small>${m[2]}</small></div><span class="metric-note">${m[3]}</span></div>`).join('');
  const max = Math.max(...days.map(d=>d.kcal), 1); $('#trendChart').innerHTML = days.map(d=>`<div class="chart-day"><div class="bar kcal" style="height:${Math.max(6,d.kcal/max*160)}px" title="${d.kcal} kcal"></div><div class="bar sugar" style="height:${Math.max(6,d.sugar/80*160)}px" title="${d.sugar} g 糖分"></div><span class="chart-label">${d.date.slice(5)}</span></div>`).join('');
  const p = protein*4, f = fat*9, c = carbs*4, total = p+f+c || 1; $('#pfcList').innerHTML = [['蛋白質',p,'var(--green)'],['脂肪',f,'var(--yellow)'],['碳水',c,'var(--pink)']].map(x=>`<div class="pfc-item"><i style="background:${x[2]}"></i><span>${x[0]}<small> ${Math.round(x[1]/total*100)}%</small></span><strong>${Math.round(x[1])} kcal</strong></div>`).join('');
  $('#recordsList').innerHTML = rows.slice().sort((a,b)=>`${b.date}${b.meal_type}`.localeCompare(`${a.date}${a.meal_type}`)).map(r=>`<div class="record"><div><div class="record-name">${r.item_name}</div><div class="record-meta"><span class="record-date">${r.date}</span>${r.meal_type} · 糖分 ${r.sugar_g}g</div></div><div class="record-kcal">${r.kcal} kcal</div></div>`).join('') || '<p class="record-meta">目前沒有紀錄，請按「載入示範資料」或新增一筆飲食。</p>';
  const avgFiber = fiber / divisor; const avgVeg = vegetables / divisor; const proteinTarget = targets?.protein || 75; const gapCards = [];
  if (protein / divisor < proteinTarget * .8) gapCards.push(`<div class="insight gap"><strong>蛋白質攝取不足</strong><p>目前平均 ${Math.round(protein/divisor)}g，低於你的建議 ${proteinTarget}g。</p><span class="insight-meta">可從你常吃的便當、雞胸肉或無糖豆漿開始增加。</span></div>`);
  if (avgFiber < 20) gapCards.push(`<div class="insight gap"><strong>膳食纖維不足</strong><p>目前平均 ${avgFiber.toFixed(1)}g，建議逐步接近每日 25g。</p><span class="insight-meta">你常吃吐司，可以試試全麥堅果吐司，或在早餐加一份堅果。</span></div>`);
  if (avgVeg < 1.5) gapCards.push(`<div class="insight gap"><strong>蔬菜份量偏少</strong><p>目前平均 ${avgVeg.toFixed(1)}份，建議每餐補一份深色蔬菜。</p><span class="insight-meta">外食時可把炸物便當換成雞胸沙拉盒或加點燙青菜。</span></div>`);
  if (warning) gapCards.push('<div class="insight gap"><strong>含糖飲料偏多</strong><p>最近有幾天糖分超過示範門檻，先從半糖改無糖最容易執行。</p><span class="insight-meta">保留你習慣的茶飲，只先調整甜度和加料。</span></div>');
  if (!gapCards.length) gapCards.push('<div class="insight good"><strong>目前營養結構穩定</strong><p>先維持紀錄，累積更多資料後會提供更精準的個人化建議。</p></div>');
  $('#insightList').innerHTML = gapCards.join('');
}
function calculateTargets(data) {
  const bmr = 10*data.weight_kg + 6.25*data.height_cm - 5*data.age + (data.sex === 'male' ? 5 : -161);
  const maintenance = bmr * Number(data.activity || 1.2); const goalFactor = data.goal === 'lose' ? .85 : data.goal === 'gain' ? 1.1 : 1;
  const kcal = Math.round(maintenance * goalFactor); const proteinFactor = data.goal === 'gain' || data.goal === 'lose' ? 1.6 : 1.2; const protein = Math.round(data.weight_kg * proteinFactor); const fat = Math.round(kcal*.27/9); const sugar = Math.round(Math.min(50,kcal*.1/4));
  return { kcal, protein, fat, sugar };
}
function openProfile(fill = true) { const form = $('#profileForm'); if (fill && profile) Object.entries(profile).forEach(([key,value])=>{ if(form.elements[key]) form.elements[key].value=value; }); $('#profileDialog').showModal(); }
$('#demoButton').addEventListener('click',()=>{ records=demoRecords.map(row=>({...row,source_type:'demo',user_confirmed:true})); saveRecords(); render(); });
$('#clearButton').addEventListener('click',()=>{ records=[]; saveRecords(); render(); });
$('#manualButton').addEventListener('click',()=>{ $('#manualForm').reset(); $('#manualForm input[name=date]').value=todayISO(); $('#manualDialog').showModal(); });
$('#manualClose').addEventListener('click',()=>$('#manualDialog').close());
$('#profileClose').addEventListener('click',()=>{ if (profile) $('#profileDialog').close(); });
$('#photoButton').addEventListener('click',()=>$('#photoInput').click());
$('#galleryButton').addEventListener('click',()=>$('#galleryInput').click());
$('#photoClose').addEventListener('click',()=>$('#photoDialog').close());
const prepareImage = (file) => new Promise((resolve,reject) => { const reader=new FileReader(); reader.onerror=()=>reject(new Error('image read failed')); reader.onload=()=>{ const image=new Image(); image.onerror=()=>reject(new Error('image decode failed')); image.onload=()=>{ const max=1600; const scale=Math.min(1,max/Math.max(image.naturalWidth,image.naturalHeight)); const canvas=document.createElement('canvas'); canvas.width=Math.max(1,Math.round(image.naturalWidth*scale)); canvas.height=Math.max(1,Math.round(image.naturalHeight*scale)); canvas.getContext('2d').drawImage(image,0,0,canvas.width,canvas.height); resolve(canvas.toDataURL('image/jpeg',.82)); }; image.src=reader.result; }; reader.readAsDataURL(file); });
const analyzePhoto = async (file) => { if(!file)return; const form=$('#photoForm'); form.reset(); form.elements.date.value=todayISO(); $('#photoPreview').src=URL.createObjectURL(file); $('#photoStatus').textContent='正在準備照片並送交 AI 分析；請稍候。'; $('#photoDialog').showModal(); try { const imageData=await prepareImage(file); const apiBase=window.DIETARY_API_BASE||'/api'; const response=await fetch(`${apiBase}/analyze-image`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image_data:imageData,filename:file.name})}); if(!response.ok){const detail=await response.json().catch(()=>({})); throw new Error(detail.error||'AI API unavailable');} const result=await response.json(); Object.entries(result).forEach(([key,value])=>{if(form.elements[key]&&value!==null)form.elements[key].value=value;}); $('#photoStatus').textContent=`AI 分析完成，信心度 ${Math.round(Number(result.confidence||0)*100)}%。請確認內容後加入。`; form.dataset.confidence=String(result.confidence||0); } catch (error) { $('#photoStatus').textContent=`AI 分析目前無法完成（${error.message}）。你仍可手動修正欄位後加入；確認前請核對營養數字。`; form.dataset.confidence='0'; } };
$('#photoInput').addEventListener('change',(e)=>{ analyzePhoto(e.target.files[0]); });
$('#galleryInput').addEventListener('change',(e)=>{ analyzePhoto(e.target.files[0]); });
document.querySelectorAll('.period-tab').forEach(button=>button.addEventListener('click',()=>{ document.querySelectorAll('.period-tab').forEach(b=>b.classList.remove('active')); button.classList.add('active'); period=button.dataset.period; render(); }));
const numericRecord = (data, source_type, confidence=1) => ({...data, source_type, confidence, user_confirmed:true, kcal:Number(data.kcal||0), sugar_g:Number(data.sugar_g||0), protein_g:Number(data.protein_g||0), fat_g:Number(data.fat_g||0), carbs_g:Number(data.carbs_g||0), fiber_g:Number(data.fiber_g||0), vegetable_servings:Number(data.vegetable_servings||0)});
$('#manualForm').addEventListener('submit',(event)=>{ event.preventDefault(); const data=Object.fromEntries(new FormData(event.target)); records.push(numericRecord(data,'manual')); saveRecords(); $('#manualDialog').close(); render(); });
$('#photoForm').addEventListener('submit',(event)=>{ event.preventDefault(); const data=Object.fromEntries(new FormData(event.target)); records.push(numericRecord(data,'ai_image',Number(event.target.dataset.confidence||0))); saveRecords(); $('#photoDialog').close(); $('#photoInput').value=''; render(); });
$('#csvInput').addEventListener('change',(event)=>{ const file=event.target.files[0]; if(!file)return; const reader=new FileReader(); reader.onload=()=>{ const lines=String(reader.result).split(/\r?\n/).filter(Boolean); if(lines.length<2){alert('CSV 沒有可讀取的資料列。');return;} const headers=parseCSVLine(lines.shift()).map(h=>h.replace(/^﻿/,'')); const imported=lines.map(line=>{const values=parseCSVLine(line); const row=Object.fromEntries(headers.map((h,i)=>[h,values[i]??''])); return numericRecord({date:row.date||todayISO(),meal_type:row.meal_type||'其他',item_name:row.item_name||'未命名品項',kcal:row.kcal||row.actual_kcal,protein_g:row.protein_g||row.actual_protein_g,fat_g:row.fat_g||row.actual_fat_g,carbs_g:row.carbs_g||row.actual_carbs_g,sugar_g:row.sugar_g||row.actual_sugar_g,fiber_g:row.fiber_g,vegetable_servings:row.vegetable_servings},'csv');}); records.push(...imported); saveRecords(); render(); alert(`已匯入 ${imported.length} 筆飲食紀錄。`); }; reader.readAsText(file,'UTF-8'); event.target.value=''; });
$('#profileButton').addEventListener('click',()=>openProfile());
$('#profileForm').addEventListener('submit',(event)=>{ event.preventDefault(); const data=Object.fromEntries(new FormData(event.target)); data.height_cm=Number(data.height_cm); data.weight_kg=Number(data.weight_kg); data.age=Number(data.age); profile=data; localStorage.setItem(profileKey,JSON.stringify(profile)); $('#profileDialog').close(); $('#profileName').textContent=`${profile.height_cm}cm／${profile.weight_kg}kg`; render(); });
$('#profileDialog').addEventListener('cancel',(event)=>{ if (!profile) event.preventDefault(); });
$('#profileForm .close-button').addEventListener('click',(event)=>{ if (!profile) event.preventDefault(); });
if (profile) { $('#profileName').textContent=`${profile.height_cm}cm／${profile.weight_kg}kg`; } else { setTimeout(()=>openProfile(false),250); }
render();
