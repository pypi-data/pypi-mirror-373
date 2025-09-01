from pydantic import BaseModel


class MQConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    publisherConfirms: bool
    publisherConfirmType: str
    virtualHost: str


class MQConsumer(BaseModel):
    enabled: bool
