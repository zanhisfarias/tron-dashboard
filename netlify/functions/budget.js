/**
 * /api/budget — Netlify Function
 * Uma única chamada na conta (nível account) em vez de uma por campanha.
 * Filtra adsets das campanhas monitoradas e soma os ativos.
 */

const API_BASE    = 'https://graph.facebook.com/v21.0';
const ACCOUNT     = 'act_1088579197977036';

const CAMPAIGN_IDS = new Set([
  '120241773113870686', // MR
  '120240938082390686', // EMP
  '120240938079060686', // C01
  '120238524414810686', // C00
  '120242553041390686', // INST
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

exports.handler = async () => {
  const TOKEN = process.env.META_ACCESS_TOKEN;

  if (!TOKEN) {
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ok: false, error: 'META_ACCESS_TOKEN não configurado' }),
    };
  }

  try {
    let total  = 0;
    let cursor = null;

    // Uma única chamada na conta — sem loop por campanha
    while (true) {
      const params = {
        fields: 'daily_budget,status,campaign_id',
        limit:  '200',
      };
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

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store',
      },
      body: JSON.stringify({ ok: true, total_daily_budget: total }),
    };
  } catch (e) {
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ok: false, error: e.message }),
    };
  }
};
