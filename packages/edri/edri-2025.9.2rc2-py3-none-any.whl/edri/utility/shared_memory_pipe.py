from inspect import signature
from multiprocessing.shared_memory import SharedMemory
from struct import calcsize, pack, unpack
from typing import Optional, Self
from math import ceil

from posix_ipc import Semaphore, O_CREX

from edri.config.setting import CHUNK_SIZE

_SHM_SUPPORTS_TRACK = "track" in signature(SharedMemory).parameters


class SharedMemoryPipe:
    HEADER_FMT = "I B 3x"  # uint32 size, uint8 eof, 3-byte pad
    HEADER_SIZE = calcsize(HEADER_FMT)

    _ALIGNMENT = 64  # bytes – tune here if you like

    @staticmethod
    def _aligned(n: int, alignment: int = _ALIGNMENT) -> int:
        "Round n up to the next multiple of *alignment*."
        return ((n + alignment - 1) // alignment) * alignment

    @classmethod
    def _compute_slot_size(cls,
                           *,
                           total_size: int | None,
                           max_slots: int,
                           min_slot_size: int) -> int:
        """
        Derive a slot size that fits *total_size* into ≤ *max_slots* slots,
        aligned for cache friendliness, and no smaller than *min_slot_size*.
        """
        if total_size is None:
            return min_slot_size

        # Bytes of **payload** we must be able to carry per slot
        payload_per_slot = ceil(total_size / max_slots)

        # Add header, align, and honour the caller’s minimum
        candidate = cls._aligned(payload_per_slot + cls.HEADER_SIZE)
        return max(min_slot_size, candidate)

    def __init__(self,
                 name: Optional[str] = None,
                 *,
                 max_slots: int = 64,
                 slot_size: int = CHUNK_SIZE,
                 total_size: int | None = None,
                 _closed: bool = False,):
        """
        If *total_size* is given (in bytes) the implementation will pick a
        cache-aligned *slot_size* large enough that the entire data fits into
        at most *max_slots* chunks – saving heap and semaphore traffic.
        """
        self.name = name
        self.max_slots = max_slots
        self.total_size = total_size
        self.slot_size = self._compute_slot_size(total_size=total_size,
                                                 max_slots=max_slots,
                                                 min_slot_size=slot_size)
        self.is_writer = self.name is None
        self._closed = _closed
        self.local_index = 0

        shm_kwargs = {}
        if _SHM_SUPPORTS_TRACK:
            shm_kwargs["track"] = False

        if self._closed:
            return
        if self.is_writer:
            shm_kwargs.update({"create": True, "size": self.slot_size * self.max_slots})
            self.shm = SharedMemory(**shm_kwargs)
            self.name = self.shm.name

            self._items_sem_name = self.shm.name + "_items"
            self._slots_sem_name = self.shm.name + "_slots"
            self.items = Semaphore(self._items_sem_name, flags=O_CREX, initial_value=0)
            self.slots = Semaphore(self._slots_sem_name, flags=O_CREX, initial_value=self.max_slots)
        else:
            shm_kwargs["name"] = self.name
            self._items_sem_name = self.name + "_items"
            self._slots_sem_name = self.name + "_slots"
            self.shm = SharedMemory(**shm_kwargs)
            self.items = Semaphore(self._items_sem_name)
            self.slots = Semaphore(self._slots_sem_name)

    def _write_slot(self, data: bytes, eof: bool):
        self.slots.acquire()

        slot_index = self.local_index % self.max_slots
        offset = slot_index * self.slot_size

        header = pack(self.HEADER_FMT, len(data), int(eof))
        self.shm.buf[offset: offset + self.HEADER_SIZE] = header
        self.shm.buf[offset + self.HEADER_SIZE: offset + self.HEADER_SIZE + len(data)] = data

        self.local_index += 1
        self.items.release()

    def write(self, data: bytes, /, *, close: bool = False):
        max_payload = self.slot_size - self.HEADER_SIZE
        total_chunks = (len(data) + max_payload - 1) // max_payload

        for i in range(total_chunks):
            chunk = data[i * max_payload: (i + 1) * max_payload]
            eof = close and (i == total_chunks - 1)
            self._write_slot(chunk, eof=eof)

    def read(self) -> Optional[bytes]:
        self.items.acquire()

        slot_index = self.local_index % self.max_slots
        offset = slot_index * self.slot_size

        header = self.shm.buf[offset: offset + self.HEADER_SIZE]
        size, eof = unpack(self.HEADER_FMT, header)

        data = bytes(self.shm.buf[offset + self.HEADER_SIZE
                                  : offset + self.HEADER_SIZE + size])
        self.local_index += 1

        self.slots.release()
        return None if eof else data

    def reader(self) -> Self:
        if not self.is_writer:
            raise RuntimeError("Only writer can spawn reader")
        return SharedMemoryPipe(name=self.name,
                                max_slots=self.max_slots,
                                slot_size=self.slot_size,
                                total_size=self.total_size)

    def close(self):
        if self._closed:
            return
        self._closed = True

        if self.is_writer:
            # send EOF downstream
            self._write_slot(b"", eof=True)
            self.shm.close()
        else:
            self.shm.close()
            self.shm.unlink()

        self.shm = None  # guard against accidental reuse

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self) -> Self:
        if self.is_writer:
            raise RuntimeError("Cannot iterate over the writer end of the pipe")
        return self

    def __next__(self) -> bytes:
        if self._closed:
            raise StopIteration

        chunk = self.read()
        if chunk is None:
            self.close()
            raise StopIteration
        return chunk

    def __getstate__(self):
        if self.is_writer:
            raise RuntimeError("Writer cannot be pickled")
        return {
            "name": self.name,
            "max_slots": self.max_slots,
            "slot_size": self.slot_size,
            "total_size": self.total_size,
            "_closed": self._closed,
        }

    def __setstate__(self, state):
        self.__init__(**state)
