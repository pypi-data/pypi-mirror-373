import os
import shutil


class FSUtils:
    """
    Filesystem helpers.
    """

    @staticmethod
    def mkdir_p(path: str):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def rm_rf(path: str):
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)

    @staticmethod
    def list_files(path: str):
        return [os.path.join(path, f) for f in os.listdir(path)]
