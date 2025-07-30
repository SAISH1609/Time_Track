# TimeTrack - Note Keeping & Time Tracking Application

A comprehensive time tracking and task management application built with Next.js frontend, FastAPI backend, and Supabase/PostgreSQL database.

## Features

- **Task & Time Tracking**: Create tasks, track time with start/pause/stop functionality
- **Sub-task Support**: Link sub-tasks to parent tasks for complex projects
- **ACE Timesheet Integration**: Seamless integration with ACE timesheet platform
- **Performance Review Preparation**: Generate comprehensive reports for reviews
- **Automated Summaries**: Send periodic summaries to supervisors via Teams/Email
- **Data Export**: Export logs and reports in CSV/Excel formats
- **AI-powered Insights**: Natural language interface for work analysis
- **Visual Dashboards**: Time allocation charts and project status tracking

## Tech Stack

- **Frontend**: Next.js 13+ with TypeScript, Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: Supabase/PostgreSQL
- **Containerization**: Docker & Docker Compose
- **Authentication**: JWT-based auth
- **AI Integration**: OpenAI API for insights

## Quick Start with Docker

### Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **Git** (to clone the repository)
  cls

### 🚀 TL;DR - Quick Start (5 minutes)

```bash
git clone <repository-url>
cd TimeTrack
docker-compose up -d
# Wait for containers to start (~2-3 minutes)
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
docker-compose exec backend alembic upgrade head
# Visit http://localhost:3000 ✅
```

### Step-by-Step Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd TimeTrack
   ```

2. **Create environment file**

   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env with your actual values (optional for development)
   # The default values work out-of-the-box for local development
   ```

   ```bash
   # The .env file is already configured with development settings
   # No changes needed for local development

   # Optional: View the current configuration
   cat .env
   ```

   **For production or custom setup**, edit the `.env` file:

   ```env
   # Database (these work out-of-the-box)
   POSTGRES_USER=timetrack_user
   POSTGRES_PASSWORD=timetrack_password
   POSTGRES_DB=timetrack_db

   # Required: Change this secret key for production
   SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

   # Optional: Add your API keys for full functionality
   OPENAI_API_KEY=your-openai-api-key
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

3. **Start the application**

   ```bash
   # Build and start all services (this may take 2-3 minutes on first run)
   docker-compose up -d

   # Watch the startup process (optional)
   docker-compose logs -f
   ```

4. **Wait for services to be ready**

   ```bash
   # Check if all services are running
   docker-compose ps

   # You should see 3 containers running:
   # timetrack_frontend    Up    0.0.0.0:3000->3000/tcp
   # timetrack_backend     Up    0.0.0.0:8000->8000/tcp
   # timetrack_postgres    Up    0.0.0.0:5432->5432/tcp
   ```

5. **Initialize the database**

   **Important:** The database needs to be set up with tables before you can use the application.

   ```bash
   # First, check if migration files exist
   docker-compose exec backend ls alembic/versions/

   # If the folder is empty, create the initial migration:
   docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

   # Then apply the migration to create tables:
   docker-compose exec backend alembic upgrade head

   # Verify tables were created:
   docker-compose exec postgres psql -U timetrack_user -d timetrack_db -c "\dt"
   ```

   **Expected output:** You should see tables like `users`, `projects`, `tasks`, `time_entries`, and `alembic_version`.

6. **Access the application**

   - **Frontend**: http://localhost:3000 (Main Application)
   - **Backend API**: http://localhost:8000/api/v1
   - **API Documentation**: http://localhost:8000/docs (Interactive API docs)

### Verification Steps

After setup, verify everything is working:

```bash
# 1. Check all services are running
docker-compose ps

# 2. Test backend health
curl http://localhost:8000/health

# 3. Test frontend (should return HTML)
curl http://localhost:3000

# 4. View logs if something isn't working
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### First Time Setup Complete!

🎉 **Your TimeTrack application is now running!**

**Next Steps:**

1. **Visit http://localhost:3000** - Main application interface
2. **Register a new account** - Use the API at http://localhost:8000/docs
3. **Start tracking time** - Use the timer widget on the homepage

**Important Notes for New Users:**

- The database starts empty - you'll need to register the first user
- All data is stored in Docker volumes (persists between restarts)
- Use http://localhost:8000/docs for API testing and user registration

**Test Registration:**

```bash
# Test if the database is ready
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### Docker Services

The application consists of three main services:

- **PostgreSQL Database** (port 5432)
- **FastAPI Backend** (port 8000)
- **Next.js Frontend** (port 3000)

### Useful Docker Commands

```bash
# Stop all services
docker-compose down

# Stop and remove all data (complete reset)
docker-compose down -v

# Rebuild and restart services (if you make changes)
docker-compose up -d --build

# View real-time logs
docker-compose logs -f

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Access backend container shell (for debugging)
docker-compose exec backend bash

# Access database directly
docker-compose exec postgres psql -U timetrack_user -d timetrack_db
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "relation 'users' does not exist" Error

