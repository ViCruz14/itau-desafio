from fastapi import APIRouter

from interfaces.http.v1 import completions, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(completions.router)
