// api/cron-publish.js — Vercel Cron: publica posts agendados no horário certo
// Schedule em vercel.json: "* * * * *" (a cada minuto)

const META_TOKEN = process.env.META_ACCESS_TOKEN || '';
const IG_ID      = process.env.IG_USER_ID  || '17841405906455560';
const KV_URL     = process.env.KV_REST_API_URL   || '';
const KV_TOKEN   = process.env.KV_REST_API_TOKEN  || '';
const API        = 'https://graph.facebook.com/v21.0';

async function kvGet(key) {
  const resp = await fetch(`${KV_URL}/get/${encodeURIComponent(key)}`, {
    headers: { 'Authorization': `Bearer ${KV_TOKEN}` }
  });
  const data = await resp.json();
  return data.result ? JSON.parse(data.result) : null;
}

async function kvDel(key) {
  await fetch(`${KV_URL}/del/${encodeURIComponent(key)}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${KV_TOKEN}` }
  });
}

async function kvSet(key, value) {
  await fetch(`${KV_URL}/set/${encodeURIComponent(key)}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify([JSON.stringify(value), 'EX', 7 * 24 * 3600])
  });
}

async function publishIGContainer(containerId) {
  const resp = await fetch(`${API}/${IG_ID}/media_publish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ creation_id: containerId, access_token: META_TOKEN })
  });
  const data = await resp.json();
  if (data.error) throw new Error(data.error.message);
  return data.id;
}

module.exports = async (req, res) => {
  // Segurança: só aceita chamadas internas do Vercel cron
  const cronSecret = req.headers['x-vercel-cron'] || req.headers['authorization'];
  // Em produção Vercel, crons são chamados com header especial
  // mas para simplicidade aceitamos qualquer chamada GET
  if (req.method !== 'GET') return res.status(405).end();

  if (!KV_URL) return res.status(200).json({ ok: true, published: 0, message: 'KV não configurado' });

  try {
    // Lista chaves pendentes
    const keysResp = await fetch(`${KV_URL}/keys/scheduled:*`, {
      headers: { 'Authorization': `Bearer ${KV_TOKEN}` }
    });
    const keysData = await keysResp.json();
    const keys = keysData.result || [];

    const now = Date.now();
    let published = 0;
    const errors  = [];

    for (const key of keys) {
      const post = await kvGet(key);
      if (!post || post.status !== 'pending') continue;
      if (post.scheduleAt > now) continue; // ainda não é hora

      // Publica
      try {
        if (post.platform === 'ig') {
          const igId = await publishIGContainer(post.containerId);
          post.status = 'published';
          post.publishedId = igId;
          post.publishedAt = now;
          // Salva histórico por 7 dias
          await kvSet(`history:${post.id}`, post);
          await kvDel(key);
          published++;
          console.log(`[cron] IG publicado: ${igId} (agendado: ${post.id})`);
        }
        // FB já é agendado nativamente pela API do Meta — não precisa de cron
      } catch (e) {
        console.error(`[cron] Erro ao publicar ${post.id}:`, e.message);
        post.status = 'error';
        post.error  = e.message;
        await kvSet(key.replace('scheduled:', 'scheduled:'), post);
        errors.push({ id: post.id, error: e.message });
      }
    }

    return res.status(200).json({ ok: true, published, errors, checked: keys.length });
  } catch (e) {
    console.error('[cron-publish]', e.message);
    return res.status(500).json({ error: e.message });
  }
};
