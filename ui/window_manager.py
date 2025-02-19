from ttkbootstrap import Notebook, Frame, Canvas, Menu, Label
import helpers.packets.PacketManager as pm
from models.frames.DriversFrame import DriversFrame
from models.frames.DataReceptionFrame import DataReceptionFrame
from models.frames.WeatherForecastFrame import WeatherForecastFrame

class WindowManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.top_frame = Frame(main_window)
        self.main_frame = Frame(main_window)
        self.map_canvas = None
        self.top_label1 = Label(self.top_frame, text="Course ", font=("Arial", 24))
        self.top_label2 = Label(self.top_frame, text="", font=("Arial", 24), width=10)

        self._init_ui()

    def _init_ui(self):
        """Initializes the UI components."""
        self.main_window.title("Telemetry Application")
        self.main_window.geometry("1480x800")

        self.top_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        notebook = Notebook(self.main_frame)
        notebook.pack(expand=True, fill="both")

        # Add frames to notebook
        pm.frames.append(DriversFrame(notebook, "Main Menu", 0))
        pm.frames.append(DriversFrame(notebook, "Damage", 1))
        pm.frames.append(DriversFrame(notebook, "Temperatures", 2))
        pm.frames.append(DriversFrame(notebook, "Laps", 3))
        pm.frames.append(DriversFrame(notebook, "ERS & Fuel", 4))

        map_frame = Frame(notebook)
        pm.frames.append(map_frame)
        map_frame.pack(expand=True, fill="both")
        self.map_canvas = Canvas(map_frame)
        self.map_canvas.pack(expand=True, fill='both')

        pm.frames.append(WeatherForecastFrame(notebook, "Weather Forecast", 6, 20))
        pm.frames.append(DataReceptionFrame(notebook, "Packet Reception", 7))

        # Add tabs to notebook
        for i, frame in enumerate(pm.frames):
            notebook.add(frame, text=frame.name if i != 5 else "Map")

        # Configure UI elements
        self.top_label1.place(relx=0.0, rely=0.5, anchor='w')
        self.top_label2.place(relx=1, rely=0.5, anchor='e', relheight=1)

        self.main_window.protocol("WM_DELETE_WINDOW", self.close_window)

        # Configure menu bar
        menubar = Menu(self.main_window)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="PORT Selection", command=pm.port_selection)
        filemenu.add_command(label="UDP Redirect", command=pm.UDP_Redirect)
        menubar.add_cascade(label="Settings", menu=filemenu)
        self.main_window.config(menu=menubar)

    def update_packet_reception(self, packet_received):
        """Updates UI with packet reception data."""
        pm.frames[7].update(packet_received)

    def refresh_ui(self):
        """Refresh UI components."""
        self.main_window.update()
        self.main_window.update_idletasks()

    def close_window(self):
        """Handles window closing event."""
        self.main_window.quit()