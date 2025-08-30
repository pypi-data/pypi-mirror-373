import asyncio
from typing import Optional

class EventLoopManager:
    """
    Singleton managing the global event loop for FletX applications.
    Ensures all components use the same event loop.
    """
    _instance = None
    _loop: Optional[asyncio.AbstractEventLoop] = None
    _loop_owner: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Get the global event loop, creating it if necessary"""

        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            self._loop_owner = True
            asyncio.set_event_loop(self._loop)
        return self._loop

    def set_loop(
        self, 
        loop: asyncio.AbstractEventLoop, 
        owner: bool = False
    ):
        """Set an existing event loop as the global loop"""

        if self._loop is not None and self._loop_owner and not self._loop.is_closed():
            self._loop.close()
        
        self._loop = loop
        self._loop_owner = owner
        asyncio.set_event_loop(loop)

    def close_loop(self):
        """Close the loop if we're the owner"""

        if self._loop_owner and self._loop is not None and not self._loop.is_closed():
            self._loop.close()
            self._loop = None
            self._loop_owner = False

    def run_until_complete(self, coro):
        """Run coroutine in the global loop"""

        return self.loop.run_until_complete(coro)

    def run_forever(self):
        """Run the loop forever"""

        self.loop.run_forever()

    def stop_loop(self):
        """Stop the running loop"""
        
        if self._loop is not None and not self._loop.is_closed():
            self._loop.stop()