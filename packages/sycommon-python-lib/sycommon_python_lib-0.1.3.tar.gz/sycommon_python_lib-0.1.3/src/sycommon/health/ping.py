from fastapi import FastAPI, APIRouter


def setup_ping_handler(app: FastAPI):
    ping_router = APIRouter()

    @ping_router.get("/ping")
    async def ping():
        return {"status": "alive"}

    app.include_router(ping_router)

    return app
