import ctypes
import socket
import pprint

pp = pprint.PrettyPrinter()
NUMBER_OF_CARS = 22


class Listener:
    def __init__(self, port=20777, address="127.0.0.1", redirect=0, redirect_port=20777):
        self.port = port
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.socket.setblocking(False)
        self.address = address
        self.redirect = redirect
        self.redirect_port = redirect_port

    def reset(self):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('', self.port))
        self.socket.setblocking(False)

    def get(self, packet=None):
        if packet is None:
            try:
                packet = self.socket.recv(2048)
                if self.redirect: self.socket.sendto(packet, (self.address, self.redirect_port))
            except ConnectionResetError: #Thrown when redirecting on a localhost port that is not ready to read the data
                return None
            except:
                return None

        header = PacketHeader.from_buffer_copy(packet)
        return header, HEADER_FIELD_TO_PACKET_TYPE[header.m_packet_id].from_buffer_copy(packet)
    
    def __str__(self) -> str:
        return str(self.__dict__)
    
    def __repr__(self) -> str:
        return str(self.__dict__)


class PacketMixin(object):
    """A base set of helper methods for ctypes based packets"""

    def get_value(self, field):
        """Returns the field's value and formats the types value"""
        return self._format_type(getattr(self, field))

    def pack(self):
        """Packs the current data structure into a compressed binary

        Returns:
            (bytes):
                - The packed binary

        """
        return bytes(self)

    @classmethod
    def size(cls):
        return ctypes.sizeof(cls)

    @classmethod
    def unpack(cls, buffer):
        """Attempts to unpack the binary structure into a python structure

        Args:
            buffer (bytes):
                - The encoded buffer to decode

        """
        return cls.from_buffer_copy(buffer)

    def to_dict(self):
        """Returns a ``dict`` with key-values derived from _fields_"""
        return {k: self.get_value(k) for k, _ in self._fields_}

    def to_json(self):
        """Returns a ``str`` of sorted JSON derived from _fields_"""
        return str(self.to_dict())

    def _format_type(self, value):
        """A type helper to format values"""
        class_name = type(value).__name__

        if class_name == "float":
            return round(value, 3)

        if class_name == "bytes":
            return value.decode()

        '''if isinstance(value, ctypes.Array):
            return _format_array_type(value)'''

        if hasattr(value, "to_dict"):
            return value.to_dict()

        return value


class Packet(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1

    def __str__(self):
        return pp.pformat(self.to_dict())

    def __repr__(self):
        return pp.pformat(self.to_dict())


class PacketHeader(ctypes.LittleEndianStructure):
    _pack_ = 1  # Prevent padding/alignment issues
    _fields_ = [
        ("m_packetFormat", ctypes.c_uint16),       # 2024
        ("m_gameYear", ctypes.c_uint8),           # Game year (24)
        ("m_gameMajorVersion", ctypes.c_uint8),  # Major version
        ("m_gameMinorVersion", ctypes.c_uint8),  # Minor version
        ("m_packetVersion", ctypes.c_uint8),      # Packet version
        ("m_packetId", ctypes.c_uint8),           # Packet type identifier
        ("m_sessionUID", ctypes.c_uint64),        # Session UID
        ("m_sessionTime", ctypes.c_float),        # Session time
        ("m_frameIdentifier", ctypes.c_uint32),   # Frame identifier
        ("m_overallFrameIdentifier", ctypes.c_uint32),  # Overall frame identifier
        ("m_playerCarIndex", ctypes.c_uint8),    # Player car index
        ("m_secondaryPlayerCarIndex", ctypes.c_uint8),  # Secondary player car index
    ]


class CarMotionData(Packet):
    _fields_ = [
        ("m_worldPositionX", ctypes.c_float),  # World space X position
        ("m_worldPositionY", ctypes.c_float),  # World space Y position
        ("m_worldPosiitionZ", ctypes.c_float),  # World space Z position
        ("m_worldVelocityX", ctypes.c_float),  # Velocity in world space X
        ("m_worldVelocityY", ctypes.c_float),  # Velocity in world space Y
        ("m_worldVelocityZ", ctypes.c_float),  # Velocity in world space Z
        ("m_worldForwardDirX", ctypes.c_int16),  # World space forward X direction
        # (normalised)
        ("m_worldForwardDirY", ctypes.c_int16),
        # World space forward Y direction (normalised)
        ("m_worldForwardDirZ", ctypes.c_int16),
        # World space forward Z direction (normalised)
        ("m_worldRightDirX", ctypes.c_int16),
        # World space right X direction (normalised)
        ("m_worldRightDirY", ctypes.c_int16),
        # World space right Y direction (normalised)
        ("m_worldRightDirZ", ctypes.c_int16),
        # World space right Z direction (normalised)
        ("m_gForceLateral", ctypes.c_float),  # Lateral G-Force component
        ("m_gForceLongitudinal", ctypes.c_float),  # Longitudinal G-Force component
        ("m_gForceVertical", ctypes.c_float),  # Vertical G-Force component
        ("m_yaw", ctypes.c_float),  # Yaw angle in radians
        ("m_pitch", ctypes.c_float),  # Pitch angle in radians
        ("m_roll", ctypes.c_float),  # Roll angle in radians
    ]


class PacketMotionData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_carMotionData", CarMotionData * NUMBER_OF_CARS),  # Data for all cars on track
    ]


