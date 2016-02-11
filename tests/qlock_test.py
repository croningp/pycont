# inspired from http://stackoverflow.com/questions/19688550/how-do-i-queue-my-python-locks

import time
import threading

from pycont.qlock import QLock


def test_lock(lock):
    lock.acquire()

    acqorder = []
    threads = []

    def work(name):
        lock.acquire()
        acqorder.append(name)

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for letter in letters:
        thread = threading.Thread(target=work, args=(letter,))
        thread.start()
        threads.append(thread)
        time.sleep(0.1)  # probably enough time for .acquire() to run

    for thread in threads:
        while not lock.locked():
            time.sleep(0)  # yield time slice
        lock.release()

    for thread in threads:
        thread.join()

    assert lock.locked()
    lock.release()
    assert not lock.locked()

    return "".join(acqorder)


print 'With normal lock:'
for i in range(10):
    print test_lock(threading.Lock())


print 'With queued lock:'
for i in range(10):
    print test_lock(QLock())
