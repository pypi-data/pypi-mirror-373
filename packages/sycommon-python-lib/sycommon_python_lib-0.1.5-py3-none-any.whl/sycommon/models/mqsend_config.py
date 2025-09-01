from typing import Optional
from sycommon.models.mqlistener_config import RabbitMQListenerConfig


class RabbitMQSendConfig(RabbitMQListenerConfig):
    """MQ消息发送配置模型，继承自监听器配置"""
    # 是否自动连接
    auto_connect: bool = True
