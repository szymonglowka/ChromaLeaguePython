import time
import copy
from typing import List

class Animation:
    def __init__(self, duration: float):
        self.start_time = time.time()
        self.duration = duration

    @property
    def is_active(self) -> bool:
        return time.time() - self.start_time < self.duration

    def get_frame(self, base_matrix: List[List[int]]) -> List[List[int]]:
        return base_matrix

class FlashAnimation(Animation):
    def __init__(self, duration: float, color: int):
        super().__init__(duration)
        self.color = color

    def get_frame(self, base_matrix: List[List[int]]) -> List[List[int]]:
        if not self.is_active:
            return base_matrix
        return [[self.color] * 22 for _ in range(6)]

class PulseAnimation(Animation):
    def __init__(self, duration: float, color: int, pulses: int):
        super().__init__(duration)
        self.color = color
        self.pulses = pulses

    def get_frame(self, base_matrix: List[List[int]]) -> List[List[int]]:
        if not self.is_active:
            return base_matrix
        
        elapsed = time.time() - self.start_time
        pulse_duration = self.duration / self.pulses
        
        # Determine if we are in the 'on' or 'off' phase of a pulse
        in_pulse_phase = (elapsed % pulse_duration) < (pulse_duration / 2)
        
        if in_pulse_phase:
            return [[self.color] * 22 for _ in range(6)]
        return base_matrix

class DoubleKillAnimation(PulseAnimation):
    def __init__(self, color: int):
        super().__init__(1.5, color, pulses=2)

class TripleKillAnimation(PulseAnimation):
    def __init__(self, color: int):
        super().__init__(2.0, color, pulses=3)

class QuadraKillAnimation(PulseAnimation):
    def __init__(self, color: int):
        super().__init__(2.5, color, pulses=4)

class PentaKillAnimation(Animation):
    def __init__(self, color: int):
        super().__init__(3.0)
        self.color = color

    def get_frame(self, base_matrix: List[List[int]]) -> List[List[int]]:
        if not self.is_active:
            return base_matrix
        
        # Rainbow/Intense wave effect
        elapsed = time.time() - self.start_time
        offset = int(elapsed * 20) % 22
        
        frame: List[List[int]] = [list(r) for r in base_matrix]
        for r_idx in range(6):
            for c_idx in range(22):
                if (c_idx + offset) % 22 < 5:
                    frame[r_idx][c_idx] = self.color
        return frame
