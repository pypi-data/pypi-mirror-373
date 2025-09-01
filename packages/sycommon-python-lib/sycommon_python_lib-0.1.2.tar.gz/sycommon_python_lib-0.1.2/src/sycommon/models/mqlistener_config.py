from pydantic import BaseModel, Field
from typing import Callable, Coroutine, Optional
from aio_pika.abc import AbstractIncomingMessage

from sycommon.models.mqmsg_model import MQMsgModel


class RabbitMQListenerConfig(BaseModel):
    """RabbitMQ监听器配置模型"""
    # 监听器唯一名称
    # name: str = Field(..., description="监听器唯一标识名称")

    # 队列配置
    queue_name: str = Field(..., description="队列名称")
    # 使用.分割queue_name取出第一部分
    # routing_key: str = Field(..., description="路由键")

    # 消息处理器
    handler: Callable[[MQMsgModel, AbstractIncomingMessage], Coroutine] | None = Field(
        None, description="消息处理函数"
    )

    # 可选配置参数
    host: Optional[str] = Field(None, description="RabbitMQ主机地址")
    port: Optional[int] = Field(None, description="RabbitMQ端口")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    virtualhost: Optional[str] = Field(None, description="虚拟主机")
    exchange_name: Optional[str] = Field(None, description="交换机名称")
    exchange_type: str = Field("topic", description="交换机类型")
    durable: bool = Field(True, description="是否持久化")
    auto_delete: bool = Field(False, description="是否自动删除队列")
    auto_parse_json: bool = Field(True, description="是否自动解析JSON消息")

    class Config:
        """模型配置"""
        # 允许存储函数类型
        arbitrary_types_allowed = True
