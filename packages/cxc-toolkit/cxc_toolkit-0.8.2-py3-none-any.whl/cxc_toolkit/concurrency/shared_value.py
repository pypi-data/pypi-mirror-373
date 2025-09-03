# coding=utf-8
from cxc_toolkit.concurrency.filelock import FileLock


class Value(object):

    def __init__(self, filename='ipc.value', lock_name='ipc.lock'):
        self.filename = filename
        self.lock = FileLock(lock_name)

    def set(self, value):
        with self.lock:
            with open(self.filename, 'w+') as f:
                f.write(value)

    def get(self):
        with self.lock:
            with open(self.filename, 'r') as f:
                return f.read()
