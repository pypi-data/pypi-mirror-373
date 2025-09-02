import asyncio
import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, scoped_session

load_dotenv()


sqlalchemy_database_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///fallback.db")
sqlalchemy_database_name = os.getenv("SQLALCHEMY_DATABASE_NAME", "default")
sqlalchemy_echo = os.getenv("SQLALCHEMY_ECHO", "False").lower() in ("true", "1", "yes")  # 转换为布尔值
sqlalchemy_pool_size = int(os.getenv("SQLALCHEMY_POOL_SIZE", 10))  # 转换为整数
sqlalchemy_max_overflow = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 5))  # 转换为整数
sqlalchemy_pool_pre_ping = os.getenv("SQLALCHEMY_POOL_PRE_PING", "True").lower() in ("true", "1", "yes")  # 转换为布尔值
sqlalchemy_pool_recycle = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 1800))  # 转换为整数


# 创建引擎
engine = create_engine(
    url=f'{sqlalchemy_database_uri}/{sqlalchemy_database_name}',
    echo=sqlalchemy_echo,  # 是否打印SQL
    pool_size=sqlalchemy_pool_size,  # 连接池的大小，指定同时在连接池中保持的数据库连接数，默认:5
    max_overflow=sqlalchemy_max_overflow,  # 超出连接池大小的连接数，超过这个数量的连接将被丢弃,默认: 5
    pool_pre_ping=sqlalchemy_pool_pre_ping,
    pool_recycle=sqlalchemy_pool_recycle,
    # connect_args={ "use_unicode": True}  
)
# print("Database engine created")
# print(f"DATABASE_URL: {settings.sqlalchemy_database_uri}")
# 封装获取会话
_Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False, autocommit=False, autoflush=False))


# 实例化SessionLocal类
@contextmanager
def get_db_session(auto_commit_by_exit=False, auto_close=False):
    """使用上下文管理资源关闭"""
    _session = _Session()
    try:
        yield _session
        # 退出时，是否自动提交
        if auto_commit_by_exit:
            _session.commit()
    except OperationalError as e:
        # 捕获连接超时异常并重新初始化会话
        _session.close()
        _session = _Session()
        yield _session
        if auto_commit_by_exit:
            _session.commit()
    except Exception as e:
        _session.rollback()
        raise e
    finally:
        if auto_close:
            _session.close()

async def keepalive():
    while True:
        try:
            with get_db_session() as session:
                session.execute(text("SELECT 1"))
                session.commit()
        except Exception as e:
            print(f"Keepalive failed: {e}")
            keepalive()
        await asyncio.sleep(300)  # 每5分钟执行一次
