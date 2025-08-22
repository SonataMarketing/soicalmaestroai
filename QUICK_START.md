# SocialMaestro - Quick Start Guide

Get SocialMaestro running with authentication in 5 minutes!

## 🚀 Step 1: Start the Backend

First, you need the SocialMaestro backend running:

```bash
cd ai-social-manager/backend

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with minimum required settings:
# SECRET_KEY=your-secret-key-here
# DATABASE_URL=postgresql://username:password@localhost:5432/ai_social_manager
# GEMINI_API_KEY=your-gemini-api-key (optional for now)

# Create database (PostgreSQL required)
createdb ai_social_manager

# Start the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend should now be running at `http://localhost:8000`

## 🔧 Step 2: Create Admin User

You have 3 options to create the first admin user:

### Option A: Using the Frontend (Recommended)
1. Visit `http://localhost:3000/signup`
2. You'll see "First-Time Setup" screen
3. Create your admin account

### Option B: Using CLI Script
```bash
cd ai-social-manager/backend
python scripts/create_admin.py create
```

### Option C: Using API Directly
```bash
curl -X POST "http://localhost:8000/api/auth/bootstrap" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "AdminPass123!",
    "confirm_password": "AdminPass123!"
  }'
```

## 🎯 Step 3: Configure Frontend

```bash
# Create frontend environment file
cd ai-social-manager
cp frontend-env-example.txt .env.local

# The file should contain:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## ✅ Step 4: Test Login

1. Visit `http://localhost:3000/login`
2. Use the credentials you created in Step 2
3. You should be redirected to the dashboard!

## 🐛 Troubleshooting

### "Login failed" Error
- ✅ Check backend is running: visit `http://localhost:8000/health`
- ✅ Verify admin user exists: run `python scripts/create_admin.py status`
- ✅ Check credentials match what you created

### "Bootstrap needed" on Signup
- This is normal for first-time setup
- Create your admin account through the signup form

### Database Connection Error
```bash
# Make sure PostgreSQL is running
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database if it doesn't exist
createdb ai_social_manager
```

### Backend Not Starting
```bash
# Check Python dependencies
pip install -r requirements.txt

# Verify .env file exists with required settings
cat .env
```

## 🆘 Still Having Issues?

1. **Check the browser console** for any JavaScript errors
2. **Check backend logs** for API errors
3. **Verify ports**: Backend on 8000, Frontend on 3000
4. **Test API directly**: `curl http://localhost:8000/health`

## 📝 Demo Credentials

After creating your admin account, you can create additional demo users:

```bash
# Login as admin first, then create demo users via API
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@example.com",
    "full_name": "Marketing Manager",
    "password": "ManagerPass123!",
    "role": "manager"
  }'
```

Once you have the backend running with an admin user, the login will work perfectly! 🎉
