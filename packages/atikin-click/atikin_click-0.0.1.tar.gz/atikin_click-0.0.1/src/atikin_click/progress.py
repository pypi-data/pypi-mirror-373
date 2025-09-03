"""Simple progress bar and spinner (no extra deps)"""
import sys
import time
import threading
from contextlib import contextmanager

class ProgressBar:
    def __init__(self, total: int, width: int = 40, prefix: str = ""):
        self.total = max(1, total)
        self.width = width
        self.prefix = prefix
        self.current = 0
        self._lock = threading.Lock()
        self._start = time.time()

    def update(self, n=1):
        with self._lock:
            self.current += n
            self._draw()

    def _draw(self):
        frac = self.current / self.total
        filled = int(self.width * frac)
        bar = "[" + "#" * filled + "-" * (self.width - filled) + "]"
        percent = f"{frac * 100:6.2f}%"
        elapsed = time.time() - self._start
        sys.stdout.write(f"\r{self.prefix} {bar} {percent} elapsed:{int(elapsed)}s")
        sys.stdout.flush()
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def __enter__(self):
        self._draw()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.current < self.total:
            self.current = self.total
            self._draw()

class Spinner:
    def __init__(self, text="working"):
        self.text = text
        self._running = False
        self._thread = None
        self._frames = ["|", "/", "-", "\\"]

    def _spin(self):
        i = 0
        while self._running:
            sys.stdout.write(f"\r{self._frames[i % len(self._frames)]} {self.text}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write("\r")
        sys.stdout.flush()

    def __enter__(self):
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._running = False
        if self._thread:
            self._thread.join()
        # clear line after finish
        sys.stdout.write("\r")
        sys.stdout.flush()
