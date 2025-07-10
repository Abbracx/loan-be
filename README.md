# Loan Management System API

A Django REST API for managing loan applications with automated fraud detection, admin controls, and email notifications.

## Features

- **Loan Application Management**: Submit, view, and manage loan applications
- **Automated Fraud Detection**: Real-time fraud checks based on multiple criteria
- **Role-based Permissions**: Different access levels for users and admins
- **Email Notifications**: Async email alerts for flagged loans using Celery
- **Caching**: Redis-based caching for improved performance
- **Comprehensive Logging**: Detailed audit trails and error tracking
- **Admin Interface**: Django admin for loan management
- **API Documentation**: Swagger/ReDoc integration

## Installation & Setup

### Prerequisites

- Python 3.12+
- Redis (for caching and Celery)
- PostgreSQL (optional, SQLite used by default)

### Option 1: Local Installation

1. **Clone the repository**
```bash
git clone git@github.com:Abbracx/loan-be.git
cd loan-be
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env.local for local development settings
```

5. **Install and start Redis**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# Test Redis connection
redis-cli ping  # Should return: PONG
```

6. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

7. **Create logs directory**
```bash
mkdir logs
```

8. **Run the application**
```bash
# Terminal 1: Django server
export DJANGO_SETTINGS_MODULE=loan_be.settings.development
python manage.py runserver

# Terminal 2: Celery worker
celery -A loan_be worker --loglevel=info

# Terminal 3: Celery flower (optional monitoring)
celery -A loan_be flower
```

### Option 2: Docker Installation

1. **Clone and navigate**
```bash
git clone git@github.com:Abbracx/loan-be.git
cd loan-be
```

2. **Environment setup**
```bash
cp .env.example .env
# Edit .env for Docker settings (use service names like 'redis', 'postgres')
```

3. **Build and run**
```bash
make build
```

4. **Create superuser** (in new terminal)
```bash
make superuser
```

5. **Access services**
- **API**: http://localhost:8080
- **Admin**: http://localhost:8080/admin
- **MailHog**: http://localhost:8025 (Email testing)
- **Flower**: http://localhost:5555 (Celery monitoring)

### Docker Commands (using Makefile)

```bash
# Build and start containers
make build

# Start containers
make up

# Stop containers
make down

# View logs
make show-logs

# Access web container shell
make exec

# Run migrations
make migrate

# Create superuser
make superuser

# Run tests
make test

# Code formatting
make black
make isort

# Stop and remove volumes
make down-v
```

## Configuration

### Environment Variables

#### For Local Development (.env.local)

```bash
# Security
SECRET_KEY='django-insecure-2-ffsi9@x@wm86_baw*n-ipjd%dg8$cuy1$k1g@lh02hpqzxn'
SIGNING_KEY='ffsi9@x@wm86_baw*n-ipjd%dg8$cuy1$k1g@lh02hpqzxn'
DEBUG=True

# Domain
DOMAIN=localhost:8000

# Database (Local - use SQLite by default)
# DATABASE_URL=sqlite:///db.sqlite3

# Redis (Local)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# Email (Local - use console backend or SMTP)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@example.com
```

#### For Docker Development (.env)

```bash
# Security
SECRET_KEY='django-insecure-2-ffsi9@x@wm86_baw*n-ipjd%dg8$cuy1$k1g@lh02hpqzxn'
SIGNING_KEY='ffsi9@x@wm86_baw*n-ipjd%dg8$cuy1$k1g@lh02hpqzxn'
DEBUG=True

# Domain
DOMAIN=0.0.0.0:8000

# Database (Docker)
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Password123
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=loan-be-db
DATABASE_URL=postgres://postgres:Password123@postgres:5432/loan-be-db

# Redis (Docker)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
REDIS_URL=redis://redis:6379/0

# Email (Docker - using MailHog)
EMAIL_HOST=mailhog
EMAIL_PORT=1025
EMAIL_HOST_USER=mailtrap_user
EMAIL_HOST_PASSWORD=Password123
DEFAULT_FROM_EMAIL=Loan BE <no-reply@localhost>
```

### Key Differences: Local vs Docker

| Component | Local | Docker |
|-----------|-------|--------|
| Redis URL | `redis://localhost:6379/0` | `redis://redis:6379/0` |
| Database | SQLite or local PostgreSQL | `postgres://postgres:Password123@postgres:5432/loan-be-db` |
| Email | SMTP or console backend | MailHog (`mailhog:1025`) |
| Domain | `localhost:8000` | `0.0.0.0:8000` |

### Settings Structure

- `base.py`: Common settings
- `development.py`: Development overrides
- `test.py`: Test-specific settings
- `production.py`: Production configuration (create as needed)

## Troubleshooting

### Redis Connection Issues

**Local Development:**
- Ensure Redis is running: `redis-cli ping`
- Use `localhost` in Redis URLs

**Docker Development:**
- Use service names in Redis URLs: `redis://redis:6379/0`
- Ensure Redis service is running: `docker-compose ps`

### Database Issues

**Local:**
- Default uses SQLite (no setup required)
- For PostgreSQL: Install locally and update DATABASE_URL

