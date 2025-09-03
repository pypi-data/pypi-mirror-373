import threading


# Based on tornado.ioloop.IOLoop.instance() approach.
# See https://github.com/facebook/tornado
class SingletonMixin():
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls(*args, **kwargs)
        return cls.__singleton_instance
