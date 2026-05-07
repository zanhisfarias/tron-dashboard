/**
 * /api/status — Netlify Function
 * Retorna status simples (sem background thread em serverless).
 */
exports.handler = async () => ({
  statusCode: 200,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    loading:    false,
    updated_at: new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }),
    error:      null,
    next_in_secs: 0,
  }),
});
