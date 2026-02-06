from fastapi import FastAPI

from src.api_router import router

app = FastAPI(title="Voice Assistant Server", version="1.0.0")

app.include_router(router, prefix="/api", tags=["API"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # noqa: S104
