from ttkbootstrap import Frame, Label

class BaseFrame(Frame): 
    """
    BaseFrame is a custom frame that serves as a template for other frames in the application.
    It initializes a grid layout with a specified number of lines, each containing a label.
    Attributes:
        parent (Frame): The parent frame in which this frame is contained.
        name (str): The name of the frame.
        id (int): An identifier for the frame.
        number_of_lines (int): The number of lines to create in the frame.
        frames_list (list): A list to hold the created frames and labels.
    """
    def __init__(self, parent, name, id, number_of_lines):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.name = name
        self.id = id
        self.number_of_lines = number_of_lines
        self.frames_list = []
        for i in range(number_of_lines):
            frame = Frame(self)
            frame.grid(row=i, column=0, sticky="nsew", pady=2, padx=5)
            label = Label(frame, text="Driver"+str(i), font="Helvetica 12")
            label.pack(side='left')
            self.frames_list.append((frame, label))
        self.pack(expand=True, fill="both")
