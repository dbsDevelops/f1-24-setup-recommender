from ttkbootstrap import Label
from models.frames.base_frame import BaseFrame
from models.driver import Driver
from utils.dictionnaries import teams_color_dictionary, actual_tyre_compound, tyres_color_dictionnary

class DriversFrame(BaseFrame):
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 20)
        self.label_tyres = []
        for i in range(self.n_lines):
            label = Label(self.liste_frame[i][0], text="S", foreground="#FF0000", font="Helvetica 12")
            label.pack(side='left')
            self.liste_frame[i][1].pack_forget()
            self.liste_frame[i][1].pack(side='left')
            self.label_tyres.append(label)
        # Insère le label pour les pneus

    def update_drivers(self, drivers: list[Driver], session):
        if not drivers:
            for i in range(self.n_lines):
                frame, label = self.liste_frame[i]
                label.config(text="")
                self.label_tyres[i].config(text="")
            return

        if session.Seance != 18:
            for index in range(min(22, len(drivers))):
                player = drivers[index]
                pos = player.position - 1
                if pos < 0 or pos >= len(self.liste_frame):
                    continue
                frame, label = self.liste_frame[pos]
                label.config(
                    text=player.printing(self.id, drivers, session.Seance),
                    foreground=teams_color_dictionary.get(player.teamId, "black")
                )
                self.label_tyres[pos].config(
                    text=actual_tyre_compound[player.tyres],
                    foreground=tyres_color_dictionnary.get(player.tyres, "black")
                )
            for i in range(session.number_of_drivers, self.n_lines):
                frame, label = self.liste_frame[i]
                label.config(text="")
                self.label_tyres[i].config(text="")
        else:
            if len(drivers) >= 4:
                player = drivers[0]
                record = drivers[1]
                rival = drivers[3]

                frame, label = self.liste_frame[0]
                label.config(
                    text=player.printing(self.id, drivers, session.Seance),
                    foreground=teams_color_dictionary.get(player.teamId, "black")
                )
                self.label_tyres[0].config(
                    text=actual_tyre_compound[player.tyres],
                    foreground=tyres_color_dictionnary.get(player.tyres, "black")
                )

                frame, label = self.liste_frame[1]
                label.config(
                    text=record.printing(self.id, drivers, session.Seance),
                    foreground=teams_color_dictionary.get(record.teamId, "black")
                )
                self.label_tyres[1].config(
                    text=actual_tyre_compound[record.tyres],
                    foreground=tyres_color_dictionnary.get(record.tyres, "black")
                )

                frame, label = self.liste_frame[2]
                label.config(
                    text=rival.printing(self.id, drivers, session.Seance),
                    foreground=teams_color_dictionary.get(rival.teamId, "black")
                )
                self.label_tyres[2].config(
                    text=actual_tyre_compound[rival.tyres],
                    foreground=tyres_color_dictionnary.get(rival.tyres, "black")
                )

                for i in range(3, self.n_lines):
                    frame, label = self.liste_frame[i]
                    label.config(text="")
                    self.label_tyres[i].config(text="")
            else:
                for i in range(len(drivers)):
                    player = drivers[i]
                    frame, label = self.liste_frame[i]
                    label.config(
                        text=player.printing(self.id, drivers, session.Seance),
                        foreground=teams_color_dictionary.get(player.teamId, "black")
                    )
                    self.label_tyres[i].config(
                        text=actual_tyre_compound[player.tyres],
                        foreground=tyres_color_dictionnary.get(player.tyres, "black")
                    )
                for i in range(len(drivers), self.n_lines):
                    frame, label = self.liste_frame[i]
                    label.config(text="")
                    self.label_tyres[i].config(text="")
