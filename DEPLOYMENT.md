# Core Cartographer - Deployment Guide

**Version:** 2.0
**Last Updated:** December 18, 2024

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Production Deployment Options](#production-deployment-options)
4. [Docker Deployment (Recommended)](#docker-deployment-recommended)
5. [Manual Deployment](#manual-deployment)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Scaling Considerations](#scaling-considerations)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- **Docker & Docker Compose** (for Docker deployment)
- **Python 3.11+** (for manual deployment)
- **Node.js 18+** (for manual deployment)
- **Anthropic API Key** with sufficient credits
- **Domain name** (for production)
- **SSL Certificate** (recommended for production)

### Optional
- **Nginx** or reverse proxy
- **Monitoring tools** (Prometheus, Grafana)
- **Log aggregation** (ELK stack, Papertrail)

---

## Environment Configuration

### Backend Environment Variables

Create `.env` in `backend/`:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
MODEL=claude-opus-4-5-20251101  # AI model to use
DEBUG_MODE=false                 # Debug mode (save prompts)
CACHE_EXPIRY_HOURS=1            # Cache expiration time
```

### Frontend Environment Variables

Create `.env.local` in `frontend/`:

```bash
# Optional (defaults to http://localhost:8000)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Production Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Set production values:**
   ```bash
   # Backend
   ANTHROPIC_API_KEY=your_production_key
   DEBUG_MODE=false

   # Frontend
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```

3. **Secure permissions:**
   ```bash
   chmod 600 .env
   ```

---

## Production Deployment Options

### Option 1: Docker Deployment (Recommended)

**Pros:**
- ✅ Consistent environment
- ✅ Easy scaling
- ✅ Isolated dependencies
- ✅ Simple updates

**Cons:**
- ❌ Requires Docker knowledge
- ❌ Additional resource overhead

### Option 2: Manual Deployment

**Pros:**
- ✅ Direct control
- ✅ No Docker overhead
- ✅ Easier debugging

**Cons:**
- ❌ Manual dependency management
- ❌ Platform-specific issues
- ❌ More complex scaling

---

## Docker Deployment (Recommended)

### Step 1: Prepare Configuration

1. **Clone repository:**
   ```bash
   git clone https://github.com/yourusername/core-cartographer.git
   cd core-cartographer
   ```

2. **Configure environment:**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   nano backend/.env  # Add ANTHROPIC_API_KEY

   # Frontend
   cp frontend/.env.example frontend/.env.local
   nano frontend/.env.local  # Configure API URL if needed
   ```

### Step 2: Build Images

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Verify images
docker images | grep cartographer
```

### Step 3: Start Services

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 4: Verify Deployment

```bash
# Check health endpoints
curl http://localhost:8000/health  # Backend
curl http://localhost:3000         # Frontend

# Access application
open http://localhost:3000
```

### Step 5: Configure Nginx (Optional)

If using the included Nginx configuration:

1. **SSL certificates (required for HTTPS):**
   ```bash
   mkdir -p nginx/ssl
   # Copy your SSL certificates to nginx/ssl/
   cp /path/to/cert.pem nginx/ssl/
   cp /path/to/key.pem nginx/ssl/
   ```

2. **Update nginx.conf:**
   ```bash
   nano nginx/nginx.conf
   # Uncomment HTTPS server block
   # Update server_name to your domain
   ```

3. **Restart Nginx:**
   ```bash
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

### Docker Management Commands

```bash
# Stop services
docker-compose -f docker-compose.prod.yml stop

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Remove services
docker-compose -f docker-compose.prod.yml down

# Remove services and volumes
docker-compose -f docker-compose.prod.yml down -v

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Execute commands in containers
docker-compose -f docker-compose.prod.yml exec backend bash
docker-compose -f docker-compose.prod.yml exec frontend sh
```

---

## Manual Deployment

### Backend Deployment

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install system dependencies
sudo apt install build-essential libpq-dev
```

#### Step 2: Application Setup

```bash
# Clone repository
git clone https://github.com/yourusername/core-cartographer.git
cd core-cartographer/backend

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt gunicorn

# Configure environment
cp .env.example .env
nano .env  # Add ANTHROPIC_API_KEY
```

#### Step 3: Run with Gunicorn

```bash
# Test run
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# Create systemd service
sudo nano /etc/systemd/system/cartographer-backend.service
```

**Service file content:**
```ini
[Unit]
Description=Core Cartographer Backend
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/core-cartographer/backend
Environment="PATH=/var/www/core-cartographer/backend/.venv/bin"
ExecStart=/var/www/core-cartographer/backend/.venv/bin/gunicorn \
  src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable cartographer-backend
sudo systemctl start cartographer-backend
sudo systemctl status cartographer-backend
```

### Frontend Deployment

#### Step 1: Build Application

```bash
cd ../frontend

# Install dependencies
npm ci --only=production

# Build Next.js
npm run build
```

#### Step 2: Run with PM2

```bash
# Install PM2
npm install -g pm2

# Start application
pm2 start npm --name "cartographer-frontend" -- start

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

#### Step 3: Configure Nginx

```bash
# Install Nginx
sudo apt install nginx

# Create configuration
sudo nano /etc/nginx/sites-available/cartographer
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/cartographer /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Monitoring & Health Checks

### Health Endpoints

**Backend:**
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","service":"core-cartographer-api"}
```

**Frontend:**
```bash
curl http://localhost:3000
# Response: 200 OK (HTML)
```

### Monitoring Setup

#### Docker Health Checks

Built-in health checks in `docker-compose.prod.yml`:
- Check interval: 30 seconds
- Timeout: 10 seconds
- Start period: 40 seconds
- Retries: 3

View health status:
```bash
docker-compose -f docker-compose.prod.yml ps
```

#### External Monitoring

**UptimeRobot** (free tier available):
- Monitor `/health` endpoint
- Email alerts on downtime

**Prometheus + Grafana** (advanced):
1. Add metrics endpoint to backend
2. Configure Prometheus scraping
3. Create Grafana dashboards

### Log Management

**View Docker logs:**
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

**Manual deployment logs:**
```bash
# Backend (systemd)
sudo journalctl -u cartographer-backend -f

# Frontend (PM2)
pm2 logs cartographer-frontend
```

---

## Scaling Considerations

### Vertical Scaling

**Backend:**
- Increase Gunicorn workers (1-2 per CPU core)
- Increase memory allocation
- Use faster storage for cache

**Frontend:**
- Increase Node.js memory
- Enable Next.js caching

### Horizontal Scaling

**Load Balancer Setup:**
```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

upstream frontend {
    least_conn;
    server frontend1:3000;
    server frontend2:3000;
}
```

**Shared Cache:**
- Replace local file cache with Redis
- Share extracted results across instances

### Resource Requirements

**Minimum (1-10 concurrent users):**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB

**Recommended (10-50 concurrent users):**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB

**High Load (50+ concurrent users):**
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 100GB+
- Multiple instances behind load balancer

---

## Security Best Practices

### API Key Management

1. **Never commit `.env` files**
   ```bash
   echo ".env" >> .gitignore
   echo "*.env.*" >> .gitignore
   ```

2. **Use environment-specific keys:**
   - Development: Limited rate limits
   - Staging: Separate key
   - Production: Dedicated key with monitoring

3. **Rotate keys regularly:**
   - Set reminders for quarterly rotation
   - Update in deployment immediately

### Network Security

1. **Use HTTPS in production:**
   - Get free SSL with Let's Encrypt
   - Redirect all HTTP to HTTPS

2. **Configure firewall:**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **Rate limiting:**
   - Nginx configuration includes rate limits
   - API: 10 req/sec
   - Uploads: 5 req/min

### Application Security

1. **CORS configuration:**
   - Limit to specific domains in production
   - Update `backend/src/api/main.py`

2. **Input validation:**
   - File size limits enforced (10MB)
   - File type validation
   - Pydantic models validate all inputs

3. **Regular updates:**
   ```bash
   # Backend
   pip list --outdated
   pip install --upgrade package_name

   # Frontend
   npm outdated
   npm update
   ```

---

## Troubleshooting

### Backend Issues

**Container won't start:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common issues:
# 1. Missing ANTHROPIC_API_KEY
# 2. Port 8000 already in use
# 3. Permission issues with cache directory
```

**API calls failing:**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Check API key
docker-compose -f docker-compose.prod.yml exec backend \
  printenv | grep ANTHROPIC

# Test from inside container
docker-compose -f docker-compose.prod.yml exec backend bash
curl http://localhost:8000/health
```

### Frontend Issues

**Build fails:**
```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

**Can't connect to backend:**
```bash
# Check environment variable
printenv | grep NEXT_PUBLIC_API_URL

# Test backend connectivity
curl http://backend:8000/health  # From frontend container
curl http://localhost:8000/health  # From host
```

### Docker Issues

**Out of disk space:**
```bash
# Clean up Docker
docker system prune -a --volumes

# Check disk usage
docker system df
```

**Network issues:**
```bash
# Restart Docker network
docker-compose -f docker-compose.prod.yml down
docker network prune
docker-compose -f docker-compose.prod.yml up -d
```

---

## Updating the Application

### Docker Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose -f docker-compose.prod.yml build

# Rolling update (zero downtime)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend
docker-compose -f docker-compose.prod.yml up -d --no-deps --build frontend
```

### Manual Deployment

**Backend:**
```bash
cd backend
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart cartographer-backend
```

**Frontend:**
```bash
cd frontend
git pull
npm install
npm run build
pm2 restart cartographer-frontend
```

---

## Backup & Recovery

### What to Backup

1. **Environment files** (`.env`)
2. **Docker volumes** (if using persistent storage)
3. **SSL certificates**
4. **Configuration files**

### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/cartographer"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup environment files
cp backend/.env $BACKUP_DIR/backend.env.$DATE
cp frontend/.env.local $BACKUP_DIR/frontend.env.$DATE

# Backup SSL certificates
cp -r nginx/ssl $BACKUP_DIR/ssl.$DATE

# Backup Docker volumes (if any)
docker run --rm -v cartographer_backend-cache:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/cache.$DATE.tar.gz /data

echo "Backup completed: $BACKUP_DIR"
```

---

## Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor health endpoints
- Check error logs
- Verify API credits

**Weekly:**
- Review application logs
- Check disk space
- Monitor response times

**Monthly:**
- Update dependencies
- Rotate API keys
- Review security settings
- Test backups

### Getting Help

- **Documentation:** `/docs` folder
- **API Docs:** `http://your-domain/docs`
- **GitHub Issues:** Report bugs and feature requests
- **Health Check:** `http://your-domain/health`

---

**Deployment Guide v2.0** - Core Cartographer

For questions about deployment, please open an issue on GitHub.
