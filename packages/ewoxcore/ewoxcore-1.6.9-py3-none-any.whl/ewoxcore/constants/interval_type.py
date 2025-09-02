from enum import IntEnum


class IntervalType(IntEnum):
    FireAndForget = 0   # will run immediately
    FireAndForgetAt = 1 # will run based on start date
    Year = 2
    Month = 3
    Week = 4
    Day = 5
    Hour = 6
    Minute = 7
    Second = 8
