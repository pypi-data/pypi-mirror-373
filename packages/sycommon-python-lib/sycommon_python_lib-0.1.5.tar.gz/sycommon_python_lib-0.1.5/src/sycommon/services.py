from typing import Any, Callable, Dict, List, Tuple, Union, Optional, Awaitable
import asyncio
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import yaml
from sycommon.config.Config import SingletonMeta
from sycommon.models.mqlistener_config import RabbitMQListenerConfig
from sycommon.models.mqsend_config import RabbitMQSendConfig
from sycommon.rabbitmq.rabbitmq_service import RabbitMQService


class Services(metaclass=SingletonMeta):
    _loop: Optional[asyncio.AbstractEventLoop] = None
    _config: Optional[dict] = None
    _initialized: bool = False
    _registered_senders: List[str] = []
    _mq_tasks: List[asyncio.Task] = []
    _pending_setup: Optional[Callable[..., Awaitable[None]]] = None
    _instance: Optional['Services'] = None

    def __init__(self, config):
        if not Services._config:
            Services._config = config
        Services._instance = self

    @classmethod
    def get_lifespan(cls, config):
        """返回 FastAPI 的 lifespan 管理器"""
        cls._config = config

        @asynccontextmanager
        async def lifespan(app):
            # 应用启动时初始化
            cls._loop = asyncio.get_running_loop()
            cls._initialized = True
            logging.info("Services initialized with FastAPI event loop")

            # 执行之前缓存的MQ设置
            if cls._pending_setup:
                try:
                    await cls._pending_setup()
                except Exception as e:
                    logging.error(f"执行MQ初始化失败: {str(e)}", exc_info=True)
                finally:
                    cls._pending_setup = None

            try:
                yield
            finally:
                # 应用关闭时清理
                await cls.shutdown()
                logging.info("Services shutdown completed")

        return lifespan

    @classmethod
    def plugins(cls,
                middleware: Optional[Tuple[Callable, FastAPI]] = None,
                nacos_service: Optional[Callable] = None,
                logging_service: Optional[Callable] = None,
                database_service: Optional[Union[Tuple[Callable, str],
                                                 List[Tuple[Callable, str]]]] = None,
                rabbitmq_listeners: Optional[List[RabbitMQListenerConfig]] = None,
                rabbitmq_senders: Optional[List[RabbitMQSendConfig]] = None
                ) -> None:
        """
        类方法：注册各种服务插件
        确保单例实例存在后调用实例方法的register_plugins
        """
        # 确保实例已创建
        if not cls._instance:
            if not cls._config:
                raise ValueError("Services尚未初始化，请先提供配置")
            cls._instance = Services(cls._config)

        cls._instance.register_plugins(
            middleware=middleware,
            nacos_service=nacos_service,
            logging_service=logging_service,
            database_service=database_service,
            rabbitmq_listeners=rabbitmq_listeners,
            rabbitmq_senders=rabbitmq_senders
        )

    def register_plugins(
        self,
        middleware: Optional[Tuple[Callable, FastAPI]] = None,
        nacos_service: Optional[Callable] = None,
        logging_service: Optional[Callable] = None,
        database_service: Optional[Union[Tuple[Callable,
                                               str], List[Tuple[Callable, str]]]] = None,
        rabbitmq_listeners: Optional[List[RabbitMQListenerConfig]] = None,
        rabbitmq_senders: Optional[List[RabbitMQSendConfig]] = None
    ) -> None:
        """实例方法：实际执行各种服务插件的注册逻辑"""
        # 注册非异步服务
        if middleware:
            self._setup_middleware(middleware)
        if nacos_service:
            nacos_service(self._config)
        if logging_service:
            logging_service(self._config)
        if database_service:
            self._setup_database(database_service)

        RabbitMQService.init(self._config)

        # MQ设置异步函数
        async def setup_mq_components():
            if rabbitmq_senders:
                self._setup_senders(rabbitmq_senders)
            if rabbitmq_listeners:
                self._setup_listeners(rabbitmq_listeners)

        # 存储到_pending_setup，等待lifespan异步执行
        Services._pending_setup = setup_mq_components

    def _setup_database(self, database_service):
        if isinstance(database_service, tuple):
            db_setup, db_name = database_service
            db_setup(self._config, db_name)
        elif isinstance(database_service, list):
            for db_setup, db_name in database_service:
                db_setup(self._config, db_name)

    def _setup_middleware(self, middleware):
        if isinstance(middleware, tuple):
            middleware_setup, app = middleware
            middleware_setup(app, self._config)

    def _setup_senders(self, rabbitmq_senders):
        Services._registered_senders = [
            sender.queue_name for sender in rabbitmq_senders]
        if self._loop:  # 确保loop存在
            task = self._loop.create_task(
                self._setup_and_wait(
                    RabbitMQService.setup_senders, rabbitmq_senders)
            )
            self._mq_tasks.append(task)
        logging.info(f"已注册的RabbitMQ发送器: {Services._registered_senders}")

    def _setup_listeners(self, rabbitmq_listeners):
        if self._loop:  # 确保loop存在
            task = self._loop.create_task(
                self._setup_and_wait(
                    RabbitMQService.setup_listeners, rabbitmq_listeners)
            )
            self._mq_tasks.append(task)

    async def _setup_and_wait(self, setup_func, *args, **kwargs):
        try:
            await setup_func(*args, **kwargs)
        except Exception as e:
            logging.error(
                f"Error in {setup_func.__name__}: {str(e)}", exc_info=True)

    @classmethod
    async def send_message(
        cls,
        queue_name: str,
        data: Union[str, Dict[str, Any], BaseModel, None],
        max_retries: int = 3,  # 最大重试次数
        retry_delay: float = 1.0,  # 重试间隔（秒）
        **kwargs
    ) -> None:
        """发送消息，添加重试机制处理发送器不存在的情况"""
        if not cls._initialized or not cls._loop:
            logging.error("Services not properly initialized!")
            raise ValueError("服务未正确初始化")

        # 重试逻辑
        for attempt in range(max_retries):
            try:
                # 检查发送器是否已注册
                if queue_name not in cls._registered_senders:
                    # 可能是初始化尚未完成，尝试刷新注册列表
                    cls._registered_senders = RabbitMQService.sender_client_names
                    if queue_name not in cls._registered_senders:
                        raise ValueError(f"发送器 {queue_name} 未注册")

                # 获取发送器
                sender = RabbitMQService.get_sender(queue_name)
                if not sender:
                    raise ValueError(f"发送器 '{queue_name}' 不存在")

                # 发送消息
                await RabbitMQService.send_message(data, queue_name, ** kwargs)
                logging.info(f"消息发送成功（尝试 {attempt+1}/{max_retries}）")
                return  # 成功发送，退出函数

            except Exception as e:
                # 最后一次尝试失败则抛出异常
                if attempt == max_retries - 1:
                    logging.error(
                        f"消息发送失败（已尝试 {max_retries} 次）: {str(e)}", exc_info=True)
                    raise

                # 非最后一次尝试，记录警告并等待重试
                logging.warning(
                    f"消息发送失败（尝试 {attempt+1}/{max_retries}）: {str(e)}，"
                    f"{retry_delay}秒后重试..."
                )
                await asyncio.sleep(retry_delay)

    @staticmethod
    async def shutdown():
        for task in Services._mq_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        await RabbitMQService.shutdown()