class MarshalZone(Packet):
    _fields_ = [
        ("m_zoneStart", ctypes.c_float),
        # Fraction (0..1) of way through the lap the marshal zone starts
        ("m_zoneFlag", ctypes.c_int8),
        # -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow, 4 = red
    ]


class WeatherForecastSample(Packet):
    _fields_ = [
        ("m_sessionType", ctypes.c_uint8),
        # 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P, 5 = Q1
        # 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ, 10 = R, 11 = R2
        # 12 = Time Trial
        ("m_timeOffset", ctypes.c_uint8),  # Time in minutes the forecast is for
        ("m_weather", ctypes.c_uint8),
        # Weather - 0 = clear, 1 = light cloud, 2 = overcast
        # 3 = light rain, 4 = heavy rain, 5 = storm
        ("m_trackTemperature", ctypes.c_int8),  # Track temp. in degrees Celsius
        ("m_trackTemperatureChange", ctypes.c_int8),
        # Track temp. change – 0 = up, 1 = down, 2 = no change
        ("m_airTemperature", ctypes.c_int8),  # Air temp. in degrees celsius
        ("m_airTemperatureChange", ctypes.c_int8),
        # Air temp. change – 0 = up, 1 = down, 2 = no change
        ("m_rainPercentage", ctypes.c_uint8),  # Rain percentage (0-100)
    ]


class PacketSessionData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_weather", ctypes.c_uint8),
        # Weather - 0 = clear, 1 = light cloud, 2 = overcast
        # 3 = light rain, 4 = heavy rain, 5 = storm
        ("m_trackTemperature", ctypes.c_int8),  # Track temp. in degrees celsius
        ("m_airTemperature", ctypes.c_int8),  # Air temp. in degrees celsius
        ("m_totalLaps", ctypes.c_uint8),  # Total number of laps in this race
        ("m_trackLength", ctypes.c_uint16),  # Track length in metres
        ("m_sessionType", ctypes.c_uint8),
        # 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P
        # 5 = Q1, 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ
        # 10 = R, 11 = R2, 12 = R3, 13 = Time Trial
        ("m_trackId", ctypes.c_int8),  # -1 for unknown, 0-21 for tracks, see appendix
        ("m_formula", ctypes.c_uint8),
        # Formula, 0 = F1 Modern, 1 = F1 Classic, 2 = F2,
        # 3 = F1 Generic
        ("m_sessionTimeLeft", ctypes.c_uint16),  # Time left in session in seconds
        ("m_sessionDuration", ctypes.c_uint16),  # Session duration in seconds
        ("m_pitSpeedLimit", ctypes.c_uint8),  # Pit speed limit in kilometres per hour
        ("m_gamePaused", ctypes.c_uint8),  # Whether the game is paused
        ("m_isSpectating", ctypes.c_uint8),  # Whether the player is spectating
        ("m_spectatorCarIndex", ctypes.c_uint8),  # Index of the car being spectated
        ("m_sliProNativeSupport", ctypes.c_uint8),
        # SLI Pro support, 0 = inactive, 1 = active
        ("m_numMarshalZones", ctypes.c_uint8),  # Number of marshal zones to follow
        ("m_marshalZones", MarshalZone * 21),  # List of marshal zones – max 21
        ("m_safetyCarStatus", ctypes.c_uint8),  # 0 = no safety car, 1 = full
        # 2 = virtual, 3 = formation lap
        ("m_networkGame", ctypes.c_uint8),  # 0 = offline, 1 = online
        ("m_numWeatherForecastSamples", ctypes.c_uint8),
        # Number of weather samples to follow
        ("m_weatherForecastSamples", WeatherForecastSample * 64),
        # Array of weather forecast samples
        ("m_forecastAccuracy", ctypes.c_uint8),  # 0 = Perfect, 1 = Approximate
        ("m_aiDifficulty", ctypes.c_uint8),  # AI Difficulty rating – 0-110
        ("m_seasonLinkIdentifier", ctypes.c_uint32),
        # Identifier for season - persists across saves
        ("m_weekendLinkIdentifier", ctypes.c_uint32),
        # Identifier for weekend - persists across saves
        ("m_sessionLinkIdentifier", ctypes.c_uint32),
        # Identifier for session - persists across saves
        ("m_pitStopWindowIdealLap", ctypes.c_uint8),
        # Ideal lap to pit on for current strategy (player)
        ("m_pitStopWindowLatestLap", ctypes.c_uint8),
        # Latest lap to pit on for current strategy (player)
        ("m_pitStopRejoinPosition", ctypes.c_uint8),
        # Predicted position to rejoin at (player)
        ("m_steeringAssist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_brakingAssist", ctypes.c_uint8),  # 0 = off, 1 = low, 2 = medium, 3 = high
        ("m_gearboxAssist", ctypes.c_uint8),
        # 1 = manual, 2 = manual & suggested gear, 3 = auto
        ("m_pitAssist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_pitReleaseAssist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_ERSAssist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_DRSAssist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_dynamicRacingLine", ctypes.c_uint8),
        # 0 = off, 1 = corners only, 2 = full
        ("m_dynamicRacingLineType", ctypes.c_uint8),  # 0 = 2D, 1 = 3D
        ("m_gameMode", ctypes.c_uint8),
        ("m_ruleSet", ctypes.c_uint8),
        ("m_timeOfDay", ctypes.c_uint32),
        ("m_sessionLength", ctypes.c_uint8),

        ("m_speedUnitsLeadPlayer", ctypes.c_uint8),
        ("m_temperatureUnitsLeadPlayer", ctypes.c_uint8),
        ("m_speedUnitsSecondaryPlayer", ctypes.c_uint8),
        ("m_temperatureUnitsSecondaryPlayer", ctypes.c_uint8),
        ("m_numSafetyCarPeriods", ctypes.c_uint8),
        ("m_numVirtualSafetyCarPeriods", ctypes.c_uint8),
        ("m_numRedFlagPeriods", ctypes.c_uint8),
        ("m_equalCarPerformance", ctypes.c_uint8),
        ("m_recoveryMode", ctypes.c_uint8),
        ("m_flashbackLimit", ctypes.c_uint8),
        ("m_surfaceType", ctypes.c_uint8),
        ("m_lowFuelMode", ctypes.c_uint8),
        ("m_raceStarts", ctypes.c_uint8),
        ("m_tyreTemperature", ctypes.c_uint8),
        ("m_pitLaneTyreSim", ctypes.c_uint8),
        ("m_carDamage", ctypes.c_uint8),
        ("m_carDamageRate", ctypes.c_uint8),
        ("m_collisions", ctypes.c_uint8),
        ("m_collisionsOffForFirstLapOnly", ctypes.c_uint8),
        ("m_mpUnsafePitRelease", ctypes.c_uint8),
        ("m_mpOffForGriefing", ctypes.c_uint8),
        ("m_cornerCuttingStringency", ctypes.c_uint8),
        ("m_parcFermeRules", ctypes.c_uint8),
        ("m_pitStopExperience", ctypes.c_uint8),
        ("m_safetyCar", ctypes.c_uint8),
        ("m_safetyCarExperience", ctypes.c_uint8),
        ("m_formationLap", ctypes.c_uint8),
        ("m_formationLapExperience", ctypes.c_uint8),
        ("m_redFlags", ctypes.c_uint8),
        ("m_affectsLicenceLevelSolo", ctypes.c_uint8),
        ("m_affectsLicenceLevelMP", ctypes.c_uint8),
        ("m_numSessionsInWeekend", ctypes.c_uint8),
        ("m_weekendStructure", ctypes.c_uint8*12),
        ("m_sector2LapDistanceStart", ctypes.c_float),
        ("m_sector3LapDistanceStart", ctypes.c_float)
        

    ]


