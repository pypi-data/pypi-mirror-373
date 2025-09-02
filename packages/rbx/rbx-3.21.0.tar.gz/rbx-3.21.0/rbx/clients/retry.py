"""Helpers for retrying functions with exponential back-off.

The `Retry` decorator can be used to retry functions that raise exceptions using exponential
backoff. The retry is limited by a `deadline`. The deadline is the maxmimum amount of time a
method can block.

This decorator will retry transient exceptions.

>>> @retry.Retry()
>>> def call_method():
>>>     return client.method()
"""

import functools
import logging
import random
import time

import arrow

from .. import exceptions

logger = logging.getLogger(__name__)

_DEFAULT_INITIAL_DELAY = 1.0  # seconds
_DEFAULT_MAXIMUM_DELAY = 60.0  # seconds
_DEFAULT_DELAY_MULTIPLIER = 2.0
_DEFAULT_DEADLINE = 60.0 * 2.0  # seconds


def if_exception_type(*exception_types):
    """Creates a predicate to check if the exception is of a given type.

    Parameters:
        exception_types (Sequence[Exception]):
            The exception types to check for.
    Returns:
        Callable[Exception]:
            A predicate that returns True if the provided exception is of the given type(s).
    """

    def if_exception_type_predicate(exception):
        """Bound predicate for checking an exception type."""
        return isinstance(exception, exception_types)

    return if_exception_type_predicate


"""A predicate that checks if an exception is a transient error.

The following server errors are considered transient:
- rbx.exceptions.RequestTimeout
- rbx.exceptions.ServerError
- rbx.exceptions.TooManyRequests
- rbx.exceptions.TransientException
"""
if_transient_error = if_exception_type(
    exceptions.RequestTimeout,
    exceptions.ServerError,
    exceptions.TooManyRequests,
    exceptions.TransientException,
)


def exponential_sleep_generator(initial, maximum, multiplier=_DEFAULT_DELAY_MULTIPLIER):
    """Generates sleep intervals based on the exponential back-off algorithm.

    This implements the `Truncated Exponential Back-off`_ algorithm:
    https://en.wikipedia.org/wiki/Exponential_backoff

    Parameters:
        initial (float):
            The minimum amount of time to delay. This must be greater than 0.
        maximum (float):
            The maximum amount of time to delay.
        multiplier (float):
            The multiplier applied to the delay.

    Yields:
        float: successive sleep intervals.
    """
    delay = initial
    while True:
        # Introduce jitter by yielding a delay that is uniformly distributed
        # to average out to the delay time.
        yield min(random.uniform(0.0, delay * 2.0), maximum)
        delay = delay * multiplier


def retry_target(target, predicate, sleep_generator, deadline, on_error=None):
    """Call a function and retry if it fails.

    This is the lowest-level retry helper. Generally, you'll use the
    higher-level retry helper :class:`Retry`.

    Parameters:
        target(Callable):
            The function to call and retry.
        predicate (Callable[Exception]):
            A callable used to determine if an exception raised by the target should be considered
            retryable. It should return True to retry or False otherwise.
        sleep_generator (Iterable[float]):
            An infinite iterator that determines how long to sleep between retries.
        deadline (float):
            How long to keep retrying the target. The last sleep period is shortened as necessary,
            so that the last retry runs at ``deadline`` (and not considerably beyond it).
        on_error (Callable[Exception]):
            A function to call while processing a retryable exception. Any error raised by this
            function will *not* be caught.

    Returns:
        Any: the return value of the target function.

    Raises:
        rbx.exceptions.RetryError: If the deadline is exceeded while retrying.
        ValueError: If the sleep generator stops yielding values.
        Exception: If the target raises a method that isn't retryable.
    """
    if deadline is not None:
        deadline_datetime = arrow.utcnow().shift(seconds=deadline).datetime
    else:
        deadline_datetime = None

    last_exc = None

    for sleep in sleep_generator:
        try:
            return target()

        # pylint: disable=broad-except
        # This function explicitly must deal with broad exceptions.
        except Exception as exc:
            if not predicate(exc):
                raise
            last_exc = exc
            if on_error is not None:
                on_error(exc)

        now = arrow.utcnow().datetime

        if deadline_datetime is not None:
            if deadline_datetime <= now:
                raise exceptions.RetryError(
                    f"Deadline of {deadline:.1f}s exceeded while calling {target}",
                    last_exc,
                ) from last_exc
            else:
                time_to_deadline = (deadline_datetime - now).total_seconds()
                sleep = min(time_to_deadline, sleep)

        logger.debug(f"Retrying due to {last_exc}, sleeping {sleep:.1f}s ...")
        time.sleep(sleep)

    raise ValueError("Sleep generator stopped yielding sleep values.")


class Retry:
    """Exponential retry decorator.

    This class is a decorator used to add exponential back-off retry behavior.

    Parameters:
        predicate (Callable[Exception]):
            A callable that should return ``True`` if the given exception is retryable.
        initial (float):
            The minimum a,out of time to delay in seconds. This must be greater than 0.
        maximum (float):
            The maximum amout of time to delay in seconds.
        multiplier (float):
            The multiplier applied to the delay.
        deadline (float):
            How long to keep retrying in seconds. The last sleep period is shortened as necessary,
            so that the last retry runs at ``deadline`` (and not considerably beyond it).
    """

    def __init__(
        self,
        predicate=if_transient_error,
        initial=_DEFAULT_INITIAL_DELAY,
        maximum=_DEFAULT_MAXIMUM_DELAY,
        multiplier=_DEFAULT_DELAY_MULTIPLIER,
        deadline=_DEFAULT_DEADLINE,
        on_error=None,
    ):
        self._predicate = predicate
        self._initial = initial
        self._multiplier = multiplier
        self._maximum = maximum
        self._deadline = deadline
        self._on_error = on_error

    def __call__(self, func, on_error=None):
        """Wrap a callable with retry behavior.

        Parameters:
            func (Callable): The callable to add retry behavior to.
            on_error (Callable[Exception]): A function to call while processing
                a retryable exception. Any error raised by this function will
                *not* be caught.

        Returns:
            Callable: A callable that will invoke ``func`` with retry
                behavior.
        """
        if self._on_error is not None:
            on_error = self._on_error

        @functools.wraps(func)
        def retry_wrapped_func(*args, **kwargs):
            """A wrapper that calls target function with retry."""
            target = functools.partial(func, *args, **kwargs)
            sleep_generator = exponential_sleep_generator(
                self._initial, self._maximum, multiplier=self._multiplier
            )
            return retry_target(
                target,
                self._predicate,
                sleep_generator,
                self._deadline,
                on_error=on_error,
            )

        return retry_wrapped_func

    @property
    def deadline(self):
        return self._deadline

    def __str__(self):
        return (
            "<Retry predicate={}, initial={:.1f}, maximum={:.1f}, "
            "multiplier={:.1f}, deadline={:.1f}, on_error={}>".format(
                self._predicate,
                self._initial,
                self._maximum,
                self._multiplier,
                self._deadline,
                self._on_error,
            )
        )
