// api/get-scheduled.js — Lista posts agendados do KV
const crypto = require('crypto');
const SECRET    = process.env.SESSION_SECRET || 'tron-dash-secret-2026';
const KV_URL    = process.env.KV_REST_API_URL   || '';
const KV_TOKEN  = process.env.KV_REST_API_TOKEN  || '';

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

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET')    return res.status(405).json({ error: 'Método não permitido' });

  const auth = (req.headers.authorization || '').replace('Bearer ', '');
  if (!verifySession(auth)) return res.status(401).json({ error: 'Sessão inválida' });

  if (!KV_URL) return res.status(200).json({ posts: [] });

  try {
    // Lista todas as chaves scheduled:*
    const keysResp = await fetch(`${KV_URL}/keys/scheduled:*`, {
      headers: { 'Authorization': `Bearer ${KV_TOKEN}` }
    });
    const keysData = await keysResp.json();
    const keys = keysData.result || [];

    const posts = [];
    await Promise.all(keys.map(async (key) => {
      const valResp = await fetch(`${KV_URL}/get/${encodeURIComponent(key)}`, {
        headers: { 'Authorization': `Bearer ${KV_TOKEN}` }
      });
      const valData = await valResp.json();
      if (valData.result) {
        try { posts.push(JSON.parse(valData.result)); } catch {}
      }
    }));

    posts.sort((a, b) => a.scheduleAt - b.scheduleAt);
    return res.status(200).json({ posts });
  } catch (e) {
    console.error('[get-scheduled]', e.message);
    return res.status(500).json({ error: e.message });
  }
};
