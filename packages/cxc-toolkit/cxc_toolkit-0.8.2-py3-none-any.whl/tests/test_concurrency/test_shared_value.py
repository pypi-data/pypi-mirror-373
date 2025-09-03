# coding=utf-8
import time
import logging
import multiprocessing

from cxc_toolkit.concurrency.shared_value import Value


logger = logging.getLogger(__name__)


class TestValue(object):

    def test_base(self):
        value = Value(filename='test.value')
        words = [
            'hello, world!',
            'Emmm, I feel confused',
            '我能吞下玻璃且伤害身体',
        ]

        def set_worker():
            for w in words:
                value.set(w)
                time.sleep(1)

        def get_worker():
            for i in range(len(words)):
                w = value.get()
                logger.info('Word: {}'.format(w))
                assert w == words[i]
                time.sleep(1)

        set_process = multiprocessing.Process(target=set_worker)
        get_process = multiprocessing.Process(target=get_worker)
        set_process.start()
        get_process.start()
        set_process.join()
        get_process.join()
