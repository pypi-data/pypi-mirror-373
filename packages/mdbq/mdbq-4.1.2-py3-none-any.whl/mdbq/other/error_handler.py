import traceback
import sys
from functools import wraps
import inspect
import asyncio
from typing import Callable, Optional, Any, List
import logging
import json


class _ErrorHandlerHelper:
    @staticmethod
    def get_default_logger():
        default_logger = logging.getLogger("mdbq.error_handler.default")
        handler_exists = any(isinstance(h, logging.StreamHandler) for h in default_logger.handlers)
        if not handler_exists:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            default_logger.addHandler(handler)
        default_logger.setLevel(logging.INFO)
        default_logger.propagate = False
        return default_logger

    @staticmethod
    def filter_fields(info: dict, log_fields):
        if not log_fields:
            return info
        return {k: info[k] for k in log_fields if k in info}

    @staticmethod
    def build_error_info(func, e, args, kwargs, stack_summary):
        tb = traceback.extract_tb(sys.exc_info()[2])
        last_tb = tb[-1] if tb else None
        return {
            '函数': func.__name__,
            '模块': func.__module__,
            '类型': type(e).__name__,
            '消息': str(e),
            '签名': str(inspect.signature(func)),
            'args': [str(arg) for arg in args] if args else [],
            'kwargs': {k: str(v) for k, v in kwargs.items()} if kwargs else {},
            '函数文件': func.__code__.co_filename,
            '函数行号': func.__code__.co_firstlineno,
            '异常行号': last_tb.lineno if last_tb else None,
            '异常文件': last_tb.filename if last_tb else None,
            '堆栈': stack_summary,
        }

    @staticmethod
    def build_final_error_info(func, last_exception, max_retries):
        tb = traceback.extract_tb(sys.exc_info()[2])
        last_tb = tb[-1] if tb else None
        return {
            '函数': func.__name__,
            '最终错误类型': type(last_exception).__name__,
            '最终错误消息': str(last_exception),
            '总尝试次数': max_retries,
            '堆栈跟踪': traceback.format_exc(),
            '异常行号': last_tb.lineno if last_tb else None,
            '异常文件': last_tb.filename if last_tb else None,
        }

    @staticmethod
    def get_stack_summary():
        stack_lines = traceback.format_exc().splitlines(keepends=True)
        if len(stack_lines) > 40:
            return ''.join(stack_lines[:20]) + '\n...\n' + ''.join(stack_lines[-20:])
        else:
            return ''.join(stack_lines)


