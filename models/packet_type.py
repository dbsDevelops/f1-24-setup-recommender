from enum import Enum

class PacketType(Enum):
    MOTION_DATA = 0
    SESSION_DATA = 1
    LAP_DATA = 2
    CAR_SETUP_DATA = 5
    CAR_TELEMETRY_DATA = 6
    TIME_TRIAL_DATA = 14