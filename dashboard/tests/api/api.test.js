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

describe('File Upload API', () => {
  const fs = require('fs');
  const path = require('path');

  it('POST /api/v1/upload should accept valid .xlsx file', async () => {
    // Create a test file
    const testFilePath = path.join(__dirname, '..', '..', '..', 'FXRate_20260320.xlsx');

    if (!fs.existsSync(testFilePath)) {
      console.log('Skipping upload test: test file not found');
      return;
    }

    const response = await request(app)
      .post('/api/v1/upload')
      .attach('file', testFilePath)
      .expect('Content-Type', /json/);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('success', true);
    expect(response.body).toHaveProperty('message', '文件上传成功');
    expect(response.body).toHaveProperty('file');
    expect(response.body.file).toHaveProperty('filename');
    expect(response.body.file).toHaveProperty('size');
    expect(response.body.file).toHaveProperty('uploaded_at');
  });

  it('POST /api/v1/upload should reject missing file', async () => {
    const response = await request(app)
      .post('/api/v1/upload')
      .expect('Content-Type', /json/);

    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error');
    expect(response.body.error).toHaveProperty('code', 'INVALID_REQUEST');
    expect(response.body.error.message).toContain('未上传文件');
  });
});