def log_on_exception(
    logger=None,
    *,
    on_exception: Optional[Callable[[dict], None]] = None,
    default_return: Any = None,
    log_fields: Optional[List[str]] = None,
):
    """
    :param logger: 日志对象，需实现 debug/info/warning/error/critical 方法
    :param on_exception: 异常回调，参数为 error_info 字典
    :param default_return: 异常时返回的默认值
    :param log_fields: 只记录 error_info 的部分字段
    """
    if logger is not None:
        for method in ("debug", "info", "warning", "error", "critical"):
            if not hasattr(logger, method):
                raise TypeError(
                    f"logger 参数必须有 {method} 方法，当前类型为: {type(logger)}"
                )
    def decorator(func):
        is_async = asyncio.iscoroutinefunction(func)
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                stack_summary = _ErrorHandlerHelper.get_stack_summary()
                error_info = _ErrorHandlerHelper.build_error_info(func, e, args, kwargs, stack_summary)
                error_info = _ErrorHandlerHelper.filter_fields(error_info, log_fields)
                use_logger = logger if logger is not None else _ErrorHandlerHelper.get_default_logger()
                if use_logger:
                    if logger is None:
                        use_logger.error(f"执行失败\n详细信息: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
                    else:
                        use_logger.error("执行失败", {'details': error_info})
                if on_exception:
                    try:
                        on_exception(error_info)
                    except Exception:
                        pass
                return default_return
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                stack_summary = _ErrorHandlerHelper.get_stack_summary()
                error_info = _ErrorHandlerHelper.build_error_info(func, e, args, kwargs, stack_summary)
                error_info = _ErrorHandlerHelper.filter_fields(error_info, log_fields)
                use_logger = logger if logger is not None else _ErrorHandlerHelper.get_default_logger()
                if use_logger:
                    if logger is None:
                        use_logger.error(f"执行失败\n详细信息: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
                    else:
                        use_logger.error("执行失败", {'details': error_info})
                if on_exception:
                    try:
                        on_exception(error_info)
                    except Exception:
                        pass
                return default_return
        return async_wrapper if is_async else sync_wrapper
    return decorator


def log_on_exception_with_retry(
    max_retries=3,
    delay=1,
    logger=None,
    *,
    on_exception: Optional[Callable[[dict], None]] = None,
    default_return: Any = None,
    log_fields: Optional[List[str]] = None,
):
    """
    :param logger: 日志对象，需实现 debug/info/warning/error/critical 方法
    :param on_exception: 异常回调，参数为 error_info 字典
    :param default_return: 异常时返回的默认值
    :param log_fields: 只记录 error_info 的部分字段
    """
    if logger is not None:
        for method in ("debug", "info", "warning", "error", "critical"):
            if not hasattr(logger, method):
                raise TypeError(
                    f"logger 参数必须有 {method} 方法，当前类型为: {type(logger)}"
                )
    def decorator(func):
        is_async = asyncio.iscoroutinefunction(func)
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            import time
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_info = {
                        '函数': func.__name__,
                        '重试': attempt + 1,
                        '最大重试': max_retries,
                        '类型': type(e).__name__,
                        '消息': str(e),
                    }
                    error_info = _ErrorHandlerHelper.filter_fields(error_info, log_fields)
                    use_logger = logger if logger is not None else _ErrorHandlerHelper.get_default_logger()
                    if use_logger:
                        if logger is None:
                            use_logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败\n详细信息: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
                        else:
                            use_logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败", {'details': error_info})
                    if on_exception:
                        try:
                            on_exception(error_info)
                        except Exception:
                            pass
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        if use_logger:
                            use_logger.info(f"第 {attempt + 1} 次尝试失败，{delay}秒后重试...")
                    else:
                        if use_logger:
                            if logger is None:
                                use_logger.error(f"函数 {func.__name__} 在 {max_retries} 次尝试后仍然失败\n详细信息: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
                            else:
                                use_logger.error(f"函数 {func.__name__} 在 {max_retries} 次尝试后仍然失败", {'details': error_info})
            final_error_info = _ErrorHandlerHelper.build_final_error_info(func, last_exception, max_retries)
            final_error_info = _ErrorHandlerHelper.filter_fields(final_error_info, log_fields)
            if use_logger:
                if logger is None:
                    use_logger.error(f"最终执行失败\n详细信息: {json.dumps(final_error_info, ensure_ascii=False, indent=2)}")
                else:
                    use_logger.error("最终执行失败", {'details': final_error_info})
            if on_exception:
                try:
                    on_exception(final_error_info)
                except Exception:
                    pass
            return default_return
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            import time
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_info = {
                        '函数': func.__name__,
                        '重试': attempt + 1,
                        '最大重试': max_retries,
                        '类型': type(e).__name__,
                        '消息': str(e),
                    }
                    error_info = _ErrorHandlerHelper.filter_fields(error_info, log_fields)
                    use_logger = logger if logger is not None else _ErrorHandlerHelper.get_default_logger()
                    if use_logger:
                        if logger is None:
                            use_logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败\n详细信息: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
                        else:
                            use_logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败", {'details': error_info})
                    if on_exception:
                        try:
                            on_exception(error_info)
                        except Exception:
                            pass
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        if use_logger:
                            use_logger.info(f"第 {attempt + 1} 次尝试失败，{delay}秒后重试...")
                    else:
                        if use_logger:
                            if logger is None:
                                use_logger.error(f"函数 {func.__name__} 在 {max_retries} 次尝试后仍然失败\n详细信息: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
                            else:
                                use_logger.error(f"函数 {func.__name__} 在 {max_retries} 次尝试后仍然失败", {'details': error_info})
            final_error_info = _ErrorHandlerHelper.build_final_error_info(func, last_exception, max_retries)
            final_error_info = _ErrorHandlerHelper.filter_fields(final_error_info, log_fields)
            if use_logger:
                if logger is None:
                    use_logger.error(f"最终执行失败\n详细信息: {json.dumps(final_error_info, ensure_ascii=False, indent=2)}")
                else:
                    use_logger.error("最终执行失败", {'details': final_error_info})
            if on_exception:
                try:
                    on_exception(final_error_info)
                except Exception:
                    pass
            return default_return
        return async_wrapper if is_async else sync_wrapper
    return decorator


if __name__ == "__main__":
    @log_on_exception(logger=None)
    def divide_numbers(a, b):
        """测试函数：除法运算"""
        return a / b

    result1 = divide_numbers(10, 0)
   