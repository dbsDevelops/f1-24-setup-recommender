from ttkbootstrap import Notebook, Frame, Canvas, Menu, Label
import helpers.packets.packet_manager as pm
from models.frames.drivers_frame import DriversFrame
from models.frames.data_reception_frame import DataReceptionFrame
from models.frames.weather_forecast_frame import WeatherForecastFrame

MAIN_MENU = 0
DAMAGE = 1
TEMPERATURES = 2
LAPS = 3
ERS_AND_FUEL = 4
MAP = 5
WEATHER_FORECAST = 6
DATA_RECEPTION = 7

class WindowManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.top_frame = Frame(main_window)
        self.main_frame = Frame(main_window)
        self.map_canvas = None
        self.top_label1 = Label(self.top_frame, text="Circuit ", font=("Arial", 24))
        self.top_label2 = Label(self.top_frame, text="", font=("Arial", 24), width=10)

        self._init_ui()
        self._init_menu()

    def _init_ui(self):
        """Initializes the UI components."""
        self.main_window.title("Telemetry Application")
        self.main_window.geometry("1480x800")

        # Ensure main window resizes properly
        self.main_window.columnconfigure(0, weight=1)
        self.main_window.rowconfigure(0, weight=0)  # Top frame does not expand
        self.main_window.rowconfigure(1, weight=1)  # Main frame should expand

        self.top_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        # Allow the main frame to expand
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        notebook = Notebook(self.main_frame)
        notebook.grid(row=0, column=0, sticky="nsew")

        # Add frames to notebook
        pm.frames.append(DriversFrame(notebook, "Main Menu", MAIN_MENU))
        pm.frames.append(DriversFrame(notebook, "Damage", DAMAGE))
        pm.frames.append(DriversFrame(notebook, "Temperatures", TEMPERATURES))
        pm.frames.append(DriversFrame(notebook, "Laps", LAPS))
        pm.frames.append(DriversFrame(notebook, "ERS & Fuel", ERS_AND_FUEL))

        map_frame = Frame(notebook)
        pm.frames.append(map_frame)
        map_frame.pack(expand=True, fill="both")
        self.map_canvas = Canvas(map_frame)
        self.map_canvas.pack(expand=True, fill='both')

        pm.frames.append(WeatherForecastFrame(notebook, "Weather Forecast", WEATHER_FORECAST, 20))
        pm.frames.append(DataReceptionFrame(notebook, "Packet Reception", DATA_RECEPTION))

        # Add tabs to notebook
        for i, frame in enumerate(pm.frames):
            notebook.add(frame, text=frame.name if i != MAP else "Map")

        # Configure UI elements
        self.top_label1.pack(side='left', padx=10)
        self.top_label2.pack(side='right', padx=10)

        self.main_window.protocol("WM_DELETE_WINDOW", self.close_window)

    def _init_menu(self):
        """Initializes the menu bar independently."""
        menubar = Menu(self.main_window)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="PORT Selection", command=pm.port_selection)
        filemenu.add_command(label="UDP Redirect", command=pm.UDP_Redirect)
        menubar.add_cascade(label="Settings", menu=filemenu)

        # Set menu bar on the main window
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