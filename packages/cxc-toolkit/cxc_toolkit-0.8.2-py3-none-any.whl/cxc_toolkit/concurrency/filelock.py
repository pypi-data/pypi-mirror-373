# coding=utf-8
# A file lock implements using python, provides a simple way of inter-process
# communication.
import os
import time
import fcntl
import logging
import os.path


logger = logging.getLogger(__name__)


class FileLock(object):

    def __init__(self, lock_file, timeout=5):
        """
        :params lock_file: lock name
        :type lock_file: str
        """
        self._lock_file = lock_file
        self._lock_file_fd = None
        self._timeout = timeout

    @property
    def is_locked(self):
        """
        True, if the object holds the file lock.
        """
        return self._lock_file_fd is not None

    def acquire(self, poll_intervall=0.01):
        start = time.time()
        while True:
            if not self.is_locked:
                logger.debug('Attempting to acquire lock on {}...'.format(self._lock_file))
                open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
                fd = os.open(self._lock_file, open_mode)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except (IOError, OSError):
                    os.close(fd)
                else:
                    self._lock_file_fd = fd

            if self.is_locked:
                logger.info('Lock acquired on {}'.format(self._lock_file))
                break
            elif self._timeout >= 0 and time.time() - start > self._timeout:
                msg = 'Timeout on acquiring lock {}'.format(self._lock_file)
                logger.debug(msg)
                raise OSError(msg)
            else:
                time.sleep(poll_intervall)

    def release(self):
        logger.debug('Going to release lock {}...'.format(self._lock_file))
        fd = self._lock_file_fd
        self._lock_file_fd = None
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
