/**
 * /api/data — Netlify Function
 * Busca dados de hoje + adsets da Meta Ads API.
 * Retorna { data: { partial: true, ... } } para que o dashboard
 * faça merge com o histórico já embutido no HTML.
 */

const API_BASE = 'https://graph.facebook.com/v21.0';

const CAMPAIGN_IDS = {
  MR:   '120241773113870686',
  EMP:  '120240938082390686',
  C01:  '120240938079060686',
  C00:  '120238524414810686',
  INST: '120242553041390686',
};

const CAMPAIGN_META = {
  MR:   { label: 'MR Contábil',   color: '#6366F1' },
  EMP:  { label: 'Empresarial',   color: '#F59E0B' },
  C01:  { label: 'Contábil 01',   color: '#10B981' },
  C00:  { label: 'Contábil 00',   color: '#8B5CF6' },
  INST: { label: 'Institucional', color: '#64748B' },
};

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

function getLeads(actions) {
  for (const a of (actions || [])) {
    if (a.action_type === 'lead') return parseInt(a.value || 0, 10);
  }
  return 0;
}

async function fetchTodayInsights(token) {
  const today = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' });
  const dateRange = JSON.stringify({ since: today, until: today });
  const allData = {};

  await Promise.all(
    Object.entries(CAMPAIGN_IDS).map(async ([code, campId]) => {
      try {
        const resp = await apiGet(`${campId}/insights`, {
          fields: 'date_start,impressions,clicks,spend,actions',
          time_increment: '1',
          time_range: dateRange,
          limit: '10',
        }, token);

        for (const row of (resp.data || [])) {
          const d     = row.date_start;
          const impr  = parseInt(row.impressions || 0, 10);
          const click = parseInt(row.clicks || 0, 10);
          const spend = parseFloat(row.spend || 0);
          const leads = getLeads(row.actions);
          if (!allData[d]) allData[d] = {};
          allData[d][code] = {
            leads, impr, clicks: click, spend,
            ctr: impr  ? (click / impr * 100) : 0,
            cpc: click ? (spend / click)       : 0,
            cpm: impr  ? (spend / impr * 1000) : 0,
            cpl: leads ? (spend / leads)        : 0,
          };
        }
      } catch (e) {
        console.warn(`[data] Insights ${code}:`, e.message);
      }
    })
  );

  return { today, allData };
}

async function fetchAdsets(token) {
  const adsets = [];

  await Promise.all(
    Object.entries(CAMPAIGN_IDS).map(async ([code, campId]) => {
      let cursor = null;
      while (true) {
        try {
          const params = { fields: 'id,name,daily_budget,status', limit: '50' };
          if (cursor) params.after = cursor;
          const resp = await apiGet(`${campId}/adsets`, params, token);
          for (const a of (resp.data || [])) {
            adsets.push({
              id:     a.id,
              camp:   code,
              name:   a.name,
              budget: Math.floor(parseInt(a.daily_budget || 0, 10) / 100),
              status: a.status === 'ACTIVE' ? 'active' : 'paused',
            });
          }
          if (!resp.paging?.next) break;
          cursor = resp.paging?.cursors?.after || null;
        } catch (e) {
          console.warn(`[data] Adsets ${code}:`, e.message);
          break;
        }
      }
    })
  );

  return adsets;
}

exports.handler = async (event) => {
  const TOKEN = process.env.META_ACCESS_TOKEN;

  if (!TOKEN) {
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'META_ACCESS_TOKEN não configurado', loading: false }),
    };
  }

  try {
    const [{ today, allData }, adsets] = await Promise.all([
      fetchTodayInsights(TOKEN),
      fetchAdsets(TOKEN),
    ]);

    const totalBudget = adsets
      .filter(a => a.status === 'active')
      .reduce((s, a) => s + a.budget, 0);

    const budgets = Object.fromEntries(Object.keys(CAMPAIGN_IDS).map(c => [c, 0]));
    for (const a of adsets) {
      if (a.status === 'active') budgets[a.camp] = (budgets[a.camp] || 0) + a.budget;
    }

    const campaigns = {};
    for (const [code, meta] of Object.entries(CAMPAIGN_META)) {
      campaigns[code] = { ...meta, budget: budgets[code] || 0 };
    }

    const updatedAt = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'no-store',
      },
      body: JSON.stringify({
        data: {
          campaigns,
          all_data:           allData,
          all_dates:          [today],
          adsets_raw:         adsets,
          total_daily_budget: totalBudget,
          partial:            true,
        },
        updated_at: updatedAt,
        loading:    false,
        error:      null,
      }),
    };
  } catch (e) {
    console.error('[data] erro:', e);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: e.message, loading: false }),
    };
  }
};
