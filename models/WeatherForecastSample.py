from utils.dictionnaries import weather_types

class WeatherForecastSample:
    def __init__(self, time, weather, tktp, airtp, rainP):
        self.time = time
        self.weather = weather
        self.track_temperature = tktp
        self.air_temperature = airtp
        self.rain_percentage = rainP
        self.weather_forecast_accuracy = -1

    def __repr__(self):
        return f"{self.time}m : {[self.weather]}, Track : {self.track_temperature}°C, " \
               f"Air : {self.air_temperature}°C, Humidity : {self.rain_percentage}% "

    def __str__(self):
        return f"{self.time}m : {weather_types[self.weather]}, Track : {self.track_temperature}°C, " \
               f"Air : {self.air_temperature}°C, Humidity : {self.rain_percentage}% "
