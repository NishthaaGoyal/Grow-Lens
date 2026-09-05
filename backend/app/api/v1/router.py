"""
Central API v1 router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    users,
    watchlists,
    snapshots,
    events,
    dashboard,
)

api_router = APIRouter()

api_router.include_router(users.router,      prefix="/users",      tags=["Users"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["Watchlists"])
api_router.include_router(snapshots.router,  prefix="/snapshots",  tags=["Snapshots"])
api_router.include_router(events.router,     prefix="/events",     tags=["Events"])
api_router.include_router(dashboard.router,  prefix="/dashboard",  tags=["Dashboard"])
