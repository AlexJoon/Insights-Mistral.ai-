# Deployment Guide

Complete guide for deploying the Mistral Chat application to production.

## Pre-Deployment Checklist

### Backend
- [ ] API key configured in environment variables
- [ ] Debug mode disabled (`DEBUG=false`)
- [ ] CORS origins updated for production domain
- [ ] Logging configured for production
- [ ] Error tracking enabled (optional: Sentry)
- [ ] Health check endpoint tested

### Frontend
- [ ] API URL configured for production backend
- [ ] Build tested locally (`npm run build`)
- [ ] Environment variables set
- [ ] Error boundaries implemented
- [ ] Analytics configured (optional)

## Backend Deployment Options

### Option 1: Railway (Recommended - Easiest)

1. **Install Railway CLI**
```bash
npm i -g @railway/cli
```

2. **Login and Initialize**
```bash
railway login
cd backend
railway init
```

3. **Set Environment Variables**
```bash
railway variables set MISTRAL_API_KEY=your_api_key_here
railway variables set MISTRAL_MODEL=mistral-large-latest
railway variables set SERVER_PORT=8000
railway variables set DEBUG=false
railway variables set CORS_ORIGINS=https://your-frontend-domain.com
```

4. **Deploy**
```bash
railway up
```

5. **Get URL**
```bash
railway domain
# Note this URL for frontend configuration
```

### Option 2: Docker + Any Cloud Provider

1. **Create Dockerfile**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "backend.main"]
```

2. **Build Image**
```bash
cd backend
docker build -t mistral-chat-backend .
```

3. **Test Locally**
```bash
docker run -p 8000:8000 \
  -e MISTRAL_API_KEY=your_key \
  -e DEBUG=false \
  mistral-chat-backend
```

4. **Push to Registry**
```bash
# Docker Hub
docker tag mistral-chat-backend yourusername/mistral-chat-backend
docker push yourusername/mistral-chat-backend

# Or AWS ECR, Google Container Registry, etc.
```

5. **Deploy to Cloud**
- **AWS ECS/Fargate**: Use task definition
- **Google Cloud Run**: `gcloud run deploy`
- **Azure Container Instances**: `az container create`

### Option 3: Heroku

1. **Create Procfile**
```
web: python -m backend.main
```

2. **Deploy**
```bash
heroku create mistral-chat-backend
heroku config:set MISTRAL_API_KEY=your_key
heroku config:set DEBUG=false
git push heroku main
```

### Option 4: AWS Lambda (Serverless)

1. **Install Mangum**
```bash
pip install mangum
```

2. **Update app.py**
```python
from mangum import Mangum

app = create_application()
handler = Mangum(app)  # Lambda handler
```

3. **Deploy with AWS SAM or Serverless Framework**

## Frontend Deployment Options

### Option 1: Vercel (Recommended - Easiest)

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Configure Environment**
Create `frontend/.env.production`:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

3. **Deploy**
```bash
cd frontend
vercel --prod
```

4. **Set Environment Variables in Vercel Dashboard**
- Go to project settings
- Add `NEXT_PUBLIC_API_URL`

### Option 2: Netlify

1. **Build Locally**
```bash
cd frontend
npm run build
```

2. **Deploy**
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=out
```

3. **Configure Environment**
- Go to Site Settings → Environment Variables
- Add `NEXT_PUBLIC_API_URL`

### Option 3: Docker + Cloud

1. **Create Dockerfile**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
```

2. **Build and Deploy**
```bash
docker build -t mistral-chat-frontend .
docker push yourusername/mistral-chat-frontend
```

### Option 4: Static Export (CDN)

1. **Configure for Static Export**
```javascript
// frontend/next.config.js
module.exports = {
  output: 'export',
  images: {
    unoptimized: true,
  },
}
```

2. **Build**
```bash
npm run build
```

3. **Deploy to CDN**
- **CloudFront + S3**: Upload `out/` folder
- **Cloudflare Pages**: Connect GitHub repo
- **Firebase Hosting**: `firebase deploy`

## Environment Variables Reference

### Backend Production Variables

```env
# Required
MISTRAL_API_KEY=your_production_api_key

# API Configuration
MISTRAL_API_BASE_URL=https://api.mistral.ai/v1
MISTRAL_MODEL=mistral-large-latest
MISTRAL_MAX_TOKENS=4096
MISTRAL_TEMPERATURE=0.7

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# CORS (Important!)
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

### Frontend Production Variables

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## Post-Deployment Steps

### 1. Verify Backend

```bash
curl https://your-backend-url.com/health
# Should return: {"status":"healthy","service":"mistral-chat-api"}
```

### 2. Test SSE Streaming

```bash
curl -X POST https://your-backend-url.com/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'
```

### 3. Monitor Logs

- Railway: `railway logs`
- Heroku: `heroku logs --tail`
- Docker: `docker logs -f container_id`
- Vercel: Check dashboard

### 4. Test Frontend

