# Deployment Guide - Portia AI Job Platform

This guide covers deployment options for the Portia AI Job Application Platform across different environments.

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend builds)
- Python 3.11+ (for backend)
- PostgreSQL 15+ database
- Redis 7+ cache
- Domain name (for production)
- SSL certificates (for production)

##  Architecture Overview

```

   Frontend              Backend             Chrome
   (React SPA)      (FastAPI)            Extension
   Port: 5173           Port: 8000

   PostgreSQL             Redis              Celery
   Port: 5432           Port: 6379           Workers

```

##  Docker Deployment (Recommended)

### 1. Production Docker Setup

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    environment:
      - VITE_API_BASE_URL=https://api.yourdomain.com/api
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/portia_jobplatform
      - REDIS_URL=redis://redis:6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=portia_jobplatform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.celery_app worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/portia_jobplatform
      - REDIS_URL=redis://redis:6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/portia_jobplatform
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: portia-network
```

### 2. Environment Configuration

Create `.env.prod`:

```env
# Database
POSTGRES_PASSWORD=your_secure_password_here

# AI Services
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Security
JWT_SECRET_KEY=your_super_secure_jwt_secret_here

# External Services
GOOGLE_CREDENTIALS_PATH=/app/credentials/google-credentials.json
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
GITHUB_TOKEN=your_github_token

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
```

### 3. Deploy with Docker

```bash
# Clone the repository
git clone https://github.com/your-username/portia-ai-job-platform.git
cd portia-ai-job-platform

# Set up environment
cp .env.example .env.prod
# Edit .env.prod with your configuration

# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker-compose -f docker-compose.prod.yml exec backend python scripts/init_db.py

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

##  Cloud Platform Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Create ECR repositories**:
```bash
aws ecr create-repository --repository-name portia-ai-frontend
aws ecr create-repository --repository-name portia-ai-backend
```

2. **Build and push images**:
```bash
# Frontend
cd frontend
docker build -t portia-ai-frontend .
docker tag portia-ai-frontend:latest ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/portia-ai-frontend:latest
docker push ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/portia-ai-frontend:latest

# Backend
cd ../backend
docker build -t portia-ai-backend .
docker tag portia-ai-backend:latest ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/portia-ai-backend:latest
docker push ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/portia-ai-backend:latest
```

3. **Create ECS task definition** (`ecs-task-definition.json`)

4. **Deploy with AWS CLI or CDK**

#### Using AWS App Runner (Simpler Option)

```yaml
# apprunner.yaml
version: 1.0
runtime: python3.11
build:
  commands:
    build:
      - echo "Installing dependencies..."
      - pip install -r requirements.txt
run:
  runtime-version: 3.11
  command: uvicorn main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
    env_vars:
      - name: DATABASE_URL
        value: ${DATABASE_URL}
      - name: REDIS_URL
        value: ${REDIS_URL}
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and deploy backend
cd backend
gcloud run deploy portia-ai-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=${DATABASE_URL},REDIS_URL=${REDIS_URL}

# Build and deploy frontend
cd ../frontend
npm run build
gcloud run deploy portia-ai-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Microsoft Azure

#### Using Container Instances

```bash
# Create resource group
az group create --name portia-ai-rg --location eastus

# Deploy backend
az container create \
  --resource-group portia-ai-rg \
  --name portia-ai-backend \
  --image your-registry/portia-ai-backend:latest \
  --dns-name-label portia-ai-backend \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL=${DATABASE_URL} \
    REDIS_URL=${REDIS_URL}
```

##  Frontend Deployment

### Vercel (Recommended for Frontend)

1. **Connect GitHub repository**
2. **Configure build settings**:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Environment Variables**:
   ```
   VITE_API_BASE_URL=https://your-backend-url.com/api
   ```

### Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build and deploy
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

### Static Hosting (Nginx)

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /usr/share/nginx/html;
    index index.html;

    # Handle client-side routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

##  Database Setup

### PostgreSQL on AWS RDS

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier portia-ai-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password ${DB_PASSWORD} \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxx
```

### PostgreSQL on Google Cloud SQL

```bash
# Create Cloud SQL instance
gcloud sql instances create portia-ai-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

### Redis Setup

#### Redis on AWS ElastiCache

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id portia-ai-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

##  Security Configuration

### SSL/TLS Setup

```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

### Environment Security

1. **Use secrets management**:
   - AWS Secrets Manager
   - Google Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

2. **Database security**:
   - Enable SSL connections
   - Use VPC/private networks
   - Regular backups
   - Access logging

3. **API security**:
   - Rate limiting
   - CORS configuration
   - Input validation
   - Authentication middleware

##  Monitoring and Logging

### Application Monitoring

```python
# Add to main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

### Health Checks

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": "connected",
        "redis": "connected"
    }
```

### Log Management

```yaml
# docker-compose.yml logging
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

##  CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Build Frontend
      run: |
        cd frontend
        npm ci
        npm run build

    - name: Deploy to Vercel
      uses: vercel/action@v1
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}

    - name: Deploy Backend
      run: |
        # Deploy backend to your cloud provider
        echo "Deploying backend..."
```

##  Chrome Extension Distribution

### Chrome Web Store

1. **Prepare extension package**:
```bash
cd extension
zip -r portia-ai-extension.zip . -x "*.git*" "node_modules/*" "*.md"
```

2. **Upload to Chrome Web Store**:
   - Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/)
   - Upload zip file
   - Fill out store listing
   - Submit for review

### Enterprise Distribution

```json
{
  "name": "Portia AI Job Tracker - Enterprise",
  "version": "1.0.0",
  "update_url": "https://your-domain.com/updates.xml"
}
```

##  Maintenance

### Database Backups

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > /backups/portia_ai_$DATE.sql
aws s3 cp /backups/portia_ai_$DATE.sql s3://your-backup-bucket/
```

### Updates and Migrations

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Scaling

```yaml
# docker-compose.yml for scaling
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

##  Troubleshooting

### Common Issues

1. **Database connection failed**:
   - Check DATABASE_URL format
   - Verify network connectivity
   - Check firewall rules

2. **Redis connection failed**:
   - Verify REDIS_URL
   - Check Redis service status
   - Validate network access

3. **AI agents not working**:
   - Verify API keys
   - Check rate limits
   - Review error logs

### Performance Optimization

1. **Database optimization**:
   - Add indexes
   - Connection pooling
   - Query optimization

2. **Caching**:
   - Redis caching
   - CDN for static assets
   - API response caching

3. **Load balancing**:
   - Multiple backend instances
   - Database read replicas
   - Geographic distribution

---

##  Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- Review configuration files
- Consult cloud provider documentation
- Open GitHub issue with deployment details

**Happy Deploying! **