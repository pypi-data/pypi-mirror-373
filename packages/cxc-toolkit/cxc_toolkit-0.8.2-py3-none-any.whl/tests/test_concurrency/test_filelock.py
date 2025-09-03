# coding=utf-8
import os
import errno

from cxc_toolkit.concurrency.filelock import FileLock


class TestBase(object):
    # The path to the lockfile.
    LOCK_PATH = "test.lock"

    def setUp(self):
        """Deletes the potential lock file at :attr:`LOCK_PATH`"""
        self.delete_if_exists(self.LOCK_PATH)

    def tearDown(self):
        """Deletes the potential lock file at :attr:`LOCK_PATH`"""
        self.delete_if_exists(self.LOCK_PATH)

    @staticmethod
    def delete_if_exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            # File not found
            if e.errno != errno.ENOENT:
                raise

    def test_simple(self):
        """
        Asserts that the lock is locked in a context statement and that the
        return value of the *__enter__* is the lock.
        """
        lock = FileLock(self.LOCK_PATH)

        with lock as inner_lock:
            assert lock.is_locked is True
            assert lock is inner_lock
        assert lock.is_locked is False

    def test_process(self):
        """
        Runs 250 processes, which need the filelock. The lock must be acquired
        if at least one thread required it and released, as soon as all threads
        stopped.
        """
        lock = FileLock(self.LOCK_PATH)

        def simple_process():
            for i in range(10):
                with lock:
                    assert lock.is_locked is True

        num_processes = 250

        import multiprocessing
        processes = [multiprocessing.Process(target=simple_process) for i in range(num_processes)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

        assert lock.is_locked is False
