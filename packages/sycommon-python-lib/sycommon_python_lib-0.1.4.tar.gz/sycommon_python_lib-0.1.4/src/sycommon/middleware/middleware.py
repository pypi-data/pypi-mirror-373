from sycommon.health.ping import setup_ping_handler
from sycommon.middleware.cors import setup_cors_handler
from sycommon.middleware.exception import setup_exception_handler
from sycommon.middleware.monitor_memory import setup_monitor_memory_middleware
from sycommon.middleware.mq import setup_mq_middleware
from sycommon.middleware.timeout import setup_request_timeout_middleware
from sycommon.middleware.traceid import setup_trace_id_handler
from sycommon.health.health_check import setup_health_handler


class Middleware:

    @classmethod
    def setup_middleware(cls, app, config: dict):
        # 设置请求超时中间件
        app = setup_request_timeout_middleware(app, config)

        # 设置异常处理
        app = setup_exception_handler(app, config)

        # 设置 trace_id 处理中间件
        app = setup_trace_id_handler(app)

        # 设置内存监控中间件
        # app = setup_monitor_memory_middleware(app)

        # 设置cors
        # app = setup_cors_handler(app)

        # 健康检查
        app = setup_health_handler(app)

        # ping
        app = setup_ping_handler(app)

        # 添加mq中间件
        # app = setup_mq_middleware(app)

        return app
