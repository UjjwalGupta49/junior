# Server Deployment Guide for Template Scraping System

## 🚀 Overview

This guide covers deploying the Microsoft Templates Scraper and AI Template Selector in server environments with production-ready configurations, monitoring, and error handling.

## 📋 Server Requirements

### **System Requirements**
- **OS**: Linux (Ubuntu 20.04+ recommended), CentOS 8+, or Docker
- **RAM**: Minimum 2GB, Recommended 4GB+
- **CPU**: 2+ cores recommended
- **Storage**: 1GB+ free space
- **Network**: Stable internet connection for scraping

### **Software Dependencies**
- **Python**: 3.8+ (3.9+ recommended)
- **Chrome/Chromium**: Latest stable version
- **ChromeDriver**: Auto-managed via webdriver-manager
- **System packages**: See installation section

## 🔧 Installation

### **1. System Package Installation**

#### **Ubuntu/Debian**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    xvfb \
    chromium-browser \
    chromium-chromedriver

# Install additional dependencies for headless Chrome
sudo apt install -y \
    libnss3-dev \
    libgconf-2-4 \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libgtk-3-0
```

#### **CentOS/RHEL**
```bash
# Update system packages
sudo yum update -y

# Install EPEL repository
sudo yum install -y epel-release

# Install required packages
sudo yum install -y \
    python3 \
    python3-pip \
    wget \
    curl \
    unzip \
    xorg-x11-server-Xvfb \
    chromium \
    chromium-headless

# Install additional dependencies
sudo yum install -y \
    nss \
    atk \
    at-spi2-atk \
    gtk3 \
    cups-libs \
    libdrm \
    libxkbcommon \
    libxcomposite \
    libxdamage \
    libxrandr \
    libgbm \
    libxss \
    alsa-lib
```

### **2. Python Environment Setup**

```bash
# Create project directory
sudo mkdir -p /opt/juniorAI
sudo chown $USER:$USER /opt/juniorAI
cd /opt/juniorAI

# Clone or copy your project
# git clone <your-repo> .
# OR copy files manually

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

### **3. Chrome Installation (if not available)**

```bash
# Download and install Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable
```

## ⚙️ Configuration

### **1. Environment Variables**

Create `/opt/juniorAI/.env`:
```bash
# Google Gemini AI Configuration
GOOGLE_API_KEY=your_actual_google_gemini_api_key_here
MODEL_NAME=gemini-2.5-flash-preview-05-20

# Server Configuration
LOG_LEVEL=INFO
MAX_TEMPLATES=100
HEADLESS_MODE=true

# Paths Configuration
TEMPLATES_DB_PATH=/opt/juniorAI/scripts/content/microsoft_templates.json
OUTPUT_PATH=/opt/juniorAI/scripts/output/
CONTENT_PATH=/opt/juniorAI/scripts/content/
```

### **2. Directory Structure**

```bash
# Create required directories
mkdir -p /opt/juniorAI/scripts/{content,output,template,user,logs}

# Set proper permissions
chmod 755 /opt/juniorAI/scripts/{content,output,template,user,logs}
```

### **3. Logging Configuration**

Create `/opt/juniorAI/scripts/logging.conf`:
```ini
[loggers]
keys=root,template_scraper,template_selector

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler,fileHandler

[logger_template_scraper]
level=INFO
handlers=fileHandler
qualname=template_scraper
propagate=0

[logger_template_selector]
level=INFO
handlers=fileHandler
qualname=template_selector
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=detailedFormatter
args=('/opt/juniorAI/scripts/logs/scraper.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s
```

## 🚀 Deployment Scripts

### **1. Systemd Service (Production)**

Create `/etc/systemd/system/template-scraper.service`:
```ini
[Unit]
Description=Microsoft Templates Scraper Service
After=network.target
Wants=network.target

[Service]
Type=oneshot
User=juniorai
Group=juniorai
WorkingDirectory=/opt/juniorAI/scripts
Environment=PATH=/opt/juniorAI/venv/bin
ExecStart=/opt/juniorAI/venv/bin/python template_scraper.py --headless --log-level INFO --max-templates 100
StandardOutput=journal
StandardError=journal
SyslogIdentifier=template-scraper

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/juniorAI/scripts/content /opt/juniorAI/scripts/logs

[Install]
WantedBy=multi-user.target
```

### **2. Cron Job for Regular Updates**

```bash
# Add to crontab for regular template updates
# Run every day at 2 AM
0 2 * * * cd /opt/juniorAI/scripts && /opt/juniorAI/venv/bin/python template_scraper.py --headless --log-level INFO >> /opt/juniorAI/scripts/logs/cron.log 2>&1
```

### **3. Docker Deployment**

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    chromium \
    chromium-driver \
    libnss3-dev \
    libgconf-2-4 \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY .env .env

# Create necessary directories
RUN mkdir -p scripts/{content,output,logs}

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Create non-root user
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app
USER scraper

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/test_template_scraper.py --max-templates 1 || exit 1

