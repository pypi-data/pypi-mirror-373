import contextlib
from functools import lru_cache


class Test:
    # def __init__(self):
    #     self._env = None

    # @cached_property
    @property
    @lru_cache()
    def env(self):
        def gen():
            print('1. before value')
            yield 'value'
            print('3. after value')

        self._env = gen()
        return next(self._env)

    def __del__(self):
        env_gen = getattr(self, '_env', None)
        if env_gen:
            next(env_gen, True)


# t = Test()
# print(t.env)
# print('2. payload')
# print(t.env)

@contextlib.contextmanager
def context():
    yield 'data'
    print('exit')


@contextlib.contextmanager
def fin_context():
    try:
        yield 'fin data'
    finally:
        print('exit')


class ClassContext:
    def __enter__(self):
        return 'class data'

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('exit')


class TestWith:
    @property
    @lru_cache()
    def env(self):
        # with ClassContext() as data:
        #     return data

        def gen():
            with ClassContext() as data:
            # with context() as data:
            # with fin_context() as data:
                yield data

        # self.g = gen()
        # return next(self.g)
        # return next(gen())
        for g in gen():
            return g


    def payload(self):
        print(self.env)
        print('payload')


test = TestWith()
test.payload()
print('payload 2')
