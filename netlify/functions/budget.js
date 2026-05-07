/**
 * /api/budget — Netlify Function
 * Busca verba diária total (soma dos adsets ativos) direto da Meta API.
 */

const API_BASE = 'https://graph.facebook.com/v21.0';

const CAMPAIGN_IDS = {
  MR:   '120241773113870686',
  EMP:  '120240938082390686',
  C01:  '120240938079060686',
  C00:  '120238524414810686',
  INST: '120242553041390686',
};

async function apiGet(path, params, token) {
  const url = new URL(`${API_BASE}/${path}`);
  url.searchParams.set('access_token', token);
  for (const [k, v] of Object.entries(params || {})) {
    url.searchParams.set(k, String(v));
  }
  const res = await fetch(url.toString(), { signal: AbortSignal.timeout(20000) });
  if (!res.ok) throw new Error(`Meta API ${res.status}`);
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
    let total = 0;

    await Promise.all(
      Object.entries(CAMPAIGN_IDS).map(async ([, campId]) => {
        let cursor = null;
        while (true) {
          const params = { fields: 'daily_budget,status', limit: '50' };
          if (cursor) params.after = cursor;
          const resp = await apiGet(`${campId}/adsets`, params, TOKEN);
          for (const a of (resp.data || [])) {
            if (a.status === 'ACTIVE') {
              total += Math.floor(parseInt(a.daily_budget || 0, 10) / 100);
            }
          }
          if (!resp.paging?.next) break;
          cursor = resp.paging?.cursors?.after || null;
        }
      })
    );

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
