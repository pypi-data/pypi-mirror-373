from sqlalchemy import create_engine, text

from sycommon.config.Config import SingletonMeta
from sycommon.config.DatabaseConfig import DatabaseConfig, convert_dict_keys
from sycommon.logging.kafka_log import SYLogger
from sycommon.synacos.nacos_service import NacosService


class DatabaseService(metaclass=SingletonMeta):
    _engine = None

    @staticmethod
    def setup_database(config: dict, shareConfigKey: str):
        common = NacosService(config).share_configs.get(shareConfigKey, {})
        if common and common.get('spring', {}).get('datasource', None):
            databaseConfig = common.get('spring', {}).get('datasource', None)
            converted_dict = convert_dict_keys(databaseConfig)
            db_config = DatabaseConfig.model_validate(converted_dict)
            DatabaseService._engine = DatabaseConnector(db_config).engine

    @staticmethod
    def engine():
        return DatabaseService._engine


class DatabaseConnector(metaclass=SingletonMeta):
    def __init__(self, db_config: DatabaseConfig):
        # 从 DatabaseConfig 中提取数据库连接信息
        self.db_user = db_config.username
        self.db_password = db_config.password
        # 提取 URL 中的主机、端口和数据库名
        url_parts = db_config.url.split('//')[1].split('/')
        host_port = url_parts[0].split(':')
        self.db_host = host_port[0]
        self.db_port = host_port[1]
        self.db_name = url_parts[1].split('?')[0]

        # 提取 URL 中的参数
        params_str = url_parts[1].split('?')[1] if len(
            url_parts[1].split('?')) > 1 else ''
        params = {}
        for param in params_str.split('&'):
            if param:
                key, value = param.split('=')
                params[key] = value

        # 在params中去掉指定的参数
        for key in ['useUnicode', 'characterEncoding', 'serverTimezone', 'zeroDateTimeBehavior']:
            if key in params:
                del params[key]

        # 构建数据库连接 URL
        self.db_url = f'mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

        SYLogger.info(f"Database URL: {self.db_url}")

        # 优化连接池配置
        self.engine = create_engine(
            self.db_url,
            connect_args=params,
            pool_size=10,  # 连接池大小
            max_overflow=20,  # 最大溢出连接数
            pool_timeout=30,  # 连接超时时间（秒）
            pool_recycle=3600,  # 连接回收时间（秒）
            pool_pre_ping=True  # 每次获取连接前检查连接是否有效
        )

        # 测试
        if not self.test_connection():
            raise Exception("Database connection test failed")

    def test_connection(self):
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return True
        except Exception as e:
            SYLogger.error(f"Database connection test failed: {e}")
            return False
