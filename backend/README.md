# SocialMaestro - Backend

A comprehensive AI-powered social media management backend built with FastAPI, featuring content scraping, AI content generation, automated scheduling, and multi-platform publishing.

## 🚀 Features

### Core Functionality
- **AI Content Generation**: Generate captions and content ideas using Google Gemini AI
- **Content Scraping**: Scrape trending content from Instagram and Reddit using official APIs
- **Brand Analysis**: Analyze brand voice, style, and visual identity from websites and social media
- **Automated Scheduling**: Post content twice daily, alternating between photo and video posts
- **Review Workflow**: Human approval system with notifications and feedback
- **Multi-Platform Publishing**: Post to Instagram, Twitter, LinkedIn, and Facebook
- **Real-time Notifications**: Email, Slack, Discord, and webhook notifications
- **Analytics & Insights**: Performance tracking and AI-generated recommendations

### Technical Features
- **FastAPI Backend**: Modern, fast, and async Python web framework
- **PostgreSQL Database**: Robust relational database with SQLAlchemy ORM
- **JWT Authentication**: Secure role-based access control
- **Webhook Integrations**: Automatic posting via webhooks
- **Rate Limiting**: Prevent API abuse
- **Comprehensive Logging**: Full audit trail and error tracking
- **Docker Support**: Containerized deployment
- **API Documentation**: Auto-generated with Swagger/OpenAPI

## 🏗️ Architecture

```
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment configuration template
│   │
│   ├── config/
│   │   └── settings.py        # Application settings and configuration
│   │
│   ├── database/
│   │   ├── database.py        # Database connection and session management
│   │   └── models.py          # SQLAlchemy database models
│   │
│   ├── auth/
│   │   └── security.py        # Authentication, JWT, and security utilities
│   │
│   ├── api/
│   │   ├── dependencies.py    # FastAPI dependencies for auth and validation
│   │   └── routes/
│   │       ├── auth.py        # Authentication and user management routes
│   │       ├── content.py     # Content management and CRUD operations
│   │       ├── analytics.py   # Analytics and reporting routes
│   │       └── review.py      # Content review and approval routes
│   │
│   ├── modules/
│   │   ├── scheduler.py       # Task scheduling and automation
│   │   ├── scraper.py         # Content scraping from social platforms
│   │   ├── brand_analyzer.py  # Brand analysis and style guide generation
│   │   ├── generator.py       # AI content generation
│   │   ├── notifier.py        # Notification system
│   │   ├── publisher.py       # Content publishing to platforms
│   │   └── reporter.py        # Analytics and performance reporting
│   │
│   └── integrations/
│       ├── instagram.py       # Instagram Graph API integration
│       ├── reddit.py          # Reddit API integration (PRAW)
│       ├── twitter.py         # Twitter API v2 integration
│       ├── linkedin.py        # LinkedIn API integration
│       ├── facebook.py        # Facebook Graph API integration
│       └── webhooks.py        # Webhook management and notifications
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Redis 6+ (optional, for caching)
- API keys for social media platforms

### 1. Clone and Setup
```bash
cd ai-social-manager/backend
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Database Setup
```bash
# Create PostgreSQL database
createdb ai_social_manager

# Run migrations (if using Alembic)
alembic upgrade head
```

### 4. Create First Admin User

⚠️ **Important**: You must create an admin user before using the system.

#### Option A: CLI Script (Recommended)
```bash
# Interactive admin user creation
python scripts/create_admin.py create
```

#### Option B: API Bootstrap Endpoint
```bash
# Start the server first
uvicorn main:app --reload --port 8000

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

### 5. Start the Application
```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔧 API Configuration

### Required API Keys

#### Google Gemini AI
```bash
GEMINI_API_KEY=your-gemini-api-key
```
Get your key at: https://makersuite.google.com/app/apikey

#### Instagram (Meta Business)
```bash
INSTAGRAM_APP_ID=your-app-id
INSTAGRAM_APP_SECRET=your-app-secret
INSTAGRAM_ACCESS_TOKEN=your-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-business-account-id
```
Setup at: https://developers.facebook.com/

#### Reddit API
```bash
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
```
Create app at: https://www.reddit.com/prefs/apps

#### Twitter API
```bash
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```
Apply at: https://developer.twitter.com/

