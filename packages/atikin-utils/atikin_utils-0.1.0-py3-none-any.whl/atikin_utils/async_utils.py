import asyncio


async def run_async(func, *args, **kwargs):
    """Run a function (sync or async) in async context."""
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)
