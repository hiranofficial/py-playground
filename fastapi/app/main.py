from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="FastAPI Sample App")

# Include API routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Sample!"}
