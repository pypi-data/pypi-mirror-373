import functools
import logging
import typing
from threading import Thread
from typing import ParamSpec, Union, List

import anyio.to_thread

P = ParamSpec("P")
T = typing.TypeVar("T")
from multiprocessing.pool import ThreadPool


def concurrent_execute(
    fn, data: Union[List[dict], List[str], List[tuple], List[list]], work_num=4
):
    def process_item(item):
        if isinstance(item, dict):
            return fn(**item)
        elif isinstance(item, tuple):
            return fn(*item)
        elif isinstance(item, list):
            return fn(*item)
        elif isinstance(item, (str, int, float, bool)):
            return fn(item)
        else:
            raise ValueError(f"Unsupported data type: {type(item)}")

    logging.debug(
        f"thread concurrent_execute,work_num:{work_num} fn:{fn.__name__} data: {repr(data)}"
    )

    with ThreadPool(work_num) as pool:
        results = pool.map(process_item, data)

    return results


def run_in_thread(fn):
    """
    @run_in_thread
    def test(abc):
        return abc

    test(123)
    """

    def wrapper(*k, **kw):
        t = Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t

    return wrapper


async def make_async(
    func: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    """
    Use it like this:

    ```Python
    def do_work(arg1, arg2, kwarg1="", kwarg2="") -> str:
            # Do work
            return "Some result"

    result = await make_async(do_work, "spam", "ham", kwarg1="a", kwarg2="b")
    print(result)
    ```

    """
    if kwargs:  # pragma: no cover
        # run_sync doesn't accept 'kwargs', so bind them in here
        func = functools.partial(func, **kwargs)
    return await anyio.to_thread.run_sync(func, *args)
