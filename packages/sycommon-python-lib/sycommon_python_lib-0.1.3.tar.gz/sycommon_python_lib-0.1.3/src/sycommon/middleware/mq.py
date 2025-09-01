
from sycommon.services import Services


def setup_mq_middleware(app):
    @app.on_event("shutdown")
    async def shutdown_event():
        await Services.shutdown()
    return app
