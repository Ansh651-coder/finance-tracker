# 🚀 Deployment Guide - Finance Tracker

Complete guide for deploying the Personal Finance Tracker application to various platforms.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Render Deployment](#render-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [DigitalOcean Deployment](#digitalocean-deployment)
6. [Production Checklist](#production-checklist)

---

## 📍 Local Development

### Prerequisites
- Python 3.11+
- Git
- Virtual environment support

### Quick Start

**Unix/Linux/macOS:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```batch
run.bat
```

### Manual Setup

1. **Clone and setup**
```bash
git clone <repository-url>
cd finance-tracker
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env and set SECRET_KEY
```

3. **Initialize database**
```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

4. **Seed sample data (optional)**
```bash
python3 seed_data.py
```

5. **Run application**
```bash
python3 app.py
```

Visit: `http://localhost:5000`

---

## 🐳 Docker Deployment

### Option 1: Docker Compose (Recommended)

**With SQLite:**
```bash
docker-compose up -d
```

**With PostgreSQL:**
```yaml
# Uncomment the 'db' service in docker-compose.yml
# Update web service environment:
environment:
  - DATABASE_URL=postgresql://financeuser:financepass@db:5432/financetracker
```

```bash
docker-compose up -d
```

**Access:**
- Application: `http://localhost:5000`
- PostgreSQL: `localhost:5432`

**Management:**
```bash
# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
```

### Option 2: Docker Only

1. **Build image**
```bash
docker build -t finance-tracker .
```

2. **Run container**
```bash
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///finance_tracker.db \
  -v $(pwd)/data:/app/data \
  --name finance-tracker \
  finance-tracker
```

3. **Management**
```bash
# View logs
docker logs -f finance-tracker

# Stop container
docker stop finance-tracker

# Start container
docker start finance-tracker

# Remove container
docker rm -f finance-tracker
```

---

## 🌐 Render Deployment

### Prerequisites
- GitHub account
- Render account (free tier available)

### Step 1: Prepare Repository

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name:** finance-tracker
   - **Environment:** Docker
   - **Region:** Choose nearest region
   - **Branch:** main
   - **Plan:** Free (or paid)

### Step 3: Environment Variables

Add in Render dashboard under "Environment":

```
SECRET_KEY=<generate-strong-random-key>
FLASK_ENV=production
```

**Generate SECRET_KEY:**
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### Step 4: Database (Optional - PostgreSQL)

1. **Create PostgreSQL database:**
   - Click **New +** → **PostgreSQL**
   - Name: finance-tracker-db
   - Plan: Free (or paid)

2. **Get connection string:**
   - Copy "Internal Database URL"
   - Format: `postgresql://user:pass@host/database`

3. **Add to Web Service:**
   - Environment variable: `DATABASE_URL`
   - Value: <internal-database-url>

### Step 5: Deploy

1. Click **Create Web Service**
2. Wait for build and deployment
3. Access at: `https://your-app.onrender.com`

### Step 6: Initialize Database

**Via Render Shell:**
```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

**Seed data (optional):**
```bash
python3 seed_data.py
```

### Render Configuration Files

**render.yaml** (optional - for infrastructure as code):
```yaml
services:
  - type: web
    name: finance-tracker
    env: docker
    plan: free
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: finance-tracker-db
          property: connectionString

databases:
  - name: finance-tracker-db
    plan: free
```

---

## 🔷 Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed

### Step 1: Prepare Application

1. **Create Procfile:**
```
web: gunicorn app:app
```

2. **Create runtime.txt:**
```
python-3.11.6
```

### Step 2: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create finance-tracker-app

# Set environment variables
heroku config:set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set FLASK_ENV=production

# Add PostgreSQL (optional)
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main

# Initialize database
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Seed data (optional)
heroku run python seed_data.py

# Open app
heroku open
```

### Heroku Management

```bash
# View logs
heroku logs --tail

# Scale dynos
heroku ps:scale web=1

# Restart app
heroku restart

# Database backup
heroku pg:backups:capture
heroku pg:backups:download
```

---

## 💧 DigitalOcean Deployment

### Option 1: App Platform

1. **Create App:**
   - Go to DigitalOcean Dashboard
   - Click **Create** → **Apps**
   - Connect GitHub repository

2. **Configure:**
   - **Name:** finance-tracker
   - **Environment Variables:** Add SECRET_KEY, DATABASE_URL
   - **Build Command:** (auto-detected from Dockerfile)
   - **Run Command:** `gunicorn --bind 0.0.0.0:8080 app:app`

3. **Add Database:**
   - Click **Add Component** → **Database**
   - Choose PostgreSQL
   - Link to app

4. **Deploy:**
   - Review and click **Create Resources**

### Option 2: Droplet (VPS)

1. **Create Droplet:**
   - Ubuntu 22.04 LTS
   - Choose size (Basic $6/month minimum)
   - Add SSH key

2. **Connect via SSH:**
```bash
ssh root@your-droplet-ip
```

3. **Setup Server:**
```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3.11 python3.11-venv python3-pip nginx git postgresql postgresql-contrib

# Create app user
useradd -m -s /bin/bash appuser
su - appuser

# Clone repository
git clone <your-repo-url> finance-tracker
cd finance-tracker

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Configure environment
cp .env.example .env
nano .env  # Edit SECRET_KEY and DATABASE_URL

# Initialize database
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

4. **Create Systemd Service:**
```bash
sudo nano /etc/systemd/system/finance-tracker.service
```

```ini
[Unit]
Description=Finance Tracker Application
After=network.target

[Service]
User=appuser
WorkingDirectory=/home/appuser/finance-tracker
Environment="PATH=/home/appuser/finance-tracker/venv/bin"
ExecStart=/home/appuser/finance-tracker/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

[Install]
WantedBy=multi-user.target
```

5. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/finance-tracker
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /home/appuser/finance-tracker/static;
    }
}
```

6. **Enable and Start:**
```bash
sudo ln -s /etc/nginx/sites-available/finance-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable finance-tracker
sudo systemctl start finance-tracker
```

7. **SSL with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## ✅ Production Checklist

### Security

- [ ] Change default SECRET_KEY to strong random value
- [ ] Use HTTPS (SSL certificate)
- [ ] Enable CORS only for trusted domains
- [ ] Set strong database password
- [ ] Disable debug mode (FLASK_ENV=production)
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Review file upload restrictions

### Database

- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up regular backups
- [ ] Configure connection pooling
- [ ] Add database indexes for performance
- [ ] Monitor database size

### Performance

- [ ] Use Gunicorn with multiple workers
- [ ] Enable caching (Redis/Memcached)
- [ ] Compress static files
- [ ] Use CDN for static assets
- [ ] Optimize database queries
- [ ] Set up load balancing (if needed)

### Monitoring

- [ ] Set up application logging
- [ ] Configure error tracking (Sentry)
- [ ] Monitor server resources
- [ ] Set up uptime monitoring
- [ ] Configure alerts

### Backup

- [ ] Database backup automation
- [ ] User uploaded files backup
- [ ] Configuration backup
- [ ] Disaster recovery plan

### Documentation

- [ ] Document deployment process
- [ ] Create user guide
- [ ] API documentation
- [ ] Update README with production URL

---

## 🔧 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ | - | JWT signing key (use strong random value) |
| `DATABASE_URL` | ✅ | `sqlite:///finance_tracker.db` | Database connection string |
| `FLASK_ENV` | ✅ | `production` | Environment (development/production) |
| `PORT` | ❌ | `5000` | Application port |
| `MAX_CONTENT_LENGTH` | ❌ | `16777216` | Max upload size (bytes) |

---

## 📊 Scaling Considerations

### Horizontal Scaling
- Use PostgreSQL (not SQLite)
- Externalize session storage
- Use Redis for caching
- Implement queue system (Celery + Redis)

### Vertical Scaling
- Increase worker count
- Add more memory
- Optimize database queries
- Use database connection pooling

---

## 🆘 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

**Database connection errors:**
```bash
# Check database URL
echo $DATABASE_URL

# Test connection
python3 -c "from app import db; print(db.engine.url)"
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Permission errors (Linux):**
```bash
# Fix ownership
sudo chown -R appuser:appuser /path/to/app

# Fix permissions
chmod -R 755 /path/to/app
```

---

## 📞 Support

For deployment issues:
1. Check application logs
2. Review this deployment guide
3. Check platform-specific documentation
4. Open an issue on GitHub

---

**Happy Deploying! 🎉**