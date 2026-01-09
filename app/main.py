from fastapi import FastAPI
from routers.chat import router as chat_router

app = FastAPI()

app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Legal AI Backend"}