class LapData(Packet):
    _fields_ = [
        ("m_lastLapTimeInMS", ctypes.c_uint32),  # Last lap time in milliseconds
        ("m_currentLapTimeInMS", ctypes.c_uint32),
        # Current time around the lap in milliseconds
        ("m_sector1TimeInMS", ctypes.c_uint16),  # Sector 1 time in milliseconds
        ("m_sector1TimeInMinutes", ctypes.c_uint8),
        ("m_sector2TimeInMS", ctypes.c_uint16),  # Sector 2 time in milliseconds
        ("m_sector2TimeInMinutes", ctypes.c_uint8),

        ("m_deltaToCarInFrontMSPart", ctypes.c_uint16),
        ("m_deltaToCarInFrontMinutesPart", ctypes.c_uint8),

        ("m_deltaToRaceLeaderMSPart", ctypes.c_uint16),
        ("m_deltaToRaceLeaderMinutesPart", ctypes.c_uint8),

        ("m_lapDistance", ctypes.c_float),
        # Distance vehicle is around current lap in metres – could
        # be negative if line hasn’t been crossed yet
        ("m_totalDistance", ctypes.c_float),
        # Total distance travelled in session in metres – could
        # be negative if line hasn’t been crossed yet
        ("m_safetyCarDelta", ctypes.c_float),  # Delta in seconds for safety car
        ("m_carPosition", ctypes.c_uint8),  # Car race position
        ("m_currentLapNum", ctypes.c_uint8),  # Current lap number
        ("m_pitStatus", ctypes.c_uint8),  # 0 = none, 1 = pitting, 2 = in pit area
        ("m_numPitStops", ctypes.c_uint8),  # Number of pit stops taken in this race
        ("m_sector", ctypes.c_uint8),  # 0 = sector1, 1 = sector2, 2 = sector3
        ("m_currentLapInvalid", ctypes.c_uint8),
        # Current lap invalid - 0 = valid, 1 = invalid
        ("m_penalties", ctypes.c_uint8),
        # Accumulated time penalties in seconds to be added
        ("m_totalWarnings", ctypes.c_uint8),  # Accumulated number of warnings issued
        ("m_cornerCuttingWarnings", ctypes.c_uint8),
        ("m_numUnservedDriveThroughPens", ctypes.c_uint8),
        # Num drive through pens left to serve
        ("m_numUnservedStopGoPens", ctypes.c_uint8),
        # Num stop go pens left to serve
        ("m_gridPosition", ctypes.c_uint8),
        # Grid position the vehicle started the race in
        ("m_driverStatus", ctypes.c_uint8),
        # Status of driver - 0 = in garage, 1 = flying lap
        # 2 = in lap, 3 = out lap, 4 = on track
        ("m_resultStatus", ctypes.c_uint8),
        # Result status - 0 = invalid, 1 = inactive, 2 = active
        # 3 = finished, 4 = didnotfinish, 5 = disqualified
        # 6 = not classified, 7 = retired
        ("m_pitLaneTimerActive", ctypes.c_uint8),
        # Pit lane timing, 0 = inactive, 1 = active
        ("m_pitLaneTimeInLaneInMS", ctypes.c_uint16),
        # If active, the current time spent in the pit lane in ms
        ("m_pitStopTimerInMS", ctypes.c_uint16),
        # Time of the actual pit stop in ms
        ("m_pitStopShouldServePen", ctypes.c_uint8),
        # Whether the car should serve a penalty at this stop
        ("m_speedTrapFastestSpeed", ctypes.c_float),
        ("m_speedTrapFastestLap", ctypes.c_uint8),
    ]


