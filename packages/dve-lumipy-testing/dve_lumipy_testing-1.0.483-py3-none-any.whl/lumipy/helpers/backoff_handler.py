from typing import Optional
import math
import time


class BackoffHandler:
    def __init__(self, pause_time: Optional[float] = 0.1, max_pause_time: Optional[float] = 10, beta: Optional[float] = math.exp(1/200)):
        if pause_time < 0.1 or pause_time > max_pause_time:
            raise ValueError(f"Pause time must be between 0.1 and {max_pause_time}, both inclusive.")
        if beta < 1:
            raise ValueError('Beta must be greater than 1.')

        self.max_pause_time = max_pause_time
        self.beta = beta
        self.pause_time = pause_time

    def _update_pause_time(self):
        self.pause_time = min(self.pause_time * self.beta, self.max_pause_time)

    def sleep(self):
        time.sleep(self.pause_time)
        self._update_pause_time()
