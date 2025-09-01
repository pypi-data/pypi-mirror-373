from enum import Enum
import time


class State(Enum):
    PAUSE = 'pause'
    STOP = 'stop'
    START = 'start'


s = State.START

print(s != State.PAUSE)

n = 0
while 1:
    n = n + 1
    print('aaa', n)
    time.sleep(1)
    while True:
        print('bb', n)
        time.sleep(1)
        print('ccc', n)
        time.sleep(1)
        continue
        print('eeee')
        time.sleep(1)
    print('ddd', n)
    time.sleep(1)
