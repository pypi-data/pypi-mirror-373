import logging
import logging.handlers
import datetime
import json
import os
import sys
import time
import threading
import queue
from typing import Optional, Dict, Any, List, Callable
import atexit
import traceback
import inspect
import psutil
import multiprocessing


def get_caller_filename(default='mylogger'):
    stack = inspect.stack()
    for frame_info in stack:
        filename = frame_info.filename
        if not filename.endswith('mylogger.py'):
            return os.path.splitext(os.path.basename(filename))[0]
    return default

class MyLogger:
    """
    日志记录器

    功能：
    - 异步日志记录（减少I/O阻塞）
    - 上下文管理器支持
    - 自定义日志过滤器
    - 更丰富的系统指标采集
    - 日志采样控制
    - 动态日志级别调整
    - 请求跟踪ID
    - 多线程安全
    - 日志缓冲和批量写入
    - 自定义异常处理

    使用示例：
    logger = MyLogger(
        name='app_logger',
        logging_mode='both',
        log_level='INFO',
        log_file='app.log',
        max_log_size=50,
        backup_count=5,
        enable_async=True
    )

    with logger.context(request_id='12345'):
        logger.info("处理请求", extra={'user': 'admin'})
    """

    def __init__(
            self,
            name: Optional[str] = None,
            logging_mode: str = 'console',  # 'both', 'console', 'file', 'none'
            log_level: str = 'INFO',  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
            log_file: Optional[str] = None,
            log_format: str = 'json',  # 默认json格式，可选'simple'
            max_log_size: int = 50,  # MB
            backup_count: int = 5,
            sensitive_fields: Optional[List[str]] = None,
            enable_async: bool = False,
            buffer_size: int = 1000,
            sample_rate: float = 1.0,
            filters: Optional[List[Callable]] = None,
            enable_metrics: bool = False,
            metrics_interval: int = 300,
            message_limited: int = 1000,
            flush_interval: int = 5,
            enable_multiprocess: bool = False
    ):
        """
        初始化日志器

        :param name: 日志器名称
        :param logging_mode: 输出模式
        :param log_level: 日志级别
        :param log_file: 日志文件路径
        :param max_log_size: 单个日志文件最大大小(MB)
        :param backup_count: 保留的日志文件数量
        :param sensitive_fields: 敏感字段列表(会被过滤)
        :param enable_async: 是否启用异步日志
        :param buffer_size: 日志缓冲大小(仅异步模式有效)
        :param sample_rate: 控制日志的采样率(0.0-1.0)，使用消息内容的哈希值来决定是否记录，减少日志量，防止日志过于冗长
        :param filters: 自定义日志过滤器列表
        :param enable_metrics: 是否启用系统指标采集
        :param metrics_interval: 指标采集间隔(秒)
        :param message_limited: 简化日志内容，避免过长
        :param flush_interval: 定时刷新日志器间隔(秒)
        :param enable_multiprocess: 是否启用多进程安全日志
        """
        log_path = os.path.join(os.path.expanduser("~"), 'logfile')
        if name is None:
            name = get_caller_filename()
        self.name = name
        self.logging_mode = logging_mode.lower()
        self.log_level = log_level.upper()
        if log_file is None:
            self.log_file = os.path.join(log_path, f"{self.name}.log")
        else:
            self.log_file = os.path.join(os.path.expanduser("~"), log_file)
        if not os.path.isdir(os.path.dirname(self.log_file)):
            os.makedirs(os.path.dirname(self.log_file))
        self.log_format = log_format
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        self.sensitive_fields = sensitive_fields or []
        self.enable_async = enable_async
        self.buffer_size = buffer_size
        self.sample_rate = max(0.0, min(1.0, sample_rate))
        self.filters = filters or []
        self.enable_metrics = enable_metrics
        self.metrics_interval = metrics_interval
        self.message_limited = max(1, int(message_limited))
        self.flush_interval = max(1, int(flush_interval))
        self.enable_multiprocess = enable_multiprocess
        self._mp_queue = None
        self._mp_writer_process = None
        self._is_main_process = multiprocessing.current_process().name == 'MainProcess'
        self._stop_event = threading.Event()
        self._flush_thread = None

        # 上下文相关
        self._context = threading.local()
        self._context.data = {}

        # 系统指标相关
        self._last_metrics_time = 0
        self._metrics_cache = {}

        # 异步日志相关（标准库实现）
        self._log_queue = None
        self._queue_listener = None
        self._handlers = []

        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self._init_logging()

        if self.enable_multiprocess:
            self._setup_multiprocess_logging()
        elif self.enable_async:
            self._setup_async_logging()

        atexit.register(self.shutdown)

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.shutdown()
        if exc_type is not None:
            self.error(f"上下文内异常: {exc_val}",
                       extra={'类型': str(exc_type)})
        return False

    def context(self, **kwargs):
        """返回一个上下文管理器，可以设置临时上下文变量"""
        return self._ContextManager(self, kwargs)

    class _ContextManager:
        def __init__(self, logger, context_vars):
            self.logger = logger
            self.context_vars = context_vars
            self.old_context = {}

        def __enter__(self):
            self.old_context = getattr(self.logger._context, 'data', {}).copy()
            self.logger._context.data.update(self.context_vars)
            return self.logger

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.logger._context.data = self.old_context
            if exc_type is not None:
                self.logger.error(f"上下文内异常2: {exc_val}", extra={'类型': str(exc_type)})
            return False

    def _init_logging(self):
        """初始化日志配置"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_levels:
            self.log_level = 'INFO'
        self.logger.setLevel(self.log_level)
        if self.logger.handlers:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
        if self.log_format.lower() == 'simple':
            class SimpleFormatter(logging.Formatter):
                def format(self, record):
                    msg = super().format(record)
                    # 统一处理 extra_data 字段
                    extra_data = getattr(record, 'extra_data', None)
                    if not extra_data and hasattr(record, 'extra'):
                        extra_data = getattr(record, 'extra', None)
                    if extra_data:
                        # 优先显示func信息
                        func_name = extra_data.get('func', '')
                        module_name = extra_data.get('model', '')
                        line_number = extra_data.get('lines', '')
                        if func_name:
                            msg += f" | Function: {func_name}"
                        if module_name:
                            msg += f" | Module: {module_name}"
                        if line_number:
                            msg += f" | Line: {line_number}"
                        
                        context_data = extra_data.get('context_data', {})
                        if context_data:
                            msg += f" | Context: {context_data}"
                        metrics = extra_data.get('性能指标', {})
                        if metrics:
                            msg += f" | Metrics: {metrics}"
                        extra = {k: v for k, v in extra_data.items()
                                 if k not in ('context_data', '性能指标', 'func', 'model', 'lines')}
                        if extra:
                            msg += f" | Extra: {extra}"
                    return msg
            formatter = SimpleFormatter('%(asctime)s - %(levelname)s - %(message)s')
            formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        else:
            class StructuredFormatter(logging.Formatter):
                def format(self, record):
                    log_data = {
                        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'level': record.levelname,
                        'msg': record.getMessage(),
                    }
                    if hasattr(record, 'extra_data'):
                        log_data.update(record.extra_data)
                    if hasattr(record, 'context_data'):
                        log_data.update(record.context_data)
                    if record.exc_info:
                        log_data['异常'] = self.formatException(record.exc_info)
                    if hasattr(record, 'extra_data') and '过滤' in record.extra_data:
                        sensitive_fields = record.extra_data['过滤']
                        for field in sensitive_fields:
                            if field in log_data:
                                log_data[field] = '***'
                            if isinstance(log_data.get('message'), str):
                                log_data['message'] = log_data['message'].replace(field, '***')
                    return json.dumps(log_data, ensure_ascii=False, default=str)
            formatter = StructuredFormatter()

        # 只创建handlers，不加到logger上（异步时由QueueListener管理）
        self._handlers = []
        if self.logging_mode in ('both', 'console'):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self._handlers.append(console_handler)
        if self.logging_mode in ('both', 'file'):
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            file_handler = logging.handlers.RotatingFileHandler(
                filename=self.log_file,
                maxBytes=self.max_log_size * 1024 * 1024,
                backupCount=self.backup_count,
                encoding='utf-8',
                delay=False
            )
            file_handler.setFormatter(formatter)
            self._handlers.append(file_handler)
        if not self.enable_async:
            for handler in self._handlers:
                self.logger.addHandler(handler)

    def _setup_async_logging(self):
        self._log_queue = queue.Queue(maxsize=self.buffer_size)
        queue_handler = logging.handlers.QueueHandler(self._log_queue)
        self.logger.addHandler(queue_handler)
        self._queue_listener = logging.handlers.QueueListener(
            self._log_queue, *self._handlers, respect_handler_level=True
        )
        self._queue_listener.start()

    def _setup_multiprocess_logging(self):
        """多进程安全日志：主进程写日志，子进程投递消息"""
        self._mp_queue = multiprocessing.Queue(self.buffer_size)
        if self._is_main_process:
            # 主进程：启动写入进程
            self._mp_writer_process = multiprocessing.Process(
                target=self._mp_writer_worker,
                args=(self._mp_queue,),
                name=f"{self.name}_mp_writer",
                daemon=True
            )
            self._mp_writer_process.start()
        else:
            # 子进程：不需要写入进程
            pass

    def _mp_writer_worker(self, log_queue):
        """日志写入进程，消费队列并写日志"""
        # 重新初始化logger和handlers（避免多进程fork后锁混乱）
        self._init_logging()
        while True:
            try:
                record = log_queue.get()
                if record is None:
                    break
                level, message, extra = record
                self._sync_log(level, message, extra)
            except Exception as e:
                try:
                    self.logger.error(f"多进程日志写入异常: {e}", extra={'extra_data': {'mp_writer_error': str(e)}})
                except:
                    pass

    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统资源使用指标"""
        if not self.enable_metrics:
            return {}
        try:
            return {
                '内存': {
                    '使用率': psutil.virtual_memory().percent,
                    '已使用': psutil.virtual_memory().used,
                    '可用': psutil.virtual_memory().available,
                },
                'CPU': {
                    '使用率': psutil.cpu_percent(),
                    '核心数': psutil.cpu_count(),
                },
                '磁盘': {
                    '使用率': psutil.disk_usage('/').percent,
                    '已使用': psutil.disk_usage('/').used,
                    '剩余': psutil.disk_usage('/').free,
                },
                '网络': {
                    '发送字节数': psutil.net_io_counters().bytes_sent,
                    '接收字节数': psutil.net_io_counters().bytes_recv,
                },
                '进程': {
                    'PID': os.getpid(),
                    '线程数': threading.active_count(),
                }
            }
        except Exception as e:
            self.logger.warning(f"无法采集系统性能指标: {e}", extra={'extra_data': {'metrics_error': str(e)}})
            return {}

    def _apply_filters(self, level: str, message: str, extra: Dict) -> bool:
        """应用自定义过滤器"""
        for filter_func in self.filters:
            try:
                if not filter_func(level, message, extra):
                    return False
            except Exception as e:
                self.logger.warning(f"过滤失败: {e}",
                                    extra={'extra_data': {'filter_error': str(e)}})
        return True

    def log_error_handler(retry_times=0, fallback_level='error'):
        """
        日志错误处理装饰器

        参数:
        - retry_times: 异常时重试次数
        - fallback_level: 降级日志级别
        """

        def decorator(log_method):
            def wrapper(self, level: str, message: str, extra: Optional[Dict] = None):
                last_exception = None
                for attempt in range(retry_times + 1):
                    try:
                        return log_method(self, level, message, extra)
                    except Exception as e:
                        last_exception = e
                        if attempt < retry_times:
                            time.sleep(0.1 * (attempt + 1))
                            continue

                        try:
                            logging.basicConfig()
                            fallback_logger = logging.getLogger(f"{getattr(self, 'name', 'mylogger')}_fallback")
                            fallback_msg = f"[降级处理] {message}"[:1000]
                            getattr(fallback_logger, fallback_level)(
                                f"日志记录失败(尝试{attempt + 1}次): {e}\n原始消息: {fallback_msg}"
                            )
                        except:
                            sys.stderr.write(f"严重: 日志系统完全失败 - {last_exception}\n")

                return None

            return wrapper

        return decorator

    @log_error_handler(retry_times=1, fallback_level='warning')
    def _sync_log(self, level: str, message: str, extra: Optional[Dict] = None):
        if self.enable_multiprocess and not self._is_main_process:
            # 子进程：只投递消息
            try:
                self._mp_queue.put((level, message, extra), block=False)
            except Exception as e:
                # 投递失败降级本地输出
                logging.basicConfig()
                fallback_logger = logging.getLogger(f"{getattr(self, 'name', 'mylogger')}_mp_fallback")
                fallback_logger.warning(f"[多进程投递失败] {message} {e}")
            return
        # 主进程/普通模式：正常写日志
        if not hasattr(self.logger, level.lower()):
            return
        if not isinstance(message, str):
            message = str(message)
        if len(message) > self.message_limited:
            message = message[:self.message_limited] + '...'
        if self.enable_metrics:
            now = time.time()
            if now - self._last_metrics_time > self.metrics_interval:
                self._metrics_cache = self._get_system_metrics()
                self._last_metrics_time = now
        log_extra = {}
        if self.enable_metrics:
            log_extra['性能指标'] = self._metrics_cache
        if extra:
            log_extra.update(extra)

        # 获取当前调用func
        try:
            frame = inspect.currentframe()
            # 跳过logger内部函数，找到真正的调用者
            caller_frame = frame.f_back
            skip_functions = ['_sync_log', 'log', 'debug', 'info', 'warning', 'error', 'critical', 'wrapper', 'log_error_handler', 'decorator']
            while caller_frame and caller_frame.f_code.co_name in skip_functions:
                caller_frame = caller_frame.f_back
            if caller_frame:
                log_extra['func'] = caller_frame.f_code.co_name
                log_extra['model'] = caller_frame.f_globals.get('__name__', '')
                log_extra['lines'] = caller_frame.f_lineno
            del frame
        except Exception:
            # 如果获取函数信息失败，不影响正常日志记录
            pass

        # 添加上下文信息
        if hasattr(self._context, 'data') and self._context.data:
            log_extra['context_data'] = self._context.data.copy()

        # 添加敏感字段过滤
        if self.sensitive_fields:
            log_extra['过滤'] = self.sensitive_fields

        # 应用日志采样
        if self.sample_rate < 1.0 and level.lower() in ('debug', 'info'):
            if hash(message) % 100 >= self.sample_rate * 100:
                return

        # 应用过滤器
        if not self._apply_filters(level, message, log_extra):
            return

        # 记录日志（直接走logger，异步/同步由handler决定）
        getattr(self.logger, level.lower())(message, extra={'extra_data': log_extra})

    def log(self, level: str, message: str, extra: Optional[Dict] = None):
        """
        记录日志

        :param level: 日志级别 ('debug', 'info', 'warning', 'error', 'critical')
        :param message: 日志消息
        :param extra: 额外数据字典
        """
        if not hasattr(self.logger, level.lower()):
            return
        self._sync_log(level, message, extra)

    def set_level(self, level: str):
        """动态设置日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        level = level.upper()
        if level in valid_levels:
            self.log_level = level
            self.logger.setLevel(level)
            for handler in self.logger.handlers:
                handler.setLevel(level)

    def add_filter(self, filter_func: Callable):
        """添加日志过滤器"""
        if callable(filter_func):
            self.filters.append(filter_func)

    def set_context(self, **kwargs):
        """设置上下文变量"""
        if not hasattr(self._context, 'data'):
            self._context.data = {}
        self._context.data.update(kwargs)

    def get_context(self, key: str, default=None):
        """获取上下文变量"""
        if hasattr(self._context, 'data'):
            return self._context.data.get(key, default)
        return default

    def clear_context(self):
        """清除所有上下文变量"""
        if hasattr(self._context, 'data'):
            self._context.data.clear()

    def debug(self, message: str, extra: Optional[Dict] = None):
        """记录调试信息"""
        self.log('debug', message, extra)

    def info(self, message: str, extra: Optional[Dict] = None):
        """记录一般信息"""
        self.log('info', message, extra)

    def warning(self, message: str, extra: Optional[Dict] = None):
        """记录警告信息"""
        self.log('warning', message, extra)

    def error(self, message: str, extra: Optional[Dict] = None):
        """记录错误信息"""
        self.log('error', message, extra)

    def critical(self, message: str, extra: Optional[Dict] = None):
        """记录严重错误信息"""
        self.log('critical', message, extra)

    def exception(self, message: str, exc_info: Exception, extra: Optional[Dict] = None):
        """记录异常信息"""
        if not extra:
            extra = {}
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back.f_back
            extra.update({
                'module': caller_frame.f_globals.get('__name__', ''),
                'function': caller_frame.f_code.co_name,
                'line': caller_frame.f_lineno,
                'file': caller_frame.f_code.co_filename,
                '异常': str(exc_info),
                '类型': exc_info.__class__.__name__,
                '堆栈': self._format_traceback(exc_info)
            })
        finally:
            del frame
        self.log('error', message, extra)

    def _format_traceback(self, exc_info):
        """格式化异常堆栈"""
        if exc_info is None:
            return "No traceback available"
        return ''.join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__))

    def timeit(self, message: str = "Execution time"):
        """返回一个计时器上下文管理器"""
        return self._Timer(self, message)

    class _Timer:
        def __init__(self, logger, message):
            self.logger = logger
            self.message = message
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed = time.time() - self.start_time
            self.logger.info(f"{self.message}: {elapsed:.3f}s", extra={'elapsed_seconds': f"{elapsed:.3f}"})
            return False

    def _start_flush_thread(self):
        """启动定时刷新线程"""
        self._stop_event.clear()
        self._flush_thread = threading.Thread(
            target=self._flush_worker,
            name=f"{self.name}_flush_thread",
            daemon=True
        )
        self._flush_thread.start()

    def _flush_worker(self):
        """定时刷新工作线程"""
        while not self._stop_event.is_set():
            try:
                time.sleep(self.flush_interval)
                self._flush_handlers()
            except Exception as e:
                try:
                    self.logger.error(f"刷新线程异常: {e}",
                                      extra={'extra_data': {'flush_error': str(e)}})
                except:
                    pass

    def _flush_handlers(self):
        """刷新所有handler"""
        for handler in self.logger.handlers:
            try:
                handler.flush()
            except Exception as e:
                try:
                    self.logger.error(f"刷新handler失败: {e}",
                                      extra={'extra_data': {'handler_flush_error': str(e)}})
                except:
                    pass

    def shutdown(self):
        """关闭日志记录器，确保所有日志被刷新"""
        if self.enable_multiprocess and self._is_main_process and self._mp_writer_process:
            try:
                self._mp_queue.put(None)
                self._mp_writer_process.join(timeout=5)
            except:
                pass
        if self.enable_multiprocess and self._mp_queue is not None:
            try:
                self._mp_queue.close()
                self._mp_queue.join_thread()
            except:
                pass
            self._mp_queue = None
        if self.enable_async and self._queue_listener:
            self._queue_listener.stop()
        for handler in self.logger.handlers[:]:
            try:
                handler.close()
            except:
                pass
            self.logger.removeHandler(handler)
        for handler in getattr(self, '_handlers', []):
            try:
                handler.close()
            except:
                pass

def main():
    logger = MyLogger(
        name='my_app',
        logging_mode='both',
        log_level='DEBUG',
        log_file='my_app.log',
        log_format='json',
        max_log_size=50,
        backup_count=5,
        enable_async=False,  # 是否启用异步日志
        sample_rate=1,  # 采样DEBUG/INFO日志
        sensitive_fields=[],  #  敏感字段列表
        enable_metrics=False,  # 是否启用性能指标
    )
    logger.info('123', extra={'extra_data': {'test': 'test'}})
    logger.shutdown()


if __name__ == '__main__':
    pass
