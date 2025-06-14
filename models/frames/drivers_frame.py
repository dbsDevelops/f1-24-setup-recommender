from ttkbootstrap import Label
from models.frames.base_frame import BaseFrame
from models.driver import Driver
from utils.dictionnaries import teams_color_dictionary, actual_tyre_compound, tyres_color_dictionnary

class DriversFrame(BaseFrame):
    """
    DriversFrame is a custom frame that displays the list of drivers and their tyre compounds.
    It inherits from BaseFrame and initializes a grid layout with a specified number of lines,
    each containing a label for the driver's information and a label for the tyre compound.

    Attributes:
        parent (Frame): The parent frame in which this frame is contained.
        name (str): The name of the frame.
        id (int): An identifier for the frame.
        number_of_lines (int): The number of lines to create in the frame, set to 20.
        tyre_labels (list): A list to hold the labels for tyre compounds.

    """
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 20)
        self.tyre_labels = []
        for i in range(self.number_of_lines):
            label = Label(self.frames_list[i][0], text="S", foreground="#FF0000", font="Helvetica 12")
            label.pack(side='left')
            self.frames_list[i][1].pack_forget()
            self.frames_list[i][1].pack(side='left')
            self.tyre_labels.append(label)
        # Insère le label pour les pneus

    def update_drivers(self, drivers: list[Driver], session):
        if not drivers:
            for i in range(self.number_of_lines):
                frame, label = self.frames_list[i]
                label.config(text="")
                self.tyre_labels[i].config(text="")
            return

        if session.Seance != 18:
            for index in range(min(22, len(drivers))):
                player = drivers[index]
                pos = player.position - 1
                if pos < 0 or pos >= len(self.frames_list):
                    continue
                frame, label = self.frames_list[pos]
                label.config(
                    text=player.printing(self.id, drivers, session.Seance),
                    foreground=teams_color_dictionary.get(player.teamId, "black")
                )
                self.tyre_labels[pos].config(
                    text=actual_tyre_compound[player.tyres],
                    foreground=tyres_color_dictionnary.get(player.tyres, "black")
                )
            for i in range(session.number_of_drivers, self.number_of_lines):
                frame, label = self.frames_list[i]
                label.config(text="")
                self.tyre_labels[i].config(text="")
        else:
            if len(drivers) >= 4:
                player = drivers[0]
                record = drivers[1]
                rival = drivers[3]

                frame, label = self.frames_list[0]
                label.config(
                    text=player.printing(self.id, drivers, session.Seance),
                    foreground=teams_color_dictionary.get(player.teamId, "black")
                )
                self.tyre_labels[0].config(
                    text=actual_tyre_compound[player.tyres],
                    foreground=tyres_color_dictionnary.get(player.tyres, "black")
                )

                frame, label = self.frames_list[1]
                label.config(
                    text=record.printing(self.id, drivers, session.Seance),
                    foreground=teams_color_dictionary.get(record.teamId, "black")
                )
                self.tyre_labels[1].config(
                    text=actual_tyre_compound[record.tyres],
                    foreground=tyres_color_dictionnary.get(record.tyres, "black")
                )

                frame, label = self.frames_list[2]
                label.config(
                    text=rival.printing(self.id, drivers, session.Seance),
                    foreground=teams_color_dictionary.get(rival.teamId, "black")
                )
                self.tyre_labels[2].config(
                    text=actual_tyre_compound[rival.tyres],
                    foreground=tyres_color_dictionnary.get(rival.tyres, "black")
                )

                for i in range(3, self.number_of_lines):
                    frame, label = self.frames_list[i]
                    label.config(text="")
                    self.tyre_labels[i].config(text="")
            else:
                for i in range(len(drivers)):
                    player = drivers[i]
                    frame, label = self.frames_list[i]
                    label.config(
                        text=player.printing(self.id, drivers, session.Seance),
                        foreground=teams_color_dictionary.get(player.teamId, "black")
                    )
                    self.tyre_labels[i].config(
                        text=actual_tyre_compound[player.tyres],
                        foreground=tyres_color_dictionnary.get(player.tyres, "black")
                    )
                for i in range(len(drivers), self.number_of_lines):
                    frame, label = self.frames_list[i]
                    label.config(text="")
                    self.tyre_labels[i].config(text="")
