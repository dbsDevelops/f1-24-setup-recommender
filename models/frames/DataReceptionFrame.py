from models.frames.BaseFrame import BaseFrame
from utils.dictionnaries import packets

class DataReceptionFrame(BaseFrame):
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 15)

    def update(self, packet_received):
        for i in range(self.n_lines):
            frame, label = self.liste_frame[i]
            label.config(text=f"{packets[i]} : {packet_received[i]}/s")
