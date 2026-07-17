/**
 * /api/google-ads — Vercel Serverless Function
 * Busca dados de campanhas Google Ads via REST API v21 (read-only)
 */

const OAUTH_URL = 'https://oauth2.googleapis.com/token';
const ADS_BASE  = 'https://googleads.googleapis.com/v21';

async function getAccessToken() {
  const res = await fetch(OAUTH_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id:     process.env.GOOGLE_ADS_CLIENT_ID,
      client_secret: process.env.GOOGLE_ADS_CLIENT_SECRET,
      refresh_token: process.env.GOOGLE_ADS_REFRESH_TOKEN,
      grant_type:    'refresh_token',
    }),
  });
  const data = await res.json();
  if (!data.access_token) throw new Error('Falha no access_token: ' + JSON.stringify(data));
  return data.access_token;
}

async function gaql(accessToken, customerId, loginId, query) {
  const headers = {
    'Authorization':  'Bearer ' + accessToken,
    'developer-token': process.env.GOOGLE_ADS_DEVELOPER_TOKEN,
    'Content-Type':   'application/json',
  };
  if (loginId && loginId !== customerId) headers['login-customer-id'] = loginId;

  const res = await fetch(`${ADS_BASE}/customers/${customerId}/googleAds:search`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ query }),
    signal: AbortSignal.timeout(25000),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Google Ads API ${res.status}: ${txt.slice(0, 400)}`);
  }
  return res.json();
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');

  const CUSTOMER_ID = process.env.GOOGLE_ADS_CUSTOMER_ID || '3898746298';

  if (!process.env.GOOGLE_ADS_REFRESH_TOKEN || !process.env.GOOGLE_ADS_DEVELOPER_TOKEN) {
    return res.status(500).json({ error: 'Google Ads: credenciais não configuradas', loading: false });
  }

  const today        = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' });
  const firstOfMonth = today.slice(0, 8) + '01';
  const since = (req.query?.since && /^\d{4}-\d{2}-\d{2}$/.test(req.query.since)) ? req.query.since : firstOfMonth;
  const until = (req.query?.until && /^\d{4}-\d{2}-\d{2}$/.test(req.query.until)) ? req.query.until : today;

  try {
    const accessToken = await getAccessToken();
    const loginId     = null; // acesso direto, sem MCC

    // ── Query 1: métricas por campanha no período ──────────────────
    const campQuery = `
      SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc,
        metrics.search_impression_share
      FROM campaign
      WHERE segments.date BETWEEN '${since}' AND '${until}'
        AND campaign.status != 'REMOVED'
      ORDER BY metrics.cost_micros DESC
    `;

    // ── Query 2: dados diários para gráfico de tendência ──────────
    const dailyQuery = `
      SELECT
        segments.date,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions
      FROM campaign
      WHERE segments.date BETWEEN '${since}' AND '${until}'
        AND campaign.status != 'REMOVED'
      ORDER BY segments.date ASC
    `;

    const [campResult, dailyResult] = await Promise.all([
      gaql(accessToken, CUSTOMER_ID, loginId, campQuery),
      gaql(accessToken, CUSTOMER_ID, loginId, dailyQuery),
    ]);

    // ── Processa campanhas ─────────────────────────────────────────
    const campaigns = (campResult.results || []).map(row => {
      const c = row.campaign;
      const m = row.metrics;
      const spend  = (m.costMicros   || 0) / 1_000_000;
      const clicks = parseInt(m.clicks       || 0, 10);
      const convs  = parseFloat(m.conversions || 0);
      const impr   = parseInt(m.impressions   || 0, 10);
      return {
        id:            c.id,
        name:          c.name,
        status:        c.status,
        type:          c.advertisingChannelType,
        spend,
        clicks,
        impr,
        convs,
        ctr:           m.ctr ? m.ctr * 100 : 0,
        cpc:           (m.averageCpc || 0) / 1_000_000,
        cpl:           convs ? spend / convs : 0,
        imprShare:     m.searchImpressionShare || 0,
      };
    });

    // ── Processa dados diários ─────────────────────────────────────
    const dailyMap = {};
    for (const row of (dailyResult.results || [])) {
      const d = row.segments.date;
      const m = row.metrics;
      if (!dailyMap[d]) dailyMap[d] = { spend: 0, clicks: 0, impr: 0, convs: 0 };
      dailyMap[d].spend  += (m.costMicros   || 0) / 1_000_000;
      dailyMap[d].clicks += parseInt(m.clicks       || 0, 10);
      dailyMap[d].impr   += parseInt(m.impressions   || 0, 10);
      dailyMap[d].convs  += parseFloat(m.conversions || 0);
    }
    const allDates = Object.keys(dailyMap).sort();

    // ── Totais ─────────────────────────────────────────────────────
    const totals = campaigns.reduce((acc, c) => ({
      spend:  acc.spend  + c.spend,
      clicks: acc.clicks + c.clicks,
      impr:   acc.impr   + c.impr,
      convs:  acc.convs  + c.convs,
    }), { spend: 0, clicks: 0, impr: 0, convs: 0 });

    totals.ctr      = totals.impr   ? totals.clicks / totals.impr * 100  : 0;
    totals.cpc      = totals.clicks ? totals.spend  / totals.clicks       : 0;
    totals.cpl      = totals.convs  ? totals.spend  / totals.convs        : 0;
    totals.convRate = totals.clicks ? totals.convs  / totals.clicks * 100 : 0;

    const updatedAt = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

    return res.status(200).json({
      data: {
        campaigns,
        totals,
        daily_data:  dailyMap,
        all_dates:   allDates,
        since,
        until,
        customer_id: CUSTOMER_ID,
      },
      updated_at: updatedAt,
      loading:    false,
      error:      null,
    });

  } catch (e) {
    console.error('[google-ads] erro:', e);
    return res.status(500).json({ error: e.message, loading: false });
  }
};
