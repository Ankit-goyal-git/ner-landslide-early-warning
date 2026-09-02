import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router

app = FastAPI(
    title="AI-Based Landslide Early Warning & Risk Monitoring System (NER)",
    description="Operational MVP for landslide hazard assessment, early warning, GIS mapping, and citizen reporting across 8 North-East Indian states.",
    version="1.0.0-hackathon-mvp",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(router)

# Mount Frontend static files if built
frontend_dist = os.path.join("frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    @app.get("/")
    def root():
        return {
            "project": "AI-Based Early Warning and Landslide Risk Monitoring System in North-East India (NER)",
            "version": "1.0.0-hackathon-mvp",
            "documentation": "/docs",
            "health_check": "/api/health",
            "mode": "Demo Mode — Historical NASA GLC Dataset & Calibrated Random Forest Model"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
