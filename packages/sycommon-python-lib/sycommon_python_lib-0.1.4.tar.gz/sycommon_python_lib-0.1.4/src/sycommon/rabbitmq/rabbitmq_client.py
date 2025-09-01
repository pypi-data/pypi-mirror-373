import asyncio
import logging
import aio_pika
import json
from aio_pika.abc import AbstractIncomingMessage, ExchangeType
from typing import Callable, Coroutine, Optional, Dict, Any, Union

from sycommon.models.mqmsg_model import MQMsgModel
from aiormq.exceptions import ChannelInvalidStateError, ConnectionClosed

# 最大重试次数限制
MAX_RETRY_COUNT = 3


class RabbitMQClient:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        virtualhost: str = "/",
        exchange_name: str = "system.topic.exchange",
        exchange_type: str = "topic",
        queue_name: Optional[str] = None,
        routing_key: str = "#",
        durable: bool = True,
        auto_delete: bool = False,
        auto_parse_json: bool = True,
        create_if_not_exists: bool = True,
        connection_timeout: int = 10,
        rpc_timeout: int = 10,
        app_name: str = "",
        reconnection_delay: int = 3,
        max_reconnection_attempts: int = 5,
        heartbeat: int = 30,
        keepalive_interval: int = 15
    ):
        """初始化RabbitMQ客户端，增加心跳和保活配置"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtualhost = virtualhost
        self.exchange_name = exchange_name
        self.exchange_type = ExchangeType(exchange_type)
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.durable = durable
        self.auto_delete = auto_delete
        self.auto_parse_json = auto_parse_json
        self.create_if_not_exists = create_if_not_exists
        self.connection_timeout = connection_timeout
        self.rpc_timeout = rpc_timeout
        self.app_name = app_name

        # 连接保活相关配置
        self.heartbeat = heartbeat
        self.keepalive_interval = keepalive_interval
        self.last_activity_timestamp = asyncio.get_event_loop().time()

        # 重连相关配置
        self.reconnection_delay = reconnection_delay
        self.max_reconnection_attempts = max_reconnection_attempts

        # 连接和通道相关属性
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.RobustChannel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.queue: Optional[aio_pika.Queue] = None

        self._exchange_exists = False
        self._queue_exists = False
        self._queue_bound = False

        # 消息处理器
        self.message_handler: Optional[Callable[
            [Union[AbstractIncomingMessage, Dict[str, Any]], AbstractIncomingMessage],
            Coroutine
        ]] = None

        # 消费相关
        self._consumer_tag: Optional[str] = None
        self._consuming_task: Optional[asyncio.Task] = None
        self._is_consuming: bool = False
        self._reconnect_task: Optional[asyncio.Task] = None
        self._closed: bool = False
        self._keepalive_task: Optional[asyncio.Task] = None  # 保活任务

    @property
    def is_connected(self) -> bool:
        """检查连接是否有效"""
        return (not self._closed and
                self.connection is not None and
                not self.connection.is_closed and
                self.channel is not None and
                not self.channel.is_closed)

    def _update_activity_timestamp(self):
        """更新最后活动时间戳"""
        self.last_activity_timestamp = asyncio.get_event_loop().time()

    async def _check_exchange_exists(self) -> bool:
        """检查交换机是否存在，增加超时控制"""
        if not self.channel:
            return False

        try:
            await asyncio.wait_for(
                self.channel.declare_exchange(
                    name=self.exchange_name,
                    type=self.exchange_type,
                    passive=True
                ),
                timeout=self.rpc_timeout
            )
            self._exchange_exists = True
            self._update_activity_timestamp()
            return True
        except asyncio.TimeoutError:
            logging.error(f"检查交换机 '{self.exchange_name}' 超时")
            return False
        except Exception as e:
            logging.debug(f"交换机 '{self.exchange_name}' 不存在: {str(e)}")
            return False

    async def _check_queue_exists(self) -> bool:
        """检查队列是否存在，增加超时控制"""
        if not self.channel or not self.queue_name:
            return False

        try:
            await asyncio.wait_for(
                self.channel.declare_queue(
                    name=self.queue_name,
                    passive=True
                ),
                timeout=self.rpc_timeout
            )
            self._queue_exists = True
            self._update_activity_timestamp()
            return True
        except asyncio.TimeoutError:
            logging.error(f"检查队列 '{self.queue_name}' 超时")
            return False
        except Exception as e:
            logging.debug(f"队列 '{self.queue_name}' 不存在: {str(e)}")
            return False

    async def _bind_queue(self) -> bool:
        """绑定队列到交换机，增加超时控制和重试"""
        if not self.channel or not self.queue or not self.exchange:
            return False

        retries = 2  # 绑定操作重试次数
        for attempt in range(retries + 1):
            try:
                bind_routing_key = self.routing_key if self.routing_key else '#'
                await asyncio.wait_for(
                    self.queue.bind(
                        self.exchange,
                        routing_key=bind_routing_key
                    ),
                    timeout=self.rpc_timeout
                )
                self._queue_bound = True
                self._update_activity_timestamp()
                logging.info(
                    f"队列 '{self.queue_name}' 已绑定到交换机 '{self.exchange_name}'，路由键: {bind_routing_key}")
                return True
            except asyncio.TimeoutError:
                logging.warning(
                    f"队列 '{self.queue_name}' 绑定超时（第{attempt+1}次尝试）")
                if attempt >= retries:
                    self._queue_bound = False
                    return False
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"队列绑定失败（第{attempt+1}次尝试）: {str(e)}")
                if attempt >= retries:
                    self._queue_bound = False
                    return False
                await asyncio.sleep(1)
        return False

    async def connect(self, force_reconnect: bool = False, max_retries: int = 3) -> None:
        """建立连接并检查/创建资源"""
        if self.is_connected and not force_reconnect:
            return

        # 如果正在重连，先取消
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()

        logging.debug(
            f"尝试连接RabbitMQ - 主机: {self.host}:{self.port}, "
            f"虚拟主机: {self.virtualhost}, "
            f"队列: {self.queue_name}, "
            f"心跳间隔: {self.heartbeat}s"
        )

        # 重置状态
        self._exchange_exists = False
        self._queue_exists = False
        self._queue_bound = False

        retries = 0
        last_exception = None

        while retries < max_retries:
            try:
                # 关闭旧连接
                if self.connection and not self.connection.is_closed:
                    await self.connection.close()

                # 建立新连接 - 配置更短的心跳间隔
                self.connection = await asyncio.wait_for(
                    aio_pika.connect_robust(
                        host=self.host,
                        port=self.port,
                        login=self.username,
                        password=self.password,
                        virtualhost=self.virtualhost,
                        heartbeat=self.heartbeat,
                        client_properties={
                            "connection_name": self.app_name or "rabbitmq-client"}  # 增加连接标识
                    ),
                    timeout=self.connection_timeout
                )

                # 创建通道
                self.channel = await asyncio.wait_for(
                    self.connection.channel(),
                    timeout=self.rpc_timeout
                )
                await self.channel.set_qos(prefetch_count=2)

                # 1. 处理交换机
                exchange_exists = await self._check_exchange_exists()
                if not exchange_exists:
                    if self.create_if_not_exists:
                        # 创建交换机
                        self.exchange = await asyncio.wait_for(
                            self.channel.declare_exchange(
                                name=self.exchange_name,
                                type=self.exchange_type,
                                durable=self.durable,
                                auto_delete=self.auto_delete
                            ),
                            timeout=self.rpc_timeout
                        )
                        self._exchange_exists = True
                        logging.info(f"已创建交换机 '{self.exchange_name}'")
                    else:
                        raise Exception(
                            f"交换机 '{self.exchange_name}' 不存在且不允许自动创建")
                else:
                    # 获取已有交换机
                    self.exchange = await asyncio.wait_for(
                        self.channel.get_exchange(self.exchange_name),
                        timeout=self.rpc_timeout
                    )
                    logging.info(f"使用已存在的交换机 '{self.exchange_name}'")

                # 2. 处理队列
                if self.queue_name:
                    queue_exists = await self._check_queue_exists()

                    if not queue_exists:
                        if self.create_if_not_exists:
                            # 创建队列
                            self.queue = await asyncio.wait_for(
                                self.channel.declare_queue(
                                    name=self.queue_name,
                                    durable=self.durable,
                                    auto_delete=self.auto_delete,
                                    exclusive=False,
                                    passive=False
                                ),
                                timeout=self.rpc_timeout
                            )
                            self._queue_exists = True
                            logging.info(f"已创建队列 '{self.queue_name}'")
                        else:
                            raise Exception(
                                f"队列 '{self.queue_name}' 不存在且不允许自动创建")
                    else:
                        # 获取已有队列
                        self.queue = await asyncio.wait_for(
                            self.channel.get_queue(self.queue_name),
                            timeout=self.rpc_timeout
                        )
                        logging.info(f"使用已存在的队列 '{self.queue_name}'")

                # 3. 绑定队列到交换机
                if self.queue and self.exchange:
                    bound = await self._bind_queue()
                    if not bound:
                        raise Exception(
                            f"队列 '{self.queue_name}' 绑定到交换机 '{self.exchange_name}' 失败")

                # 如果之前在消费，重新开始消费
                if self._is_consuming and self.message_handler:
                    await self.start_consuming()

                # 启动连接监控和保活任务
                self._start_connection_monitor()
                self._start_keepalive_task()

                self._update_activity_timestamp()
                logging.info(f"RabbitMQ客户端连接成功 (队列: {self.queue_name})")
                return

            except Exception as e:
                retries += 1
                last_exception = e
                logging.warning(
                    f"连接失败（{retries}/{max_retries}）: {str(e)}，重试中...")

            if retries < max_retries:
                await asyncio.sleep(self.reconnection_delay)

        logging.error(f"最终连接失败: {str(last_exception)}", exc_info=True)
        raise Exception(
            f"经过{max_retries}次重试后仍无法完成连接和资源初始化。"
            f"最后错误: {str(last_exception)}"
        )

    def _start_connection_monitor(self):
        """启动连接监控任务，检测连接/通道关闭"""
        if self._closed:
            return

        async def monitor_task():
            while not self._closed and self.connection:
                try:
                    # 检查连接状态
                    if self.connection.is_closed:
                        logging.warning("检测到RabbitMQ连接已关闭")
                        await self._schedule_reconnect()
                        return

                    # 检查通道状态
                    if self.channel and self.channel.is_closed:
                        logging.warning("检测到RabbitMQ通道已关闭")
                        await self._recreate_channel()
                        continue
                except Exception as e:
                    logging.error(f"连接监控任务出错: {str(e)}")
                    await asyncio.sleep(1)

                await asyncio.sleep(5)

        # 创建监控任务
        asyncio.create_task(monitor_task())

    async def _recreate_channel(self):
        """重建通道并恢复绑定和消费"""
        try:
            if not self.connection or self.connection.is_closed:
                return

            # 重新创建通道
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=2)

            # 重新绑定队列和交换机
            if self.queue and self.exchange:
                await self._bind_queue()

            # 重新开始消费
            if self._is_consuming and self.message_handler:
                await self.start_consuming()

            logging.info("通道已重新创建并恢复服务")
            self._update_activity_timestamp()
        except Exception as e:
            logging.error(f"重建通道失败: {str(e)}")
            await self._schedule_reconnect()

    def _start_keepalive_task(self):
        """启动连接保活任务，适配RobustConnection的特性"""
        if self._closed or (self._keepalive_task and not self._keepalive_task.done()):
            return

        async def keepalive_task():
            while not self._closed and self.is_connected:
                current_time = asyncio.get_event_loop().time()
                # 检查是否超过指定时间无活动
                if current_time - self.last_activity_timestamp > self.heartbeat * 1.5:
                    logging.debug(f"连接 {self.heartbeat*1.5}s 无活动，执行保活检查")
                    try:
                        # 针对RobustConnection的兼容处理
                        if self.connection:
                            # 检查连接状态
                            if self.connection.is_closed:
                                logging.warning("连接已关闭，触发重连")
                                await self._schedule_reconnect()
                                return

                            # 尝试一个轻量级操作来保持连接活跃
                            if self.channel:
                                # 使用通道声明一个空的交换机（被动模式）作为保活检测
                                await asyncio.wait_for(
                                    self.channel.declare_exchange(
                                        name=self.exchange_name,
                                        type=self.exchange_type,
                                        passive=True  # 被动模式不会创建交换机，仅检查存在性
                                    ),
                                    timeout=5
                                )

                            self._update_activity_timestamp()
                    except asyncio.TimeoutError:
                        logging.warning("保活检查超时，触发重连")
                        await self._schedule_reconnect()
                    except Exception as e:
                        logging.warning(f"保活检查失败: {str(e)}，触发重连")
                        await self._schedule_reconnect()

                await asyncio.sleep(self.keepalive_interval)

        self._keepalive_task = asyncio.create_task(keepalive_task())

    async def _schedule_reconnect(self):
        """安排重新连接"""
        if self._reconnect_task and not self._reconnect_task.done():
            return

        logging.info(f"将在 {self.reconnection_delay} 秒后尝试重新连接...")

        async def reconnect_task():
            try:
                await asyncio.sleep(self.reconnection_delay)
                if not self._closed:
                    await self.connect(force_reconnect=True, max_retries=self.max_reconnection_attempts)
            except Exception as e:
                logging.error(f"重连任务失败: {str(e)}")
                # 如果重连失败，再次安排重连
                if not self._closed:
                    await self._schedule_reconnect()

        self._reconnect_task = asyncio.create_task(reconnect_task())

    async def close(self) -> None:
        """关闭连接，清理所有任务"""
        self._closed = True
        self._is_consuming = False

        # 取消保活任务
        if self._keepalive_task and not self._keepalive_task.done():
            self._keepalive_task.cancel()

        # 取消重连任务
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()

        # 停止消费
        if self._consuming_task and not self._consuming_task.done():
            self._consuming_task.cancel()

        # 关闭连接
        if self.connection and not self.connection.is_closed:
            try:
                await asyncio.wait_for(self.connection.close(), timeout=5)
            except Exception as e:
                logging.warning(f"关闭连接时出错: {str(e)}")

        # 重置状态
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
        self._exchange_exists = False
        self._queue_exists = False
        self._queue_bound = False
        self._consumer_tag = None
        self._consuming_task = None
        self._keepalive_task = None

    async def send_message(
        self,
        message_body: Union[str, Dict[str, Any]],
        content_type: str = "application/json",
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        """发送消息到RabbitMQ，带连接检查和重试机制"""
        if not self.is_connected:
            logging.warning("连接已关闭，尝试重新连接后发送消息")
            await self.connect(force_reconnect=True)

        if not self.channel or not self.exchange:
            raise Exception("RabbitMQ连接未初始化")

        try:
            if isinstance(message_body, dict):
                message_body_str = json.dumps(message_body, ensure_ascii=False)
                if content_type == "text/plain":
                    content_type = "application/json"
            else:
                message_body_str = str(message_body)

            message = aio_pika.Message(
                headers=headers,
                body=message_body_str.encode(),
                content_type=content_type,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT if self.durable else aio_pika.DeliveryMode.TRANSIENT
            )

            await self.exchange.publish(
                message,
                routing_key=self.routing_key or '#'
            )
            self._update_activity_timestamp()  # 更新活动时间
        except (ChannelInvalidStateError, ConnectionClosed) as e:
            logging.warning(f"通道/连接已关闭，消息发送失败: {str(e)}")
            await self._recreate_channel()
            raise
        except Exception as e:
            logging.warning(f"消息发送失败，尝试重连后再次发送: {str(e)}")
            # 尝试重连
            await self.connect(force_reconnect=True)
            # 重连后再次尝试发送
            raise  # 让上层处理重发逻辑

    def set_message_handler(
        self,
        handler: Callable[
            [Union[AbstractIncomingMessage, Dict[str, Any]], AbstractIncomingMessage],
            Coroutine
        ]
    ) -> None:
        """设置消息处理函数"""
        self.message_handler = handler

    async def start_consuming(self, timeout: Optional[float] = None) -> str:
        """开始消费消息并返回consumer_tag，支持超时控制"""
        if self._is_consuming:
            logging.debug("已经在消费中，返回现有consumer_tag")
            return self._consumer_tag

        if not self.is_connected:
            await self.connect()

        if not self.queue:
            raise Exception("队列未初始化")

        if not self.message_handler:
            raise Exception("未设置消息处理函数")

        self._is_consuming = True

        async def consume_task():
            try:
                while self._is_consuming and self.is_connected:
                    try:
                        # 消费消息
                        self._consumer_tag = await self.queue.consume(self._message_wrapper)
                        logging.info(f"消费者已启动，tag: {self._consumer_tag}")

                        # 保持消费循环
                        while self._is_consuming and self.is_connected:
                            await asyncio.sleep(1)

                        # 如果退出循环，取消消费（增加重试逻辑）
                        if self._consumer_tag and self.queue and not self.queue.channel.is_closed:
                            await self._safe_cancel_consumer()

                    except (ChannelInvalidStateError, ConnectionClosed) as e:
                        if self._closed or not self._is_consuming:
                            break

                        logging.error(f"通道/连接异常: {str(e)}，尝试重建通道")
                        await self._recreate_channel()
                        await asyncio.sleep(1)
                    except Exception as e:
                        if self._closed or not self._is_consuming:
                            break

                        logging.error(f"消费过程中出错: {str(e)}", exc_info=True)
                        # 如果连接仍然有效，等待后重试
                        if self.is_connected:
                            await asyncio.sleep(self.reconnection_delay)
                        else:
                            # 连接无效，等待重连
                            while not self.is_connected and self._is_consuming and not self._closed:
                                await asyncio.sleep(1)
            except asyncio.CancelledError:
                logging.info("消费任务已取消")
            except Exception as e:
                logging.error(f"消费任务出错: {str(e)}", exc_info=True)
            finally:
                self._is_consuming = False
                self._consumer_tag = None
                logging.info("消费任务已结束")

        # 保存消费任务引用
        self._consuming_task = asyncio.create_task(consume_task())
        return self._consumer_tag

    async def _safe_cancel_consumer(self, max_retries: int = 3) -> bool:
        """安全取消消费者，增加重试机制"""
        if not self._consumer_tag or not self.queue:
            return True

        for attempt in range(max_retries):
            try:
                await asyncio.wait_for(
                    self.queue.cancel(self._consumer_tag),
                    timeout=self.rpc_timeout
                )
                logging.info(f"消费者 {self._consumer_tag} 已取消")
                return True
            except ChannelInvalidStateError:
                if attempt >= max_retries - 1:
                    logging.error(f"取消消费者 {self._consumer_tag} 失败：通道已关闭")
                    return False
                logging.warning(f"取消消费者尝试 {attempt+1} 失败，通道状态异常，重试中...")
                await asyncio.sleep(1)
            except asyncio.TimeoutError:
                if attempt >= max_retries - 1:
                    logging.error(f"取消消费者 {self._consumer_tag} 超时")
                    return False
                logging.warning(f"取消消费者尝试 {attempt+1} 超时，重试中...")
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"取消消费者异常: {str(e)}")
                return False
        return False

    async def stop_consuming(self, timeout: float = 5.0) -> None:
        """停止消费消息，延长超时时间并增加重试"""
        self._is_consuming = False

        if self.queue and self._consumer_tag:
            await self._safe_cancel_consumer()

        # 等待消费任务结束
        if self._consuming_task and not self._consuming_task.done():
            try:
                await asyncio.wait_for(self._consuming_task, timeout=timeout)
            except asyncio.TimeoutError:
                logging.warning(f"等待消费任务结束超时，强制取消")
                self._consuming_task.cancel()
            finally:
                self._consuming_task = None

    async def _parse_message(self, message: AbstractIncomingMessage) -> Union[Dict[str, Any], str]:
        """解析消息体，更新活动时间戳"""
        try:
            body_str = message.body.decode('utf-8')
            self._update_activity_timestamp()  # 收到消息时更新活动时间

            if self.auto_parse_json:
                return json.loads(body_str)
            return body_str
        except json.JSONDecodeError:
            logging.warning(f"消息解析JSON失败，返回原始字符串: {body_str}")
            return body_str
        except Exception as e:
            logging.error(f"消息解析出错: {str(e)}")
            return message.body.decode('utf-8')

    async def _message_wrapper(self, message: AbstractIncomingMessage) -> None:
        if not self.message_handler or not self._is_consuming:
            logging.warning("未设置消息处理器或已停止消费，确认消息")
            # await message.ack()
            return

        try:
            parsed_data = await self._parse_message(message)
            await self.message_handler(MQMsgModel(** parsed_data), message)
            await message.ack()
            self._update_activity_timestamp()
        except Exception as e:
            current_headers = message.headers or {}
            retry_count = current_headers.get('x-retry-count', 0)
            retry_count += 1

            logging.error(
                f"消息处理出错（第{retry_count}次重试）: {str(e)}",
                exc_info=True
            )

            # 判断是否超过最大重试次数
            if retry_count >= MAX_RETRY_COUNT:
                logging.error(
                    f"消息已达到最大重试次数({MAX_RETRY_COUNT}次)，将被标记为失败不再重试")
                await message.ack()
                self._update_activity_timestamp()
                return

            # 确保新头信息不为None，基于现有头信息复制（处理首次为None的情况）
            new_headers = current_headers.copy()
            new_headers['x-retry-count'] = retry_count

            new_message = aio_pika.Message(
                body=message.body,
                content_type=message.content_type,
                headers=new_headers,
                delivery_mode=message.delivery_mode
            )

            # 拒绝原消息（不重新入队）
            await message.reject(requeue=False)

            # 将新消息重新发布到交换机，实现重试并保留次数记录
            if self.exchange:
                await self.exchange.publish(
                    new_message,
                    routing_key=self.routing_key or '#'
                )
                self._update_activity_timestamp()
                logging.info(f"消息已重新发布，当前重试次数: {retry_count}")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
