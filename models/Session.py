from models.weather_forecast_sample import WeatherForecastSample
from utils.dictionnaries import session_types, conversion, track_ids, flag_colours

class Session:
    """
    Class to store session data.
    Attributes:

        air_temperature (int): Air temperature in degrees Celsius.
        track_temperature (int): Track temperature in degrees Celsius.
        number_of_laps (int): Total number of laps in the session.
        current_lap (int): Current lap number.
        previous_lap (int): Previous lap number.
        session_id (int): Session type identifier.
        is_finished (bool): Indicates if the session is finished.
        time_left (int): Time left in the session in seconds.
        legned (str): Legend for the session.
        track (int): Track identifier.
        marshal_zones (list): List of marshal zones.
        index_of_best_lap_time (int): Index of the best lap time.
        best_lap_time (int): Best lap time in milliseconds.
        safety_car_status (int): Status of the safety car.
        track_length (int): Length of the track in meters.
        weather_forecast_samples (list): List of weather forecast samples.
        number_of_weather_forecast_samples (int): Number of weather forecast samples.
        weather_forecast_accuracy (int): Accuracy of the weather forecast.
        start_time (int): Start time of the session in seconds since epoch.
        number_of_drivers (int): Number of drivers in the session.
        is_formation_lap_completed (bool): Indicates if the formation lap is done.
        circuit_changed (bool): Indicates if the circuit has changed.
        segments (list): List of segments for marshal zones.
        num_marshal_zones (int): Number of marshal zones.
        packet_received (list): List indicating which packets have been received.
        is_yellow_flag_active (bool): Indicates if there is any yellow flag condition.
    """
    def __init__(self):
        self.air_temperature = 0
        self.track_temperature = 0
        self.number_of_laps = 0
        self.current_lap = 0
        self.previous_lap = 0
        self.session_id = 0
        self.is_finished = False
        self.time_left = 0
        self.legend = ""
        self.track = -1
        self.marshal_zones = []
        self.index_of_best_lap_time = -1
        self.best_lap_time = 5000
        self.safety_car_status = 0
        self.track_length = 0
        self.weather_forecast_samples: list[WeatherForecastSample] = []
        self.number_weather_of_forecast_samples = 0
        self.weather_forecast_accuracy = 0
        self.start_time = 0
        self.number_of_drivers = 22
        self.is_formation_lap_completed = False
        self.circuit_changed = False
        self.segments = []
        self.num_marshal_zones = 0
        self.packet_received = [0]*14
        self.is_yellow_flag_active = False

    def add_slot(self, slot):
        """
        Adds a weather forecast sample to the session.
        
        :param slot: An object containing weather forecast data.
        """
        self.weather_forecast_samples.append(WeatherForecastSample(slot.m_time_offset, slot.m_weather, slot.m_track_temperature,
                                                      slot.m_air_temperature, slot.m_rain_percentage))

    def clear_slot(self):
        """
        Clears the list of weather forecast samples.
        """
        self.weather_forecast_samples = []

    def title_display(self):
        """
        Generates a string to display the current session status.
        
        :return: A formatted string with session details.
        """
        if self.session_id == 18:
            string = f"Time Trial : {track_ids[self.track][0]}"
        elif self.session_id in [15,16,17]:
            string = f"Session : {session_types[self.session_id]}, Lap : {self.current_lap}/{self.number_of_laps}, " \
                        f"Air : {self.air_temperature}°C / Track : {self.track_temperature}°C"
        elif self.session_id in [5,6,7,8,9]:
            string = f" Qualy : {conversion(self.time_left, 1)}"
        else:
            string = f" FP : {conversion(self.time_left, 1)}"
        return string

    def update_marshal_zones(self, map_canvas):
        """
        Updates the display of marshal zones on the map canvas.

        :param map_canvas: The canvas where marshal zones are displayed.
        """
        for i in range(len(self.segments)):
            map_canvas.itemconfig(self.segments[i], fill=flag_colours[self.marshal_zones[i].m_zone_flag])
