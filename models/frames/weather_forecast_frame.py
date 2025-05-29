from models.frames.base_frame import BaseFrame
from models.session import Session

class WeatherForecastFrame(BaseFrame):
    """
    WeatherForecastFrame is a custom frame that displays the weather forecast for a session.
    It inherits from BaseFrame and initializes a grid layout with a specified number of lines,
    each containing a label to show the weather conditions.
    Attributes:
        parent (Frame): The parent frame in which this frame is contained.
        name (str): The name of the frame.
        id (int): An identifier for the frame.
        n_lines (int): The number of lines to create in the frame, set to 20.
        frames_list (list): A list to hold the created frames and labels.
    """
    def __init__(self, parent, name, id, n_lines):
        super().__init__(parent, name, id, n_lines)

    def update(self, session : Session):
        """
        Updates the weather forecast labels based on the session data.
        
        :parama Session session: The session object containing weather data.
        """
        try:
            for i in range(session.number_weather_of_forecast_samples):
                frame, label = self.frames_list[i]
                label.config(text=session.weather_forecast_samples[i])
            for i in range(session.number_weather_of_forecast_samples, 20):
                frame, label = self.frames_list[i]
                label.config(text="")
        except: pass