class PacketLapData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_lapData", LapData * NUMBER_OF_CARS),  # Lap data for all cars on track
        ("m_timeTrialPBCarIdx", ctypes.c_uint8),
        ("m_timeTrialRivalCarIdx", ctypes.c_int8),
    ]


class FastestLap(Packet):
    _fields_ = [
        ("m_vehicleIdx", ctypes.c_uint8),  # Vehicle index of car achieving fastest lap
        ("m_lapTime", ctypes.c_float),  # Lap time is in seconds
    ]


class Retirement(Packet):
    _fields_ = [
        ("m_vehicleIdx", ctypes.c_uint8),  # Vehicle index of car retiring
    ]


class TeamMateInPits(Packet):
    _fields_ = [
        ("m_vehicleIdx", ctypes.c_uint8),  # Vehicle index of team mate
    ]


class RaceWinner(Packet):
    _fields_ = [
        ("m_vehicleIdx", ctypes.c_uint8),  # Vehicle index of the race winner
    ]


class Penalty(Packet):
    _fields_ = [
        ("m_penaltyType", ctypes.c_uint8),  # Penalty type – see Appendices
        ("m_infringementYype", ctypes.c_uint8),  # Infringement type – see Appendices
        ("m_vehicleIdx", ctypes.c_uint8),
        # Vehicle index of the car the penalty is applied to
        ("m_otherVehicleIdx", ctypes.c_uint8),
        # Vehicle index of the other car involved
        ("m_time", ctypes.c_uint8),
        # Time gained, or time spent doing action in seconds
        ("m_lapNum", ctypes.c_uint8),  # Lap the penalty occurred on
        ("m_placesGained", ctypes.c_uint8),  # Number of places gained by this
    ]


class SpeedTrap(Packet):
    _fields_ = [
        ("m_vehicleIdx", ctypes.c_uint8),
        # Vehicle index of the vehicle triggering speed trap
        ("m_speed", ctypes.c_float),  # Top speed achieved in kilometres per hour
        ("m_overallFastestInSession", ctypes.c_uint8),
        # Overall fastest speed in session = 1, otherwise 0
        ("m_driverFastestInSession", ctypes.c_uint8),
        # Fastest speed for driver in session = 1, otherwise 0
        ("m_fastestVehicleIdxInSession", ctypes.c_uint8),
        ("m_fastestSpeedInSession", ctypes.c_float), 
    ]


class StartLights(Packet):
    _fields_ = [
        ("m_numLights", ctypes.c_uint8),  # Number of lights showing
    ]


class DriveThroughPenaltyServed(Packet):
    _fields_ = [
        ("m_vehicleIdx", ctypes.c_uint8),
        # Vehicle index of the vehicle serving drive through
    ]


class StopGoPenaltyServed(Packet):
    _fields_ = [
        ("m_vehicleIdx", ctypes.c_uint8),
        # Vehicle index of the vehicle serving stop go
    ]


class Flashback(Packet):
    _fields_ = [
        ("m_flashback_FrameIdentifier", ctypes.c_uint32),
        # Frame identifier flashed back to
        ("m_flashbackSessionTime", ctypes.c_float),  # Session time flashed back to
    ]


class Buttons(Packet):
    _fields_ = [
        ("m_", ctypes.c_uint32),
        # Bit flags specifying which buttons are being pressed
        # currently - see appendices
    ]


class Overtake(Packet):
    _fields_ = [
        ("m_overtakingVehicleIdx", ctypes.c_uint8),
        ("m_beingOvertakenVehicleIdx", ctypes.c_uint8),
    ]

class SafetyCar(Packet):
    _fields_ = [
        ("m_safetyCarType", ctypes.c_uint8),
        ("m_eventType", ctypes.c_uint8),
    ]


class Collision(Packet):
    _fields_ = [
        ("m_vehicle1Idx", ctypes.c_uint8),
        ("m_vehicle2Idx", ctypes.c_uint8),
    ]


class EventDataDetails(ctypes.Union, PacketMixin):  # Potentiel Problème ici
    _fields_ = [
        ("m_fastestLap", FastestLap),
        ("m_retirement", Retirement),
        ("m_teamMateInPits", TeamMateInPits),
        ("m_raceWinner", RaceWinner),
        ("m_penalty", Penalty),
        ("m_speedTrap", SpeedTrap),
        ("m_startLights", StartLights),
        ("m_driveThroughPenaltyServed", DriveThroughPenaltyServed),
        ("m_stopGoPenaltyServed", StopGoPenaltyServed),
        ("m_flashback", Flashback),
        ("m_buttons", Buttons),
        ("m_overtake", Overtake),
        ("m_satefyCar", SafetyCar),
        ("m_collision", Collision)
    ]


class PacketEventData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_eventStringCode", ctypes.c_uint8 * 4),  # Event string code, see below
        ("m_eventDetails", EventDataDetails),
        # Event details - should be interpreted differently
        # for each type
    ]


