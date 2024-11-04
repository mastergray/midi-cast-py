# Dependencies
import asyncio  # For managing queues with

class PrioQueue(asyncio.Queue):

    """Extends asyncio queue to include a method for placing messages at front of queue"""

    async def put_front(self, item):
        # Acquire the lock, then insert the item at the front of the queue
        async with self._putters_lock:
            self._queue.appendleft(item)
            self._wakeup_next(self._getters)

    def clear(self):
        """Remove all items from the queue."""
        self._queue.clear()
