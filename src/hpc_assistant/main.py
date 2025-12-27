from fastapi import FastAPI
from .api import endpoints
from .models.inference import initialize_model

app = FastAPI(
    title="HPC Assistant Server",
    description="A self-hosted assistant for research, analysis, and coding workflows on HPC clusters.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    print("Initializing model...")
    initialize_model()
    print("Model initialization complete.")

app.include_router(endpoints.router)

@app.get("/")
async def root():
    return {"message": "HPC Assistant Server is running."}


