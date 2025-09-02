"""Timing decorator"""

import asyncio
import logging
import os
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, overload

T = TypeVar('T')
P = ParamSpec('P')

log = logging.getLogger(__name__)

SHOULD_DISPLAY = os.environ.get('LAYRZ_SDK_DISPLAY_TIMING', '1') == '1'


@overload
def func_timing(func: Callable[P, T]) -> Callable[P, T]: ...


@overload
def func_timing(*, depth: int) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


def func_timing(
  func: Callable[P, T] | None = None,
  *,
  depth: int = 0,
) -> Any:
  """
  Decorator to time a function execution.

  :param depth: The depth of the function call for logging indentation.
  :return: The wrapped function with timing functionality.
  """

  def decorator(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to time a function"""
    import time

    prefix = '\t' * depth

    @wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
      start_time = time.perf_counter_ns()
      result: T = await func(*args, **kwargs)  # type: ignore
      diff = time.perf_counter_ns() - start_time

      if SHOULD_DISPLAY:
        log.info(f'{prefix}{func.__name__}() took {_readable_time(diff)}')

      return result

    @wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
      start_time = time.perf_counter_ns()
      result = func(*args, **kwargs)
      diff = time.perf_counter_ns() - start_time

      if SHOULD_DISPLAY:
        log.info(f'{prefix}{func.__name__}() took {_readable_time(diff)}')

      return result

    if asyncio.iscoroutinefunction(func):
      return async_wrapper  # type: ignore
    return sync_wrapper

  if func is None:
    return decorator
  return decorator(func)


def _readable_time(diff: int) -> str:
  """Convert nanoseconds to a readable format"""
  if diff < 1_000:
    return f'{diff} ns'

  diff = diff // 1_000
  if diff < 1_000:
    return f'{diff} μs'

  diff = diff // 1_000
  if diff < 1_000:
    return f'{diff} ms'

  diff = diff // 1_000
  if diff < 60:
    return f'{diff} s'

  diff = diff // 60
  if diff < 60:
    return f'{diff} m'

  return f'{diff // 60} h'