class ParticipantData(Packet):
    _fields_ = [
        ("m_aiControlled", ctypes.c_uint8),
        # Whether the vehicle is AI (1) or Human (0) controlled
        ("m_driverId", ctypes.c_uint8),
        # Driver id - see appendix, 255 if network human
        ("m_networkId", ctypes.c_uint8),
        # Network id – unique identifier for network players
        ("m_teamId", ctypes.c_uint8),  # Team id - see appendix
        ("m_myTeam", ctypes.c_uint8),  # My team flag – 1 = My Team, 0 = otherwise
        ("m_raceNumber", ctypes.c_uint8),  # Race number of the car
        ("m_nationality", ctypes.c_uint8),  # Nationality of the driver
        ("m_name", ctypes.c_char * 48),
        # Name of participant in UTF-8 format – null terminated
        # Will be truncated with … (U+2026) if too long
        ("m_yourTelemetry", ctypes.c_uint8),
        # The player's UDP setting, 0 = restricted, 1 = public
        ("m_showOnlineNames", ctypes.c_uint8),
        ("m_techTevel", ctypes.c_uint16),
        ("m_platform", ctypes.c_uint8)
    ]


class PacketParticipantsData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_numActiveCars", ctypes.c_uint8),
        # Number of active cars in the data – should match number of
        # cars on HUD
        ("m_participants", ParticipantData * NUMBER_OF_CARS),
    ]


class CarSetupData(Packet):
    _fields_ = [
        ("m_frontWing", ctypes.c_uint8),  # Front wing aero
        ("m_rearWing", ctypes.c_uint8),  # Rear wing aero
        ("m_onThrottle", ctypes.c_uint8),
        # Differential adjustment on throttle (percentage)
        ("m_offThrottle", ctypes.c_uint8),
        # Differential adjustment off throttle (percentage)
        ("m_frontCamber", ctypes.c_float),  # Front camber angle (suspension geometry)
        ("m_rearCamber", ctypes.c_float),  # Rear camber angle (suspension geometry)
        ("m_frontToe", ctypes.c_float),  # Front toe angle (suspension geometry)
        ("m_rearToe", ctypes.c_float),  # Rear toe angle (suspension geometry)
        ("m_frontSuspension", ctypes.c_uint8),  # Front suspension
        ("m_rearSuspension", ctypes.c_uint8),  # Rear suspension
        ("m_frontAntiRollBar", ctypes.c_uint8),  # Front anti-roll bar
        ("m_rearAntiRollBar", ctypes.c_uint8),  # Front anti-roll bar
        ("m_frontSuspensionHeight", ctypes.c_uint8),  # Front ride height
        ("m_rearSuspensionHeight", ctypes.c_uint8),  # Rear ride height
        ("m_brakePressure", ctypes.c_uint8),  # Brake pressure (percentage)
        ("m_brakeBias", ctypes.c_uint8),  # Brake bias (percentage)
        ("m_engineBraking", ctypes.c_uint8),
        ("m_rearLeftTyrePressure", ctypes.c_float),  # Rear left tyre pressure (PSI)
        ("m_rearRightTyrePressure", ctypes.c_float),
        # Rear right tyre pressure (PSI)
        ("m_frontLeftTyrePressure", ctypes.c_float),
        # Front left tyre pressure (PSI)
        ("m_frontRightTyrePressure", ctypes.c_float),
        # Front right tyre pressure (PSI)
        ("m_ballast", ctypes.c_uint8),  # Ballast
        ("m_fuelLoad", ctypes.c_float),  # Fuel load
    ]

    def __str__(self):
        string = ""
        for i in range(20):
            string += str(self.get_value(self._fields_[i][0])) + " "
        return string

    def __repr__(self):
        string = ""
        for i in range(20):
            string += str(self.get_value(self._fields_[i][0])) + " "
        return string


class PacketCarSetupData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_carSetups", CarSetupData * NUMBER_OF_CARS),
        ("m_nextFrontWingValue", ctypes.c_float)
    ]


class CarTelemetryData(Packet):
    _fields_ = [
        ("m_speed", ctypes.c_uint16),  # Speed of car in kilometres per hour
        ("m_throttle", ctypes.c_float),  # Amount of throttle applied (0.0 to 1.0)
        ("m_steer", ctypes.c_float),
        # Steering (-1.0 (full lock left) to 1.0 (full lock right))
        ("m_brake", ctypes.c_float),  # Amount of brake applied (0.0 to 1.0)
        ("m_clutch", ctypes.c_uint8),  # Amount of clutch applied (0 to 100)
        ("m_gear", ctypes.c_int8),  # Gear selected (1-8, N=0, R=-1)
        ("m_engineRPM", ctypes.c_uint16),  # Engine RPM
        ("m_drs", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_revLightsPercent", ctypes.c_uint8),  # Rev lights indicator (percentage)
        ("m_revLightsBitValue", ctypes.c_uint16),
        # Rev lights (bit 0 = leftmost LED, bit 14 = rightmost LED)
        ("m_brakesTemperature", ctypes.c_uint16 * 4),  # Brakes temperature (celsius)
        ("m_tyresSurfaceTemperature", ctypes.c_uint8 * 4),
        # Tyres surface temperature (celsius)
        ("m_tyresInnerTemperature", ctypes.c_uint8 * 4),
        # Tyres inner temperature (celsius)
        ("m_engineTemperature", ctypes.c_uint16),  # Engine temperature (celsius)
        ("m_tyresPressure", ctypes.c_float * 4),  # Tyres pressure (PSI)
        ("m_surfaceType", ctypes.c_uint8 * 4),  # Driving surface, see appendices
    ]


class PacketCarTelemetryData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_carTelemetryData", CarTelemetryData * NUMBER_OF_CARS),
        ("m_mfdPanelIndex", ctypes.c_uint8),
        # Index of MFD panel open - 255 = MFD closed
        # Single player, race – 0 = Car setup, 1 = Pits
        # 2 = Damage, 3 =  Engine, 4 = Temperatures
        # May vary depending on game mode
        ("m_mfdPanelIndexSecondaryPlayer", ctypes.c_uint8),  # See above
        ("m_suggestedGear", ctypes.c_int8),  # Suggested gear for the player (1-8)
        # 0 if no gear suggested
    ]


