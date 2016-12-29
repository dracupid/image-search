import logging
import threading


class MultiThreadMapper:
    def __init__(self, fun, data: list):
        self.consume_lock = threading.Lock()
        self.input = data
        self.input_len = len(data)
        self.output = [None] * self.input_len
        self.pos = 0
        self.fun = fun
        self.logger = logging.getLogger("MTM")
        self.logger.setLevel(logging.WARNING)

    def _thread_fun(self, thread_id: int):
        while True:
            with self.consume_lock:
                if self.pos == self.input_len:
                    break
                self.logger.info("Thread %d consume data" % thread_id)
                cur_pos = self.pos
                self.pos += 1

            res = self.fun(self.input[cur_pos])
            self.output[cur_pos] = res

    def create_threads(self, thread_per_process: int = 4, start: bool = False) -> list:
        threads = []
        for i in range(thread_per_process):
            thread = threading.Thread(target=self._thread_fun, args=(i,))
            threads.append(thread)
            if start:
                thread.start()
        return threads

    def run(self, thread_per_process: int = 4) -> list:
        threads = self.create_threads(thread_per_process, True)
        for thread in threads:
            thread.join()
        return self.output
