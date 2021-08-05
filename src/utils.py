async def async_wrapper(callback):
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, callback)