class CarStatusData(Packet):
    _fields_ = [
        ("m_tractionControl", ctypes.c_uint8),
        # Traction control - 0 = off, 1 = medium, 2 = full
        ("m_antiLockBrakes", ctypes.c_uint8),  # 0 (off) - 1 (on)
        ("m_fuelMix", ctypes.c_uint8),
        # Fuel mix - 0 = lean, 1 = standard, 2 = rich, 3 = max
        ("m_frontBrakebias", ctypes.c_uint8),  # Front brake bias (percentage)
        ("m_pitLimiterStatus", ctypes.c_uint8),
        # Pit limiter status - 0 = off, 1 = on
        ("m_fuelInTank", ctypes.c_float),  # Current fuel mass
        ("m_fuelCapacity", ctypes.c_float),  # Fuel capacity
        ("m_fuelRemainingLaps", ctypes.c_float),
        # Fuel remaining in terms of laps (value on MFD)
        ("m_maxRPM", ctypes.c_uint16),  # Cars max RPM, point of rev limiter
        ("m_idleRPM", ctypes.c_uint16),  # Cars idle RPM
        ("m_maxGears", ctypes.c_uint8),  # Maximum number of gears
        ("m_drsAllowed", ctypes.c_uint8),  # 0 = not allowed, 1 = allowed
        ("m_drsActivationDistance", ctypes.c_uint16),
        # 0 = DRS not available, non-zero - DRS will be available
        # in [X] metres
        ("m_actualTyreCompound", ctypes.c_uint8),
        # F1 Modern - 16 = C5, 17 = C4, 18 = C3, 19 = C2, 20 = C1
        # 7 = inter, 8 = wet
        # F1 Classic - 9 = dry, 10 = wet
        # F2 – 11 = super soft, 12 = soft, 13 = medium, 14 = hard
        # 15 = wet
        ("m_visualTyreCompound", ctypes.c_uint8),
        # F1 visual (can be different from actual compound)
        # 16 = soft, 17 = medium, 18 = hard, 7 = inter, 8 = wet
        # F1 Classic – same as above
        # F2 ‘19, 15 = wet, 19 – super soft, 20 = soft
        # 21 = medium , 22 = hard
        ("m_tyresAgeLaps", ctypes.c_uint8),  # Age in laps of the current set of tyres
        ("m_vehicleFiaFlags", ctypes.c_int8),
        # -1 = invalid/unknown, 0 = none, 1 = green
        # 2 = blue, 3 = yellow, 4 = red
        ("m_enginePowerICE", ctypes.c_float),
        ("m_enginePowerMGUK", ctypes.c_float),
        ("m_ersStoreEnergy", ctypes.c_float),  # ERS energy store in Joules
        ("m_ersDeployMode", ctypes.c_uint8),
        # ERS deployment mode, 0 = none, 1 = medium
        # 2 = hotlap, 3 = overtake
        ("m_ersHarvestedThisLapMGUK", ctypes.c_float),
        # ERS energy harvested this lap by MGU-K
        ("m_ersHarvestedThisLapMGUH", ctypes.c_float),
        # ERS energy harvested this lap by MGU-H
        ("m_ersDeployedThisLap", ctypes.c_float),  # ERS energy deployed this lap
        ("m_networkPaused", ctypes.c_uint8),
        # Whether the car is paused in a network game
    ]


class PacketCarStatusData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_carStatusData", CarStatusData * NUMBER_OF_CARS),
    ]


class FinalClassificationData(Packet):
    _fields_ = [
        ("m_position", ctypes.c_uint8),  # Finishing position
        ("m_numLaps", ctypes.c_uint8),  # Number of laps completed
        ("m_gridPosition", ctypes.c_uint8),  # Grid position of the car
        ("m_points", ctypes.c_uint8),  # Number of points scored
        ("m_numPitStops", ctypes.c_uint8),  # Number of pit stops made
        ("m_resultStatus", ctypes.c_uint8),
        # Result status - 0 = invalid, 1 = inactive, 2 = active
        # 3 = finished, 4 = didnotfinish, 5 = disqualified
        # 6 = not classified, 7 = retired
        # Best lap time of the session in milliseconds
        ("m_bestLapTimeInMS", ctypes.c_uint32),
        # Total race time in seconds without penalties
        ("m_totalRaceTime", ctypes.c_double),
        ("m_penaltiesTime", ctypes.c_uint8),  # Total penalties accumulated in seconds
        # Number of penalties applied to this driver
        ("m_numPenalties", ctypes.c_uint8),
        ("m_numTyreStints", ctypes.c_uint8),  # Number of tyres stints up to maximum
        # Actual tyres used by this driver
        ("m_tyreStintsActual", ctypes.c_uint8 * 8),
        # Visual tyres used by this driver
        ("m_tyreStintsVisual", ctypes.c_uint8 * 8),
        ("m_tyreStintsEndLaps", ctypes.c_uint8 * 8),
    ]


