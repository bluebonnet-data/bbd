import threading
from collections.abc import Callable
from queue import Queue, Empty
from typing import NamedTuple, Any


class QueueItem(NamedTuple):
    func: Callable
    arg: Any


class ThreadPool:
    def __init__(self, num_threads: int):
        self.input: Queue[QueueItem] = Queue()
        self.output = Queue()
        self.running = True
        self.input_count = 0
        self.processing_count = 0
        self.output_count = 0
        self.count_lock = threading.Lock()

        self.threads = [threading.Thread(target=self.consumer) for _ in range(num_threads)]
        for t in self.threads:
            t.start()

    def __repr__(self):
        return f'ThreadPool(input_count={self.input_count}, processing_count={self.processing_count}, output_count={self.output_count})'

    def __len__(self):
        with self.count_lock:
            return self.input_count + self.processing_count + self.output_count

    def __iter__(self):
        while len(self) > 0 and self.running:
            try:
                out = self.output.get(block=True, timeout=1)
                self.output.task_done()
                with self.count_lock:
                    self.output_count -= 1
                yield out
            except Empty:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()

    def join(self):
        self.input.join()
        self.running = False
        for t in self.threads:
            t.join()

    def add_item(self, func, arg):
        self.input.put(QueueItem(func, arg))
        with self.count_lock:
            self.input_count += 1

    def get_item(self):
        out = self.output.get()
        self.output.task_done()
        with self.count_lock:
            self.output_count -= 1
        return out

    def consumer(self):
        while self.running:
            try:
                item = self.input.get(block=True, timeout=1)
                with self.count_lock:
                    self.input_count -= 1
                    self.processing_count += 1
                self.output.put(item.func(item.arg))
                self.input.task_done()
                with self.count_lock:
                    self.processing_count -= 1
                    self.output_count += 1
            except Empty:
                pass
