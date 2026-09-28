# Deployment Guide: AI-Powered Smart University Digital Ecosystem

This guide provides step-by-step instructions for deploying the platform across various environments (Docker, Cloud VPS, Render/Vercel/SaaS, and Enterprise On-Premise).

---

## 1. Environment Variables Configuration

Before deploying, ensure your environment variables are configured. Copy `.env.example` to `.env` or set them in your deployment platform:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smart_university_db

# JWT Security
JWT_SECRET=your-production-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com

# AI Provider Configuration
AI_PROVIDER=local  # Options: local, openai, gemini, nvidia, glm
AI_MODEL=glm-4.7
AI_API_KEY=your-ai-api-key-if-not-local
AI_BASE_URL=
AI_TIMEOUT_SECONDS=20

# Frontend Configuration (for build time)
VITE_API_URL=https://api.your-domain.com/api/v1
```

---

## 2. Option A: Docker Compose Deployment (Single VPS / AWS EC2 / DigitalOcean)

Docker Compose is the fastest way to deploy the complete stack on a Linux virtual server.

### Prerequisites
- Docker & Docker Compose installed on your server.
- Domain name pointed to your server IP address (e.g. `api.yourdomain.com` and `app.yourdomain.com`).

### Deployment Steps

1. **Clone the repository on your server:**
   ```bash
   git clone https://github.com/your-org/smart-university-ecosystem.git
   cd smart-university-ecosystem
   ```

2. **Configure production environment:**
   Create a `.env` file in the root directory using the environment variable template above.

3. **Start the application stack:**
   ```bash
   docker-compose up -d --build
   ```

4. **Verify running containers:**
   ```bash
   docker-compose ps
   ```

5. **Set up Reverse Proxy & HTTPS (Nginx + Certbot):**

   Install Nginx and Certbot:
   ```bash
   sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx
   ```

   Nginx configuration (`/etc/nginx/sites-available/smartuniv`):
   ```nginx
   # Frontend App
   server {
       server_name app.yourdomain.com;
       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }

   # Backend API
   server {
       server_name api.yourdomain.com;
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   Enable site and obtain SSL certificate:
   ```bash
   sudo ln -s /etc/nginx/sites-available/smartuniv /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   sudo certbot --nginx -d app.yourdomain.com -d api.yourdomain.com
   ```

---

## 3. Option B: Cloud SaaS Deployment (Render / Railway / Vercel)

### Backend Deployment (Render or Railway)
1. Connect your GitHub repository to Render / Railway.
2. Select **Web Service** and set root directory to `backend/`.
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Add Environment Variables (`DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, etc.).

### Frontend Deployment (Vercel or Netlify)
1. Connect your GitHub repository to Vercel.
2. Set Root Directory to `frontend/`.
3. Set **Framework Preset**: Vite.
4. Set **Build Command**: `npm run build`
5. Set **Output Directory**: `dist`
6. Add Environment Variable: `VITE_API_URL=https://your-backend-api.onrender.com/api/v1`

---

## 4. Database Migrations & Seeding

When deploying to a new environment, initialize the database and seed initial demo accounts:

```bash
# Exec into running backend container
docker-compose exec backend python3 -c "from app.db.session import engine, Base, SessionLocal; from app.models import all_models; from app.services.demo_seed import seed_demo_accounts; Base.metadata.create_all(bind=engine); db=SessionLocal(); seed_demo_accounts(db); print('Database initialized & seeded!')"
```

---

## 5. Production Health Checks & Monitoring

- **API Documentation & Swagger UI**: `https://api.yourdomain.com/docs`
- **Health Check Endpoint**: `https://api.yourdomain.com/api/v1/academic/departments`
- **System Audit Logs**: Access via Admin Portal -> Audit Logs tab.
