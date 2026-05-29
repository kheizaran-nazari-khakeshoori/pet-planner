from pet_planner import PetPlanner
from datetime import time


def test_parse_valid_time():
    planner = PetPlanner()
    t = planner._parse_time("09:30")
    assert isinstance(t, time)
    assert t.hour == 9 and t.minute == 30


def test_parse_invalid_time_returns_none():
    planner = PetPlanner()
    t = planner._parse_time("99:99")
    assert t is None
