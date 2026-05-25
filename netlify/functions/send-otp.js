// send-otp.js — Gera e envia código OTP por e-mail
// Requer env vars: SESSION_SECRET, RESEND_API_KEY, ALLOWED_EMAILS
const crypto = require('crypto');

const SECRET   = process.env.SESSION_SECRET   || 'tron-dash-secret-2026';
const RESEND   = process.env.RESEND_API_KEY   || '';
const FROM     = process.env.OTP_FROM_EMAIL   || 'Dashboard Tron <onboarding@resend.dev>';
const ALLOWED  = (process.env.ALLOWED_EMAILS  || '').split(',').map(e => e.trim().toLowerCase()).filter(Boolean);

function generateOTP(email) {
  const bucket = Math.floor(Date.now() / 600000); // janela de 10 min
  const hmac   = crypto.createHmac('sha256', SECRET);
  hmac.update(email.toLowerCase() + ':' + bucket);
  const hex  = hmac.digest('hex');
  const code = String(parseInt(hex.slice(0, 8), 16) % 1000000).padStart(6, '0');
  return code;
}

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers, body: '' };
  if (event.httpMethod !== 'POST')    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Método não permitido' }) };

  let email = '';
  try { email = JSON.parse(event.body || '{}').email || ''; } catch {}
  email = email.toLowerCase().trim();

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'E-mail inválido' }) };
  }

  if (ALLOWED.length > 0 && !ALLOWED.includes(email)) {
    return { statusCode: 403, headers, body: JSON.stringify({ error: 'E-mail não autorizado' }) };
  }

  const otp = generateOTP(email);

  // Envia via Resend
  if (RESEND) {
    try {
      const resp = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + RESEND, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from: FROM,
          to: [email],
          subject: '🔐 ' + otp + ' — Código de acesso Dashboard Tron',
          html: `
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0F1117;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif">
  <div style="max-width:420px;margin:40px auto;background:#1A1D27;border-radius:16px;overflow:hidden;border:1px solid #2A2D3E">
    <div style="padding:24px 32px;background:linear-gradient(135deg,#1A1D27,#12141C)">
      <div style="font-size:22px;font-weight:800;color:#6366F1;letter-spacing:-0.5px">TRON</div>
      <div style="font-size:12px;color:#6B7280;margin-top:2px">Dashboard de Performance</div>
    </div>
    <div style="padding:32px">
      <p style="color:#D1D5DB;font-size:14px;margin:0 0 24px">Seu código de verificação:</p>
      <div style="background:#0F1117;border-radius:12px;padding:20px;text-align:center;letter-spacing:12px;font-size:38px;font-weight:800;color:#818CF8;border:1px solid #2A2D3E">
        ${otp}
      </div>
      <p style="color:#6B7280;font-size:12px;margin:20px 0 0;line-height:1.6">
        ⏱ Válido por <strong>10 minutos</strong>.<br>
        Não compartilhe este código com ninguém.
      </p>
    </div>
    <div style="padding:16px 32px;background:#12141C;border-top:1px solid #2A2D3E">
      <p style="color:#4B5563;font-size:11px;margin:0">Se você não solicitou este código, ignore este e-mail.</p>
    </div>
  </div>
</body>
</html>`
        })
      });
      if (!resp.ok) {
        const err = await resp.text();
        console.error('Resend error:', err);
        return { statusCode: 500, headers, body: JSON.stringify({ error: 'Falha ao enviar e-mail. Tente novamente.' }) };
      }
    } catch (e) {
      console.error('Resend exception:', e);
      return { statusCode: 500, headers, body: JSON.stringify({ error: 'Erro ao enviar e-mail.' }) };
    }
  } else {
    // Modo dev — loga o código no console da function
    console.log('[DEV] OTP para', email, ':', otp);
  }

  return { statusCode: 200, headers, body: JSON.stringify({ ok: true }) };
};
