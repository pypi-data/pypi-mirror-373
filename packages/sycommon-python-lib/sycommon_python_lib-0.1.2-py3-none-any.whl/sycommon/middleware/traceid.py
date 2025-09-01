import json
import re
from typing import Dict, Any
from fastapi import Request, Response
from sycommon.logging.kafka_log import SYLogger
from sycommon.tools.snowflake import Snowflake


def setup_trace_id_handler(app):
    @app.middleware("http")
    async def trace_id_and_log_middleware(request: Request, call_next):
        # 生成或获取 traceId
        trace_id = request.headers.get("x-traceId-header")
        if not trace_id:
            trace_id = Snowflake.next_id()

        # 设置 trace_id 上下文
        token = SYLogger.set_trace_id(trace_id)

        # 获取请求参数
        query_params = dict(request.query_params)
        request_body: Dict[str, Any] = {}
        files_info: Dict[str, str] = {}

        # 检测请求内容类型
        content_type = request.headers.get("content-type", "").lower()

        if "application/json" in content_type and request.method in ["POST", "PUT", "PATCH"]:
            try:
                request_body = await request.json()
            except Exception as e:
                request_body = {"error": f"Failed to parse JSON: {str(e)}"}

        elif "multipart/form-data" in content_type and request.method in ["POST", "PUT"]:
            try:
                # 从请求头中提取boundary
                boundary = None
                if "boundary=" in content_type:
                    boundary = content_type.split("boundary=")[1].strip()
                    boundary = boundary.encode('ascii')

                if boundary:
                    # 读取原始请求体
                    body = await request.body()

                    # 尝试从原始请求体中提取文件名
                    parts = body.split(boundary)
                    for part in parts:
                        part_str = part.decode('utf-8', errors='ignore')

                        # 使用正则表达式查找文件名
                        filename_match = re.search(
                            r'filename="([^"]+)"', part_str)
                        if filename_match:
                            field_name_match = re.search(
                                r'name="([^"]+)"', part_str)
                            field_name = field_name_match.group(
                                1) if field_name_match else "unknown"
                            filename = filename_match.group(1)
                            files_info[field_name] = filename
            except Exception as e:
                request_body = {
                    "error": f"Failed to process form data: {str(e)}"}

        # 构建请求日志信息
        request_message = {
            "method": request.method,
            "url": str(request.url),
            "query_params": query_params,
            "request_body": request_body,
            "uploaded_files": files_info if files_info else None
        }
        request_message_str = json.dumps(request_message, ensure_ascii=False)
        SYLogger.info(request_message_str)

        try:
            # 处理请求
            response = await call_next(request)

            content_type = response.headers.get("Content-Type", "")
            if "text/event-stream" in content_type:
                # 处理 SSE 响应
                response.headers["x-traceId-header"] = trace_id
                return response

            response_body = b""
            try:
                async for chunk in response.body_iterator:
                    response_body += chunk

                content_disposition = response.headers.get(
                    "Content-Disposition", "")

                # 判断是否能添加 trace_id
                if "application/json" in content_type and not content_disposition.startswith("attachment"):
                    try:
                        data = json.loads(response_body)
                        data["trace_id"] = trace_id
                        new_body = json.dumps(
                            data, ensure_ascii=False).encode()
                        response = Response(
                            content=new_body,
                            status_code=response.status_code,
                            headers=dict(response.headers)
                        )
                        response.headers["Content-Length"] = str(len(new_body))
                    except json.JSONDecodeError:
                        pass
            except StopAsyncIteration:
                pass

            # 构建响应日志信息
            response_message = {
                "status_code": response.status_code,
                "response_body": response_body.decode('utf-8', errors='ignore'),
            }
            response_message_str = json.dumps(
                response_message, ensure_ascii=False)
            SYLogger.info(response_message_str)

            response.headers["x-traceId-header"] = trace_id

            return response
        except Exception as e:
            error_message = {
                "error": str(e),
                "query_params": query_params,
                "request_body": request_body,
                "uploaded_files": files_info if files_info else None
            }
            error_message_str = json.dumps(error_message, ensure_ascii=False)
            SYLogger.error(error_message_str)  # 无需显式传递 trace_id
            raise
        finally:
            # 清理上下文变量，防止泄漏
            SYLogger.reset_trace_id(token)

    return app
