// api/always-on.js — Lê e grava o planejamento Always On no Vercel KV
// GET  /api/always-on  → retorna { overrides: {}, deleted: [] }
// POST /api/always-on  → salva   { overrides, deleted }

const KV_URL   = process.env.KV_REST_API_URL  || '';
const KV_TOKEN = process.env.KV_REST_API_TOKEN || '';
const KV_KEY   = 'always_on:data';

async function kvGet() {
  if (!KV_URL) return null;
  const r = await fetch(`${KV_URL}/get/${KV_KEY}`, {
    headers: { Authorization: `Bearer ${KV_TOKEN}` },
  });
  const j = await r.json();
  return j.result ? JSON.parse(j.result) : null;
}

async function kvSet(value) {
  if (!KV_URL) return;
  await fetch(`${KV_URL}/set/${KV_KEY}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ value: JSON.stringify(value) }),
  });
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') return res.status(200).end();

  // ── GET ────────────────────────────────────────────────
  if (req.method === 'GET') {
    try {
      const data = await kvGet();
      return res.status(200).json(data || { overrides: {}, deleted: [] });
    } catch (e) {
      console.error('[always-on GET]', e.message);
      return res.status(500).json({ error: e.message });
    }
  }

  // ── POST ───────────────────────────────────────────────
  if (req.method === 'POST') {
    try {
      const body = req.body || {};
      const overrides = body.overrides || {};
      const deleted   = body.deleted   || [];
      await kvSet({ overrides, deleted });
      return res.status(200).json({ ok: true });
    } catch (e) {
      console.error('[always-on POST]', e.message);
      return res.status(500).json({ error: e.message });
    }
  }

  return res.status(405).json({ error: 'Método não permitido' });
};
