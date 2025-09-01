import os
import sys
import traceback
import asyncio
import atexit
from datetime import datetime
import json
import re
import socket
import time
import threading
from queue import Queue, Full, Empty
from kafka import KafkaProducer
from loguru import logger
import loguru
from sycommon.config.Config import Config, SingletonMeta
from sycommon.middleware.context import current_trace_id
from sycommon.tools.snowflake import Snowflake

# 配置Loguru的颜色方案
LOGURU_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


class KafkaLogger(metaclass=SingletonMeta):
    _producer = None
    _topic = None
    _service_id = None
    _log_queue = Queue(maxsize=10000)
    _stop_event = threading.Event()
    _sender_thread = None
    _log_pattern = re.compile(
        r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s*\|\s*(\w+)\s*\|\s*(\S+):(\S+):(\d+)\s*-\s*(\{.*\})\s*$'
    )
    _queue_warning_threshold = 9000
    _queue_warning_interval = 60  # 秒
    _last_queue_warning = 0
    _shutdown_timeout = 15  # 关闭超时时间，秒
    _config = None  # 配置变量存储

    @staticmethod
    def setup_logger(config: dict):
        # 保存配置到类变量
        KafkaLogger._config = config

        from sycommon.synacos.nacos_service import NacosService
        KafkaLogger._topic = "shengye-json-log"
        KafkaLogger._service_id = NacosService(config).service_name

        # 获取 common 配置
        common = NacosService(config).share_configs.get("common.yml", {})
        bootstrap_servers = common.get("log", {}).get(
            "kafka", {}).get("servers", None)

        # 创建生产者，优化配置参数
        KafkaLogger._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(
                v, ensure_ascii=False).encode('utf-8'),
            max_block_ms=60000,  # 增加最大阻塞时间从30秒到60秒
            retries=10,  # 增加重试次数从5次到10次
            request_timeout_ms=30000,  # 增加请求超时时间从10秒到30秒
            compression_type='gzip',  # 添加压缩以减少网络传输量
            batch_size=16384,  # 增大批处理大小
            linger_ms=5,  # 添加短暂延迟以允许更多消息批处理
            buffer_memory=67108864,  # 增大缓冲区内存
            connections_max_idle_ms=540000,  # 连接最大空闲时间
            reconnect_backoff_max_ms=10000,  # 增加重连退避最大时间
        )

        # 启动后台发送线程
        KafkaLogger._sender_thread = threading.Thread(
            target=KafkaLogger._send_logs,
            daemon=True
        )
        KafkaLogger._sender_thread.start()

        # 注册退出处理
        atexit.register(KafkaLogger.close)

        # 设置全局异常处理器
        sys.excepthook = KafkaLogger._handle_exception

        def custom_log_handler(record):
            # 检查record是否是Message对象
            if isinstance(record, loguru._handler.Message):
                # 从Message对象中获取原始日志记录
                record = record.record

                # 提取基本信息
                message = record["message"]
                level = record["level"].name
                time_str = record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                # 提取文件、函数和行号信息
                file_info = record["file"].name
                function_info = record["function"]
                line_info = record["line"]

                # 尝试从message中提取trace_id
                trace_id = None
                try:
                    if isinstance(message, str):
                        msg_dict = json.loads(message)
                        trace_id = msg_dict.get("trace_id")
                except json.JSONDecodeError:
                    trace_id = None

                if not trace_id:
                    trace_id = SYLogger.get_trace_id() or Snowflake.next_id()

                # 获取线程/协程信息
                thread_info = SYLogger._get_execution_context()

                # 获取主机信息
                try:
                    ip = socket.gethostbyname(socket.gethostname())
                except socket.gaierror:
                    ip = '127.0.0.1'
                host_name = socket.gethostname()

                # 检查是否有错误信息并设置detail字段
                error_detail = ""
                if level == "ERROR" and record["exception"] is not None:
                    error_detail = "".join(traceback.format_exception(
                        record["exception"].type,
                        record["exception"].value,
                        record["exception"].traceback
                    ))

                # 获取logger名称作为类名
                class_name = record["name"]

                # 合并文件名和类名信息
                if file_info and class_name:
                    full_class_name = f"{file_info}:{class_name}"
                elif file_info:
                    full_class_name = file_info
                else:
                    full_class_name = class_name

                # 构建日志条目
                log_entry = {
                    "traceId": trace_id,
                    "sySpanId": "",
                    "syBizId": "",
                    "ptxId": "",
                    "time": time_str,
                    "day": datetime.now().strftime("%Y.%m.%d"),
                    "msg": message,
                    "detail": error_detail,
                    "ip": ip,
                    "hostName": host_name,
                    "tenantId": "",
                    "userId": "",
                    "customerId": "",
                    "env": Config().config['Nacos']['namespaceId'],
                    "priReqSource": "",
                    "reqSource": "",
                    "serviceId": KafkaLogger._service_id,
                    "logLevel": level,
                    "classShortName": "",
                    "method": "",
                    "line": "",
                    "theadName": thread_info,
                    "className": "",
                    "sqlCost": 0,
                    "size": len(str(message)),
                    "uid": int(trace_id) if trace_id and trace_id.isdigit() else 0
                }

                # 智能队列管理
                if not KafkaLogger._safe_put_to_queue(log_entry):
                    logger.warning(json.dumps({
                        "trace_id": trace_id,
                        "message": "Log queue is full, log discarded",
                        "level": "WARNING"
                    }, ensure_ascii=False))

        # 配置日志处理器
        logger.remove()

        # 添加Kafka日志处理器
        logger.add(
            custom_log_handler,
            level="INFO",
            enqueue=True  # 使用Loguru的队列功能
        )

        # 添加控制台错误日志处理器
        logger.add(
            sink=sys.stdout,
            level="ERROR",
            format=LOGURU_FORMAT,
            colorize=True,  # 启用颜色
            filter=lambda record: record["level"].name == "ERROR"
        )

    @staticmethod
    def _handle_exception(exc_type, exc_value, exc_traceback):
        """全局异常处理器"""
        # 跳过键盘中断（Ctrl+C）
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # 获取当前的trace_id
        trace_id = SYLogger.get_trace_id() or Snowflake.next_id()

        # 构建错误日志
        error_log = {
            "trace_id": trace_id,
            "message": f"Uncaught exception: {exc_type.__name__}: {str(exc_value)}",
            "level": "ERROR",
            "detail": "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        }

        # 使用Loguru记录错误，确保包含完整堆栈跟踪
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).error(
            json.dumps(error_log, ensure_ascii=False)
        )

    @staticmethod
    def _safe_put_to_queue(log_entry):
        """安全放入队列，提供更健壮的队列管理"""
        try:
            # 检查队列水位并发出警告
            current_time = time.time()
            qsize = KafkaLogger._log_queue.qsize()

            if qsize > KafkaLogger._queue_warning_threshold:
                if current_time - KafkaLogger._last_queue_warning > KafkaLogger._queue_warning_interval:
                    warning_msg = f"Log queue at {qsize}/{KafkaLogger._log_queue.maxsize} capacity"
                    print(warning_msg)
                    logger.warning(json.dumps({
                        "trace_id": log_entry.get("traceId"),
                        "message": warning_msg,
                        "level": "WARNING"
                    }, ensure_ascii=False))
                    KafkaLogger._last_queue_warning = current_time

            # 尝试快速放入
            KafkaLogger._log_queue.put(log_entry, block=False)
            return True
        except Full:
            # 队列已满时的处理策略
            if KafkaLogger._stop_event.is_set():
                # 关闭过程中直接丢弃日志
                return False

            # 尝试移除最旧的日志并添加新日志
            try:
                with threading.Lock():  # 添加锁确保操作原子性
                    if not KafkaLogger._log_queue.empty():
                        KafkaLogger._log_queue.get_nowait()
                    KafkaLogger._log_queue.put_nowait(log_entry)
                return True
            except Exception:
                return False

    @staticmethod
    def _send_logs():
        """后台线程：批量发送日志到Kafka，优化内存使用"""
        batch = []
        last_flush = time.time()
        batch_size = 100
        flush_interval = 1  # 秒
        consecutive_errors = 0
        max_consecutive_errors = 10  # 最大连续错误数，超过则降低处理速度
        last_reconnect_attempt = 0
        reconnect_interval = 30  # 重新连接尝试间隔，秒

        while not KafkaLogger._stop_event.is_set():
            try:
                # 检查生产者状态，如果长时间失败，尝试重新创建生产者
                current_time = time.time()
                if consecutive_errors > max_consecutive_errors and current_time - last_reconnect_attempt > reconnect_interval:
                    logger.warning(json.dumps({
                        "trace_id": "system",
                        "message": "尝试重新创建Kafka生产者以解决连接问题",
                        "level": "WARNING"
                    }, ensure_ascii=False))
                    last_reconnect_attempt = current_time

                    # 尝试重新创建生产者
                    try:
                        # 使用类变量中存储的配置
                        from sycommon.synacos.nacos_service import NacosService
                        common = NacosService(
                            KafkaLogger._config).share_configs.get("common.yml", {})
                        bootstrap_servers = common.get("log", {}).get(
                            "kafka", {}).get("servers", None)

                        # 关闭旧生产者
                        if KafkaLogger._producer:
                            KafkaLogger._producer.close(timeout=5)

                        # 创建新生产者
                        KafkaLogger._producer = KafkaProducer(
                            bootstrap_servers=bootstrap_servers,
                            value_serializer=lambda v: json.dumps(
                                v, ensure_ascii=False).encode('utf-8'),
                            max_block_ms=60000,
                            retries=10,
                            request_timeout_ms=30000,
                            compression_type='gzip',
                            batch_size=16384,
                            linger_ms=5,
                            buffer_memory=67108864,
                            connections_max_idle_ms=540000,
                            reconnect_backoff_max_ms=10000,
                        )
                        consecutive_errors = 0
                        logger.info(json.dumps({
                            "trace_id": "system",
                            "message": "Kafka生产者已重新创建",
                            "level": "INFO"
                        }, ensure_ascii=False))
                    except Exception as e:
                        logger.error(json.dumps({
                            "trace_id": "system",
                            "message": f"重新创建Kafka生产者失败: {str(e)}",
                            "level": "ERROR"
                        }, ensure_ascii=False))

                # 批量获取日志
                while len(batch) < batch_size and not KafkaLogger._stop_event.is_set():
                    try:
                        # 使用超时获取，避免长时间阻塞
                        log_entry = KafkaLogger._log_queue.get(timeout=0.5)
                        batch.append(log_entry)
                    except Empty:
                        break

                # 定时或定量发送
                current_time = time.time()
                if batch and (len(batch) >= batch_size or (current_time - last_flush > flush_interval)):
                    try:
                        # 分批发送，避免一次发送过大
                        sub_batch_size = min(50, batch_size)
                        for i in range(0, len(batch), sub_batch_size):
                            sub_batch = batch[i:i+sub_batch_size]
                            for entry in sub_batch:
                                KafkaLogger._producer.send(
                                    KafkaLogger._topic, entry)
                            KafkaLogger._producer.flush(timeout=15)

                        batch = []  # 发送成功后清空批次
                        last_flush = current_time
                        consecutive_errors = 0  # 重置错误计数
                    except Exception as e:
                        consecutive_errors += 1
                        error_msg = f"Kafka发送失败: {e}"
                        print(error_msg)
                        logger.error(json.dumps({
                            "trace_id": "system",
                            "message": error_msg,
                            "level": "ERROR"
                        }, ensure_ascii=False))

                        # 连续错误过多时增加休眠时间，避免CPU空转
                        if consecutive_errors > max_consecutive_errors:
                            sleep_time = min(5, consecutive_errors // 2)
                            time.sleep(sleep_time)

            except Exception as e:
                print(f"日志处理线程异常: {e}")
                time.sleep(1)  # 短暂休眠恢复

        # 退出前发送剩余日志
        if batch:
            try:
                for entry in batch:
                    KafkaLogger._producer.send(KafkaLogger._topic, entry)
                KafkaLogger._producer.flush(
                    timeout=KafkaLogger._shutdown_timeout)
            except Exception as e:
                print(f"关闭时发送剩余日志失败: {e}")

    @staticmethod
    def close():
        """安全关闭资源，增强可靠性"""
        if KafkaLogger._stop_event.is_set():
            return

        print("开始关闭Kafka日志系统...")
        KafkaLogger._stop_event.set()

        # 等待发送线程结束
        if KafkaLogger._sender_thread and KafkaLogger._sender_thread.is_alive():
            print(f"等待日志发送线程结束，超时时间: {KafkaLogger._shutdown_timeout}秒")
            KafkaLogger._sender_thread.join(
                timeout=KafkaLogger._shutdown_timeout)

            # 如果线程仍在运行，强制终止（虽然daemon线程会自动终止，但这里显式处理）
            if KafkaLogger._sender_thread.is_alive():
                print("日志发送线程未能及时结束，将被强制终止")

        # 关闭生产者
        if KafkaLogger._producer:
            try:
                print("关闭Kafka生产者...")
                KafkaLogger._producer.close(
                    timeout=KafkaLogger._shutdown_timeout)
                print("Kafka生产者已关闭")
            except Exception as e:
                print(f"关闭Kafka生产者失败: {e}")

        # 清空队列防止内存滞留
        remaining = 0
        while not KafkaLogger._log_queue.empty():
            try:
                KafkaLogger._log_queue.get_nowait()
                remaining += 1
            except Empty:
                break

        print(f"已清空日志队列，剩余日志数: {remaining}")


class SYLogger:
    @staticmethod
    def get_trace_id():
        """从上下文中获取当前的 trace_id"""
        return current_trace_id.get()

    @staticmethod
    def set_trace_id(trace_id: str):
        """设置当前的 trace_id"""
        return current_trace_id.set(trace_id)

    @staticmethod
    def reset_trace_id(token):
        """重置当前的 trace_id"""
        current_trace_id.reset(token)

    @staticmethod
    def _get_execution_context() -> str:
        """获取当前执行上下文的线程或协程信息，返回格式化字符串"""
        try:
            # 尝试获取协程信息
            task = asyncio.current_task()
            if task:
                task_name = task.get_name()
                return f"coroutine:{task_name}"
        except RuntimeError:
            # 不在异步上下文中，获取线程信息
            thread = threading.current_thread()
            return f"thread:{thread.name}"

        return "unknown"

    @staticmethod
    def _log(msg: any, level: str = "INFO"):
        trace_id = SYLogger.get_trace_id()

        if isinstance(msg, dict) or isinstance(msg, list):
            msg_str = json.dumps(msg, ensure_ascii=False)
        else:
            msg_str = str(msg)

        # 获取执行上下文信息并格式化为字符串
        thread_info = SYLogger._get_execution_context()

        # 构建日志结构，添加线程/协程信息到threadName字段
        request_log = {
            "trace_id": str(trace_id) if trace_id else Snowflake.next_id(),
            "message": msg_str,
            "level": level,
            "threadName": thread_info
        }

        # 选择日志级别
        _log = ''
        if level == "ERROR":
            _log = json.dumps(request_log, ensure_ascii=False)
            logger.error(_log)
        elif level == "WARNING":
            _log = json.dumps(request_log, ensure_ascii=False)
            logger.warning(_log)
        else:
            _log = json.dumps(request_log, ensure_ascii=False)
            logger.info(_log)

        if os.getenv('DEV-LOG', 'false').lower() == 'true':
            print(_log)

    @staticmethod
    def info(msg: any):
        SYLogger._log(msg, "INFO")

    @staticmethod
    def warning(msg: any):
        SYLogger._log(msg, "WARNING")

    @staticmethod
    def error(msg: any):
        SYLogger._log(msg, "ERROR")

    @staticmethod
    def exception(msg: any):
        """记录异常信息，包括完整堆栈"""
        trace_id = SYLogger.get_trace_id()

        if isinstance(msg, dict) or isinstance(msg, list):
            msg_str = json.dumps(msg, ensure_ascii=False)
        else:
            msg_str = str(msg)

        # 获取执行上下文信息
        thread_info = SYLogger._get_execution_context()

        # 构建包含异常堆栈的日志
        request_log = {
            "trace_id": str(trace_id) if trace_id else Snowflake.next_id(),
            "message": msg_str,
            "level": "ERROR",
            "threadName": thread_info
        }

        # 使用Loguru记录完整异常堆栈
        logger.opt(exception=True).error(
            json.dumps(request_log, ensure_ascii=False))
