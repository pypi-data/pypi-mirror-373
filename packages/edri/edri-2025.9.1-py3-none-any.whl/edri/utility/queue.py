from datetime import time
from queue import Queue as OriginalQueue, Full


class Queue[T](OriginalQueue[T]):
    """
    A subclass of `queue.Queue` that allows inserting items at the front of the queue.

    This class extends Python's built-in `queue.Queue` by adding an `unget` method, which enables
    placing items at the head of the queue. This is useful in scenarios where certain items
    need to be reprocessed or reprioritized.
    :Type Parameters:
        T: Type variable representing the type of items in the queue.
    """

    def unget(
        self, item: T, block: bool = True, timeout: int | None = None
    ) -> None:
        """
        Insert an item at the front of the queue.

        If the queue has a maximum size and is full, the method behaves based on the `block`
        and `timeout` parameters:

        - **Blocking Behavior:**
          - If `block` is `True` and `timeout` is `None` (default), block until a free slot
            becomes available.
          - If `block` is `True` and `timeout` is a non-negative number, block for at most
            `timeout` seconds before raising a `Full` exception if no slot becomes available.
          - If `block` is `False`, attempt to insert the item without blocking. If the queue is
            full, immediately raise a `Full` exception. The `timeout` parameter is ignored in this case.

        :param item: The item to insert at the front of the queue.
        :type item: T
        :param block: Whether to block if the queue is full. Defaults to `True`.
        :type block: bool, optional
        :param timeout: The maximum time to block (in seconds) if `block` is `True`.
                        Ignored if `block` is `False`. Defaults to `None`.
        :type timeout: int or None, optional
        :raises Full: If the queue is full and the item cannot be inserted within the specified
                      blocking behavior.

        :Examples:

            >>> from queue import Full
            >>> q = Queue[int](maxsize=2)
            >>> q.unget(1)
            >>> q.unget(2)
            >>> q.unget(3, block=False)
            Traceback (most recent call last):
                ...
            Full

            >>> q.unget(3, block=True, timeout=5)  # Blocks up to 5 seconds
            >>> q.get()
            1
            >>> q.unget(3)
            >>> q.get()
            3
        """
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._unget(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def _unget(self, item: T) -> None:
        """
        Insert an item at the front of the queue without blocking or checking for fullness.

        This is an internal method used by `unget` to place an item at the head of the queue.

        :param item: The item to insert at the front of the queue.
        :type item: T
        """
        self.queue.appendleft(item)