#### LinkedIn API
```bash
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_ACCESS_TOKEN=your-access-token
```
Setup at: https://developer.linkedin.com/

#### Facebook API
```bash
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_ACCESS_TOKEN=your-access-token
FACEBOOK_PAGE_ID=your-page-id
```
Use same Meta Developer account as Instagram

## 🚀 Usage

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

### Authentication
All API endpoints require JWT authentication. First, create the initial admin user:

```bash
# Check if bootstrap is needed
GET /api/auth/bootstrap/status

# Create first admin user (only works if no users exist)
POST /api/auth/bootstrap

# Login with admin credentials
POST /api/auth/login

# Create additional users (admin only)
POST /api/auth/register
```

### Content Management
```bash
# Generate AI content
POST /api/content/generate

# Create content manually
POST /api/content

# List content
GET /api/content

# Approve content
POST /api/content/{id}/approve

# Publish content
POST /api/content/{id}/publish
```

### Content Scraping
```bash
# Scrape trending content
POST /api/content/scrape

# Get scraped content
GET /api/content/scraped
```

### Analytics
```bash
# Get analytics
GET /api/content/analytics

# Get queue status
GET /api/content/queue-status
```

## 🔄 Automated Workflows

### Daily Schedule
- **6:00 AM**: Content scraping from Instagram and Reddit
- **8:00 AM**: Morning content generation and review requests
- **4:00 PM**: Evening content generation and review requests
- **Hourly**: Check for approval reminders and publishing queue

### Weekly Schedule
- **Monday 9:00 AM**: Brand analysis and style guide updates
- **Monday 9:30 AM**: Performance analysis and reporting

### Content Publishing
- Posts are automatically published based on schedule
- Failed posts are retried up to 3 times
- Notifications sent for all publishing events

## 📊 Database Schema

### Core Models
- **User**: Authentication and role management
- **Brand**: Brand information and style guides
- **ContentPost**: Social media posts and scheduling
- **ScrapedContent**: Discovered content from platforms
- **ContentReview**: Approval workflow and feedback
- **SocialAccount**: Connected social media accounts

### Analytics Models
- **PerformanceMetric**: Performance tracking data
- **AIInsight**: AI-generated insights and recommendations
- **ScheduledTask**: Background task management

## 🔐 Security Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (Admin, Manager, Editor, Viewer)
- Permission-based route protection
- API key authentication for webhooks

### Security Headers
- CORS protection
- Rate limiting
- Input sanitization
- Audit logging

### Data Protection
- Password hashing with bcrypt
- Secure token storage
- API key encryption
- HTTPS enforcement in production

## 🔔 Notification System

### Email Notifications
- Content approval requests
- Publishing confirmations
- Error alerts
- Weekly reports

### Webhook Integrations
- Slack notifications
- Discord alerts
- Microsoft Teams updates
- Zapier automation
- IFTTT triggers

### Real-time Notifications
- WebSocket support (planned)
- Push notifications (planned)
- Dashboard updates

## 📈 Monitoring & Analytics

### Application Metrics
- API response times
- Error rates
- User activity
- Content performance

### Business Metrics
- Content approval rates
- Publishing success rates
- Engagement analytics
- Platform-specific insights

### Health Checks
- Database connectivity
- External API status
- Background task status
- Cache performance

## 🐳 Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_social_manager
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ai_social_manager
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_content.py
```

## 📝 API Rate Limits

- **Default**: 100 requests per hour per user
- **Authentication**: 10 requests per minute
- **Content Generation**: 20 requests per hour
- **Publishing**: 50 requests per day

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Documentation: `/docs` endpoint
- Issues: GitHub Issues
- Email: support@aisocialmanager.com

## 🗺️ Roadmap

### Phase 1 (Complete)
- ✅ Core API development
- ✅ Authentication system
- ✅ Content management
- ✅ AI integration
- ✅ Multi-platform publishing

### Phase 2 (In Progress)
- 🔄 Advanced analytics
- 🔄 A/B testing for content
- 🔄 Enhanced brand analysis
- 🔄 Video content generation

### Phase 3 (Planned)
- 📋 Machine learning optimization
- 📋 Advanced automation workflows
- 📋 Mobile app support
- 📋 Enterprise features
