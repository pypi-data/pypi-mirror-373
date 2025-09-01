from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SsoUser(BaseModel):
    """SSO用户模型，对应Java的SsoUser类"""
    tenant_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    user_type: Optional[str] = None  # 用户类型
    auth_type: Optional[str] = None  # 认证类型
    system_type: Optional[str] = None  # 系统类型
    role_type: Optional[str] = None  # 角色类型
    user_id: Optional[str] = None  # 用户代码
    user_name: Optional[str] = None  # 用户名称
    real_name: Optional[str] = None  # 用户真实名称
    user_status: Optional[str] = None  # 用户状态
    last_logon_time: Optional[datetime] = None  # 上次登录时间
    num_logon_try: Optional[int] = None  # 登录重试次数
    working_right_codes: Optional[List[str]] = None  # 用户资源代码
    group_ids: Optional[List[str]] = None  # 用户组Ids
    password: Optional[str] = None  # 密码
    old_password: Optional[str] = None  # 盛易通旧密码
    request_path: Optional[str] = None  # 请求ID
    pwd_expiry_date: Optional[datetime] = None  # 过期时间
    model_flag: Optional[str] = None  # 当前模式
    sign_key: Optional[str] = None  # 签名key
    security_token: Optional[str] = None  # 安全秘钥
    mur: Optional[str] = None  # 指纹
    init_status: str = "N"  # 默认是N初始化(没有权限),Y表示权限初始化
    mobile_brand: Optional[str] = None  # 手机品牌
    mobile_type: Optional[str] = None  # 手机型号
    mobile_system_version: Optional[str] = None  # 系统版本
    platform: Optional[str] = None  # 手机平台
    ip: Optional[str] = None  # ip地址
    browser_type: Optional[str] = None  # 浏览器类型
    os_type: Optional[str] = None  # 系统类型
    access_token: Optional[str] = None  # 用于给在线用户使用

    # 申请渠道 PC-“PC”、APP-“APP”、SYSTEM-“系统生成”、YYD-“租户端”
    req_type: Optional[str] = None
    pri_req_source: Optional[str] = None  # 原始请求来源
    req_source: Optional[str] = None  # 请求来源
    identitys: Optional[List[str]] = None  # 客户身份

    # 修可登录终端，为空默认全部，1=PC，2=小程序，9=其他
    login_terminal: Optional[str] = None

    # 用户来源  3=无担保撮合（小微贷）
    user_source: Optional[str] = None

    # 登录方式 手机验证码登录：phoneCode
    login_type: Optional[str] = None

    # 是否个人账户 Y是/N否
    is_person_user: Optional[str] = None

    # 请求上下文traceId，用于MQ重发等场景
    trace_id: Optional[str] = None
