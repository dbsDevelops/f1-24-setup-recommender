from models.frames.BaseFrame import BaseFrame
from models.Session import Session

class WeatherForecastFrame(BaseFrame):
    def __init__(self, parent, name, id, n_lines):
        super().__init__(parent, name, id, n_lines)

    def update(self, session : Session):
        try:
            for i in range(session.nb_weatherForecastSamples):
                frame, label = self.liste_frame[i]
                label.config(text=session.weatherList[i])
            for i in range(session.nb_weatherForecastSamples, 20):
                frame, label = self.liste_frame[i]
                label.config(text="")
        except: pass
