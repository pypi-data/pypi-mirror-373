from threading import Condition, Lock


class DummyStopIteration(Exception):
    pass


def next_without_stop_iteration(iterator):
    try:
        return next(iterator)
    except StopIteration:
        raise DummyStopIteration()


class DisposableEvent:
    def __init__(self):
        self._cond = Condition(Lock())
        self._flag = False

    def __repr__(self):
        cls = self.__class__
        status = "set" if self._flag else "unset"
        return f"<{cls.__module__}.{cls.__qualname__} at {id(self):#x}: {status}>"

    def is_set(self):
        return self._flag

    def set(self):
        with self._cond:
            self._flag = True
            self._cond.notify_all()

    def wait(self, timeout=None):
        with self._cond:
            signaled = self._flag
            if not signaled:
                signaled = self._cond.wait(timeout)
            self._flag = False
            return signaled
