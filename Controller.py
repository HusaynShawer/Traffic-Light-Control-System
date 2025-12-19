import time
class TrafficController:
    def __init__(self, green_time):
        self.green_time = green_time
        self.last_switch_time = time.time()
        self.current_lane = 1

    def elapsed_time(self):
        return time.time() - self.last_switch_time

    def time_left(self):
        return max(0, int(self.green_time - self.elapsed_time()))

    def is_phase_finished(self):
        return self.elapsed_time() >= self.green_time

    def reset(self, new_green_time, next_lane):
        self.green_time = new_green_time
        self.last_switch_time = time.time()
        self.current_lane = next_lane