1. Open `https://your-frontend-domain.com`
2. Create a new conversation
3. Send a message
4. Verify streaming works
5. Check browser console for errors

## Monitoring & Observability

### Application Monitoring

**Backend**
```python
# Optional: Add Sentry
pip install sentry-sdk
```

**Frontend**
```typescript
// Optional: Add analytics
// Google Analytics, Mixpanel, etc.
```

### Key Metrics to Monitor

1. **Response Time**
   - SSE connection time
   - First chunk latency
   - Total response time

2. **Error Rate**
   - 4xx client errors
   - 5xx server errors
   - Mistral API errors

3. **Availability**
   - Health check uptime
   - SSE connection success rate

4. **Resource Usage**
   - Memory usage
   - CPU usage
   - Active connections

### Logging

**Backend Logging**
```python
# Already configured in utils/logger.py
# Logs go to stdout (captured by hosting platform)
```

**Log Aggregation Options**
- Logtail
- Papertrail
- AWS CloudWatch
- Google Cloud Logging

## Scaling Considerations

### Horizontal Scaling

**Backend**
- Stateless design allows multiple instances
- Use load balancer (ALB, nginx, Cloudflare)
- Session affinity not required

**Frontend**
- CDN distribution
- Edge caching
- Static assets on CDN

### Database Migration

When conversation count grows:

1. **Add PostgreSQL**
```python
# backend/services/database_service.py
from sqlalchemy import create_engine

class DatabaseService:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
```

2. **Update ConversationManager**
```python
# Replace in-memory dict with DB calls
async def get_conversation(self, conv_id):
    return await db_service.get_conversation(conv_id)
```

### Caching Strategy

**Add Redis for**
- Session storage
- Conversation caching
- Rate limiting

```python
# backend/services/cache_service.py
import redis

class CacheService:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
```

## Security Hardening

### 1. API Key Management

**Never commit API keys!**

Use secrets management:
- **Railway**: Built-in secrets
- **AWS**: AWS Secrets Manager
- **GCP**: Secret Manager
- **Azure**: Key Vault

### 2. Rate Limiting

Add rate limiting middleware:
```python
# backend/middleware/rate_limiter.py
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
```

### 3. HTTPS Only

Enforce HTTPS:
```python
# backend/middleware/https_redirect.py
if not request.url.is_secure:
    return RedirectResponse(url=str(request.url).replace("http://", "https://"))
```

### 4. Content Security Policy

Add security headers:
```python
response.headers["Content-Security-Policy"] = "default-src 'self'"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-Content-Type-Options"] = "nosniff"
```

## Backup & Recovery

### Conversation Backup

If using database:
```bash
# PostgreSQL backup
pg_dump -h localhost -U user database > backup.sql

# Restore
psql -h localhost -U user database < backup.sql
```

### Configuration Backup

Keep `.env.example` updated:
```bash
cp .env .env.backup
```

## Cost Optimization

### Mistral API Costs

- Monitor token usage
- Set max_tokens limits
- Implement user quotas
- Cache common responses

### Hosting Costs

**Budget-Friendly Options**
- Railway: ~$5/month (hobby plan)
- Vercel: Free tier sufficient for small apps
- Heroku: ~$7/month (basic)

**Scale-Up Options**
- AWS: Pay as you go
- GCP: Similar to AWS
- Azure: Enterprise features

## Troubleshooting

### Backend Issues

**Problem**: CORS errors in production
```
Solution: Update CORS_ORIGINS environment variable
railway variables set CORS_ORIGINS=https://your-frontend.com
```

**Problem**: SSE not working behind reverse proxy
```
Solution: Disable buffering in nginx/proxy
proxy_buffering off;
proxy_cache off;
```

**Problem**: Connection timeout
```
Solution: Increase timeout limits
uvicorn --timeout-keep-alive 120
```

### Frontend Issues

**Problem**: API calls failing
```
Solution: Check NEXT_PUBLIC_API_URL is set correctly
Verify CORS configuration on backend
```

**Problem**: Environment variables not working
```
Solution: Rebuild after changing env vars
Variables must start with NEXT_PUBLIC_
```

## Rollback Procedure

### Railway
```bash
railway rollback
```

### Vercel
```bash
vercel rollback
```

### Docker
```bash
# Deploy previous version
docker pull yourusername/mistral-chat:previous-tag
docker service update --image yourusername/mistral-chat:previous-tag
```

## Health Checks

### Backend Health Check

```bash
# Add to monitoring
curl -f https://api.your-domain.com/health || exit 1
```

### Uptime Monitoring

Use services like:
- UptimeRobot (free)
- Pingdom
- StatusCake
- Better Uptime

## Continuous Deployment

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

## Summary

Your application is now ready for production deployment with:

✅ Multiple deployment options
✅ Environment configuration
✅ Monitoring setup
✅ Security hardening
✅ Scaling path defined
✅ Backup procedures
✅ Cost optimization

Choose the deployment option that best fits your needs and follow the steps above!
