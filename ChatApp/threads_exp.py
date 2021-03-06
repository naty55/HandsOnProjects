import random
import threading
from time import sleep
import logging
import concurrent.futures
from threading import Thread, Lock

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


SENTINEL = object()


def producer(pipeline):
    """Pretend we're getting a message from the network."""
    for index in range(10):
        message = random.randint(1, 101)
        logging.info("Producer got message: %s", message)
        pipeline.set_message(message, "Producer")

    # Send a sentinel message to tell consumer we're done
    pipeline.set_message(SENTINEL, "Producer")


def consumer(pipeline):
    """Pretend we're saving a number in the database."""
    message = 0
    while message is not SENTINEL:
        message = pipeline.get_message("Consumer")
        if message is not SENTINEL:
            logging.info("Consumer storing message: %s", message)


class Pipeline:
    """
    Class to allow a single element pipeline between producer and consumer.
    """
    def __init__(self):
        self.message = 0
        self.producer_lock = threading.Lock()
        self.consumer_lock = threading.Lock()
        self.consumer_lock.acquire()

    def get_message(self, name):
        #logging.debug("%s:about to acquire getlock", name)
        self.consumer_lock.acquire()
        #logging.debug("%s:have getlock", name)
        message = self.message
        #logging.debug("%s:about to release setlock", name)
        self.producer_lock.release()
        #logging.debug("%s:setlock released", name)
        return message

    def set_message(self, message, name):
        #logging.debug("%s:about to acquire setlock", name)
        self.producer_lock.acquire()
        #logging.debug("%s:have setlock", name)
        self.message = message
        #logging.debug("%s:about to release getlock", name)
        self.consumer_lock.release()
        #logging.debug("%s:getlock released", name)

def append(val, o):
    sleep(random.random() * 10)
    o.append(val)



if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)
    a = []
    for i in range(10):
        Thread(target=append, args=(i, a)).start()
    sleep(5 * 10)
    print(a)


"""
    pipeline = Pipeline()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer, pipeline)
        executor.submit(consumer, pipeline)
"""