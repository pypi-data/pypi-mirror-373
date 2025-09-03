import unittest

from cxc_toolkit.patterns.singleton import SingletonMixin


class TestSingleton(unittest.TestCase):

    def test_singleton(self):
        class A(SingletonMixin):
            pass

        class B(SingletonMixin):
            pass

        a, a2 = A.instance(), A.instance()
        b, b2 = B.instance(), B.instance()

        assert a is a2
        assert b is b2
        assert a is not b
