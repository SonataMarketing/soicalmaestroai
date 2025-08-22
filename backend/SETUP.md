# SocialMaestro Backend Setup Guide

This guide will help you set up the SocialMaestro backend for development and production.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis (for caching and task queues)
- Git

## Quick Setup

### 1. Automated Setup
Run the setup script to automatically install dependencies:

```bash
cd backend
python setup.py
```

### 2. Manual Setup

#### Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file with your configuration
nano .env  # or your preferred editor
```

## Database Setup

### PostgreSQL Installation

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS (using Homebrew)
```bash
brew install postgresql
brew services start postgresql
```

#### Windows
Download and install from: https://www.postgresql.org/download/windows/

### Database Configuration
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE socialmaestro_db;
CREATE USER socialmaestro_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE socialmaestro_db TO socialmaestro_user;

# Exit PostgreSQL
\q
```

### Initialize Database
```bash
# Run database initialization script
python scripts/init_db.py
```

## Redis Setup (Optional but Recommended)

### Installation

#### Ubuntu/Debian
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

#### macOS (using Homebrew)
```bash
brew install redis
brew services start redis
```

#### Windows
Download from: https://redis.io/download

## Environment Variables

Update your `.env` file with the following required variables:

### Database Configuration
```env
DATABASE_URL=postgresql://socialmaestro_user:your_password@localhost:5432/socialmaestro_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=socialmaestro_db
DATABASE_USER=socialmaestro_user
DATABASE_PASSWORD=your_password
```

### Security
```env
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

### API Keys (Optional for basic functionality)
```env
# OpenAI (for AI content generation)
OPENAI_API_KEY=your-openai-api-key

# Social Media APIs
INSTAGRAM_APP_ID=your-instagram-app-id
INSTAGRAM_APP_SECRET=your-instagram-app-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
```

## Running the Application

### Development Mode
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the development server
python main.py
```

The API will be available at:
- Main API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Production Mode
```bash
# Set environment to production
export DEBUG=False

# Run with Gunicorn (recommended for production)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Testing the Setup

### Health Checks
```bash
# Test API health
curl http://localhost:8000/health

# Test database connection
curl http://localhost:8000/health/database

# Test detailed health
curl http://localhost:8000/health/detailed
```

### Authentication Test
```bash
# Check if bootstrap is needed
curl http://localhost:8000/api/auth/bootstrap/status

# Create admin user (if bootstrap is needed)
curl -X POST http://localhost:8000/api/auth/bootstrap \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@socialmaestro.com",
    "full_name": "Admin User",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@socialmaestro.com",
    "password": "SecurePassword123!"
  }'
```

## Troubleshooting

### Common Issues

#### Database Connection Error
- Ensure PostgreSQL is running
- Check database credentials in .env file
- Verify database and user exist

#### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

#### Permission Errors
- Check file permissions
- Ensure virtual environment has proper permissions

#### Port Already in Use
- Change the port in main.py or kill the process using port 8000
- Check with: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows)

### Logs
Check the application logs for detailed error information:
- Development: Console output
- Production: `app.log` file

## Development Workflow

### Making Changes
1. Activate virtual environment
2. Make your changes
3. Test locally
4. Run tests (when available)
5. Commit changes

### Database Migrations
```bash
# When you modify models, recreate tables (development only)
python scripts/init_db.py

# For production, use proper migrations (TODO: Add Alembic)
```

## Production Deployment

### Environment Setup
- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Configure proper CORS origins
- Set up SSL/TLS
- Use environment-specific database

### Process Management
Consider using:
- **Systemd** (Linux)
- **PM2** (Node.js process manager)
- **Docker** (containerization)
- **Gunicorn** with multiple workers

### Monitoring
- Set up logging aggregation
- Monitor database performance
- Set up health check endpoints
- Configure alerts

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Support

If you encounter issues:
1. Check this documentation
2. Review error logs
3. Check GitHub issues
4. Contact support

---

## API Key Setup Guides

### OpenAI API
1. Visit https://platform.openai.com/
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Add to your .env file

### Social Media APIs

#### Instagram Basic Display API
1. Visit https://developers.facebook.com/
2. Create a new app
3. Add Instagram Basic Display product
4. Configure OAuth redirect URIs
5. Get App ID and App Secret

#### Facebook Graph API
1. Use the same app from Instagram setup
2. Add Facebook Login product
3. Configure permissions
4. Get App ID and App Secret

#### Twitter API v2
1. Visit https://developer.twitter.com/
2. Apply for developer account
3. Create a new app
4. Generate API keys and tokens
5. Add to your .env file

#### LinkedIn API
1. Visit https://www.linkedin.com/developers/
2. Create a new app
3. Configure OAuth 2.0 settings
4. Get Client ID and Client Secret

Remember to keep all API keys secure and never commit them to version control!
