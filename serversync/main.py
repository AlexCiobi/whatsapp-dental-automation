import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes.health import router as health_router
from routes.whatsapp import router as whatsapp_router
from routes.vapi import router as vapi_router
from routes.appointments import router as appointments_router
from scheduler import start_scheduler, shutdown_scheduler

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="ServeSync AI", lifespan=lifespan)
app.include_router(health_router)
app.include_router(whatsapp_router)
app.include_router(vapi_router)
app.include_router(appointments_router)
