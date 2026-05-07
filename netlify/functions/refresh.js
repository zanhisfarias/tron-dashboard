/**
 * /api/refresh — Netlify Function
 * Em serverless não há background thread; retorna OK e o próximo
 * poll de /api/data já trará dados frescos.
 */
exports.handler = async () => ({
  statusCode: 200,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ok: true }),
});
