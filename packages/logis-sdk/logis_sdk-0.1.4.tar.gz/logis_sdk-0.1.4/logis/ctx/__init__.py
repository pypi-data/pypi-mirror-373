import asyncio
from collections import defaultdict
from contextvars import ContextVar
from numbers import Number
from typing import Any, List


class Context:
    """
    上下文,按照协程隔离
    """

    # _thread_local = threading.local()
    _context_vars_ = ContextVar("__logis_context_vars__", default=None)

    @classmethod
    def errors(cls) -> List[Any]:
        return cls.get("errors", [], create=True)

    @classmethod
    def _is_in_asyncio(cls):
        try:
            task = asyncio.current_task(asyncio.get_running_loop())
            return task is not None
        except Exception as e:
            return False

    @classmethod
    def init(cls, v={}):
        if cls._context_vars_.get() is None:
            cls._context_vars_.set(v)

    @classmethod
    def set(cls, key, value):
        cls.init()
        cls._context_vars_.get()[key] = value

        # setattr(cls._thread_local, key, value)

    @classmethod
    def get(cls, key, default=None, create=False):
        dc = cls.get_all()
        result = default if dc is None else dc.get(key, default)
        if create:
            cls.set(key, result)
        # return getattr(cls._thread_local, key, None)
        return result

    @classmethod
    def get_all(cls) -> dict | None:
        return cls._context_vars_.get()

    @classmethod
    def reset(cls):
        """
        清除上下文
        """
        if dc := cls.get_all():
            dc.clear()
        cls._context_vars_.set(None)
        # cls._thread_local.__dict__.clear()

    @classmethod
    def count(cls, name: str, value: Number, override=False):
        """
        计数
        Args:
            name: 待统计量
            value: 值
            override: 是否直接覆盖旧值
        """
        k = "__logis_counter__"
        if k not in cls.get_all():
            cls.set(k, defaultdict(float))
        if override:
            cls.get(k)[name] = value
        else:
            cls.get(k)[name] += value

    @classmethod
    def start_timing_if_not(cls, key: str, now: float) -> bool:
        """
        如果还没有开始计时就从现在开始计时

        Args:
            key: 时长键
            now: 当前时间

        Returns:
            bool: 是否是首次开始计时
        """
        dx = cls.duration(key, now, update_end_time=False)
        return dx is None

    @classmethod
    def stop_timing(cls, key: str, now: float):
        dx = cls.duration(key, now, update_end_time=True)
        assert dx is not None, f"请先开始计时:{key}"

        return dx

    @classmethod
    def duration(cls, key: str, now: float = 0, update_end_time=False) -> float | None:
        """
        计算时长
        Args:
            key: 时长键
            now: 当前时间
            update_end_time: 是否更新结束时间

        Returns:
            float | None: 时长,如果是首次开始计时则返回None
        """
        k = "__logis_duration__"
        obj = cls.get(k, default={}, create=True)
        first_time = False
        if key not in obj:
            obj[key] = [now, None]
            first_time = True
        if update_end_time:
            obj[key][1] = now
        return None if first_time else now - obj[key][0]
