import math
import os
import threading
from multiprocessing import Pool


class RunnerProcess:
    def __init__(self, fun, data):
        self.queue_lock = threading.Lock()
        self.data = data
        self.fun = fun

    def thread_fun(self):
        while True:
            self.queue_lock.acquire()
            if len(self.data) == 0:
                self.queue_lock.release()
                break
            cur_data = self.data.pop()
            self.queue_lock.release()
            self.fun(cur_data)

    def get_threads(self, thread_per_process=4, start=False):
        threads = []
        for i in range(thread_per_process):
            thread = threading.Thread(target=self.thread_fun)
            if start:
                thread.start()
            threads.append(thread)
        return threads


class ConcurrencyRunner:
    def __init__(self, fun, data, thread_per_process=4, process_num=os.cpu_count()):  # 不保证顺序
        #  TODO: data too short
        self.fun = fun
        self.data = data
        self.thread_per_process = thread_per_process
        total_num = len(data)
        self.process_num = process_num
        block_size = math.floor(total_num / self.process_num)
        self.split_data = []
        self.thread_data = []
        # 为多进程做数据准备

        for i in range(self.process_num):
            self.split_data.append(data[i * block_size: ((i + 1) * block_size)])

    def process_fun(self, data):
        running = RunnerProcess(self.fun, data)
        threads = running.get_threads(thread_per_process=self.thread_per_process, start=True)
        for thread in threads:
            thread.join()

    def run(self):
        if self.process_num == 1:
            self.process_fun(self.split_data[0])
        else:
            pool = Pool(processes=self.process_num)
            pool.map(self.process_fun, self.split_data)


if __name__ == '__main__':
    def test_fun(x):
        print(x)
        return x


    runner = ConcurrencyRunner(test_fun, list(range(100)))
    runner.run()
    print("done")
