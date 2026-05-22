// api/post-media.js — Publica ou agenda posts no Instagram e Facebook
const crypto = require('crypto');

const META_TOKEN  = process.env.META_ACCESS_TOKEN || '';
const IG_ID       = process.env.IG_USER_ID   || '17841405906455560';
const FB_PAGE_ID  = process.env.FB_PAGE_ID   || '183895946291';
const BLOB_TOKEN  = process.env.BLOB_READ_WRITE_TOKEN || '';
const KV_URL      = process.env.KV_REST_API_URL   || '';
const KV_TOKEN    = process.env.KV_REST_API_TOKEN  || '';
const SECRET      = process.env.SESSION_SECRET || 'tron-dash-secret-2026';
const API         = 'https://graph.facebook.com/v21.0';

// ── Auth ────────────────────────────────────────────────────────────────────
function verifySession(token) {
  if (!token) return null;
  try {
    const decoded = Buffer.from(token, 'base64url').toString('utf8');
    const parts   = decoded.split('|');
    if (parts.length < 3) return null;
    const sig     = parts.pop();
    const expires = parseInt(parts[parts.length - 1]);
    const email   = parts.slice(0, -1).join('|');
    if (Date.now() > expires) return null;
    const payload  = email + '|' + expires;
    const expected = crypto.createHmac('sha256', SECRET).update(payload).digest('hex');
    return sig === expected ? email : null;
  } catch { return null; }
}

// ── Vercel Blob ──────────────────────────────────────────────────────────────
async function uploadToBlob(base64, mimeType, filename) {
  if (!BLOB_TOKEN) throw new Error('BLOB_READ_WRITE_TOKEN não configurado');
  const buffer = Buffer.from(base64, 'base64');
  const resp = await fetch(`https://blob.vercel-storage.com/tron-posts/${filename}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${BLOB_TOKEN}`,
      'x-content-type': mimeType,
      'content-type': mimeType,
    },
    body: buffer
  });
  if (!resp.ok) throw new Error('Blob upload falhou: ' + await resp.text());
  const data = await resp.json();
  return data.url;
}

// ── Vercel KV ────────────────────────────────────────────────────────────────
async function kvSet(key, value) {
  if (!KV_URL || !KV_TOKEN) throw new Error('KV não configurado');
  const resp = await fetch(`${KV_URL}/set/${encodeURIComponent(key)}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify([JSON.stringify(value), 'EX', 30 * 24 * 3600])
  });
  if (!resp.ok) throw new Error('KV set falhou: ' + await resp.text());
}

// ── Meta helpers ─────────────────────────────────────────────────────────────
async function getPageToken() {
  const resp = await fetch(`${API}/${FB_PAGE_ID}?fields=access_token&access_token=${META_TOKEN}`);
  const data = await resp.json();
  if (data.error) throw new Error('Page token error: ' + data.error.message);
  return data.access_token || META_TOKEN;
}

async function createIGContainer(imageUrl, caption) {
  const resp = await fetch(`${API}/${IG_ID}/media`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_url: imageUrl, caption, access_token: META_TOKEN })
  });
  const data = await resp.json();
  if (data.error) throw new Error('IG container: ' + data.error.message);
  return data.id;
}

async function publishIGContainer(containerId) {
  const resp = await fetch(`${API}/${IG_ID}/media_publish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ creation_id: containerId, access_token: META_TOKEN })
  });
  const data = await resp.json();
  if (data.error) throw new Error('IG publish: ' + data.error.message);
  return data.id;
}

async function publishToFB(imageUrl, caption, scheduleTs, pageToken) {
  const body = { url: imageUrl, caption, access_token: pageToken };
  if (scheduleTs) {
    body.scheduled_publish_time = Math.floor(scheduleTs / 1000);
    body.published = 'false';
  }
  const resp = await fetch(`${API}/${FB_PAGE_ID}/photos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await resp.json();
  if (data.error) throw new Error('FB publish: ' + data.error.message);
  return data.id || data.post_id;
}

// ── Handler ──────────────────────────────────────────────────────────────────
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')   return res.status(405).json({ error: 'Método não permitido' });

  const auth = (req.headers.authorization || '').replace('Bearer ', '');
  if (!verifySession(auth)) return res.status(401).json({ error: 'Sessão inválida' });

  const { caption = '', imageBase64, imageType = 'image/jpeg', platforms = [], scheduleAt } = req.body || {};

  if (!imageBase64)    return res.status(400).json({ error: 'Imagem obrigatória' });
  if (!platforms.length) return res.status(400).json({ error: 'Selecione ao menos uma plataforma' });

  const ext      = (imageType.split('/')[1] || 'jpg').replace('jpeg', 'jpg');
  const ts       = Date.now();
  const filename = `post_${ts}.${ext}`;

  try {
    // 1. Upload imagem para Blob storage (URL pública)
    const imageUrl = await uploadToBlob(imageBase64, imageType, filename);

    const scheduleTs = scheduleAt ? new Date(scheduleAt).getTime() : null;
    const isScheduled = scheduleTs && scheduleTs > Date.now() + 60_000;

    const results = {};

    // 2. Instagram
    if (platforms.includes('ig')) {
      const containerId = await createIGContainer(imageUrl, caption);
      if (isScheduled) {
        const postId = `ig_${ts}`;
        await kvSet(`scheduled:${postId}`, {
          id: postId, platform: 'ig', imageUrl, caption,
          containerId, scheduleAt: scheduleTs,
          status: 'pending', createdAt: ts
        });
        results.ig = { scheduled: true, id: postId, scheduleAt: scheduleTs };
      } else {
        const igPostId = await publishIGContainer(containerId);
        results.ig = { published: true, id: igPostId };
      }
    }

    // 3. Facebook
    if (platforms.includes('fb')) {
      const pageToken = await getPageToken();
      const fbId = await publishToFB(imageUrl, caption, isScheduled ? scheduleTs : null, pageToken);
      results.fb = isScheduled
        ? { scheduled: true, id: fbId, scheduleAt: scheduleTs }
        : { published: true, id: fbId };
    }

    return res.status(200).json({ ok: true, results, imageUrl });

  } catch (e) {
    console.error('[post-media]', e.message);
    return res.status(500).json({ error: e.message });
  }
};
