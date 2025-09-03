import time

class TimeUtil:
    @staticmethod
    def current_time_millis():
        return int(time.time() * 1000)