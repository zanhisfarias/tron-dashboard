/**
 * /api/budget — Vercel Serverless Function
 */

const API_BASE = 'https://graph.facebook.com/v21.0';
const ACCOUNT  = 'act_1088579197977036';

const CAMPAIGN_IDS = new Set([
  '120241773113870686',
  '120240938082390686',
  '120240938079060686',
  '120238524414810686',
  '120242553041390686',
]);

async function apiGet(path, params, token) {
  const url = new URL(`${API_BASE}/${path}`);
  url.searchParams.set('access_token', token);
  for (const [k, v] of Object.entries(params || {})) {
    url.searchParams.set(k, String(v));
  }
  const res = await fetch(url.toString(), { signal: AbortSignal.timeout(25000) });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Meta API ${res.status}: ${text.slice(0, 200)}`);
  }
  return res.json();
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');

  const TOKEN = process.env.META_ACCESS_TOKEN;
  if (!TOKEN) {
    return res.status(500).json({ ok: false, error: 'META_ACCESS_TOKEN não configurado' });
  }

  try {
    let total  = 0;
    let cursor = null;

    while (true) {
      const params = { fields: 'daily_budget,status,campaign_id', limit: '200' };
      if (cursor) params.after = cursor;

      const resp = await apiGet(`${ACCOUNT}/adsets`, params, TOKEN);

      for (const a of (resp.data || [])) {
        if (a.status === 'ACTIVE' && CAMPAIGN_IDS.has(a.campaign_id)) {
          total += Math.floor(parseInt(a.daily_budget || 0, 10) / 100);
        }
      }

      if (!resp.paging?.next) break;
      cursor = resp.paging?.cursors?.after || null;
    }

    return res.status(200).json({ ok: true, total_daily_budget: total });
  } catch (e) {
    return res.status(500).json({ ok: false, error: e.message });
  }
};