**Docker:**
- Uses PostgreSQL service automatically
- Check service health: `make show-logs`

## API Endpoints

### Authentication
- `POST /api/v1/auth/jwt/create/` - Login
- `POST /api/v1/auth/jwt/refresh/` - Refresh token
- `POST /api/v1/auth/users/` - Register user

### Loan Applications
- `GET /api/v1/loans/applications/` - List user's loans
- `POST /api/v1/loans/applications/` - Submit loan application
- `GET /api/v1/loans/applications/{id}/` - Get loan details
- `POST /api/v1/loans/applications/{id}/approve/` - Approve loan (admin)
- `POST /api/v1/loans/applications/{id}/reject/` - Reject loan (admin)
- `POST /api/v1/loans/applications/{id}/flag/` - Flag loan (admin)

### Admin Endpoints
- `GET /api/v1/loans/flagged/` - List flagged loans (admin)
- `GET /api/v1/auth/users/` - List all users (admin)

### Documentation
- `GET /api/v1/auth/swagger/` - Swagger UI
- `GET /api/v1/auth/redoc/` - ReDoc UI

## Testing

### Run Tests
```bash
# Local
pytest tests/ --ds=loan_be.settings.test -v

# Docker
make test

# Verbose output
pytest tests/ --ds=loan_be.settings.test -vv -s
```

### Test Coverage
```bash
# Local
pytest tests/ --cov=apps --cov-report=html

# Docker
make cov-html
```

## Key Implementation Details

### Models

**LoanApplication**
- Uses UUID for public IDs
- Inherits from TimeStampedModel for audit trails
- Status choices: pending, approved, rejected, flagged
- Foreign key to User model

**FraudFlag**
- Links to LoanApplication
- Stores fraud detection reasons
- Timestamped for audit purposes

### Fraud Detection Logic

The system automatically flags loans based on:

1. **Multiple Applications**: >3 loans in 24 hours
2. **High Amount**: >NGN 5,000,000
3. **Suspicious Domain**: Email domain used by >10 users

### Permissions System

- **Regular Users**: Can only view/create their own loans
- **Admin Users**: Full access to all loans and admin actions
- **Object-level permissions**: Implemented via custom permission classes

### Caching Strategy

- **Loan Lists**: Cached per user with query parameters
- **Flagged Loans**: Cached for admin views
- **Domain Counts**: Cached for fraud detection (1 hour TTL)
- **Cache Invalidation**: Automatic on data changes

### Email System

- **Async Processing**: Uses Celery for non-blocking email sending
- **Fraud Notifications**: Automatic admin alerts for flagged loans
- **Retry Logic**: Built-in Celery retry mechanisms
- **Test Mode**: Synchronous execution in tests

## Assumptions & Design Decisions

### Business Logic Assumptions

1. **Fraud Detection**: 
   - Thresholds are configurable but hardcoded for simplicity
   - All three checks run simultaneously
   - Flagged loans require manual admin review

2. **User Management**:
   - Email is the primary login field
   - Account locking after 3 failed attempts
   - Admin users have full system access

3. **Loan Processing**:
   - Only admins can change loan status
   - Fraud detection runs on every submission
   - Status changes are logged for audit

### Technical Assumptions

1. **Database**:
   - SQLite for development/testing
   - PostgreSQL recommended for production
   - UUID used for public-facing IDs

2. **Caching**:
   - Redis available for caching and Celery
   - 5-minute TTL for most cached data
   - Cache invalidation on data changes

3. **Email**:
   - SMTP server available for email sending
   - Admin email addresses configured
   - Celery worker running for async processing

4. **Security**:
   - JWT tokens for authentication
   - CORS configured for API access
   - Rate limiting not implemented (add nginx/middleware)

### Scalability Considerations

1. **Database Optimization**:
   - Indexes on frequently queried fields
   - Prefetch related objects to reduce N+1 queries
   - Pagination on all list endpoints

2. **Caching Strategy**:
   - Strategic caching of expensive queries
   - Cache invalidation patterns
   - Redis clustering for high availability

3. **Background Processing**:
   - Celery for async tasks
   - Separate queues for different task types
   - Monitoring via Flower

## Monitoring & Logging

### Log Levels
- **INFO**: Normal operations, cache hits/misses
- **WARNING**: Fraud flags, failed login attempts
- **ERROR**: System errors, email failures

### Log Files
- Console output for development
- File logging: `logs/loan_be.log`
- Separate loggers for different apps

### Monitoring
- Celery Flower for task monitoring
- Django admin for data management
- Custom management commands for maintenance

## Production Deployment

### Additional Requirements
1. **Web Server**: Nginx/Apache for static files
2. **WSGI Server**: Gunicorn/uWSGI
3. **Database**: PostgreSQL with connection pooling
4. **Caching**: Redis cluster
5. **Monitoring**: Sentry for error tracking
6. **Security**: SSL certificates, security headers

### Environment Setup
```bash
# Production settings
DJANGO_SETTINGS_MODULE=loan_be.settings.production
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

This documentation provides a complete guide for setting up, running, and understanding the loan management system with all its features and assumptions clearly outlined.