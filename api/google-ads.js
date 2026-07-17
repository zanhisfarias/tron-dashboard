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

// Lista contas acessíveis pelo token (retorna IDs sem o MCC pai)
async function listAccessibleCustomers(accessToken, devToken) {
  const res = await fetch(`${ADS_BASE}/customers:listAccessibleCustomers`, {
    method: 'GET',
    headers: {
      'Authorization':   'Bearer ' + accessToken,
      'developer-token': devToken,
    },
    signal: AbortSignal.timeout(15000),
  });
  if (!res.ok) return [];
  const data = await res.json();
  // resourceNames format: "customers/1234567890"
  return (data.resourceNames || []).map(r => r.replace('customers/', ''));
}

// Lista contas filhas não-manager de um MCC via customer_client
async function listChildCustomers(accessToken, mccId, devToken) {
  const headers = {
    'Authorization':     'Bearer ' + accessToken,
    'developer-token':   devToken,
    'login-customer-id': mccId,
    'Content-Type':      'application/json',
  };
  const query = `
    SELECT customer_client.id, customer_client.descriptive_name, customer_client.manager
    FROM customer_client
    WHERE customer_client.level = 1
  `;
  const res = await fetch(`${ADS_BASE}/customers/${mccId}/googleAds:search`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ query }),
    signal: AbortSignal.timeout(15000),
  });
  if (!res.ok) {
    const txt = await res.text();
    console.error('[google-ads] listChildCustomers error:', res.status, txt.slice(0, 200));
    return [];
  }
  const data = await res.json();
  return (data.results || [])
    .filter(r => !r.customerClient?.manager)
    .map(r => ({ id: String(r.customerClient.id), name: r.customerClient.descriptiveName || '' }));
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');

  const MCC_ID = process.env.GOOGLE_ADS_CUSTOMER_ID || '3898746298';

  if (!process.env.GOOGLE_ADS_REFRESH_TOKEN || !process.env.GOOGLE_ADS_DEVELOPER_TOKEN) {
    return res.status(500).json({ error: 'Google Ads: credenciais não configuradas', loading: false });
  }

  const today        = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' });
  const firstOfMonth = today.slice(0, 8) + '01';
  const since = (req.query?.since && /^\d{4}-\d{2}-\d{2}$/.test(req.query.since)) ? req.query.since : firstOfMonth;
  const until = (req.query?.until && /^\d{4}-\d{2}-\d{2}$/.test(req.query.until)) ? req.query.until : today;

  try {
    const accessToken = await getAccessToken();
    const devToken    = process.env.GOOGLE_ADS_DEVELOPER_TOKEN;

    // 1. Tenta via customer_client (lista filhas do MCC)
    let customerIds = await listChildCustomers(accessToken, MCC_ID, devToken);

    // 2. Fallback: listAccessibleCustomers (todos os IDs com acesso pelo token)
    if (customerIds.length === 0) {
      const allIds = await listAccessibleCustomers(accessToken, devToken);
      customerIds = allIds
        .filter(id => id !== MCC_ID)
        .map(id => ({ id, name: '' }));
    }

    // 3. Último recurso: usa o próprio ID
    if (customerIds.length === 0) customerIds = [{ id: MCC_ID, name: '' }];

    // login-customer-id = MCC em todas as chamadas
    const loginId = MCC_ID;

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

    // ── Busca em todas as contas filhas em paralelo ────────────────
    const accountErrors = [];
    const results = await Promise.all(customerIds.map(async ({ id, name }) => {
      try {
        const [campResult, dailyResult] = await Promise.all([
          gaql(accessToken, id, loginId, campQuery),
          gaql(accessToken, id, loginId, dailyQuery),
        ]);
        return { id, name, campResult, dailyResult };
      } catch (e) {
        console.error(`[google-ads] erro na conta ${id}:`, e.message);
        accountErrors.push({ id, name, error: e.message });
        return { id, name, campResult: { results: [] }, dailyResult: { results: [] } };
      }
    }));

    // ── Processa campanhas de todas as contas ──────────────────────
    const campaigns = results.flatMap(({ id: cid, name: cname, campResult }) =>
      (campResult.results || []).map(row => {
        const c = row.campaign;
        const m = row.metrics;
        const spend  = (m.costMicros   || 0) / 1_000_000;
        const clicks = parseInt(m.clicks       || 0, 10);
        const convs  = parseFloat(m.conversions || 0);
        const impr   = parseInt(m.impressions   || 0, 10);
        return {
          id:         c.id,
          name:       c.name,
          account:    cname || cid,
          status:     c.status,
          type:       c.advertisingChannelType,
          spend, clicks, impr, convs,
          ctr:        m.ctr ? m.ctr * 100 : 0,
          cpc:        (m.averageCpc || 0) / 1_000_000,
          cpl:        convs ? spend / convs : 0,
          imprShare:  m.searchImpressionShare || 0,
        };
      })
    ).sort((a, b) => b.spend - a.spend);

    // ── Agrega dados diários de todas as contas ────────────────────
    const dailyMap = {};
    for (const { dailyResult } of results) {
      for (const row of (dailyResult.results || [])) {
        const d = row.segments.date;
        const m = row.metrics;
        if (!dailyMap[d]) dailyMap[d] = { spend: 0, clicks: 0, impr: 0, convs: 0 };
        dailyMap[d].spend  += (m.costMicros   || 0) / 1_000_000;
        dailyMap[d].clicks += parseInt(m.clicks       || 0, 10);
        dailyMap[d].impr   += parseInt(m.impressions   || 0, 10);
        dailyMap[d].convs  += parseFloat(m.conversions || 0);
      }
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
        daily_data:   dailyMap,
        all_dates:    allDates,
        since,
        until,
        customer_ids:   customerIds,
        mcc_id:         MCC_ID,
        account_errors: accountErrors,
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