class PacketFinalClassificationData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_numCars", ctypes.c_uint8),  # Number of cars in the final classification
        ("m_classificationData", FinalClassificationData * NUMBER_OF_CARS),
    ]


class LobbyInfoData(Packet):
    _fields_ = [
        ("m_aiControlled", ctypes.c_uint8),
        # Whether the vehicle is AI (1) or Human (0) controlled
        ("m_teamId", ctypes.c_uint8),
        # Team id - see appendix (255 if no team currently selected)
        ("m_nationality", ctypes.c_uint8),  # Nationality of the driver
        ("m_platform", ctypes.c_uint8),
        # Name of participant in UTF-8 format – null terminated
        ("m_name", ctypes.c_char * 48),
        # Will be truncated with ... (U+2026) if too long
        ("m_carNumber", ctypes.c_uint8),  # Car number of the player
        ("m_yourTelemetry", ctypes.c_uint8),
        ("m_showOnlineNames", ctypes.c_uint8),
        ("m_techLevel", ctypes.c_uint16),
        ("m_readyStatus", ctypes.c_uint8),  # 0 = not ready, 1 = ready, 2 = spectating
    ]


class PacketLobbyInfoData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        # Packet specific data
        ("m_numPlayers", ctypes.c_uint8),  # Number of players in the lobby data
        ("m_lobbyPlayers", LobbyInfoData * NUMBER_OF_CARS),
    ]


class CarDamageData(Packet):
    _fields_ = [
        ("m_tyresWear", ctypes.c_float * 4),  # Tyre wear (percentage)
        ("m_tyresDamage", ctypes.c_uint8 * 4),  # Tyre damage (percentage)
        ("m_brakesDamage", ctypes.c_uint8 * 4),  # Brakes damage (percentage)
        # Front left wing damage (percentage)
        ("m_frontLeftWingDamage", ctypes.c_uint8),
        # Front right wing damage (percentage)
        ("m_frontRightWingDamage", ctypes.c_uint8),
        ("m_rearWingDamage", ctypes.c_uint8),  # Rear wing damage (percentage)
        ("m_floorDamage", ctypes.c_uint8),  # Floor damage (percentage)
        ("m_diffuserDamage", ctypes.c_uint8),  # Diffuser damage (percentage)
        ("m_sidepodDamage", ctypes.c_uint8),  # Sidepod damage (percentage)
        ("m_drsFault", ctypes.c_uint8),  # Indicator for DRS fault, 0 = OK, 1 = fault
        ("m_ersFault", ctypes.c_uint8),
        ("m_gearBoxDamage", ctypes.c_uint8),  # Gear box damage (percentage)
        ("m_engineDamage", ctypes.c_uint8),  # Engine damage (percentage)
        ("m_engineMGUHWear", ctypes.c_uint8),  # Engine wear MGU-H (percentage)
        ("m_engineESWear", ctypes.c_uint8),  # Engine wear ES (percentage)
        ("m_engineCEWear", ctypes.c_uint8),  # Engine wear CE (percentage)
        ("m_engineICEWear", ctypes.c_uint8),  # Engine wear ICE (percentage)
        ("m_engineMGUKWear", ctypes.c_uint8),  # Engine wear MGU-K (percentage)
        ("m_engineTCWear", ctypes.c_uint8),  # Engine wear TC (percentage)
        ("m_engineBlown", ctypes.c_uint8),
        ("m_engineSeized", ctypes.c_uint8),
    ]


class PacketCarDamageData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_carDamageData", CarDamageData * NUMBER_OF_CARS),
    ]


class LapHistoryData(Packet):
    _fields_ = [
        ("m_lapTimeInMS", ctypes.c_uint32),  # Lap time in milliseconds
        ("m_sector1TimeInMS", ctypes.c_uint16),  # Sector 1 time in milliseconds
        ("m_sector1TimeInMinutesPart", ctypes.c_uint8),
        ("m_sector2TimeInMS", ctypes.c_uint16),  # Sector 2 time in milliseconds
        ("m_sector2TimeInMinutesPart", ctypes.c_uint8),
        ("m_sector3TimeInMS", ctypes.c_uint16),  # Sector 3 time in milliseconds
        ("m_sector3TimeInMinutesPart", ctypes.c_uint8),
        ("m_lapValidBitFlags", ctypes.c_uint8),
        # 0x01 bit set-lap valid,      0x02 bit set-sector 1 valid
        # 0x04 bit set-sector 2 valid, 0x08 bit set-sector 3 valid
    ]


class TyreStintHistoryData(Packet):
    _fields_ = [
        # Lap the tyre usage ends on (255 of current tyre)
        ("m_endLap", ctypes.c_uint8),
        ("m_tyreActualCompound", ctypes.c_uint8),  # Actual tyres used by this driver
        ("m_tyreVisualCompound", ctypes.c_uint8),  # Visual tyres used by this driver
    ]


