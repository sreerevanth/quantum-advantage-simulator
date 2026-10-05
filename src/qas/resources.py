"""Sample process RSS without instrumenting each Python allocation."""

import threading

import psutil


class MemorySampler:
    def __enter__(self):
        self.process = psutil.Process()
        self.start = self.peak = self.process.memory_info().rss
        self.stop = threading.Event()

        def sample():
            while not self.stop.wait(0.01):
                self.peak = max(self.peak, self.process.memory_info().rss)

        self.thread = threading.Thread(target=sample, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.peak = max(self.peak, self.process.memory_info().rss)
        self.stop.set()
        self.thread.join()
