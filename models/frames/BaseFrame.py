from ttkbootstrap import Frame, Label
from models.Player import Driver
from utils.dictionnaries import teams_color_dictionary, packets, actual_tyre_compound, tyres_color_dictionnary
from models.Session import Session


class BaseFrame(Frame): 
    def __init__(self, parent, name, id, number_of_lines):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.name = name
        self.id = id
        self.n_lines = number_of_lines
        self.liste_frame = []
        for i in range(number_of_lines):
            frame = Frame(self)
            frame.grid(row=i, column=0, sticky="nsew", pady=2, padx=5)
            label = Label(frame, text="Driver"+str(i), font="Helvetica 12")
            label.pack(side='left')
            self.liste_frame.append((frame, label))
        self.pack(expand=True, fill="both")
