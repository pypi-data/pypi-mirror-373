from fastapi import FastAPI, APIRouter


def setup_health_handler(app: FastAPI):
    health_router = APIRouter()

    @health_router.get("/actuator/health")
    async def health_check():
        """返回应用的健康状态"""
        return {
            "status": "UP",
            "groups": ["liveness", "readiness"]
        }

    app.include_router(health_router)

    return app
