from models.frames.base_frame import BaseFrame
from utils.dictionnaries import packet_ids

class DataReceptionFrame(BaseFrame):
    """
    DataReceptionFrame is a custom frame that displays the number of packets received per type.
    It inherits from BaseFrame and initializes a grid layout with a specified number of lines,
    each containing a label to show the packet count.
    Attributes:
        parent (Frame): The parent frame in which this frame is contained.
        name (str): The name of the frame.
        id (int): An identifier for the frame.
        number_of_lines (int): The number of lines to create in the frame, set to 15.
        frames_list (list): A list to hold the created frames and labels.
    """
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 15)

    def update(self, packet_received):
        for i in range(self.number_of_lines):
            frame, label = self.frames_list[i]
            label.config(text=f"{packet_ids[i]} : {packet_received[i]}/s")
