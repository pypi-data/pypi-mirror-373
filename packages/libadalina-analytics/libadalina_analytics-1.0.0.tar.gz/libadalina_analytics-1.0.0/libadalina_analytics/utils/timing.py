import time

class Timing:

    def __init__(self, message: str = 'Running time {.1:f}'):
        self.__message = message
        self.__start = None

    def __enter__(self):
        self.__start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.__start
        print(self.__message.format(elapsed))