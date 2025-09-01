
import tracemalloc
from fastapi import Request

from sycommon.logging.kafka_log import SYLogger


def setup_monitor_memory_middleware(app):
    @app.middleware("http")
    async def before_request(request: Request, call_next):
        # if not tracemalloc.is_tracing():
        #     tracemalloc.start()

        # snapshot1 = tracemalloc.take_snapshot()
        # await call_next(request)
        # snapshot2 = tracemalloc.take_snapshot()

        # top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        # if top_stats:
        #     SYLogger.info(f"内存增长最大项: {top_stats[0]}")
        pass
    return app
