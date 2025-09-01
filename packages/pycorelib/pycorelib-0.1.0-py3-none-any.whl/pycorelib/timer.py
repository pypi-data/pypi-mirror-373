import time


class Timer:
    """
    Context manager for measuring execution time.
    """

    def __init__(self, name="block"):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start
        print(f"[Timer] {self.name} took {elapsed:.4f}s")
