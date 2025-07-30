from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, timer
# Import all models to ensure they are registered with SQLAlchemy
from app.models import User, Project, Task, TimeEntry


def create_application() -> FastAPI:
    """Create FastAPI application with all configurations."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="TimeTrack API - Time tracking and task management application"
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin)
                           for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include routers
    app.include_router(
        auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
    app.include_router(
        timer.router, prefix=f"{settings.API_V1_STR}/timer", tags=["timer"])

    @app.get("/")
    async def root():
        return {
            "message": "TimeTrack API",
            "version": settings.VERSION,
            "status": "running"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_application()
