class NumUtils:
    """
    Numeric utilities.
    """

    @staticmethod
    def moving_average(arr, window_size: int):
        if window_size <= 0:
            raise ValueError("window_size must be > 0")
        return [
            sum(arr[i:i + window_size]) / window_size
            for i in range(len(arr) - window_size + 1)
        ]

    @staticmethod
    def normalize(arr):
        min_val, max_val = min(arr), max(arr)
        if min_val == max_val:
            return [0 for _ in arr]
        return [(x - min_val) / (max_val - min_val) for x in arr]
