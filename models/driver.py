from utils.dictionnaries import *

class Driver:
    """
    Represents a driver in the racing simulation.
    Attributes:
        position (int): The current position of the driver in the race.
        tyre_wear (list): A list representing the wear level of the tyres.
        tyres (int): The type of tyres currently equipped.
        warnings (int): The number of warnings the driver has received.
        ERS_mode (int): The current ERS (Energy Recovery System) mode.
        ERS_pourcentage (int): The percentage of ERS charge remaining.
        fuelRemainingLaps (float): The estimated number of laps the driver can complete with the remaining fuel.
        fuelMix (int): The current fuel mix setting.
        numero (int): The driver's number.
        teamId (int): The ID of the driver's team.
        pit (int): The number of pit stops the driver has made.
        FrontLeftWingDamage (int): Damage level of the front left wing.
        FrontRightWingDamage (int): Damage level of the front right wing.
        tyres_temp_inner (list): Inner temperatures of the tyres [rear-left, rear-right, front-left, front-right].
        tyres_temp_surface (list): Surface temperatures of the tyres [rear-left, rear-right, front-left, front-right].
        tyresAgeLaps (int): The number of laps completed on the current set of tyres.
        lastLapTime (float): The time of the driver's last completed lap.
        currentSectors (list): The current sector times for the ongoing lap.
        lastLapSectors (list): The sector times of the last completed lap.
        bestLapSectors (list): The sector times of the driver's best lap.
        worldPositionX (float): The driver's X-coordinate in the world.
        worldPositionZ (float): The driver's Z-coordinate in the world.
        penalties (int): The number of penalties the driver has received.
        driverStatus (int): The current status of the driver (e.g., racing, in pits).
        bestLapTime (float): The time of the driver's best lap.
        drs (int): The DRS (Drag Reduction System) status.
        yourTelemetry (int): Indicates if telemetry data is available for the driver.
        speed (int): The current speed of the driver in km/h.
        rearWingDamage (int): Damage level of the rear wing.
        floorDamage (int): Damage level of the car's floor.
        diffuserDamage (int): Damage level of the diffuser.
        sidepodDamage (int): Damage level of the sidepods.
        name (str): The name of the driver.
        S200_reached (bool): Indicates if the driver has reached 200 km/h.
        currentLapTime (float): The time of the driver's current lap.
        setup_array (list): The car setup configuration.
        oval (Any): Reserved for oval-specific data (currently unused).
        Xmove (float): Movement in the X direction.
        Zmove (float): Movement in the Z direction.
        etiquette (str): A label or tag associated with the driver.
        aiControlled (int): Indicates if the driver is AI-controlled (-1 for unknown).
        hasRetired (bool): Indicates if the driver has retired from the race.
        speed_trap (int): The speed recorded at the speed trap in km/h.
        delta_to_leader (float): The time difference to the race leader in milliseconds.
        currentLapInvalid (int): Indicates if the current lap is invalid (1 for invalid, 0 for valid).
    """
    def __init__(self):
        self.position: int = 0
        self.tyre_wear = []
        self.tyres = 0
        self.warnings = 0
        self.ERS_mode = -1
        self.ERS_pourcentage = 0
        self.fuelRemainingLaps = 0
        self.fuelMix = 0
        self.numero = 0
        self.teamId = -1
        self.pit: int = 0
        self.FrontLeftWingDamage = 0
        self.FrontRightWingDamage = 0
        self.tyres_temp_inner = [0, 0, 0, 0]
        self.tyres_temp_surface = [0, 0, 0, 0]
        self.tyresAgeLaps = 0
        self.lastLapTime: float = 0
        self.currentSectors = [0] * 3
        self.lastLapSectors = [0] * 3
        self.bestLapSectors = [0] * 3
        self.worldPositionX = 0
        self.worldPositionZ = 0
        self.penalties = 0
        self.driverStatus = 0
        self.bestLapTime = 0
        self.drs: int = 0
        self.yourTelemetry: int = 0
        self.speed: int = 0
        self.rearWingDamage = 0
        self.floorDamage = 0
        self.diffuserDamage = 0
        self.sidepodDamage = 0
        self.name = " "
        self.S200_reached = True
        self.currentLapTime = 0
        self.setup_array = []
        self.oval = None
        self.oval = None
        self.Xmove = 0
        self.Zmove = 0
        self.etiquette = ""
        self.aiControlled = -1
        self.hasRetired = False
        self.speed_trap = 0
        self.delta_to_leader = 0
        self.currentLapInvalid = 1
        self.hasRetired = False
        self.speed_trap = 0
        self.delta_to_leader = 0
        self.currentLapInvalid = 1

    def __str__(self):
        return self.name + str(self.position)

    def printing(self, button_id, session):
        """
        Returns a formatted string representation of the driver's information based on the button ID.

        :param button_id: The ID of the button pressed to determine which information to display.
        :param session: The current session object containing session-specific data.
        :return: A formatted string with the driver's information.
        """
        if button_id == 0:  # Menu principal
            if session in [5, 6, 7, 8, 9, 13]: # Qualif
                return (
                    f"P{self.position}, {self.name} Lap :{conversion(self.currentLapTime, 2)} {ERS_dictionary[self.ERS_mode]},"
                    f"P{self.position}, {self.name} Lap :{conversion(self.currentLapTime, 2)} {ERS_dictionary[self.ERS_mode]},"
                    f" num = {self.numero} Last lap : {conversion(self.lastLapTime, 2)}"
                    f" Fastest lap : {conversion(self.bestLapTime, 2)} {pit_dictionary[self.pit]}")
            else: #Course
                return f"P{self.position}, {self.name} {self.tyresAgeLaps} tours " \
                       f"Gap :{'%.3f'%(self.delta_to_leader/1000)} {self.ERS_pourcentage}% {ERS_dictionary[self.ERS_mode]} " \
                       f"Warnings = {self.warnings} num = {self.numero} {pit_dictionary[self.pit]} {DRS_dict[self.drs]} "

        elif button_id == 1:  # Dégâts
            return (f"P{self.position}, {self.name} "
                    f"usure = {self.tyre_wear}, FW = [{self.FrontLeftWingDamage},  "
                    f"{self.FrontRightWingDamage}] | "
                    f"RW ={self.rearWingDamage} | "
                    f"floor = {self.floorDamage} | "
                    f"diffuser = {self.diffuserDamage} | "
                    f"sidepod = {self.sidepodDamage} | "
                    f"{pit_dictionary[self.pit]}")

        elif button_id == 2:  # Températures
            return (
                f"P{self.position}  {self.name},  RL : {self.tyres_temp_surface[0]}|{self.tyres_temp_inner[0]}, "
                f"P{self.position}  {self.name},  RL : {self.tyres_temp_surface[0]}|{self.tyres_temp_inner[0]}, "
                f"RR :{self.tyres_temp_surface[1]}|{self.tyres_temp_inner[1]} "
                f"FL : {self.tyres_temp_surface[2]}|{self.tyres_temp_inner[2]}, "
                f"FR : {self.tyres_temp_surface[3]}|{self.tyres_temp_inner[3]}, {pit_dictionary[self.pit]} ")

        elif button_id == 3:  # Laps
            return f"P{self.position}, {self.name} "+ \
            f"Current lap : {conversion(self.currentLapTime, 2)} [{', '.join('%.3f'%truc for truc in self.currentSectors)}] " + \
            f"Last lap : {conversion(self.lastLapTime, 2)} [{', '.join('%.3f'%truc for truc in self.lastLapSectors)}]  " + \
            f"Fastest lap : {conversion(self.bestLapTime, 2)} [{', '.join('%.3f'%truc for truc in self.bestLapSectors)}] "  + \
            f"{pit_dictionary[self.pit]}"

        elif button_id == 4:
            return f"P{self.position}, {self.name} ERS = {self.ERS_pourcentage}% | {ERS_dictionary[self.ERS_mode]}  " \
                   f"Fuel = {round(self.fuelRemainingLaps, 2)} tours | {self.penalties}s | {self.speed_trap}km/h"

    def is_not_on_lap(self):
        """
        Determines if the driver is not currently on a valid lap.
        A driver is considered not on a lap if:
        - The current lap time is zero.
        - The telemetry is available and the ERS mode is zero.
        - The current sector time is greater than the best lap sector time for the first sector.
        - The current sector time is greater than the best lap sector time for the second sector.
        :return: True if the driver is not on a valid lap, False otherwise.
        """
        return self.currentLapTime == 0 or (self.yourTelemetry==1 and self.ERS_mode == 0) or \
               (self.currentSectors[0] + 1 > self.bestLapSectors[0] != 0) or \
               (self.currentSectors[1] + 1 > self.bestLapSectors[1] != 0)

    def get_qualification_status(self, MnT_team):
        """
        Determines the qualification status color based on the driver's team and lap status.
        
        :param MnT_team: The team ID of the main telemetry team.
        :return: A color string representing the driver's qualification status.
        """
        if MnT_team is None:
            return "black"
        else:
            if self.teamId == MnT_team:
                return "blue"
            else:
                return "green" if self.is_not_on_lap() else "red"
