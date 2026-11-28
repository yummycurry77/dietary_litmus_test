const MAX_IMAGE_CHARS = 8_000_000;
const ALLOWED_IMAGE_TYPES = new Set(['jpeg', 'jpg', 'png', 'webp', 'gif']);
const CGU_BASE_URL = (process.env.CGU_BASE_URL || 'https://air.cgu.edu.tw/cgullmapi/v1').replace(/\/$/, '');
const CGU_API_KEY = process.env.CGU_API_KEY;
const CGU_VISION_MODEL = process.env.CGU_VISION_MODEL || 'gpt-4o-mini';

const send = (res, status, body) => {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Access-Control-Allow-Origin', process.env.ALLOWED_ORIGIN || '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.end(JSON.stringify(body));
};

const readBody = (req) => new Promise((resolve, reject) => {
  let raw = '';
  req.on('data', (chunk) => {
    raw += chunk;
    if (raw.length > MAX_IMAGE_CHARS + 200_000) reject(new Error('image too large'));
  });
  req.on('end', () => resolve(raw));
  req.on('error', reject);
});

const schema = {
  type: 'object',
  additionalProperties: false,
  properties: {
    item_name: { type: 'string' },
    kcal: { type: 'number', minimum: 0 },
    protein_g: { type: 'number', minimum: 0 },
    fat_g: { type: 'number', minimum: 0 },
    carbs_g: { type: 'number', minimum: 0 },
    sugar_g: { type: 'number', minimum: 0 },
    fiber_g: { type: 'number', minimum: 0 },
    vegetable_servings: { type: 'number', minimum: 0 },
    confidence: { type: 'number', minimum: 0, maximum: 1 },
    notes: { type: 'string' }
  },
  required: ['item_name', 'kcal', 'protein_g', 'fat_g', 'carbs_g', 'sugar_g', 'fiber_g', 'vegetable_servings', 'confidence', 'notes']
};

module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') return send(res, 204, {});
  if (req.method !== 'POST') return send(res, 405, { error: 'Only POST is supported.' });
  if (!CGU_API_KEY) return send(res, 503, { error: '後端尚未設定 CGU_API_KEY。' });

  try {
    const body = JSON.parse(await readBody(req));
    if (typeof body.image_data !== 'string' || !body.image_data.startsWith('data:image/')) {
      return send(res, 400, { error: '請提供有效的食物圖片。' });
    }
    const imageType = body.image_data.match(/^data:image\/([^;]+);base64,/i)?.[1]?.toLowerCase();
    if (!imageType || !ALLOWED_IMAGE_TYPES.has(imageType)) {
      return send(res, 415, { error: '目前只支援 JPG、PNG、WebP 或 GIF 圖片。' });
    }
    if (body.image_data.length > MAX_IMAGE_CHARS) return send(res, 413, { error: '圖片太大，請重新拍攝或選擇較小的照片。' });

    const openai = await fetch(`${CGU_BASE_URL}/responses`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${CGU_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: CGU_VISION_MODEL,
        temperature: 0.1,
        input: [{ role: 'user', content: [
          { type: 'input_text', text: '你是台灣飲食紀錄助手。請辨識照片中的主要食物或飲料；若看得到營養標示，優先使用標示數值並換算成照片中一份實際攝取量。若看不到標示，請依常見份量估算，並降低 confidence。只回傳符合 JSON schema 的資料，不要把估算值說成確定值。所有數值為非負數；notes 請說明是否讀到標示、估算依據與需要使用者確認的地方。這不是醫療診斷。' },
          { type: 'input_image', image_url: body.image_data, detail: 'high' }
        ] }],
        text: { format: { type: 'json_schema', name: 'nutrition_result', strict: true, schema } }
      })
    });
    const result = await openai.json();
    if (!openai.ok) return send(res, 502, { error: result.error?.message || '視覺模型分析失敗。' });
    const text = result.output_text || result.output?.flatMap((item) => item.content || []).find((item) => item.type === 'output_text')?.text;
    if (!text) return send(res, 502, { error: '模型沒有回傳可讀取的分析結果。' });
    return send(res, 200, JSON.parse(text));
  } catch (error) {
    return send(res, 500, { error: error.message || '圖片分析服務發生錯誤。' });
  }
};
