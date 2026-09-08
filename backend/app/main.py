from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.scheduler import detener_scheduler, iniciar_scheduler
from app.routers import (
    auth,
    cartera,
    clientes,
    dashboard,
    declaraciones,
    facturas,
    leads,
    manifiestos,
    plantas,
    residuos,
    roles,
    servicios,
    usuarios,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    iniciar_scheduler()
    yield
    detener_scheduler()


app = FastAPI(title="EcoGlobal API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(roles.router)
app.include_router(clientes.router)
app.include_router(leads.router)
app.include_router(residuos.router)
app.include_router(plantas.router)
app.include_router(servicios.router)
app.include_router(manifiestos.router)
app.include_router(declaraciones.router)
app.include_router(facturas.router)
app.include_router(cartera.router)
app.include_router(dashboard.router)


@app.get("/api/v1/health")
def health():
    return {"success": True, "message": "ok", "data": None}
