// api/cancel-post.js — Cancela um post agendado (remove do KV)
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
  if (req.method !== 'DELETE') return res.status(405).json({ error: 'Método não permitido' });

  const auth = (req.headers.authorization || '').replace('Bearer ', '');
  if (!verifySession(auth)) return res.status(401).json({ error: 'Sessão inválida' });

  const { id } = req.query || {};
  if (!id) return res.status(400).json({ error: 'ID obrigatório' });

  if (!KV_URL) return res.status(200).json({ ok: true });

  try {
    const key = `scheduled:${id}`;
    await fetch(`${KV_URL}/del/${encodeURIComponent(key)}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${KV_TOKEN}` }
    });
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
};
