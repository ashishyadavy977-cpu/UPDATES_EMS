# Event Management System - Complete Setup Guide

## Overview
This guide provides step-by-step instructions for setting up the Event Management System for both development and production environments.

---

## Part 1: Development Setup (SQLite)

### System Requirements
- Windows 10/11, macOS, or Linux
- Python 3.8 or higher
- 500MB disk space
- No additional database software required

### Step 1: Navigate to Project Directory
```bash
cd "c:\Users\Ashish Yadav\Downloads\Ashish\EMS"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Expected Output:**
```
(venv) PS C:\Users\Ashish Yadav\Downloads\Ashish\EMS>
```

### Step 3: Verify Python & Pip
```bash
python --version
pip --version
```

**Expected Output:**
```
Python 3.x.x
pip 23.x.x from ... (python 3.x)
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

**Installation Progress:**
```
Collecting Flask==3.0.0
Collecting Flask-SQLAlchemy==3.1.1
...
Successfully installed flask-3.0.0 flask-login-0.6.3 ...
```

### Step 5: Verify Installation
```bash
pip list | grep -E "Flask|SQLAlchemy|Bcrypt"
```

### Step 6: Initialize Database & Seed Data
```bash
python seed_data.py
```

**Expected Output:**
```
Clearing existing data...
Creating admin user...
Creating sample users...
Creating sample events...
Creating sample registrations...

==================================================
Database seeding completed successfully!
==================================================

Admins Created: 1
  - Username: admin
  - Password: admin123

Users Created: 8
Events Created: 6
Registrations Created: XX

==================================================

Default Admin Credentials:
  Username: admin
  Password: admin123

Sample User Credentials (all users):
  Password: password123
  Emails: john@example.com, jane@example.com, alice@example.com, etc.

==================================================
```

### Step 7: Run the Application
```bash
python run.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 8: Test the Application
Open browser and navigate to:
- **Main Page:** http://localhost:5000
- **User Login:** http://localhost:5000/auth/login
- **Admin Login:** http://localhost:5000/auth/admin-login

---

## Part 2: Production Setup (MySQL)

### Prerequisites for Production
- MySQL Server 5.7+
- Python 3.8+
- Nginx or Apache (reverse proxy)
- SSL Certificate (for HTTPS)
- Domain name

### Step 1: Install MySQL Server

#### Windows
```powershell
# Option 1: Using Chocolatey
choco install mysql

# Option 2: Download Installer
# Visit: https://dev.mysql.com/downloads/mysql/
```

#### macOS
```bash
brew install mysql
brew services start mysql
```

#### Linux (Ubuntu)
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

### Step 2: Create Production Database

```bash
# Open MySQL Command Line
mysql -u root -p

# Execute SQL Commands
CREATE DATABASE ems_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ems_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON ems_production.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Verification:**
```bash
mysql -u ems_user -p ems_production
SELECT 1;  # Should return 1
EXIT;
```

### Step 3: Configure Environment Variables

Create `.env` file in project root:

```bash
# Windows
type .env.example > .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` with your production settings:

```env
FLASK_ENV=production
SECRET_KEY=your-secure-random-key
DATABASE_URL=mysql+pymysql://ems_user:secure_password_here@localhost/ems_production
DEBUG=False
```

### Step 4: Update config.py (if needed)

The configuration already supports both SQLite and MySQL via environment variables. Verify:

```python
# In config.py - should already be configured correctly
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:password@localhost/ems_production'
)
```

### Step 5: Test Database Connection

```bash
python -c "
from app import create_app
from config import ProductionConfig

app = create_app(ProductionConfig)
with app.app_context():
    from app.models import db
    db.create_all()
    print('✓ Database connection successful!')
"
```

### Step 6: Seed Production Database

```bash
python seed_data.py
```

This will create:
- 1 admin user (admin/admin123)
- 8 sample users (password123)
- 6 sample events
- Multiple registrations

### Step 7: Run on Production Server

#### Option A: Using Gunicorn (Recommended)
```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Run in background (Linux/macOS)
nohup gunicorn -w 4 -b 0.0.0.0:5000 run:app &

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 \
    --access-logfile access.log \
    --error-logfile error.log \
    run:app
```

#### Option B: Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

Build and run:
```bash
docker build -t ems-app .
docker run -p 5000:5000 --env-file .env ems-app
```

---

## Part 3: Switching from SQLite to MySQL

