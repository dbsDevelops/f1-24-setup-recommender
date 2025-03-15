from utils.dictionnaries import session_types, conversion, track_ids, flag_colours

class Session:
    def __init__(self):
        self.air_temperature = 0
        self.track_temperature = 0
        self.number_of_laps = 0
        self.current_lap = 0
        self.previous_lap = 0
        self.Seance = 0
        self.Finished = False
        self.time_left = 0
        self.legende = ""
        self.track = -1
        self.marshal_zones = []
        self.index_of_best_lap_time = -1
        self.best_lap_time = 5000
        self.safety_car_status = 0
        self.trackLength = 0
        self.weatherList: list[WeatherForecastSample] = []
        self.nb_weatherForecastSamples = 0
        self.weatherForecastAccuracy = 0
        self.startTime = 0
        self.number_of_drivers = 22
        self.formationLapDone = False
        self.circuit_changed = False
        self.segments = []
        self.num_marshal_zones = 0
        self.packet_received = [0]*14
        self.anyYellow = False

    def add_slot(self, slot):
        self.weatherList.append(WeatherForecastSample(slot.m_time_offset, slot.m_weather, slot.m_track_temperature,
                                                      slot.m_air_temperature, slot.m_rain_percentage))

    def clear_slot(self):
        self.weatherList = []

    def title_display(self):
        if self.Seance == 18:
            string = f"Time Trial : {track_ids[self.track][0]}"
        elif self.Seance in [15,16,17]:
            string = f"Session : {session_types[self.Seance]}, Lap : {self.current_lap}/{self.number_of_laps}, " \
                        f"Air : {self.air_temperature}°C / Track : {self.track_temperature}°C"
        elif self.Seance in [5,6,7,8,9]:
            string = f" Qualy : {conversion(self.time_left, 1)}"
        else:
            string = f" FP : {conversion(self.time_left, 1)}"
        return string

    def update_marshal_zones(self, map_canvas):
        for i in range(len(self.segments)):
            map_canvas.itemconfig(self.segments[i], fill=flag_colours[self.marshal_zones[i].m_zone_flag])
