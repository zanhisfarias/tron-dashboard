/**
 * /api/status — Vercel Serverless Function
 */
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  return res.status(200).json({
    loading:      false,
    updated_at:   new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }),
    error:        null,
    next_in_secs: 0,
  });
};
