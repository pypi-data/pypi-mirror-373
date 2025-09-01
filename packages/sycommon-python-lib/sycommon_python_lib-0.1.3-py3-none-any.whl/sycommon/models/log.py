from pydantic import BaseModel


class LogModel(BaseModel):
    traceId: str
    sySpanId: str
    syBizId: str
    ptxId: str
    time: str
    day: str
    msg: str
    detail: str
    IP: str
    hostName: str
    tenantId: str
    userId: str
    customerId: str
    env: str
    priReqSource: str
    reqSource: str
    serviceId: str
    logLevel: str
    classShortName: str
    method: str
    line: str
    theadName: str
    className: str
    sqlCost: float
    size: float
    uid: float
