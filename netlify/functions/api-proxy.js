// Netlify Function: proxy /api/* to Django backend (BACKEND_URL)
exports.handler = async (event) => {
  const backend = process.env.BACKEND_URL || '';
  if (!backend) {
    return {
      statusCode: 503,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        success: false,
        error: 'BACKEND_URL is not set. Set it in Netlify Site settings → Environment variables.',
      }),
    };
  }

  const path = event.queryStringParameters?.path || '';
  const apiPath = path ? `/api/${path}` : '/api/';
  const url = `${backend.replace(/\/$/, '')}${apiPath}`;

  const headers = { ...event.headers };
  delete headers['host'];
  delete headers['connection'];
  delete headers['x-forwarded-for'];
  delete headers['x-forwarded-proto'];
  delete headers['content-length'];

  let body = event.body;
  if (event.isBase64Encoded) {
    body = Buffer.from(body, 'base64').toString('utf8');
  }

  try {
    const res = await fetch(url, {
      method: event.httpMethod,
      headers,
      body: body || undefined,
    });
    const data = await res.text();
    const resHeaders = {};
    res.headers.forEach((v, k) => {
      const lower = k.toLowerCase();
      if (lower !== 'transfer-encoding') resHeaders[lower] = v;
    });
    if (!resHeaders['content-type']) resHeaders['content-type'] = 'application/json';

    return {
      statusCode: res.status,
      headers: resHeaders,
      body: data,
    };
  } catch (err) {
    return {
      statusCode: 502,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        success: false,
        error: "Server bilan bog'lanib bo'lmadi / Ошибка соединения",
        detail: err.message,
      }),
    };
  }
};
