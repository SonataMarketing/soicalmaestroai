# SocialMaestro - Setup Guide

This guide will walk you through setting up the SocialMaestro backend from scratch.

## 📋 Prerequisites

### Required Software
- **Python 3.9+** - [Download here](https://python.org/downloads/)
- **PostgreSQL 13+** - [Download here](https://postgresql.org/download/)
- **Redis 6+** (optional) - [Download here](https://redis.io/download)
- **Git** - [Download here](https://git-scm.com/downloads)

### Required API Keys
You'll need API keys for various services. See the [API Setup Guide](#api-setup-guide) below.

## 🚀 Quick Start

### 1. Clone and Install Dependencies

```bash
# Navigate to the backend directory
cd ai-social-manager/backend

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb ai_social_manager

# Or using psql
psql -c "CREATE DATABASE ai_social_manager;"
```

### 3. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred editor
```

**Minimum required settings for initial setup:**
```env
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://username:password@localhost:5432/ai_social_manager
GEMINI_API_KEY=your-gemini-api-key-here
```

### 4. Create First Admin User

You have **three options** to create the first admin user:

#### Option A: CLI Script (Recommended)
```bash
# Check if bootstrap is needed
python scripts/create_admin.py status

# Create admin user interactively
python scripts/create_admin.py create
```

#### Option B: API Bootstrap Endpoint
```bash
# Start the server first
uvicorn main:app --reload --port 8000

# Check bootstrap status
curl http://localhost:8000/api/auth/bootstrap/status

# Create admin user via API
curl -X POST "http://localhost:8000/api/auth/bootstrap" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'
```

#### Option C: Direct Database Insert
```sql
-- Only use this as a last resort
INSERT INTO users (email, full_name, hashed_password, role, is_active, created_at)
VALUES (
  'admin@example.com',
  'Admin User',
  '$2b$12$encrypted_password_hash_here',
  'admin',
  true,
  NOW()
);
```

### 5. Start the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Verify Installation

1. **API Documentation**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)
2. **Health Check**: Visit [http://localhost:8000/health](http://localhost:8000/health)
3. **Login Test**: Use the login endpoint with your admin credentials

## 🔐 API Setup Guide

### Google Gemini AI (Required)
```bash
# Get your API key
# 1. Go to https://makersuite.google.com/app/apikey
# 2. Create a new API key
# 3. Add to .env file:
GEMINI_API_KEY=your-gemini-api-key-here
```

### Instagram (Meta Business)
```bash
# 1. Create Meta Developer account: https://developers.facebook.com/
# 2. Create new app, add Instagram Basic Display
# 3. Get your credentials:
INSTAGRAM_APP_ID=your-app-id
INSTAGRAM_APP_SECRET=your-app-secret
INSTAGRAM_ACCESS_TOKEN=your-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-business-account-id
```

### Reddit API
```bash
# 1. Go to https://www.reddit.com/prefs/apps
# 2. Create new application (script type)
# 3. Add credentials:
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
```

### Twitter API
```bash
# 1. Apply for Twitter Developer account: https://developer.twitter.com/
# 2. Create new app with read/write permissions
# 3. Add credentials:
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```

### LinkedIn API
```bash
# 1. Create LinkedIn Developer account: https://developer.linkedin.com/
# 2. Create new app, request necessary permissions
# 3. Add credentials:
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_ACCESS_TOKEN=your-access-token
```

### Facebook API
```bash
# Use same Meta Developer account as Instagram
# Add Facebook Login and Pages API to your app
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_ACCESS_TOKEN=your-access-token
FACEBOOK_PAGE_ID=your-page-id
```

## 📝 Using the API

### Authentication Flow

1. **Login** to get JWT tokens:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!"
  }'
```

2. **Use the access token** in subsequent requests:
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Creating Additional Users

```bash
# Only admins can create users
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@example.com",
    "full_name": "Marketing Manager",
    "password": "SecurePass123!",
    "role": "manager"
  }'
```

### Content Operations

```bash
# Generate AI content
curl -X POST "http://localhost:8000/api/content/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": 1,
    "content_type": "photo",
    "platform": "instagram"
  }'

# List content
curl -X GET "http://localhost:8000/api/content" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Approve content
curl -X POST "http://localhost:8000/api/content/1/approve" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approve",
    "feedback": "Looks great!"
  }'
```

## 🐞 Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U your_username -d ai_social_manager
```

#### Bootstrap Not Working
```bash
# Check if users already exist
python scripts/create_admin.py status

# Reset database (⚠️ This will delete all data)
psql -c "DROP DATABASE ai_social_manager; CREATE DATABASE ai_social_manager;"
```

#### Permission Denied Errors
```bash
# Check user roles
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# List available permissions
curl -X GET "http://localhost:8000/api/auth/permissions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### API Integration Issues
```bash
# Test API configurations
python -c "
from integrations.instagram import InstagramAPI
from integrations.reddit import RedditAPI
print('Instagram configured:', InstagramAPI().is_configured())
print('Reddit configured:', RedditAPI().is_configured())
"
```

### Debug Mode

Enable detailed logging:
```env
LOG_LEVEL=DEBUG
DEBUG=true
```

### Database Reset

If you need to start fresh:
```bash
# ⚠️ WARNING: This deletes all data
psql -c "DROP DATABASE ai_social_manager;"
psql -c "CREATE DATABASE ai_social_manager;"
python scripts/create_admin.py create
```

## 🚀 Production Deployment

### Environment Variables
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-very-secure-production-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/ai_social_manager
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t ai-social-manager .
docker run -p 8000:8000 ai-social-manager

# Or use docker-compose
docker-compose up -d
```

### Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Use strong passwords for admin users
- [ ] Enable HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Enable API rate limiting
- [ ] Review and rotate API keys regularly

## 📚 Next Steps

1. **Configure Social Media APIs** - Add your platform API keys
2. **Create Brands** - Set up brand profiles and style guides
3. **Enable Automation** - Turn on automated content generation
4. **Set Up Notifications** - Configure Slack/email notifications
5. **Monitor Performance** - Check analytics and adjust settings

## 🆘 Support

- **Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Logs**: Check application logs for detailed error information
- **GitHub Issues**: Report bugs and feature requests
- **Email**: support@aisocialmanager.com

## 📖 Additional Resources

- [API Documentation](http://localhost:8000/docs)
- [Database Schema](./database/models.py)
- [Configuration Guide](./.env.example)
- [Deployment Guide](./README.md#deployment)
