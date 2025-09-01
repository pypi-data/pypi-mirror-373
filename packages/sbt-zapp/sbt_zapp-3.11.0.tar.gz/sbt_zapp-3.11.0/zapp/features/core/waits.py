import logging
from datetime import timedelta
from typing import Callable, Any, TypeVar, Tuple
from tenacity import (
    Retrying,
    wait_fixed,
    stop_after_delay,
    TryAgain,
    RetryError,
    retry_if_not_exception_type,
)

log = logging.getLogger(__name__)

T = TypeVar("T")


def wait_for(
    action_name: str,
    func: Callable[..., Tuple[bool, T]],
    delay: int,
    wait: float,
    ignore_exceptions: Tuple[Exception] = None,
    *args: Any,
    **kwargs: Any,
) -> tuple[bool, T]:
    """
    Ожидает успешного выполнения условия, проверяемого переданной функцией, с повторными попытками.
    https://tenacity.readthedocs.io/en/latest/#retrying-code-block

    Метод выполняет переданную функцию `func` до тех пор, пока она не вернёт True в качестве первого элемента кортежа,
    либо пока не истечёт отведённое время ожидания. Повторные попытки осуществляются с фиксированным интервалом.
    Поддерживает игнорирование определённых типов исключений с последующим повтором.

    Args:
        action_name (str): Название действия для логирования и отчётов (например, "ожидание появления элемента").
        func (Callable[[T, P], Tuple[bool, T]]): Функция, которая будет вызываться на каждой попытке.
            Должна принимать предыдущий результат и возвращать кортеж из bool (условие выполнено?) и результата.
        delay (int): Максимальное время ожидания в секундах.
        wait (float): Интервал между попытками в секундах.
        ignore_exceptions (Tuple[Exception], optional): Кортеж типов исключений, которые следует игнорировать
            и продолжать попытки при их возникновении. По умолчанию — None.
        *args (Any): Позиционные аргументы для передачи в `func`.
        **kwargs (Any): Именованные аргументы для передачи в `func`.

    Returns:
        Tuple[bool, T]:
            - bool: True, если условие было выполнено в течение времени ожидания, иначе False.
            - T: Последний полученный результат выполнения `func`.

    Raises:
        AssertionError: Если во время выполнения произошло непредвиденное исключение,
            не входящее в список игнорируемых.
    """
    result = None
    try:
        for attempt in Retrying(
            stop=stop_after_delay(delay),
            retry=retry_if_not_exception_type(BaseException),
            wait=wait_fixed(timedelta(seconds=wait)),
            reraise=True,
        ):
            with attempt:
                try:
                    is_satisfied, result = func(result, *args, **kwargs)
                    if not is_satisfied:
                        raise TryAgain
                except BaseException as ex:
                    if ignore_exceptions and isinstance(ex, ignore_exceptions):
                        raise TryAgain
                    else:
                        raise
    except (RetryError, TryAgain):
        return False, result
    except BaseException as ex:
        message = f'Исключение при "{action_name}" -> {type(ex).__name__}: {ex}'
        error = AssertionError(message)
        log.exception(error)
        raise error from ex
    return True, result
