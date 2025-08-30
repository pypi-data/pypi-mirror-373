import functools
import inspect
from types import AsyncGeneratorType

from fishhook import hook


"""
This script implements decorators, yield_to_sync and yield_to_async, which allow you
to leverage yielding in order to implement sync and async versions of API in a DRY-fashion.
This seems better than the existing alternatives that have either maintenance or compute overhead:
    - code duplication (see unasync or https://spwoodcock.dev/blog/2025-02-python-dry-async/)
    - write a sync version, and run it async via a separate thread
    - write an async version, and use asyncio.run

This works by putting a yield anwyhere you would expect to place an await. The yield then delegates the yielded expression to the aforementioned decorators. In the synchronous case, the expression is just left untounched (hence exhaust_by_identity). In the asynchronous case, the expression is yielded to an async function where we can succesfully apply an await if we get a coroutine and return execution back to the yield. This is essentially exactly how an event loop works, so in effect 'yield-based' approach can be seen as a general form of writing functions, which can specialise to either synchronous functions or asynchronous functions via use of the decorator.

For an example use-case, see chaiverse/database/redis_database.py.

Caveats:
    - Can complicate tracebacks/debugging
    - You cannot write functions like

      def foo(bar):
          return yield bar

      as this is invalid syntax in Python. You must assign the yield expression to a variable, and return that, as follows:

      def foo(bar):
        baz = yield bar
        return baz
    - 'async for' loops work using the usual for loop syntax, provided the for
       loop includes the following code:

       from chaiverse.lib.async_tools import YieldStop
       for i in possibly_async_generator():
           i = yield i
           if i == YieldStop; break

        The first line 'i = yield i' makes sense: at some point you must await the result of the generator if it is async. The second line is a bit of hack, and comes from the fact that it seems not possible
        to know whether an async generator has finished yielding until after the fact. This causes an extra value to be yielded to the for loop when exhausting. So we explicitly indicate the loop needs to break.

TODO: To the best of my knowledge, this approach is novel. The package https://github.com/dry-python/returns does something similar using Futures, but it seems messier and less intuitive. We could make this an open-source package.
"""


def is_generator(gen):
    return inspect.isgenerator(gen)


def is_coroutine(coro):
    return inspect.iscoroutine(coro)


class YieldStop:
    pass


@hook(AsyncGeneratorType)
def __iter__(self):
    exhausted = False
    async def advance_async_iterator():
        try:
            out = await anext(self)
        except StopAsyncIteration:
            nonlocal exhausted
            exhausted = True
            out = YieldStop
        return out
    while not exhausted:
        yield advance_async_iterator()



def exhaust_by_identity(gen):
    try:
        out = next(gen)
        while True:
            try:
                out = exhaust_by_identity(out) if is_generator(out) else out
                out = gen.send(out)
            except Exception as ex:
                if isinstance(ex, StopIteration): raise ex
                out = gen.throw(ex)
    except StopIteration as ex:
        out = ex.value
    return out


def yield_to_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        return exhaust_by_identity(gen)
    return wrapper


async def exhaust_by_await(gen):
    try:
        out = next(gen)
        while True:
            try:
                out = await exhaust_by_await(out) if is_generator(out) else out
                out = await out if is_coroutine(out) else out
                out = gen.send(out)
            except Exception as ex:
                if isinstance(ex, StopIteration): raise ex
                out = gen.throw(ex)
    except StopIteration as ex:
        out = ex.value
    return out


def yield_to_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        gen = await func(*args, **kwargs)
        return await exhaust_by_await(gen)
    return wrapper
