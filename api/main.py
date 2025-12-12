from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from storage import ensure_container
from routers import auth, files
from db import Base, engine

Base.metadata.create_all(bind=engine)


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(files.router)


@app.on_event('startup')
async def startup():
    await ensure_container()