from ttkbootstrap import Label
from models.frames.BaseFrame import BaseFrame
from models.Player import Driver
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

    def update(self, drivers:list[Driver], session):
        if session.Seance != 18:
            for i in range(session.number_of_drivers):
                player = drivers[i]
                frame, label = self.liste_frame[player.position-1]
                label.config(text=player.printing(self.id, drivers, session.Seance), foreground=teams_color_dictionary[player.teamId])
                self.label_tyres[player.position-1].config(text=actual_tyre_compound[player.tyres], foreground=tyres_color_dictionnary[player.tyres])
            for i in range(session.number_of_drivers, self.n_lines):
                label.config(text="")
                self.label_tyres[i].config(text="")
        else:
            player = drivers[0]
            record = drivers[1]
            rival = drivers[3]

            frame, label = self.liste_frame[0]
            label.config(text=player.printing(self.id, drivers, session.Seance), foreground=teams_color_dictionary[player.teamId])
            self.label_tyres[0].config(text=actual_tyre_compound[player.tyres], foreground=tyres_color_dictionnary[player.tyres])

            frame, label = self.liste_frame[1]
            label.config(text=record.printing(self.id, drivers, session.Seance), foreground=teams_color_dictionary[record.teamId])
            self.label_tyres[1].config(text=actual_tyre_compound[record.tyres], foreground=tyres_color_dictionnary[record.tyres])

            frame, label = self.liste_frame[2]
            label.config(text=rival.printing(self.id, drivers, session.Seance), foreground=teams_color_dictionary[rival.teamId])
            self.label_tyres[2].config(text=actual_tyre_compound[rival.tyres], foreground=tyres_color_dictionnary[rival.tyres])

            for i in range(3, self.n_lines):
                frame, label = self.liste_frame[i]
                label.config(text="")
                self.label_tyres[i].config(text="")
