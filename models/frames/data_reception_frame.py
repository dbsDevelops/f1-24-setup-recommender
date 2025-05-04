from models.frames.base_frame import BaseFrame
from utils.dictionnaries import packet_ids

class DataReceptionFrame(BaseFrame):
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 15)

    def update(self, packet_received):
        for i in range(self.n_lines):
            frame, label = self.liste_frame[i]
            label.config(text=f"{packet_ids[i]} : {packet_received[i]}/s")
