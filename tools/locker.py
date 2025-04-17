import os
import time
import fcntl
from pathlib import Path
from config import config
import json

class Locker:
    """
    用于文件加锁的类，支持使用with语句进行上下文管理。

    使用示例:
    ```python
    with Locker('example.lock') as lock_file:
        # 执行需要加锁的操作
        data = lock_file.get()
        data['key'] = 'value'
        lock_file.set(data)
        pass
    ```
    """
    def __init__(self, file_name):
        root_path = Path(config.root_dir)
        lock_dir = root_path / 'tmp' / 'locks'
        self.file_name = lock_dir / file_name
        self.file = None

    def lock(self):
        lock_dir = self.file_name.parent
        if not lock_dir.exists():
            lock_dir.mkdir(parents=True, exist_ok=True)
        self.file = open(str(self.file_name), 'w')
        try:
            fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.file.close()
            self.file = None
            raise

    def release(self):
        if self.file:
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
            self.file.close()
            self.file = None

    class FileWrapper:
        def __init__(self, file):
            self.file = file

        def get(self):
            self.file.seek(0)
            try:
                return json.load(self.file)
            except json.JSONDecodeError:
                return {}

        def set(self, data):
            self.file.seek(0)
            json.dump(data, self.file)
            self.file.truncate()

    def __enter__(self):
        self.lock()
        return self.FileWrapper(self.file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False