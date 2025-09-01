
import time
from fastapi import Request
from fastapi.responses import JSONResponse


def setup_request_timeout_middleware(app, config: dict):
    # 设置全局请求超时时间
    REQUEST_TIMEOUT = int(config.get('Timeout', 30000))/1000

    @app.middleware("http")
    async def before_request(request: Request, call_next):
        request.state.start_time = time.time()
        response = await call_next(request)
        duration = time.time() - request.state.start_time
        if duration > REQUEST_TIMEOUT:
            return JSONResponse(content={'code': 1, 'error': 'Request timed out'}, status_code=504)
        return response
    return app
