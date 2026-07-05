from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine, Base
from app.routes.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # =========================================
    # STARTUP
    # =========================================
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # =========================================
    # SHUTDOWN
    # =========================================


app = FastAPI(
    title="PAI Ticket Engine API",
    lifespan=lifespan
)

# =========================================
# CORS
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ROUTES
# =========================================
app.include_router(router)