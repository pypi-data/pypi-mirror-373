import pickle
import sys
import uuid
import unittest
from multiprocessing import get_context
from os import urandom
from pathlib import Path
from time import sleep

from edri.utility.shared_memory_pipe import SharedMemoryPipe


# --------------------------------------------------------------------------- #
# helpers for multiprocessing (must be top-level for forkserver compatibility)
# --------------------------------------------------------------------------- #


def writer_proc(payloads, name_holder):
    with SharedMemoryPipe() as pipe:
        name_holder[0] = pipe.name
        for p in payloads:
            pipe.write(p)


def read_all(name, result_holder):
    with SharedMemoryPipe(name=name) as pipe:
        buf = bytearray()
        while True:
            chunk = pipe.read()
            if chunk is None:
                break
            buf.extend(chunk)
        result_holder[0] = bytes(buf)


def roundtrip_reader(name, out_list):
    with SharedMemoryPipe(name=name) as pipe:
        while True:
            chunk = pipe.read()
            if chunk is None:
                break
            out_list.append(chunk)


def pickled_reader_reader(conn, result_holder):
    reader_pipe = conn.recv()
    buffer = bytearray()
    while True:
        chunk = reader_pipe.read()
        if chunk is None:
            break
        buffer.extend(chunk)
    reader_pipe.close()
    result_holder[0] = bytes(buffer)


def pickled_reader_writer(conn):
    with SharedMemoryPipe() as pipe:
        conn.send(pipe.reader())
        pipe.write(b'ping')


def unlink_check_reader(name, during_flag, after_flag):
    shm_path = Path('/dev/shm') / name
    with SharedMemoryPipe(name=name) as pipe:
        while pipe.read() is not None:
            pass
        during_flag.value = shm_path.exists()
    sleep(0.2)
    after_flag.value = shm_path.exists()


def slot_wraparound_writer(payloads, name_holder, max_slots, slot_size):
    with SharedMemoryPipe(
        max_slots=max_slots,
        slot_size=slot_size
    ) as pipe:
        name_holder[0] = pipe.name
        for chunk in payloads:
            pipe.write(chunk)
        pipe.close()


def slot_wraparound_reader(name, sink, max_slots, slot_size):
    with SharedMemoryPipe(
        name=name,
        max_slots=max_slots,
        slot_size=slot_size
    ) as pipe:
        while True:
            chunk = pipe.read()
            if chunk is None:
                break
            sink.append(chunk)


# --------------------------------------------------------------------------- #
# test class
# --------------------------------------------------------------------------- #
class TestSharedMemoryPipe(unittest.TestCase):

    def test_small_message(self):
        ctx = get_context("forkserver")
        manager = ctx.Manager()
        name_holder = manager.list([None])
        result = manager.list([None])

        p_writer = ctx.Process(target=writer_proc, args=([b'hello'], name_holder))
        p_writer.start(); p_writer.join()

        shm = name_holder[0]
        p_reader = ctx.Process(target=read_all, args=(shm, result))
        p_reader.start(); p_reader.join()

        self.assertEqual(result[0], b'hello')

    def test_eof_returns_none(self):
        ctx = get_context("forkserver")
        manager = ctx.Manager()
        name_holder = manager.list([None])
        result = manager.list([True])

        p_writer = ctx.Process(target=writer_proc, args=([], name_holder))
        p_writer.start(); p_writer.join()

        shm = name_holder[0]
        p_reader = ctx.Process(target=read_all, args=(shm, result))
        p_reader.start(); p_reader.join()

        self.assertEqual(result[0], b'')

    def test_large_message(self):
        ctx = get_context("forkserver")
        manager = ctx.Manager()
        name_holder = manager.list([None])
        result = manager.list([None])
        data = urandom(500_000)

        p_writer = ctx.Process(target=writer_proc, args=([data], name_holder))
        p_writer.start()
        sleep(0.05)
        shm = name_holder[0]
        p_reader = ctx.Process(target=read_all, args=(shm, result))
        p_reader.start()

        p_writer.join(); p_reader.join()
        self.assertEqual(result[0], data)

    def test_roundtrip_messages(self):
        ctx = get_context("forkserver")
        messages = [f"msg-{i}".encode() for i in range(10)]
        manager = ctx.Manager()
        name_holder = manager.list([None])
        collected = manager.list()

        p_writer = ctx.Process(target=writer_proc, args=(messages, name_holder))
        p_writer.start(); p_writer.join()

        shm = name_holder[0]
        p_reader = ctx.Process(target=roundtrip_reader, args=(shm, collected))
        p_reader.start(); p_reader.join()

        self.assertEqual(collected[:], messages)

    def test_reader_can_be_pickled_and_transferred(self):
        ctx = get_context("forkserver")
        parent, child = ctx.Pipe()
        manager = ctx.Manager()
        out = manager.list([None])

        p_writer = ctx.Process(target=pickled_reader_writer, args=(parent,))
        p_reader = ctx.Process(target=pickled_reader_reader, args=(child, out))
        p_writer.start(); p_reader.start()
        p_writer.join(); p_reader.join()

        self.assertEqual(out[0], b'ping')

    def test_writer_cannot_be_pickled(self):
        with SharedMemoryPipe() as pipe:
            with self.assertRaises(RuntimeError):
                pickle.dumps(pipe)

    def test_context_manager(self):
        with SharedMemoryPipe() as pipe:
            self.assertTrue(pipe.name.startswith('psm_'))

    def test_writer_can_spawn_reader(self):
        with SharedMemoryPipe() as writer:
            reader = writer.reader()
            self.assertIsInstance(reader, SharedMemoryPipe)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'requires /dev/shm')
    def test_shared_memory_unlinked_after_reader_close(self):
        ctx = get_context("forkserver")
        manager = ctx.Manager()
        name_holder = manager.list([None])

        # write in-process
        writer_proc([b'cleanup'], name_holder)

        name = name_holder[0]
        during = manager.Value('b', False)
        after = manager.Value('b', True)

        p = ctx.Process(target=unlink_check_reader, args=(name, during, after))
        p.start(); p.join()

        self.assertTrue(during.value)
        self.assertFalse(after.value)

    def test_slot_index_wraparound(self):
        ctx = get_context("forkserver")
        max_slots, slot_size = 4, 256
        payloads = [f"data-{i}".encode() for i in range(20)]

        manager = ctx.Manager()
        name_holder = manager.list([None])
        seen_holder = manager.list()

        p_writer = ctx.Process(
            target=slot_wraparound_writer,
            args=(payloads, name_holder, max_slots, slot_size)
        )
        p_writer.start()

        while name_holder[0] is None:
            sleep(0.01)

        name = name_holder[0]

        p_reader = ctx.Process(
            target=slot_wraparound_reader,
            args=(name, seen_holder, max_slots, slot_size)
        )
        p_reader.start()

        p_writer.join()
        p_reader.join()

        self.assertEqual(seen_holder[:], payloads)


if __name__ == '__main__':
    unittest.main()
