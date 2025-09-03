import os
import time
import threading
from collections import deque
from datetime import datetime
import traceback

class RateLimitedSender:
    def __init__(self, sender_func, interval=60):
        """
        :param sender_func: 实际的发送函数，参数是字符串消息
        :param interval: 最短发送间隔（秒）
        """
        self.sender_func = sender_func
        self.interval = interval
        self.queue = deque()
        self.lock = threading.Lock()
        self.last_send_time = 0

        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def send(self, message):
        """添加消息到队列（非阻塞）"""
        with self.lock:
            self.queue.append(message)

    def _flush(self):
        """立即发送队列消息（内部调用）"""
        if not self.queue:
            return
        batch_message = "\n---\n".join(self.queue)
        self.queue.clear()
        try:
            self.sender_func(batch_message)
        except Exception as e:
            print(f"[RateLimitedSender] 发送失败: {e}")
        self.last_send_time = time.time()

    def _worker(self):
        while True:
            with self.lock:
                if self.queue and (time.time() - self.last_send_time >= self.interval):
                    self._flush()
            time.sleep(1)
