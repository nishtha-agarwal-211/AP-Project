# test_clock.py
from interceptor.models.clock import LamportClock

def test_tick_strictly_increases():
    c = LamportClock()
    vals = [c.tick() for _ in range(5)]
    assert vals == [1, 2, 3, 4, 5]

def test_observe_jumps_ahead():
    c = LamportClock()
    assert c.observe(10) == 11
    assert c.observe(3) == 12  # never goes backward