class PacketSessionHistoryData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_carIdx", ctypes.c_uint8),  # Index of the car this lap data relates to
        # Num laps in the data (including current partial lap)
        ("m_numLaps", ctypes.c_uint8),
        ("m_numTyreStints", ctypes.c_uint8),  # Number of tyre stints in the data
        # Lap the best lap time was achieved on
        ("m_bestLapTimeLapNum", ctypes.c_uint8),
        # Lap the best Sector 1 time was achieved on
        ("m_bestSector1LapNum", ctypes.c_uint8),
        # Lap the best Sector 2 time was achieved on
        ("m_bestSector2LapNum", ctypes.c_uint8),
        # Lap the best Sector 3 time was achieved on
        ("m_bestSector3LapNum", ctypes.c_uint8),
        ("m_lapHistoryData", LapHistoryData * 100),  # 100 laps of data max
        ("m_tyreStintsHistoryData", TyreStintHistoryData * 8),
    ]

class TyreSetData(Packet):
    _fields_ = [
        ("m_actualTyreCompound", ctypes.c_uint8),
        ("m_visualTyreCompound", ctypes.c_uint8),
        ("m_wear", ctypes.c_uint8),
        ("m_available", ctypes.c_uint8),
        ("m_recommandedSession", ctypes.c_uint8),
        ("m_lifeSpan", ctypes.c_uint8),
        ("m_usableLife", ctypes.c_uint8),
        ("m_lapDeltaTime", ctypes.c_uint16),
        ("m_fitted", ctypes.c_uint8)
    ]

class PacketTyreSetsData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),
        ("m_carIdx", ctypes.c_uint8),
        ("m_tyreSetData", TyreSetData*20),
        ("m_fittedIdx", ctypes.c_uint8)
    ]

class PacketMotionExData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        # Extra player car ONLY data
        ("m_suspensionPosition", ctypes.c_float * 4),
        # Note: All wheel arrays have the following order:
        ("m_suspensionVelocity", ctypes.c_float * 4),  # RL, RR, FL, FR
        ("m_suspensionAcceleration", ctypes.c_float * 4),  # RL, RR, FL, FR
        ("m_wheelSpeed", ctypes.c_float * 4),  # Speed of each wheel
        ("m_wheelSlipRatio", ctypes.c_float * 4),  # Slip ratio for each wheel
        ("m_wheelSlipAngle", ctypes.c_float * 4),
        ("m_wheelLatForce", ctypes.c_float * 4),
        ("m_wheelLongForce", ctypes.c_float * 4),
        ("m_heightOfCogAboveGround", ctypes.c_float),
        ("m_localVelocityX", ctypes.c_float),  # Velocity in local space
        ("m_localVelocityY", ctypes.c_float),  # Velocity in local space
        ("m_localVelocityZ", ctypes.c_float),  # Velocity in local space
        ("m_angularVelocityX", ctypes.c_float),  # Angular velocity x-component
        ("m_angularVelocityY", ctypes.c_float),  # Angular velocity y-component
        ("m_angularVelocityZ", ctypes.c_float),  # Angular velocity z-component
        ("m_angularAccelerationX", ctypes.c_float),  # Angular velocity x-component
        ("m_angularAccelerationY", ctypes.c_float),  # Angular velocity y-component
        ("m_angularAccelerationZ", ctypes.c_float),  # Angular velocity z-component
        ("m_frontWheelsAngle", ctypes.c_float),
        ("m_wheelVertForce", ctypes.c_float*4),
        # Current front wheels angle in radians
        ("m_frontAeroHeight", ctypes.c_float),
        ("m_rearAeroHeight", ctypes.c_float),  
        ("m_frontRollAngle", ctypes.c_float),
        ("m_rearRollAngle", ctypes.c_float),
        ("m_mChassisYaw", ctypes.c_float),  
    ]


class TimeTrialDataSet(Packet):
    _fields_ = [
        ("m_carIdx", ctypes.c_uint8),
        ("m_teamId", ctypes.c_uint8),
        ("m_lapTimeInMS", ctypes.c_uint32),
        ("m_sector1TimeInMS", ctypes.c_uint32),
        ("m_sector2TimeInMS", ctypes.c_uint32),
        ("m_sector3TimeInMS", ctypes.c_uint32),
        ("m_tractionControl", ctypes.c_uint8),
        ("m_gearboxAssis", ctypes.c_uint8),
        ("m_antiLockBrakes", ctypes.c_uint8),
        ("m_equalCarPerformance", ctypes.c_uint8),
        ("m_customSetup", ctypes.c_uint8),
        ("m_valid", ctypes.c_uint8),
    ]

class PacketTimeTrialData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),
        ("m_playerSessionBestDataSet", TimeTrialDataSet),
        ("m_personalBestDataSet", TimeTrialDataSet),
        ("m_rivalDataSet", TimeTrialDataSet)
    ]

HEADER_FIELD_TO_PACKET_TYPE = {
    0: PacketMotionData,
    1: PacketSessionData,
    2: PacketLapData,
    3: PacketEventData,
    4: PacketParticipantsData,
    5: PacketCarSetupData,
    6: PacketCarTelemetryData,
    7: PacketCarStatusData,
    8: PacketFinalClassificationData,
    9: PacketLobbyInfoData,
    10: PacketCarDamageData,
    11: PacketSessionHistoryData,
    12:PacketTyreSetsData,
    13:PacketMotionExData,
    14:PacketTimeTrialData
}