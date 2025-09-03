"""
小红书工具包统一日志配置模块

提供统一的日志配置和管理功能
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from typing import Optional, Any
from loguru import logger

class LoggerConfig:
    """日志配置管理器"""

    def __init__(self, log_level: str = "INFO", log_file: str = None):
        """
        初始化日志配置

        Args:
            log_level: 日志级别
            log_file: 日志文件路径，如果为None则使用安全的默认路径
        """
        self.log_level = log_level.upper()
        self.log_file = self._get_safe_log_path(log_file)
        self._setup_loguru()
        self._setup_third_party_loggers()

    def _get_safe_log_path(self, log_file: str = None) -> str:
        """
        获取安全的日志文件路径

        Args:
            log_file: 用户指定的日志文件路径

        Returns:
            安全的日志文件路径
        """
        if log_file:
            # 如果用户指定了路径，尝试使用
            try:
                log_path = Path(log_file)
                # 如果是相对路径，转换为绝对路径
                if not log_path.is_absolute():
                    log_path = Path.cwd() / log_path

                # 确保父目录存在且可写
                log_path.parent.mkdir(parents=True, exist_ok=True)

                # 测试是否可写
                test_file = log_path.parent / f".test_write_{os.getpid()}"
                try:
                    test_file.touch()
                    test_file.unlink()
                    return str(log_path)
                except (OSError, PermissionError):
                    pass
            except Exception:
                pass

        # 尝试多个安全的路径
        safe_paths = [
            # 1. 用户主目录下的.xhs_toolkit目录
            Path.home() / ".xhs_toolkit" / "xhs_toolkit.log",
            # 2. 系统临时目录
            Path(tempfile.gettempdir()) / "xhs_toolkit.log",
            # 3. 当前工作目录（如果可写）
            Path.cwd() / "xhs_toolkit.log",
        ]

        for path in safe_paths:
            try:
                # 确保父目录存在
                path.parent.mkdir(parents=True, exist_ok=True)

                # 测试是否可写
                test_file = path.parent / f".test_write_{os.getpid()}"
                test_file.touch()
                test_file.unlink()

                return str(path)
            except (OSError, PermissionError):
                continue

        # 如果所有路径都不可用，返回None（只使用控制台输出）
        return None

    def _setup_loguru(self) -> None:
        """配置loguru日志器"""
        # 移除默认的日志处理器
        logger.remove()

        # 添加控制台输出
        logger.add(
            sys.stderr,
            level=self.log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <level>{message}</level>",
            colorize=True
        )

        # 只有在有有效日志文件路径时才添加文件输出
        if self.log_file:
            try:
                logger.add(
                    self.log_file,
                    rotation="10 MB",
                    retention="7 days",
                    level=self.log_level,
                    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
                    encoding="utf-8"
                )
            except Exception as e:
                # 如果文件日志添加失败，只使用控制台输出
                logger.warning(f"⚠️ 无法创建日志文件 {self.log_file}: {e}")
                logger.warning("📝 将只使用控制台输出日志")
                self.log_file = None

        # 如果是DEBUG级别，输出详细信息
        if self.log_level == "DEBUG":
            logger.debug("🔧 DEBUG模式已启用，将输出详细调试信息")
            logger.debug(f"🔧 日志级别: {self.log_level}")
            logger.debug(f"🔧 日志文件: {self.log_file}")
            logger.debug(f"🔧 当前工作目录: {os.getcwd()}")
            logger.debug(f"🔧 Python版本: {sys.version}")
    
    def _setup_third_party_loggers(self) -> None:
        """配置第三方库的日志器"""
        # 抑制selenium的部分警告
        selenium_logger = logging.getLogger('selenium')
        selenium_logger.setLevel(logging.WARNING)
        
        # 抑制urllib3的警告
        urllib3_logger = logging.getLogger('urllib3')
        urllib3_logger.setLevel(logging.WARNING)
        
        # 配置uvicorn和FastAPI的日志过滤器
        self._setup_asgi_filter()
    
    def _setup_asgi_filter(self) -> None:
        """设置ASGI相关的日志过滤器"""
        class ASGIErrorFilter(logging.Filter):
            def filter(self, record):
                # 过滤ASGI相关的错误信息
                asgi_error_keywords = [
                    "Expected ASGI message",
                    "RuntimeError",
                    "Exception in ASGI application",
                    "Cancel 0 running task(s)"
                ]
                return not any(keyword in record.getMessage() for keyword in asgi_error_keywords)
        
        # 应用过滤器到uvicorn日志
        uvicorn_logger = logging.getLogger("uvicorn.error")
        uvicorn_logger.addFilter(ASGIErrorFilter())
        
        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        uvicorn_access_logger.addFilter(ASGIErrorFilter())
    
    def get_logger(self, name: str) -> Any:
        """
        获取带有模块名的日志器
        
        Args:
            name: 模块名称
            
        Returns:
            配置好的日志器
        """
        return logger.bind(name=name)


# 全局日志配置实例
_logger_config: Optional[LoggerConfig] = None


def setup_logger(log_level: str = None, log_file: str = None) -> None:
    """
    设置全局日志配置

    Args:
        log_level: 日志级别，默认从环境变量LOG_LEVEL获取
        log_file: 日志文件，默认使用安全路径
    """
    global _logger_config

    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    # 不再提供默认的log_file，让LoggerConfig自己选择安全路径
    _logger_config = LoggerConfig(log_level, log_file)


def get_logger(name: Optional[str] = None) -> Any:
    """
    获取日志器实例
    
    Args:
        name: 模块名称
        
    Returns:
        配置好的日志器
    """
    if name is None:
        name = __name__
        
    if _logger_config is None:
        setup_logger()
    
    return _logger_config.get_logger(name)

# 延迟初始化，避免在导入时就创建日志文件
_logger_config = None