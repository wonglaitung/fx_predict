const request = require('supertest');
const app = require('../../server');

describe('Health API', () => {
  it('GET /health should return status ok', async () => {
    const response = await request(app)
      .get('/health')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status', 'ok');
    expect(response.body).toHaveProperty('uptime');
    expect(response.body).toHaveProperty('timestamp');
  });
});

describe('Data Loader', () => {
  it('should load all prediction files', async () => {
    const response = await request(app)
      .get('/api/v1/pairs')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('pairs');
    expect(Array.isArray(response.body.pairs)).toBe(true);
  });
});