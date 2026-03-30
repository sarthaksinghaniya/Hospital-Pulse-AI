# Hospital Pulse AI - Production Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Docker & Docker Compose
- Production server with at least 2GB RAM
- SSL certificate (recommended)
- Domain name configured

### Environment Configuration

1. **Update Environment Variables**
   ```bash
   # Copy and configure environment
   cp backend/env/.env.example backend/env/.env
   
   # Update with your production values:
   # - PROD_CORS_ORIGINS=https://yourdomain.com
   # - OPENAI_API_KEY=your-production-key (optional)
   ```

2. **Domain Configuration**
   ```bash
   # Update frontend API base URL if needed
   # In frontend/.env.production:
   VITE_API_BASE=https://api.yourdomain.com
   ```

### Deployment Options

#### Option 1: Docker Compose (Recommended)
```bash
# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Check deployment status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Option 2: Manual Deployment
```bash
# Backend Deployment
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend Deployment
cd frontend
npm run build
# Serve the dist/ folder with nginx or apache
```

### Nginx Configuration (Optional)

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend availability
curl https://yourdomain.com

# Docker health status
docker-compose -f docker-compose.prod.yml exec hospital-pulse-backend curl -f http://localhost:8000/health
```

### Monitoring & Logging

```bash
# Real-time logs
docker-compose -f docker-compose.prod.yml logs -f

# Backend logs only
docker-compose -f docker-compose.prod.yml logs hospital-pulse-backend

# Frontend logs only
docker-compose -f docker-compose.prod.yml logs hospital-pulse-frontend
```

### Security Considerations

1. **Environment Variables**
   - Never commit API keys to version control
   - Use production-only API keys
   - Rotate keys regularly

2. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Limit API rate limiting

3. **Data Protection**
   - Regular backups of model files
   - Secure database connections
   - Monitor access logs

### Troubleshooting

#### Common Issues

1. **CORS Errors**
   ```bash
   # Check CORS origins in .env
   echo $PROD_CORS_ORIGINS
   
   # Verify frontend domain matches
   ```

2. **Backend Connection Issues**
   ```bash
   # Check backend health
   docker-compose exec hospital-pulse-backend curl -f http://localhost:8000/health
   
   # Check port binding
   docker-compose exec hospital-pulse-backend netstat -tlnp | grep :8000
   ```

3. **Frontend Build Issues**
   ```bash
   # Clean build cache
   cd frontend
   rm -rf node_modules dist
   npm install
   npm run build
   ```

### Performance Optimization

1. **Backend**
   - Use multiple workers: `--workers 4`
   - Enable gzip compression
   - Configure reverse proxy caching

2. **Frontend**
   - Enable gzip on web server
   - Implement CDN for static assets
   - Use browser caching headers

### Scaling Considerations

- **Horizontal Scaling**: Multiple backend containers behind load balancer
- **Database Scaling**: Consider managed database service for high load
- **CDN**: Use content delivery network for frontend assets
- **Monitoring**: Implement application performance monitoring

### Backup Strategy

```bash
# Data backup (models, configurations)
tar -czf hospital-pulse-backup-$(date +%Y%m%d).tar.gz backend/services/ backend/env/

# Container state backup
docker-compose -f docker-compose.prod.yml down
docker save hospital-pulse-backend > hospital-pulse-backend-$(date +%Y%m%d).tar
docker save hospital-pulse-frontend > hospital-pulse-frontend-$(date +%Y%m%d).tar
```

---

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Firewall rules set
- [ ] Health checks enabled
- [ ] Logging configured
- [ ] Backup strategy implemented
- [ ] Monitoring set up
- [ ] Load testing performed
- [ ] Security audit completed

---

**Support**: For deployment issues, check logs and refer to troubleshooting section.