### For Existing Development Setup

If you've been developing with SQLite and want to switch to MySQL:

### Step 1: Backup SQLite Database
```bash
cp ems_dev.db ems_dev.db.backup
```

### Step 2: Create MySQL Database
```bash
mysql -u root -p
CREATE DATABASE ems_development;
GRANT ALL PRIVILEGES ON ems_development.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 3: Update config.py

```python
# In DevelopmentConfig class
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ems_user:password@localhost/ems_development'
```

### Step 4: Reinitialize Database
```bash
python seed_data.py
```

---

## Part 4: Running with Nginx Reverse Proxy

### Nginx Configuration

Create `/etc/nginx/sites-available/ems`:

```nginx
upstream flask_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 16M;

    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/ems/app/static;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ems /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Part 5: SSL/HTTPS Setup (Let's Encrypt)

### Using Certbot
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Updated Nginx Config
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Part 6: Maintenance & Monitoring

### Regular Backups

#### MySQL Backup
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/ems"
DATE=$(date +%Y%m%d_%H%M%S)

mysqldump -u ems_user -p ems_production > $BACKUP_DIR/ems_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

#### Cron Job Setup
```bash
crontab -e

# Add this line to backup daily at 2 AM
0 2 * * * /path/to/backup_script.sh
```

### Monitoring Health

```bash
# Check application status
curl -s http://localhost:5000/auth/login | grep -q "User Login"

# Monitor system resources
htop

# Check database connections
mysql -u ems_user -p -e "SHOW PROCESSLIST;"
```

### Log Management

```bash
# Rotate Gunicorn logs
sudo logrotate -v /etc/logrotate.d/ems

# View application logs
tail -f error.log
tail -f access.log
```

---

## Part 7: Troubleshooting

### Issue: Port 5000 Already in Use
```bash
# Find process using port
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # macOS/Linux

# Run on different port
python -c "from run import app; app.run(port=5001)"
```

### Issue: Module Import Errors
```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt

# Verify installation
python -c "from app import create_app; print('✓ Import successful')"
```

### Issue: Database Connection Failed
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1;"

# Verify credentials in .env
cat .env | grep DATABASE_URL

# Test connection
python -c "
from app import create_app
from config import ProductionConfig
app = create_app(ProductionConfig)
with app.app_context():
    from app.models import db
    db.engine.execute('SELECT 1')
    print('✓ Database connected!')
"
```

### Issue: Image Upload Not Working
```bash
# Check directory permissions
ls -la app/static/uploads/
ls -la app/static/qrcodes/

# Fix permissions
chmod 755 app/static/uploads
chmod 755 app/static/qrcodes
```

### Issue: QR Code Generation Fails
```bash
# Verify qrcode package
pip show qrcode

# Reinstall if needed
pip install --upgrade qrcode
```

---

## Part 8: Performance Optimization

### Enable Caching
```python
# In app/__init__.py
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Use with routes
@app.route('/events')
@cache.cached(timeout=300)
def get_events():
    # ...
```

### Database Query Optimization
```python
# Use eager loading for relationships
events = Event.query.options(
    db.joinedload(Event.registrations)
).all()
```

### Static File Compression
```bash
# Install brotli
pip install brotli

# Configure in Nginx
gzip on;
gzip_types text/css application/javascript;
```

---

## Part 9: Security Checklist

- [ ] Change SECRET_KEY to random value
- [ ] Set DEBUG = False in production
- [ ] Use HTTPS with valid SSL certificate
- [ ] Set secure database password
- [ ] Configure CORS if needed
- [ ] Enable rate limiting
- [ ] Set secure session cookies
- [ ] Regular database backups
- [ ] Monitor for suspicious activity
- [ ] Keep dependencies updated

---

## Part 10: Deployment Checklist

- [ ] Database created and tested
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Database seeded with initial data
- [ ] Static files collected
- [ ] Email configured (if applicable)
- [ ] Reverse proxy configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Monitoring tools set up
- [ ] Backup scripts scheduled
- [ ] Application tested thoroughly

---

## Quick Command Reference

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize database
python seed_data.py

# Run development server
python run.py

# Run production server
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Access admin
Login at: http://localhost:5000/auth/admin-login
Username: admin
Password: admin123

# Reset database (development only)
del ems_dev.db  # Windows
rm ems_dev.db  # macOS/Linux
python seed_data.py
```

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Complete
