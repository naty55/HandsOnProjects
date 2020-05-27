import threading
from time import sleep
import logging
import concurrent.futures


def thread_func(name):
    logging.info("Thread %s started", name)
    sleep(2)
    logging.info("Thread %s Finished", name)


class FakeDB:
    def __init__(self):
        self.value = 0
        self._lock = threading.RLock()

    def update(self, name):
        logging.info("Thread %s: is starting update ", name)
        local_copy = self.value
        local_copy += 1
        sleep(0.1)
        self.value = local_copy
        logging.info("Thread %s: is finishing update ", name)

    def locked_update(self, name):
        logging.info("Thread %s is starting update", name)
        logging.debug("Thread %s is about to lock", name)
        with self._lock:
            logging.debug("Thread %s has lock", name)
            local_copy = self.value
            local_copy += 1
            sleep(0.1)
            self.value = local_copy
            logging.debug("Thread %s is about to release ", name)
        logging.debug("Thread %s after release", name)
        logging.info("Thread %s is finished update", name)


if __name__ == '__main__':
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Main    : starting threads")
    database = FakeDB()
    logging.info("Testing Update starting value is %d", database.value)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for i in range(2):
            executor.submit(database.locked_update, i)

    logging.info("Testing Update ending value is %d", database.value)