# Default command
CMD ["python", "scripts/template_scraper.py", "--headless", "--log-level", "INFO"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  template-scraper:
    build: .
    container_name: juniorai-scraper
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - MODEL_NAME=${MODEL_NAME}
      - LOG_LEVEL=INFO
    volumes:
      - ./scripts/content:/app/scripts/content
      - ./scripts/output:/app/scripts/output
      - ./scripts/logs:/app/scripts/logs
    restart: unless-stopped
    mem_limit: 2g
    cpus: 1.0
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - SYS_ADMIN  # Required for Chrome sandbox
```

## 📊 Monitoring and Logging

### **1. Log Monitoring**

```bash
# Monitor real-time logs
tail -f /opt/juniorAI/scripts/logs/scraper.log

# Monitor systemd service logs
journalctl -u template-scraper -f

# Check for errors
grep -i error /opt/juniorAI/scripts/logs/scraper.log
```

### **2. Health Checks**

Create `/opt/juniorAI/scripts/health_check.py`:
```python
#!/usr/bin/env python3
"""Health check script for server monitoring"""

import sys
import os
import json
import logging
from pathlib import Path

def check_templates_database():
    """Check if templates database exists and is valid"""
    db_path = Path("./content/microsoft_templates.json")
    
    if not db_path.exists():
        return False, "Templates database not found"
    
    try:
        with open(db_path, 'r') as f:
            data = json.load(f)
        
        if 'templates' not in data or len(data['templates']) == 0:
            return False, "Templates database is empty"
        
        return True, f"Database contains {len(data['templates'])} templates"
    
    except Exception as e:
        return False, f"Database validation failed: {e}"

def check_dependencies():
    """Check if all dependencies are available"""
    try:
        import selenium
        import google.generativeai
        import webdriver_manager
        return True, "All dependencies available"
    except ImportError as e:
        return False, f"Missing dependency: {e}"

def main():
    """Run health checks"""
    checks = [
        ("Dependencies", check_dependencies),
        ("Templates Database", check_templates_database),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            status = "PASS" if passed else "FAIL"
            print(f"{status}: {check_name} - {message}")
            
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"FAIL: {check_name} - Error: {e}")
            all_passed = False
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
```

### **3. Performance Monitoring**

Create monitoring script `/opt/juniorAI/scripts/monitor.py`:
```python
#!/usr/bin/env python3
"""Performance monitoring for template scraper"""

import psutil
import time
import json
from datetime import datetime

def get_system_metrics():
    """Get current system metrics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else None
    }

def log_metrics():
    """Log system metrics to file"""
    metrics = get_system_metrics()
    
    with open("./logs/metrics.jsonl", "a") as f:
        f.write(json.dumps(metrics) + "\n")
    
    print(f"CPU: {metrics['cpu_percent']}%, Memory: {metrics['memory_percent']}%")

if __name__ == "__main__":
    log_metrics()
```

## 🔒 Security Considerations

### **1. User Permissions**

```bash
# Create dedicated user for the service
sudo useradd -r -s /bin/false -d /opt/juniorAI juniorai

# Set proper ownership
sudo chown -R juniorai:juniorai /opt/juniorAI

# Set restrictive permissions
sudo chmod 750 /opt/juniorAI
sudo chmod 640 /opt/juniorAI/.env
```

### **2. Firewall Configuration**

```bash
# Allow only necessary outbound connections
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
```

### **3. Chrome Security**

The scraper runs Chrome with security-optimized flags:
- `--no-sandbox` (required for containers)
- `--disable-dev-shm-usage` (prevents crashes)
- `--disable-gpu` (not needed for scraping)
- `--disable-extensions` (reduces attack surface)

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Chrome/ChromeDriver Issues**
```bash
# Check Chrome installation
google-chrome --version
chromium --version

# Test ChromeDriver
python -c "from selenium import webdriver; from webdriver_manager.chrome import ChromeDriverManager; print('ChromeDriver OK')"
```

#### **2. Memory Issues**
```bash
# Monitor memory usage
free -h
ps aux | grep chrome

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### **3. Network Issues**
```bash
# Test connectivity to Microsoft Create
curl -I https://create.microsoft.com/en-us/search?filters=powerpoint

# Check DNS resolution
nslookup create.microsoft.com
```

### **Error Recovery**

The system includes automatic error recovery:
- **Retry logic** for failed requests
- **Exponential backoff** for rate limiting
- **Graceful degradation** when services are unavailable
- **Automatic cleanup** of resources

## 📈 Performance Optimization

### **1. Resource Limits**

```bash
# Set memory limits for Chrome
export CHROME_FLAGS="--memory-pressure-off --max_old_space_size=2048"

# Limit concurrent processes
ulimit -u 100
```

### **2. Caching Strategy**

- Templates database cached for 24 hours
- Failed requests cached for 1 hour
- Successful scrapes cached until next update

### **3. Batch Processing**

```bash
# Process templates in batches
python template_scraper.py --max-templates 50 --log-level INFO
```

## 🔄 Maintenance

### **Daily Tasks**
- Check log files for errors
- Monitor system resources
- Verify template database updates

### **Weekly Tasks**
- Review scraping success rates
- Update Chrome/ChromeDriver if needed
- Clean old log files

### **Monthly Tasks**
- Update Python dependencies
- Review and optimize scraping performance
- Backup templates database

## 📞 Support

For server deployment issues:

1. **Check logs**: `/opt/juniorAI/scripts/logs/`
2. **Run health check**: `python health_check.py`
3. **Test scraper**: `python test_template_scraper.py --max-templates 1`
4. **Monitor resources**: `python monitor.py`

---

**🚀 Your template scraping system is now ready for production server deployment!** 