import csv
import os


class CSVUtils:
    """
    Simple CSV file reader/writer.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def read_dicts(self):
        with open(self.filepath, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def write_dicts(self, rows, fieldnames):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
