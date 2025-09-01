from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sycommon.config.Config import SingletonMeta
from sycommon.database.database_service import DatabaseService
from sycommon.logging.kafka_log import SYLogger


class BaseDBService(metaclass=SingletonMeta):
    """数据库操作基础服务类，封装会话管理功能"""

    def __init__(self):
        self.engine = DatabaseService.engine()
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def session(self):
        """
        数据库会话上下文管理器
        自动处理会话的创建、提交、回滚和关闭
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            SYLogger.error(f"Database operation failed: {str(e)}")
            raise
        finally:
            session.close()
