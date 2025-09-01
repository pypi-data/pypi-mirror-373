from typing import Any, Callable, Coroutine, Dict, List, Tuple, Union, Optional, Type
import asyncio
import logging
from pydantic import BaseModel
from aio_pika.abc import AbstractIncomingMessage

from sycommon.logging.kafka_log import SYLogger
from sycommon.models.mqmsg_model import MQMsgModel
from sycommon.models.mqlistener_config import RabbitMQListenerConfig
from sycommon.models.mqsend_config import RabbitMQSendConfig
from sycommon.models.sso_user import SsoUser
from sycommon.rabbitmq.rabbitmq_client import RabbitMQClient


class RabbitMQService:
    # 保存多个客户端实例
    clients: Dict[str, RabbitMQClient] = {}
    # 保存多个消费者任务
    consumer_tasks: Dict[str, asyncio.Task] = {}
    # 保存消息处理器
    message_handlers: Dict[str, Callable] = {}
    # 保存配置信息
    config: Optional[dict] = None
    # 存储发送客户端的名称（即队列名）
    sender_client_names: List[str] = []
    # 用于控制消费者任务退出的事件
    _consumer_events: Dict[str, asyncio.Event] = {}
    # 存储消费者标签，用于取消消费
    _consumer_tags: Dict[str, str] = {}
    # 跟踪已完成的初始化操作（全局状态）
    _initialized_queues: Dict[str, Dict[str, bool]] = {}
    # 添加异步锁
    _init_lock: Dict[str, asyncio.Lock] = {}

    @classmethod
    def init(cls, config: dict) -> Type['RabbitMQService']:
        """初始化RabbitMQ服务，保存配置"""
        from sycommon.synacos.nacos_service import NacosService
        # 获取 common 配置
        cls.config = NacosService(config).share_configs.get(
            "mq.yml", {}).get('spring', {}).get('rabbitmq', {})
        cls.config["APP_NAME"] = config.get("Name", "")
        return cls()

    @classmethod
    async def check_queue_exists(cls, channel, queue_name: str) -> bool:
        """检查队列是否存在"""
        try:
            await channel.declare_queue(
                name=queue_name,
                passive=True  # 被动模式：仅检查队列是否存在
            )
            return True
        except Exception as e:
            return False

    @classmethod
    def create_client(cls, mq_config: dict, queue_name: str, **kwargs):
        """创建并返回新的RabbitMQClient实例"""
        # 从kwargs中提取是否自动创建队列的参数，默认True
        create_if_not_exists = kwargs.get('create_if_not_exists', True)

        # 确保只在需要时处理一次队列名称
        processed_queue_name = queue_name

        # 如果是监听器且需要自动创建队列，确保队列名拼接app-name（只拼接一次）
        if create_if_not_exists and processed_queue_name and 'app_name' in kwargs and kwargs['app_name']:
            app_name = kwargs['app_name']
            # 只在队列名尚未包含app-name时进行拼接
            if not processed_queue_name.endswith(f".{app_name}"):
                processed_queue_name = f"{processed_queue_name}.{app_name}"
                logging.debug(f"监听器队列名称自动拼接app-name: {processed_queue_name}")

        return RabbitMQClient(
            host=mq_config.get('host', ""),
            port=mq_config.get('port', 0),
            username=mq_config.get('username', ""),
            password=mq_config.get('password', ""),
            virtualhost=mq_config.get('virtual-host', "/"),
            exchange_name=mq_config.get(
                'exchange_name', "system.topic.exchange"),
            exchange_type=kwargs.get('exchange_type', "topic"),
            queue_name=processed_queue_name,  # 使用处理后的队列名
            routing_key=kwargs.get(
                'routing_key', f"{processed_queue_name.split('.')[0]}.#" if processed_queue_name else "#"),
            durable=kwargs.get('durable', True),
            auto_delete=kwargs.get('auto_delete', False),
            auto_parse_json=kwargs.get('auto_parse_json', True),
            create_if_not_exists=create_if_not_exists,
            connection_timeout=kwargs.get('connection_timeout', 10),
            rpc_timeout=kwargs.get('rpc_timeout', 5),
            app_name=kwargs.get('app_name', "")
        )

    @classmethod
    async def setup_rabbitmq(
        cls,
        mq_config: dict,
        client_name: str = "default", ** kwargs
    ) -> RabbitMQClient:
        """初始化RabbitMQ客户端并注册到服务中"""
        if client_name not in cls._init_lock:
            cls._init_lock[client_name] = asyncio.Lock()

        async with cls._init_lock[client_name]:
            if client_name in cls.clients:
                client = cls.clients[client_name]
                if client.is_connected:
                    logging.debug(f"客户端 '{client_name}' 已存在且连接有效，直接返回")
                    return client
                else:
                    logging.debug(f"客户端 '{client_name}' 存在但连接已关闭，重新连接")
                    await client.connect()
                    return client

            initial_queue_name = kwargs.pop('queue_name', '')
            create_if_not_exists = kwargs.get('create_if_not_exists', True)

            # 检查队列是否已初始化
            if initial_queue_name in cls._initialized_queues:
                logging.debug(f"队列 '{initial_queue_name}' 已初始化过，直接创建客户端")
                client = RabbitMQService.create_client(
                    mq_config,
                    initial_queue_name,
                    app_name=cls.config.get("APP_NAME", ""),
                    **kwargs
                )
                await client.connect()
                cls.clients[client_name] = client
                return client

            # 处理create_if_not_exists参数，避免重复传递
            create_if_not_exists = kwargs.pop('create_if_not_exists', True)

            # 对于监听器，确保create_if_not_exists为True
            # 判断是否为监听器：客户端名称与队列名称相同通常是监听器
            is_listener = client_name == initial_queue_name and initial_queue_name
            if is_listener:
                create_if_not_exists = True
                logging.debug(f"监听器 '{client_name}' 将自动创建队列（如果不存在）")

            # 创建客户端（这里会处理队列名称，添加app-name）
            client = RabbitMQService.create_client(
                mq_config,
                initial_queue_name,
                app_name=cls.config.get("APP_NAME", ""),
                create_if_not_exists=create_if_not_exists,
                connection_timeout=mq_config.get('connection_timeout', 15),
                rpc_timeout=mq_config.get('rpc_timeout', 5), ** kwargs
            )

            # 连接时不再处理队列名称，避免重复添加app-name
            await client.connect()
            final_queue_name = client.queue_name

            if final_queue_name not in cls._initialized_queues:
                cls._initialized_queues[final_queue_name] = {
                    "declared": True,
                    "bound": True
                }

            cls.clients[client_name] = client
            return client

    @classmethod
    async def setup_senders(cls, senders: List[RabbitMQSendConfig]):
        """设置MQ发送客户端 - 保持不自动创建队列的行为"""
        async def setup_sender_tasks():
            for idx, sender_config in enumerate(senders):
                try:
                    if not sender_config.queue_name:
                        raise ValueError(f"发送器配置第{idx+1}项缺少queue_name")

                    normalized_name = sender_config.queue_name
                    app_name = cls.config.get("APP_NAME", "")
                    if app_name and normalized_name.endswith(f".{app_name}"):
                        normalized_name = normalized_name[:-
                                                          len(f".{app_name}")]

                    if normalized_name in cls.sender_client_names:
                        logging.debug(f"发送客户端 '{normalized_name}' 已存在，跳过重复配置")
                        continue

                    if normalized_name in cls.clients:
                        client = cls.clients[normalized_name]
                        if not client.is_connected:
                            await client.connect()
                    else:
                        # 发送端明确设置不自动创建队列
                        client = await cls.setup_rabbitmq(
                            cls.config,
                            client_name=normalized_name,
                            exchange_type=sender_config.exchange_type,
                            durable=sender_config.durable,
                            auto_delete=sender_config.auto_delete,
                            auto_parse_json=sender_config.auto_parse_json,
                            queue_name=sender_config.queue_name,
                            create_if_not_exists=False  # 发送端不自动创建队列
                        )

                    if normalized_name not in cls.clients:
                        cls.clients[normalized_name] = client
                        logging.info(f"客户端 '{normalized_name}' 已添加到客户端列表")

                    if normalized_name not in cls.sender_client_names:
                        cls.sender_client_names.append(normalized_name)
                        logging.info(f"发送客户端 '{normalized_name}' 初始化成功")

                except Exception as e:
                    logging.error(
                        f"初始化发送客户端第{idx+1}项失败: {str(e)}", exc_info=True)

        try:
            await setup_sender_tasks()
        except Exception as e:
            logging.error(f"设置发送器时发生错误: {str(e)}", exc_info=True)
            raise

    @classmethod
    async def setup_listeners(cls, listeners: List[RabbitMQListenerConfig]):
        """设置MQ监听器 - 确保自动创建队列"""
        for listener_config in listeners:
            # 将监听器配置转换为字典并添加到监听器
            # 强制设置create_if_not_exists为True
            listener_dict = listener_config.model_dump()
            listener_dict['create_if_not_exists'] = True
            await cls.add_listener(**listener_dict)
        # 启动所有消费者
        await cls.start_all_consumers()

    @classmethod
    async def add_listener(
        cls,
        queue_name: str,
        handler: Callable[[MQMsgModel, AbstractIncomingMessage], Coroutine], ** kwargs
    ) -> None:
        """添加RabbitMQ监听器 - 确保自动创建队列并拼接app-name"""
        if not cls.config:
            raise ValueError("RabbitMQService尚未初始化，请先调用init方法")

        if queue_name in cls.message_handlers:
            logging.debug(f"监听器 '{queue_name}' 已存在，跳过重复添加")
            return

        # 为监听器强制设置create_if_not_exists=True
        kwargs['create_if_not_exists'] = True

        # 创建并初始化客户端（会处理队列名称）
        await cls.setup_rabbitmq(
            cls.config,
            client_name=queue_name,
            queue_name=queue_name,
            **kwargs
        )

        # 注册消息处理器
        cls.register_handler(queue_name, handler)

    @classmethod
    def register_handler(
        cls,
        client_name: str,
        handler: Callable[[MQMsgModel, AbstractIncomingMessage], Coroutine]
    ) -> None:
        """为特定客户端注册消息处理器"""
        cls.message_handlers[client_name] = handler

    @classmethod
    async def start_all_consumers(cls) -> None:
        """启动所有已注册客户端的消费者"""
        for client_name in cls.clients:
            await cls.start_consumer(client_name)

    @classmethod
    async def start_consumer(cls, client_name: str = "default") -> None:
        """启动指定客户端的消费者"""
        if client_name in cls.consumer_tasks and not cls.consumer_tasks[client_name].done():
            logging.debug(f"消费者 '{client_name}' 已在运行中，无需重复启动")
            return

        if client_name not in cls.clients:
            raise ValueError(f"RabbitMQ客户端 '{client_name}' 未初始化")

        client = cls.clients[client_name]
        handler = cls.message_handlers.get(client_name)

        if not handler:
            logging.warning(f"未找到客户端 '{client_name}' 的处理器，使用默认处理器")
            handler = cls.default_message_handler

        client.set_message_handler(handler)

        stop_event = asyncio.Event()
        cls._consumer_events[client_name] = stop_event

        async def consume_task():
            try:
                consumer_tag = await client.start_consuming()
                cls._consumer_tags[client_name] = consumer_tag
                logging.info(f"消费者 '{client_name}' 开始消费，tag: {consumer_tag}")

                while not stop_event.is_set():
                    await asyncio.sleep(0.1)

                logging.info(f"消费者 '{client_name}' 退出循环")

            except asyncio.CancelledError:
                logging.info(f"消费者 '{client_name}' 被取消")
            except Exception as e:
                logging.error(
                    f"消费者 '{client_name}' 错误: {str(e)}", exc_info=True)
            finally:
                await client.stop_consuming()
                logging.info(f"消费者 '{client_name}' 已完成清理")

        task = asyncio.create_task(
            consume_task(), name=f"consumer-{client_name}")
        cls.consumer_tasks[client_name] = task

        def task_exception_handler(t: asyncio.Task):
            try:
                if t.done():
                    t.result()
            except Exception as e:
                logging.error(f"消费者任务 '{client_name}' 异常: {str(e)}")

        task.add_done_callback(task_exception_handler)

    @classmethod
    async def default_message_handler(cls, parsed_data: MQMsgModel, original_message):
        """默认消息处理器"""
        logging.info(f"\n===== 收到消息 [{original_message.routing_key}] =====")
        logging.info(f"关联ID: {parsed_data.correlationDataId}")
        logging.info(f"主题代码: {parsed_data.topicCode}")
        logging.info(f"消息内容: {parsed_data.msg}")
        logging.info("===================\n")

    @classmethod
    def get_sender(cls, client_name: Optional[str] = None) -> Optional[RabbitMQClient]:
        """获取发送客户端（仅返回已注册的客户端，移除模糊匹配）"""
        if not client_name:
            logging.warning("发送器名称不能为空")
            return None

        # 仅精确匹配已注册的客户端，不做模糊匹配
        if client_name in cls.clients:
            return cls.clients[client_name]

        # 不允许通过拼接app-name反向查找（避免绕过注册）
        app_name = cls.config.get("APP_NAME", "") if cls.config else ""
        if app_name and not client_name.endswith(f".{app_name}"):
            # 不尝试拼接app-name查找，确保只有注册的名称可被找到
            return None

        logging.debug(f"发送器 '{client_name}' 不在已注册客户端列表中")
        return None

    @classmethod
    async def send_message(
        cls,
        data: Union[BaseModel, str, Dict[str, Any], None],
        queue_name: Optional[str] = None, ** kwargs
    ) -> None:
        """发送消息到RabbitMQ"""
        sender = cls.get_sender(queue_name)

        if not sender:
            error_msg = f"未找到可用的RabbitMQ发送器 (queue_name: {queue_name})"
            logging.error(error_msg)
            raise ValueError(error_msg)

        if not sender.connection or sender.connection.is_closed:
            logging.info(f"发送器 '{queue_name}' 连接已关闭，尝试重新连接")
            try:
                await sender.connect(force_reconnect=True)
            except Exception as e:
                logging.error(f"发送器 '{queue_name}' 重新连接失败: {str(e)}")
                raise

        try:
            msg = ''
            if isinstance(data, str):
                msg = data
            elif isinstance(data, BaseModel):
                msg = data.model_dump_json()
            elif isinstance(data, dict):
                import json
                msg = json.dumps(data)

            mq_message = MQMsgModel(
                topicCode=queue_name.split('.')[0] if queue_name else "",
                msg=msg,
                correlationDataId=kwargs.get(
                    'correlationDataId', SYLogger.get_trace_id()),
                groupId=kwargs.get('groupId', ''),
                dataKey=kwargs.get('dataKey', ""),
                manualFlag=kwargs.get('manualFlag', False),
                traceId=SYLogger.get_trace_id()
            )

            # 不设置Java会解析失败导致丢掉消息
            mq_header = {
                "context": SsoUser(
                    tenant_id="T000002",
                    customer_id="SYSTEM",
                    user_id="SYSTEM",
                    user_name="SYSTEM",
                    request_path="",
                    req_type="SYSTEM",
                    trace_id=SYLogger.get_trace_id(),
                ).model_dump_json()
            }

            await sender.send_message(
                message_body=mq_message.model_dump_json(),
                headers=mq_header,
            )
            logging.info(
                f"消息发送成功 (客户端: {queue_name or cls.sender_client_names[0]})")
        except Exception as e:
            logging.error(f"消息发送失败: {str(e)}", exc_info=True)
            raise

    @classmethod
    async def shutdown(cls, timeout: float = 5.0) -> None:
        """优雅关闭所有客户端和消费者任务"""
        start_time = asyncio.get_event_loop().time()

        for client_name, event in cls._consumer_events.items():
            event.set()
            logging.info(f"已向消费者 '{client_name}' 发送退出信号")

        remaining_time = max(
            0.0, timeout - (asyncio.get_event_loop().time() - start_time))
        if remaining_time > 0:
            tasks_to_wait = [
                t for t in cls.consumer_tasks.values() if not t.done()]
            if tasks_to_wait:
                try:
                    done, pending = await asyncio.wait(
                        tasks_to_wait,
                        timeout=remaining_time,
                        return_when=asyncio.ALL_COMPLETED
                    )

                    for task in pending:
                        task_name = task.get_name()
                        logging.warning(f"任务 '{task_name}' 关闭超时，强制取消")
                        task.cancel()
                        try:
                            await task
                        except (asyncio.CancelledError, RuntimeError):
                            pass

                except Exception as e:
                    logging.error(f"等待消费者任务完成时出错: {str(e)}")

        remaining_time = max(
            0.0, timeout - (asyncio.get_event_loop().time() - start_time))
        if remaining_time > 0:
            for name, client in cls.clients.items():
                try:
                    await asyncio.wait_for(client.stop_consuming(), timeout=remaining_time/len(cls.clients))
                    await asyncio.wait_for(client.close(), timeout=remaining_time/len(cls.clients))
                except Exception as e:
                    logging.warning(f"关闭客户端 '{name}' 时出错: {str(e)}")
                logging.info(f"RabbitMQ客户端 '{name}' 已关闭")

        cls.consumer_tasks.clear()
        cls._consumer_events.clear()
        cls._consumer_tags.clear()
        cls.clients.clear()
        cls.sender_client_names.clear()
        cls._init_lock.clear()

        logging.info("RabbitMQ服务已完全关闭")
