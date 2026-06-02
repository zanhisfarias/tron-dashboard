/**
 * /api/data — Vercel Serverless Function
 * Busca dados de hoje + adsets da Meta Ads API.
 */

const API_BASE = 'https://graph.facebook.com/v21.0';
const ACCOUNT  = 'act_1088579197977036';

const CAMPAIGN_IDS = {
  MR:   '120241773113870686',
  EMP:  '120240938082390686',
  C01:  '120240938079060686',
  C00:  '120238524414810686',
  INST: '120242553041390686',
};

const CAMP_ID_TO_CODE = Object.fromEntries(
  Object.entries(CAMPAIGN_IDS).map(([code, id]) => [id, code])
);

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
    throw new Error(`Meta API ${res.status}: ${text.slice(0, 300)}`);
  }
  return res.json();
}

function getLeads(actions) {
  for (const a of (actions || [])) {
    if (a.action_type === 'lead') return parseInt(a.value || 0, 10);
  }
  return 0;
}

async function fetchInsights(token, since, until) {
  const today     = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' });
  const dateRange = JSON.stringify({ since, until });
  const allData   = {};

  for (const [code, campId] of Object.entries(CAMPAIGN_IDS)) {
    try {
      let cursor = null;
      do {
        const params = {
          fields:         'date_start,impressions,clicks,spend,actions',
          time_increment: '1',
          time_range:     dateRange,
          limit:          '100',
        };
        if (cursor) params.after = cursor;

        const resp = await apiGet(`${campId}/insights`, params, token);

        for (const row of (resp.data || [])) {
          const d     = row.date_start;
          const impr  = parseInt(row.impressions || 0, 10);
          const click = parseInt(row.clicks      || 0, 10);
          const spend = parseFloat(row.spend     || 0);
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

        cursor = resp.paging?.cursors?.after && resp.paging?.next ? resp.paging.cursors.after : null;
      } while (cursor);

    } catch (e) {
      console.warn(`[data] Insights ${code}:`, e.message);
    }
  }

  // Gera array ordenado de todas as datas com dados no range
  const allDates = Object.keys(allData).sort();

  return { today, allData, allDates };
}

async function fetchAdsets(token) {
  const adsets  = [];
  let   cursor  = null;

  while (true) {
    const params = { fields: 'id,name,daily_budget,status,campaign_id', limit: '200' };
    if (cursor) params.after = cursor;

    try {
      const resp = await apiGet(`${ACCOUNT}/adsets`, params, token);

      for (const a of (resp.data || [])) {
        const code = CAMP_ID_TO_CODE[a.campaign_id];
        if (!code) continue;
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
      console.warn('[data] Adsets:', e.message);
      break;
    }
  }

  return adsets;
}

async function fetchActiveAdsCount(token) {
  const campIds = new Set(Object.values(CAMPAIGN_IDS));
  let count  = 0;
  let cursor = null;

  while (true) {
    const params = { fields: 'id,effective_status,campaign_id', limit: '200' };
    if (cursor) params.after = cursor;

    try {
      const resp = await apiGet(`${ACCOUNT}/ads`, params, token);
      for (const a of (resp.data || [])) {
        if (a.effective_status === 'ACTIVE' && campIds.has(a.campaign_id)) count++;
      }
      if (!resp.paging?.next) break;
      cursor = resp.paging?.cursors?.after || null;
    } catch (e) {
      console.warn('[data] Ads count:', e.message);
      break;
    }
  }

  return count;
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');

  const TOKEN = process.env.META_ACCESS_TOKEN;
  if (!TOKEN) {
    return res.status(500).json({ error: 'META_ACCESS_TOKEN não configurado', loading: false });
  }

  // Aceita ?since=YYYY-MM-DD&until=YYYY-MM-DD ou usa o mês corrente como padrão
  const today = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' });
  const firstOfMonth = today.slice(0, 8) + '01'; // YYYY-MM-01
  const since = (req.query?.since && /^\d{4}-\d{2}-\d{2}$/.test(req.query.since)) ? req.query.since : firstOfMonth;
  const until = (req.query?.until && /^\d{4}-\d{2}-\d{2}$/.test(req.query.until)) ? req.query.until : today;

  try {
    const [adsets, activeAdsCount, { allData, allDates }] = await Promise.all([
      fetchAdsets(TOKEN),
      fetchActiveAdsCount(TOKEN),
      fetchInsights(TOKEN, since, until),
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

    return res.status(200).json({
      data: {
        campaigns,
        all_data:           allData,
        all_dates:          allDates,
        adsets_raw:         adsets,
        active_ads_count:   activeAdsCount,
        total_daily_budget: totalBudget,
        since,
        until,
        partial:            true,
      },
      updated_at: updatedAt,
      loading:    false,
      error:      null,
    });
  } catch (e) {
    console.error('[data] erro:', e);
    return res.status(500).json({ error: e.message, loading: false });
  }
};
