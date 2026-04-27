from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import scraper, health, model, overview, analytics
from contextlib import asynccontextmanager
from app.scraper.worker import shutdown_executor

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    shutdown_executor()

# Inisiasi FastAPI app
app = FastAPI(
    title="HomeIQ API",
    description="HomeIQ untuk AI House Price Prediction.",
    version="1.0.0",
    lifespan=lifespan,
)

# Konfigurasi CORS untuk mengizinkan frontend React (port 3000) dan domain produksi
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(overview.router, prefix="/api/overview", tags=["Overview Statistics"])
app.include_router(model.router, prefix="/api/model", tags=["Machine Learning Model"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["House Data Scraper"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["House Data Analytics"])
app.include_router(health.router, prefix="/api/health", tags=["System Check"])

@app.get("/")
def root():
    return {"message": "Welcome to HomeIQ API. Akses /docs untuk melihat dokumentasi interaktif."}
