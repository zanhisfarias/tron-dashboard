/**
 * /api/refresh — Vercel Serverless Function
 */
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  return res.status(200).json({ ok: true });
};
