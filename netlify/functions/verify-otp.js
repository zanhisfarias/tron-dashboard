// verify-otp.js — Valida o código OTP e retorna token de sessão
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
  const expires = Date.now() + 24 * 60 * 60 * 1000; // 24 horas
  const payload = email + '|' + expires;
  const sig     = crypto.createHmac('sha256', SECRET).update(payload).digest('hex');
  return Buffer.from(payload + '|' + sig).toString('base64url');
}

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
  if (event.httpMethod !== 'POST')    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Método não permitido' }) };

  let email = '', code = '';
  try { ({ email, code } = JSON.parse(event.body || '{}')); } catch {}
  email = (email || '').toLowerCase().trim();
  code  = (code  || '').replace(/\D/g, '').slice(0, 6);

  if (!email || !code) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Dados incompletos' }) };
  }

  if (ALLOWED.length > 0 && !ALLOWED.includes(email)) {
    return { statusCode: 403, headers, body: JSON.stringify({ error: 'E-mail não autorizado' }) };
  }

  const bucket  = Math.floor(Date.now() / 600000);
  // Aceita janela atual e anterior (tolerância de até 10 min)
  const valid   = [bucket, bucket - 1].some(b => generateOTP(email, b) === code);

  if (!valid) {
    return { statusCode: 401, headers, body: JSON.stringify({ error: 'Código inválido ou expirado' }) };
  }

  const session = generateSession(email);
  return { statusCode: 200, headers, body: JSON.stringify({ ok: true, session, email }) };
};