This means the database migration hasn't been run yet.

**Solution:**

```bash
# Check if migration files exist
docker-compose exec backend ls alembic/versions/

# If empty, create initial migration
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

# Apply migration
docker-compose exec backend alembic upgrade head
```

#### 2. SQLAlchemy Relationship Errors

If you see errors about missing relationships or circular imports:

**Solution:**

```bash
# Restart the backend service
docker-compose restart backend

# Check logs for specific errors
docker-compose logs backend
```

#### 3. Port Already in Use

If you get "port already in use" errors:

**Solution:**

```bash
# Check what's using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Stop any conflicting services or use different ports in docker-compose.yml
```

#### 4. Frontend Build Issues

If the frontend fails to start:

**Solution:**

```bash
# Rebuild the frontend container
docker-compose build frontend

# Check frontend logs
docker-compose logs frontend
```

#### 5. Database Connection Issues

If the backend can't connect to the database:

**Solution:**

```bash
# Ensure postgres service is running
docker-compose ps

# Check postgres logs
docker-compose logs postgres

# Restart all services in correct order
docker-compose down
docker-compose up -d postgres
sleep 10
docker-compose up -d backend frontend

# Restart a specific service
docker-compose restart backend

# Check service status
docker-compose ps

# See resource usage
docker-compose top
```

### Common First-Time Issues

**Issue: Port already in use**

```bash
# Check what's using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Solution: Kill the process or change ports in docker-compose.yml
```

**Issue: Services not starting**

```bash
# Check logs for errors
docker-compose logs

# Try rebuilding
docker-compose down
docker-compose up -d --build
```

**Issue: Database connection errors**

```bash
# Ensure PostgreSQL container is running
docker-compose ps postgres

# Reset database if needed
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

## Development Setup

For local development without Docker:

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables

Create `.env` file in the root directory:

```env
# Database Configuration
POSTGRES_USER=timetrack_user
POSTGRES_PASSWORD=timetrack_password
POSTGRES_DB=timetrack_db
DATABASE_URL=postgresql://timetrack_user:timetrack_password@localhost:5432/timetrack_db

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase Configuration (optional)
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key

# OpenAI Configuration (for AI insights)
OPENAI_API_KEY=your-openai-api-key

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Microsoft Teams Integration
TEAMS_WEBHOOK_URL=your-teams-webhook-url

# ACE Timesheet Integration
ACE_API_BASE_URL=your-ace-api-base-url
ACE_API_KEY=your-ace-api-key
```

Frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Project Structure

```
TimeTrack/
├── README.md
├── docker-compose.yml          # Multi-service orchestration
├── .env                        # Environment variables
│
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── core/              # Configuration & startup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── crud/              # Database operations
│   │   ├── services/          # Business logic
│   │   ├── routers/           # API endpoints
│   │   ├── utils/             # Helper functions
│   │   └── main.py            # FastAPI app entry point
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container config
│   └── .env                   # Backend environment variables
│
└── frontend/                  # Next.js Frontend
    ├── public/                # Static assets
    ├── src/
    │   ├── components/        # React components
    │   ├── pages/             # Next.js routes
    │   ├── hooks/             # Custom React hooks
    │   ├── lib/               # API clients & utilities
    │   ├── types/             # TypeScript definitions
    │   └── styles/            # CSS styles
    ├── package.json           # Node.js dependencies
    ├── Dockerfile             # Frontend container config
    ├── next.config.js         # Next.js configuration
    ├── tailwind.config.js     # Tailwind CSS config
    ├── tsconfig.json          # TypeScript config
    └── .env.local             # Frontend environment variables
```

## Troubleshooting

### Common Issues

**1. Port Already in Use**

```bash
# Check what's using the port
lsof -i :3000  # Frontend port
lsof -i :8000  # Backend port
lsof -i :5432  # Database port

# Kill the process or change ports in docker-compose.yml
```

**2. Database Connection Issues**

```bash
# Check if PostgreSQL container is running
docker-compose ps

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up postgres -d
```

**3. Backend API Errors**

```bash
# Check backend logs
docker-compose logs backend

# Restart backend service
docker-compose restart backend

# Access backend container for debugging
docker-compose exec backend bash
```

**4. Frontend Build Errors**

```bash
# Check frontend logs
docker-compose logs frontend

# Clear Next.js cache
docker-compose exec frontend rm -rf .next

# Rebuild frontend
docker-compose up frontend -d --build
```

**5. Environment Variables Not Loading**

```bash
# Verify .env file exists and has correct values
cat .env

# Restart all services after env changes
docker-compose down
docker-compose up -d
```

### Performance Optimization

- **Production Deployment**: Use `docker-compose.prod.yml` for production
- **Database**: Consider connection pooling for high traffic
- **Frontend**: Enable Next.js static generation where possible
- **Caching**: Implement Redis for session management and caching

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check database connectivity
docker-compose exec backend python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# Check frontend status
curl http://localhost:3000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
