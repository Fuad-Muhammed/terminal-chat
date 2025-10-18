# Terminal Chat Deployment Guide

This guide covers deploying Terminal Chat to various platforms including Docker, Railway, Render, and DigitalOcean.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Local Docker Deployment](#local-docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
   - [Railway](#railway-deployment)
   - [Render](#render-deployment)
   - [DigitalOcean](#digitalocean-deployment)
5. [Database Migration](#database-migration)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Monitoring and Logs](#monitoring-and-logs)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- Git
- PostgreSQL (for production deployments)

### Recommended
- Domain name with DNS configured
- SSL/TLS certificate (Let's Encrypt recommended)
- Monitoring service (Sentry, Datadog, etc.)

---

## Environment Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
# For SQLite (development only):
DATABASE_URL=sqlite:///./terminal_chat.db

# For PostgreSQL (production):
DATABASE_URL=postgresql://user:password@host:5432/database_name

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-use-long-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# CORS Settings (comma-separated origins)
# For development:
ALLOWED_ORIGINS=*
# For production:
# ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Environment
ENVIRONMENT=production
```

### Generating a Secure JWT Secret

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

---

## Local Docker Deployment

### Development Mode (SQLite)

1. **Build the Docker image:**
   ```bash
   docker build -t terminal-chat-server:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name terminal-chat \
     -p 8000:8000 \
     -v $(pwd)/data:/app/data \
     -e JWT_SECRET_KEY=$(openssl rand -base64 32) \
     terminal-chat-server:latest
   ```

3. **Check logs:**
   ```bash
   docker logs -f terminal-chat
   ```

4. **Stop the container:**
   ```bash
   docker stop terminal-chat
   docker rm terminal-chat
   ```

### Using Docker Compose (Recommended)

#### Development (SQLite)

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Production (PostgreSQL)

```bash
# Create .env file with production settings
cp .env.example .env
# Edit .env with your production values

# Start with PostgreSQL
docker-compose --profile production up -d

# View logs
docker-compose --profile production logs -f

# Stop
docker-compose --profile production down
```

### Docker Compose Configuration

The `docker-compose.yml` includes:
- **server**: Main chat server with SQLite
- **postgres**: PostgreSQL database (production profile)
- **server-postgres**: Server configured for PostgreSQL (production profile)

---

## Cloud Deployment

### Railway Deployment

Railway offers automatic deployments from GitHub with built-in PostgreSQL.

#### Step-by-Step

1. **Prepare Your Repository**
   ```bash
   # Ensure your code is pushed to GitHub
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Create Railway Project**
   - Go to [Railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add PostgreSQL Database**
   - In your Railway project dashboard
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will automatically provision the database

4. **Configure Environment Variables**

   In Railway project settings, add:
   ```
   JWT_SECRET_KEY=<your-generated-secret>
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   ENVIRONMENT=production
   ```

   Note: `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

5. **Configure Build Settings**

   Railway auto-detects Python projects. If needed, create `railway.json`:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn server.main:app --host 0.0.0.0 --port $PORT",
       "healthcheckPath": "/api/health",
       "healthcheckTimeout": 300
     }
   }
   ```

6. **Deploy**
   - Railway automatically deploys on git push
   - Monitor deployment in Railway dashboard
   - Access your app at the provided Railway URL

7. **Configure Custom Domain (Optional)**
   - In Railway project settings → "Domains"
   - Add custom domain
   - Update DNS records as instructed

#### Railway Tips
- Use Railway's built-in logging for debugging
- Enable automatic deployments from GitHub
- Use Railway's environment variable management
- Monitor resource usage in dashboard

---

### Render Deployment

Render provides free tier with automatic HTTPS and PostgreSQL.

#### Step-by-Step

1. **Prepare Repository**
   ```bash
   git push origin main
   ```

2. **Create Web Service**
   - Go to [Render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Web Service**

   **Settings:**
   - **Name**: `terminal-chat-server`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Choose based on needs (Free tier available)

4. **Add PostgreSQL Database**
   - In Render dashboard, click "New +" → "PostgreSQL"
   - Name your database
   - Choose region and plan
   - Create database

5. **Link Database to Web Service**
   - Copy the "Internal Database URL" from PostgreSQL dashboard
   - In Web Service → "Environment"
   - Add environment variable:
     ```
     DATABASE_URL=<internal-database-url>
     ```

6. **Add Environment Variables**

   In Web Service → "Environment", add:
   ```
   JWT_SECRET_KEY=<your-generated-secret>
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

7. **Deploy**
   - Click "Manual Deploy" or push to GitHub
   - Monitor deployment logs
   - Access via Render-provided URL

8. **Configure Custom Domain (Optional)**
   - In Web Service → "Settings" → "Custom Domain"
   - Add your domain
   - Update DNS with provided CNAME record

#### Render Tips
- Free tier spins down after inactivity (may have cold starts)
- Use Render's automatic HTTPS (no configuration needed)
- Monitor logs in real-time from dashboard
- Set up health check endpoint: `/api/health`

---

### DigitalOcean Deployment

DigitalOcean App Platform offers scalable deployment with managed databases.

#### Step-by-Step

1. **Prepare Repository**
   ```bash
   git push origin main
   ```

2. **Create App**
   - Go to [DigitalOcean](https://cloud.digitalocean.com)
   - Click "Apps" → "Create App"
   - Choose "GitHub" as source
   - Authorize and select repository
   - Select branch (usually `main`)

3. **Configure App**

   **Resources:**
   - Type: `Web Service`
   - Name: `terminal-chat-server`
   - Environment: Auto-detected (Python)

   **Build Settings:**
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `uvicorn server.main:app --host 0.0.0.0 --port 8080`

   **Environment Variables:**
   Add in App Settings → terminal-chat-server → Environment Variables:
   ```
   JWT_SECRET_KEY=<your-secret> (Encrypt this)
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   ENVIRONMENT=production
   ```

4. **Add Managed PostgreSQL Database**
   - In your App → "Create" → "Database"
   - Choose "PostgreSQL"
   - Select plan and datacenter region
   - Database will be automatically linked

5. **Configure Database Connection**
   - DigitalOcean automatically adds `DATABASE_URL`
   - Verify in App → Components → terminal-chat-server → Environment Variables

6. **Deploy**
   - Click "Save" and app will deploy automatically
   - Monitor in "Runtime Logs"
   - Access via provided `.ondigitalocean.app` URL

7. **Configure Custom Domain**
   - In App Settings → "Domains"
   - Add domain
   - Update DNS records as instructed
   - SSL certificate is automatically provisioned

#### DigitalOcean Tips
- Use managed PostgreSQL for better performance
- Enable automatic deployments from GitHub
- Set up alerts for resource usage
- Use connection pooling for database
- Monitor app health and metrics in dashboard

---

## Database Migration

### Migrating from SQLite to PostgreSQL

1. **Export Data from SQLite**
   ```bash
   # Install sqlite3 tools
   sudo apt-get install sqlite3

   # Export to SQL dump
   sqlite3 terminal_chat.db .dump > backup.sql
   ```

2. **Prepare PostgreSQL**
   ```bash
   # Create database
   createdb terminal_chat

   # Import (may need manual adjustments)
   psql terminal_chat < backup.sql
   ```

3. **Update Environment**
   ```bash
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql://user:password@localhost:5432/terminal_chat
   ```

4. **Verify Migration**
   ```bash
   # Start server and check logs
   uvicorn server.main:app --reload

   # Test authentication and message history
   ```

### Database Backup Best Practices

**PostgreSQL Backups:**
```bash
# Automated daily backup
pg_dump -U postgres terminal_chat > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U postgres terminal_chat < backup_20250118.sql
```

**Backup Strategy:**
- Daily automated backups
- Keep backups for 30 days
- Store backups off-site (S3, Backblaze, etc.)
- Test restore procedure monthly

---

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

1. **Install Nginx and Certbot**
   ```bash
   sudo apt update
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Configure Nginx**

   Create `/etc/nginx/sites-available/terminal-chat`:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/terminal-chat /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **Obtain SSL Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

5. **Auto-Renewal**
   ```bash
   # Certbot automatically sets up renewal
   # Test renewal:
   sudo certbot renew --dry-run
   ```

---

## Monitoring and Logs

### Application Logs

**Docker:**
```bash
# View logs
docker-compose logs -f server

# Last 100 lines
docker-compose logs --tail=100 server
```

**Production Server:**
```bash
# Using systemd
journalctl -u terminal-chat -f

# Using log files
tail -f /var/log/terminal-chat/app.log
```

### Health Checks

Monitor these endpoints:
- `GET /api/health` - API health
- `GET /` - Server status

**Example Health Check Script:**
```bash
#!/bin/bash
HEALTH_URL="https://yourdomain.com/api/health"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response -eq 200 ]; then
    echo "✓ Service is healthy"
    exit 0
else
    echo "✗ Service is unhealthy (HTTP $response)"
    exit 1
fi
```

### Recommended Monitoring Tools

- **Uptime Monitoring**: UptimeRobot, Pingdom
- **Error Tracking**: Sentry
- **Performance**: New Relic, Datadog
- **Logs**: Papertrail, Loggly

---

## Troubleshooting

### Common Issues

#### Database Connection Failed

**Symptoms:**
```
ERROR: could not connect to server: Connection refused
```

**Solutions:**
1. Verify `DATABASE_URL` is correct
2. Check database server is running
3. Verify network connectivity
4. Check firewall rules

```bash
# Test PostgreSQL connection
psql $DATABASE_URL

# Check if PostgreSQL is running
sudo systemctl status postgresql
```

#### WebSocket Connection Fails

**Symptoms:**
- Client can't connect to WebSocket
- Connection drops immediately

**Solutions:**
1. Verify server is running
2. Check firewall allows WebSocket connections
3. Ensure proxy (nginx) is configured for WebSocket upgrades
4. Check CORS settings

```bash
# Test WebSocket connection
wscat -c ws://localhost:8000/ws/1

# Check nginx WebSocket configuration
sudo nginx -t
```

#### High Memory Usage

**Solutions:**
1. Limit number of uvicorn workers
2. Use connection pooling for database
3. Implement rate limiting
4. Monitor with htop/top

```bash
# Monitor resources
docker stats

# Restart with limited workers
uvicorn server.main:app --workers 2
```

#### SSL Certificate Issues

**Solutions:**
```bash
# Renew certificate manually
sudo certbot renew

# Check certificate expiration
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

---

## Production Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/WSS (SSL/TLS)
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerts
- [ ] Configure logging
- [ ] Test disaster recovery procedure
- [ ] Document deployment process
- [ ] Set up CI/CD pipeline
- [ ] Review security settings
- [ ] Test with load testing tools
- [ ] Configure auto-scaling (if applicable)

---

## Performance Optimization

### Recommended Settings

```bash
# uvicorn with multiple workers
uvicorn server.main:app --workers 4 --host 0.0.0.0 --port 8000

# With gunicorn (alternative)
gunicorn server.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Database Connection Pooling

In production, use connection pooling:

```python
# In server/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

---

## Support

For deployment issues:
- Check logs first
- Review this deployment guide
- Check GitHub Issues
- Contact support team

---

**Last Updated**: 2025-01-18
**Version**: 1.0.0
