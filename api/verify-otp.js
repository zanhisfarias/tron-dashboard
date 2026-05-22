// /api/verify-otp — Vercel Serverless Function
const crypto = require('crypto');

const SECRET  = process.env.SESSION_SECRET  || 'tron-dash-secret-2026';
const ALLOWED = (process.env.ALLOWED_EMAILS || '').split(',').map(e => e.trim().toLowerCase()).filter(Boolean);

function generateOTP(email, bucket) {
  const hmac = crypto.createHmac('sha256', SECRET);
  hmac.update(email.toLowerCase() + ':' + bucket);
  const hex = hmac.digest('hex');
  return String(parseInt(hex.slice(0, 8), 16) % 1000000).padStart(6, '0');
}

function generateSession(email) {
  const expires = Date.now() + 24 * 60 * 60 * 1000;
  const payload = email + '|' + expires;
  const sig     = crypto.createHmac('sha256', SECRET).update(payload).digest('hex');
  return Buffer.from(payload + '|' + sig).toString('base64url');
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')   return res.status(405).json({ error: 'Método não permitido' });

  let email = '', code = '';
  try { ({ email = '', code = '' } = req.body || {}); } catch {}
  email = (email || '').toLowerCase().trim();
  code  = (code  || '').replace(/\D/g, '').slice(0, 6);

  if (!email || !code) return res.status(400).json({ error: 'Dados incompletos' });
  if (ALLOWED.length > 0 && !ALLOWED.includes(email))
    return res.status(403).json({ error: 'E-mail não autorizado' });

  const bucket = Math.floor(Date.now() / 600000);
  const valid  = [bucket, bucket - 1].some(b => generateOTP(email, b) === code);

  if (!valid) return res.status(401).json({ error: 'Código inválido ou expirado' });

  return res.status(200).json({ ok: true, session: generateSession(email), email });
};
