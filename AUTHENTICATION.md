# SocialMaestro Authentication System

This document explains how to set up and use the authentication system in SocialMaestro.

## 🚀 Quick Start

### First Time Setup

1. **Start the Backend**: Make sure the SocialMaestro backend is running on `http://localhost:8000`

2. **Create Environment File**:
   ```bash
   cp frontend-env-example.txt .env.local
   ```

3. **Start the Frontend**:
   ```bash
   npm run dev
   # or
   bun dev
   ```

4. **Initial Admin Setup**:
   - Visit `http://localhost:3000/signup`
   - If no users exist, you'll see a "First-Time Setup" screen
   - Create your first admin account
   - After creation, you'll be redirected to login

5. **Login**:
   - Visit `http://localhost:3000/login`
   - Use your admin credentials to sign in
   - You'll be redirected to the dashboard

## 🔐 Authentication Flow

### User Roles

The system supports 4 user roles with different permissions:

- **Admin** 👑: Full system access, can manage users and all content
- **Manager** 👥: Content & user management, approve posts
- **Editor** ✏️: Content creation & editing
- **Viewer** 👁️: Read-only access to dashboard and analytics

### Protected Routes

Most pages in SocialMaestro require authentication:

- **Dashboard** (`/`): All authenticated users
- **Content Pages** (`/scraper`, `/generator`, etc.): Role-based access
- **Analytics** (`/analytics`): Requires viewer role or higher
- **User Management**: Admin only (via API)

### Public Routes

These pages don't require authentication:

- **Login** (`/login`): Sign in page
- **Signup** (`/signup`): Account creation (with special bootstrap flow)
- **Unauthorized** (`/unauthorized`): Error page for insufficient permissions

## 🛠️ Usage

### Creating Additional Users

After setting up your admin account:

1. **Sign in as Admin**: Use your admin credentials
2. **API Access**: Use the backend API to create additional users
3. **Example**:
   ```bash
   curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "editor@example.com",
       "full_name": "Content Editor",
       "password": "SecurePass123!",
       "role": "editor"
     }'
   ```

### Password Requirements

All passwords must meet these criteria:
- At least 8 characters long
- Contains uppercase letter
- Contains lowercase letter
- Contains number
- Contains special character

### Token Management

- **Access tokens** expire after 30 minutes
- **Refresh tokens** are valid for 7 days
- Tokens are automatically refreshed when needed
- Manual logout clears all stored tokens

## 🔧 Configuration

### Environment Variables

Create `.env.local` with these variables:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# App Settings
NEXT_PUBLIC_APP_NAME=SocialMaestro
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Backend Requirements

The frontend expects these API endpoints:

- `POST /api/auth/bootstrap/status` - Check if setup needed
- `POST /api/auth/bootstrap` - Create first admin user
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Create new user (admin only)
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh access token

## 🎯 Features

### Smart Redirects

- Unauthenticated users are redirected to login
- After login, users return to their intended page
- Role-based access control with helpful error messages

### User Experience

- **Auto-login**: Stay signed in across browser sessions
- **Token refresh**: Seamless token renewal
- **Loading states**: Smooth authentication checks
- **Error handling**: Clear error messages for auth failures

### Security

- **JWT tokens**: Secure authentication
- **Role hierarchy**: Granular permission control
- **Auto-logout**: On token expiration or security issues
- **Password validation**: Strong password requirements

## 🔍 Troubleshooting

### Common Issues

**"Access Denied" Error:**
- Check your user role and permissions
- Contact admin for role upgrade
- Verify you're signed in correctly

**Login Not Working:**
- Verify backend is running on correct port
- Check credentials are correct
- Ensure user account is active

**First Setup Issues:**
- Make sure no users exist in the database
- Check backend is properly configured
- Verify API connectivity

**Token Issues:**
- Clear browser storage and re-login
- Check if backend authentication is working
- Verify API endpoint configuration

### Support

For authentication issues:
1. Check browser console for errors
2. Verify backend API is accessible
3. Ensure environment variables are set correctly
4. Contact your system administrator

## 📚 API Reference

For detailed API documentation, visit:
`http://localhost:8000/docs` (when backend is running)

This provides interactive documentation for all authentication endpoints.
