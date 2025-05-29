from utils.dictionnaries import weather_types

class WeatherForecastSample:
    """
    Class to store weather forecast sample data.
    Attributes:
        time (int): Time in minutes since the start of the session.
        weather (int): Weather condition identifier.
        track_temperature (float): Track temperature in degrees Celsius.
        air_temperature (float): Air temperature in degrees Celsius.
        rain_percentage (float): Percentage chance of rain.
        weather_forecast_accuracy (int): Accuracy of the weather forecast.
    """
    def __init__(self, time, weather, track_temperature, air_temperature, rain_percentage):
        self.time = time
        self.weather = weather
        self.track_temperature = track_temperature
        self.air_temperature = air_temperature
        self.rain_percentage = rain_percentage
        self.weather_forecast_accuracy = -1

    def __repr__(self):
        return f"{self.time}m : {[self.weather]}, Track : {self.track_temperature}°C, " \
               f"Air : {self.air_temperature}°C, Humidity : {self.rain_percentage}% "

    def __str__(self):
        return f"{self.time}m : {weather_types[self.weather]}, Track : {self.track_temperature}°C, " \
               f"Air : {self.air_temperature}°C, Humidity : {self.rain_percentage}% "
