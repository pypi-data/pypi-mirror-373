import asyncio


class AsyncBridge:
    """
    Utility to run async functions from synchronous code.
    """

    @staticmethod
    def run_async(coro):
        """
        Run an async coroutine from sync context.

        Example:
            async def task(x): return x * 2
            result = AsyncBridge.run_async(task(5))
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            return asyncio.ensure_future(coro)
        else:
            return loop.run_until_complete(coro)
