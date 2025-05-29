from models.session import Session
from models.driver import Driver
from utils.dictionnaries import *
import json
import time
from ttkbootstrap import Toplevel, LEFT, Entry, IntVar, Label
from tkinter import Message, Checkbutton, Button
from models.frames.base_frame import BaseFrame
import traceback

drivers: list[Driver] = []
session: Session = Session()
created_map = False
width_points = 6
frames = []
menu_buttons: list = ["Main Menu", "Damage", "Temperatures", "Laps", "Map", "ERS & Fuel", "Weather Forecast",
                              "Packet Reception"]

def update_motion(packet, map_canvas, *args):  # Packet 0
    """
    Updates the motion data of drivers based on the received packet.
    This function updates the world position of each driver and calculates their movement
    based on the difference between the current and previous positions.
    It also attempts to update the map canvas with the new positions of the drivers.
    If the map update fails, it tries to recreate the map.

    :param packet: The packet containing motion data for each driver.
    :param map_canvas: The canvas where the map is displayed.
    """
    for index in range(min(22, len(drivers))):
        if drivers[index].worldPositionX != 0:
            drivers[index].Xmove = packet.m_carMotionData[index].m_worldPositionX - drivers[index].worldPositionX
            drivers[index].Zmove = packet.m_carMotionData[index].m_worldPositionZ - drivers[index].worldPositionZ
        drivers[index].worldPositionX = packet.m_carMotionData[index].m_worldPositionX
        drivers[index].worldPositionZ = packet.m_carMotionData[index].m_worldPositionZ
    try:
        update_map(map_canvas)
    except Exception as e:
        try:
            traceback.print_exc()
            create_map(map_canvas)
        except Exception as e :
            pass

def update_session(packet, top_frame1, top_frame2, screen, map_canvas):  # Packet 1
    """
    Updates the session data based on the received packet.
    This function updates various session parameters such as track temperature, air temperature,
    number of laps, time left in the session, track ID, session type, marshal zones, safety car status,
    track length, and weather forecast samples. It also checks if the track or session type has changed,
    and if so, it deletes the existing map and creates a new one if necessary.
    Finally, it updates the title of the top frames and the sixth frame.

    :param packet: The packet containing session data.
    :param top_frame1: The first top frame where the session title is displayed.
    :param top_frame2: The second top frame where the safety car status is displayed.
    :param screen: The main application window.
    :param map_canvas: The canvas where the map is displayed.
    """
    global created_map
    session.track_temperature = packet.m_weatherForecastSamples[0].m_trackTemperature
    session.air_temperature = packet.m_weatherForecastSamples[0].m_airTemperature
    session.number_of_laps = packet.m_totalLaps
    session.time_left = packet.m_sessionTimeLeft
    if session.track != packet.m_trackId or session.session_id != packet.m_sessionType: # Track or session has changed
        session.track = packet.m_trackId
        delete_map(map_canvas)
    session.session_id = packet.m_sessionType
    session.marshal_zones = packet.m_marshalZones  # Array[21]
    session.marshal_zones[0].m_zone_start = session.marshal_zones[0].m_zoneStart - 1
    session.num_marshal_zones = packet.m_numMarshalZones
    session.safety_car_status = packet.m_safetyCarStatus
    session.track_length = packet.m_trackLength
    session.clear_slot()
    if packet.m_numWeatherForecastSamples != session.number_weather_of_forecast_samples:
        session.number_weather_of_forecast_samples = packet.m_numWeatherForecastSamples
        #Reconstruire le tableau 
    for i in range(session.number_weather_of_forecast_samples):
        slot = packet.m_weatherForecastSamples[i]
        session.add_slot(slot)
    update_title(top_frame1, top_frame2, screen)
    update_frame6()

def update_lap_data(packet):  # Packet 2
    """
    Updates the lap data for each driver based on the received packet.
    This function iterates through the lap data array in the packet and updates each driver's
    position, last lap time, pit status, driver status, penalties, warnings, speed trap,
    current lap time, delta to leader, and current lap invalid status.
    It also checks if the driver has completed a new lap and updates their last lap sectors accordingly.
    If a driver's best lap time is updated, it checks if it is the best lap time of the session
    and updates the session's best lap time and index of the driver with the best lap time.

    :param packet: The packet containing lap data for each driver.
    """
    mega_array = packet.m_lapData
    for index in range(min(22, len(drivers))):
        element = mega_array[index]
        player = drivers[index]
        player.position = element.m_carPosition
        player.lastLapTime = round(element.m_lastLapTimeInMS, 3)
        player.pit = element.m_pitStatus
        player.driverStatus = element.m_driverStatus
        player.penalties = element.m_penalties
        player.warnings = element.m_cornerCuttingWarnings
        player.speed_trap = round(element.m_speedTrapFastestSpeed, 2)
        player.currentLapTime = element.m_currentLapTimeInMs
        player.delta_to_leader=element.m_deltaToCarInFrontMSPart
        player.currentLapInvalid = element.m_currentLapInvalid

        if element.m_sector1_time_in_ms == 0 and player.currentSectors[0] != 0:  # On attaque un nouveau tour
            player.lastLapSectors = player.currentSectors[:]
            player.lastLapSectors[2] = player.lastLapTime / 1_000 - player.lastLapSectors[0] - player.lastLapSectors[1]

        player.currentSectors = [element.m_sector1TimeInMS / 1000, element.m_sector2TimeInMS / 1000, 0]
        if player.bestLapTime > element.m_lastLapTimeInMS != 0 or player.bestLapTime == 0:
            player.bestLapTime = element.m_lastLapTimeInMS
            player.bestLapSectors = player.lastLapSectors[:]
        if player.bestLapTime < session.bestLapTime and element.m_lastLapTimeInMS != 0 or player.bestLapTime == 0:
            session.bestLapTime = player.bestLapTime
            session.indexOfBestLapTime = index
        if element.m_carPosition == 1:
            session.currentLap = mega_array[index].m_currentLapNum
            session.previousLap = session.currentLap - 1

def warnings(packet):  # Packet 3
    """
    Processes warnings and events related to the session.
    This function checks the event string code in the packet to determine if there are any
    start lights, lights out, or retirements. It updates the session state accordingly and
    resets the drivers' states when the lights go out.

    :param packet: The packet containing event details.
    """
    if packet.m_eventStringCode[3] == 71 and packet.m_eventDetails.m_startLights.m_numLights >= 2: # Starts lights : STLG
        session.is_formation_lap_completed = True
        print(f"{packet.m_eventDetails.m_startLights.m_numLights} red lights ")
    elif packet.m_eventStringCode[0] == 76 and session.is_formation_lap_completed: #Lights out : LGOT
        print("Lights out !")
        session.is_formation_lap_completed = False
        session.start_time = time.time()
        for driver in drivers:
            driver.S200_reached = False
            driver.warnings = 0
            driver.lastLapSectors = [0] * 3
            driver.bestLapSectors = [0] * 3
            driver.lastLapTime = 0
            driver.currentSectors = [0] * 3
            driver.bestLapTime = 0
    elif packet.m_eventStringCode[2] == 82:
        drivers[packet.m_eventDetails.m_vehicleIdx].hasRetired = True

def update_participants(packet):  # Packet 4
    """
    Updates the participants in the session based on the received packet.
    This function iterates through the participants in the packet and updates each driver's
    setup array with the corresponding participant data. 
    It ensures that only the first 22 drivers are updated, 
    even if more participants are provided in the packet. 

    :param packet: The packet containing participant data.
    """
    for index in range(min(22, len(drivers))):
        element = packet.m_participants[index]
        driver = drivers[index]
        driver.numero = element.m_race_number
        driver.teamId = element.m_team_id
        driver.aiControlled = element.m_ai_controlled
        driver.yourTelemetry = element.m_your_telemetry
        try:
            driver.name = element.m_name.decode("utf-8")
        except:
            driver.name = element.m_name
        session.number_of_drivers = packet.m_numActiveCars
        if driver.name in ['Player', 'Driver']:
            driver.name = teams[driver.teamId] + "#" + str(driver.numero)
    update_frame(frames, drivers, session)

def update_car_setups(packet): # Packet 5
    """
    Updates the car setups for each driver based on the received packet.
    This function iterates through the car setups in the packet and updates each driver's
    setup array with the corresponding setup data. 
    It ensures that only the first 22 drivers are updated, 
    even if more setups are provided in the packet.
    
    :param packet: The packet containing car setup data for each driver.
    """
    array = packet.m_carSetups
    for index in range(min(22, len(drivers))):
        drivers[index].setup_array = array[index]

def update_car_telemetry(packet):  # Packet 6
    """
    Updates the car telemetry data for each driver based on the received packet.
    This function iterates through the car telemetry data in the packet and updates each driver's
    telemetry attributes such as DRS status, tyre temperatures, and speed.
    It also checks if the driver has reached a speed of 200 km/h and prints the time taken to reach that speed.
    Finally, it updates the frame with the new telemetry data.

    :param packet: The packet containing car telemetry data for each driver.
    """
    for index in range(min(22, len(drivers))):
        element = packet.m_carTelemetryData[index]
        driver = drivers[index]
        driver.drs = element.m_drs
        driver.tyres_temp_inner = element.m_tyresInnerTemperature
        driver.tyres_temp_surface = element.m_tyresSurfaceTemperature
        driver.speed = element.m_speed
        if driver.speed >= 200 and not driver.S200_reached:
            print(f"{driver.position} {driver.name}  = {time.time() - session.start_time}")
            driver.S200_reached = True
    update_frame(frames, drivers, session)

def update_car_status(packet):  # Packet 7
    """
    Updates the car status data for each driver based on the received packet.
    This function iterates through the car status data in the packet and updates each driver's
    fuel mix, fuel remaining laps, tyre age in laps, visual tyre compound, ERS mode, and ERS percentage.
    It ensures that only the first 22 drivers are updated,
    even if more car status data is provided in the packet.

    :param packet: The packet containing car status data for each driver.
    """
    for index in range(min(22, len(drivers))):
        element = packet.m_carStatusData[index]
        driver = drivers[index]
        driver.fuelMix = element.m_fuel_mix
        driver.fuelRemainingLaps = element.m_fuel_remaining_laps
        driver.tyresAgeLaps = element.m_tyres_age_laps
        if driver.tyres != element.m_visual_tyre_compound:
            driver.tyres = element.m_visual_tyre_compound
        driver.ERS_mode = element.m_ers_deploy_mode
        driver.ERS_pourcentage = round(element.m_ers_store_energy / 40_000)
    update_frame(frames, drivers, session)

def update_car_damage(packet):  # Packet 10
    """
    Updates the car damage data for each driver based on the received packet.
    This function iterates through the car damage data in the packet and updates each driver's
    tyre wear, wing damage, floor damage, diffuser damage, and sidepod damage.
    It ensures that only the first 22 drivers are updated,
    even if more car damage data is provided in the packet.

    :param packet: The packet containing car damage data for each driver.
    """
    # Only update as many drivers as we actually have in our drivers list.
    for index in range(min(22, len(drivers))):
        element = packet.m_carDamageData[index]
        print('Driver Index :', index)
        driver = drivers[index]
        driver.tyre_wear = '[' + ', '.join('%.2f' % x for x in element.m_tyres_wear) + ']'
        driver.FrontLeftWingDamage = element.m_front_left_wing_damage
        driver.FrontRightWingDamage = element.m_front_right_wing_damage
        driver.rearWingDamage = element.m_rear_wing_damage
        driver.floorDamage = element.m_floor_damage
        driver.diffuserDamage = element.m_diffuser_damage
        driver.sidepodDamage = element.m_sidepod_damage
    update_frame(frames, drivers, session)

def nothing(packet):# Packet 8, 9, 11, 12, 13
    """
    Placeholder function for packets that do not require any action.
    This function is used to handle packets that are not currently implemented or do not require any updates.
    
    :param packet: The packet that does not require any action.
    """
    pass

def create_map(map_canvas):
    """
    Creates the map for the current session based on the track data.
    This function reads the track data from a file, extracts the racing line,
    and draws the segments of the track on the map canvas.
    It also initializes the positions of the drivers on the map.
    The map is created only if it has not been created yet.
    If the map has already been created, it will not recreate it.

    :param map_canvas: The canvas where the map will be drawn.
    """
    cmi = 1
    L0, L1 = [], []
    L = []
    name, d, x_const, z_const = track_ids[session.track]
    with open(f"tracks/{name}_2020_racingline.txt", "r") as file:
        for index, line in enumerate(file):
            if index not in [0, 1]:
                dist, z, x, y, _, _ = line.strip().split(",")
                if cmi == 1:
                    L0.append((float(z) / d + x_const, float(x) / d + z_const))
                elif cmi == session.num_marshal_zones:
                    L1.append((float(z) / d + x_const, float(x) / d + z_const))
                else:
                    L.append((float(z) / d + x_const, float(x) / d + z_const))
                if (float(dist) / session.track_length) > session.marshal_zones[cmi].m_zone_start and cmi!=session.num_marshal_zones:
                    if cmi != 1:
                        session.segments.append(map_canvas.create_line(L, width=3))
                        L = []
                    cmi +=1
    session.segments.insert(0, map_canvas.create_line(L1+L0, width=3))
    for i in range(20):
        driver = drivers[i]
        if session.session_id == 18 and i!=0:
            driver.oval = map_canvas.create_oval(-1000 / d + x_const - width_points,
                                                -1000 / d + z_const - width_points,
                                                -1000 / d + x_const + width_points,
                                                -1000 / d + z_const + width_points, outline="")
        else:
            driver.oval = map_canvas.create_oval(driver.worldPositionX / d + x_const - width_points,
                                                driver.worldPositionZ / d + z_const - width_points,
                                                driver.worldPositionX / d + x_const + width_points,
                                                driver.worldPositionZ / d + z_const + width_points, outline="")
            
            driver.etiquette = map_canvas.create_text(driver.worldPositionX / d + x_const + 25,
                                                    driver.worldPositionZ / d + z_const - 25,
                                                    text=driver.name, font=("Cousine", 13))
            map_canvas.moveto(driver.oval, driver.worldPositionX / d + x_const - width_points,
                                driver.worldPositionZ / d + z_const - width_points)

def delete_map(map_canvas):
    """
    Deletes the existing map segments and driver ovals from the map canvas.
    This function iterates through the segments and driver ovals, removing them from the canvas.
    It also clears the segments list and resets the oval attributes of each driver to None.
    This is typically called when the track or session changes to ensure a fresh map can be created.

    :param map_canvas: The canvas from which the map segments and driver ovals will be deleted.
    """
    for element in session.segments:
        map_canvas.delete(element)
    session.segments = []
    for driver in drivers:
        map_canvas.delete(driver.oval)
        map_canvas.delete(driver.etiquette)
        driver.oval = None

def update_map(map_canvas):
    """
    Updates the positions of drivers on the map canvas based on their current movement.
    This function moves each driver's oval and etiquette text according to their movement vectors.
    It also updates the color of the ovals based on the driver's team ID 
    and updates the colors of the marshal zone segments.
    If the session has any yellow flags, it sets the `anyYellow` attribute to True.
    This function is typically called after motion data has been updated to reflect the new positions of drivers.

    :param map_canvas: The canvas where the map is displayed.
    """
    _, d, x, z = track_ids[session.track]
    for driver in drivers:
        if driver.position != 0:
            map_canvas.move(driver.oval, driver.Xmove / d, driver.Zmove / d)
            map_canvas.itemconfig(driver.oval, fill=teams_color_dictionary[driver.teamId])
            map_canvas.move(driver.etiquette, driver.Xmove / d, driver.Zmove / d)
            map_canvas.itemconfig(driver.etiquette, fill=teams_color_dictionary[driver.teamId], text=driver.name)
    for i in range(len(session.segments)):
        map_canvas.itemconfig(session.segments[i], fill=flag_colours[session.marshal_zones[i].m_zoneFlag])
    session.is_yellow_flag_active = any(item.m_zoneFlag==3 for item in session.marshal_zones)
        
def initialize_driver_pool():
    """
    Initializes a pool of 22 drivers with default values.
    This function creates a list of Driver objects, each representing a driver in the session.
    It is typically called at the start of the application to ensure that there are enough driver objects
    available for the telemetry data that will be received.
    """
    for _ in range(22):
        drivers.append(Driver())

def UDP_Redirect(dictionnary_settings, listener, port):
    """
    Opens a window to configure UDP redirection settings.
    This function creates a Toplevel window where the user can enable or disable UDP redirection,
    enter an IP address, and specify a port for redirection.
    It validates the input for the port and IP address, and updates the listener settings accordingly.
    If the input is valid, it saves the settings to a file and closes the window.
    If the input is invalid, it displays an error message.

    :param dictionnary_settings: Dictionary containing application settings.
    :param listener: The UDP listener object that will be updated with the new settings.
    :param PORT: A list containing the current port number as a string, which will be updated with the new port.
    """
    win = Toplevel()
    win.grab_set()
    win.wm_title("UDP Redirect")
    var1 = IntVar(value=dictionnary_settings["redirect_active"])
    checkbutton = Checkbutton(win, text="UDP Redirect", variable=var1, onvalue=1, offvalue=0, font=("Arial", 16))
    checkbutton.grid(row=0, column=0, sticky="W", padx=30, pady=10)
    Label(win, text="IP Address", font=("Arial", 16), justify=LEFT).grid(row=1, column=0, pady=10)
    e1 = Entry(win, font=("Arial", 16))
    e1.insert(0, dictionnary_settings["ip_adress"])
    e1.grid(row=2, column=0)
    Label(win, text="Port", font=("Arial", 16)).grid(row=3, column=0, pady=(10, 5))
    e2 = Entry(win, font=("Arial", 16))
    e2.insert(0, dictionnary_settings["redirect_port"])
    e2.grid(row=4, column=0, padx=30)

    def button():
        redirect_port = e2.get()
        if not redirect_port.isdigit() or not 1000 <= int(redirect_port) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=6, column=0)
        elif not valid_ip_address(e1.get()):
            Label(win, text="IP Address incorrect", foreground="red", font=("Arial", 16)).grid(
                row=6, column=0)
        else:
            listener.port = int(port[0])
            listener.redirect = int(var1.get())
            listener.adress = e1.get()
            listener.redirect_port = int(e2.get())
            Label(win, text="").grid(row=3, column=0)

            dictionnary_settings["redirect_active"] = var1.get()
            dictionnary_settings["ip_adress"] = e1.get()
            dictionnary_settings["redirect_port"] = e2.get()
            with open("settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda e: button())
    win.bind('<KP_Enter>', lambda e: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=5, column=0, pady=10)

def port_selection(dictionnary_settings, listener, port):
    """
    Opens a window to select the port for receiving UDP packets.
    This function creates a Toplevel window where the user can enter a port number.
    It validates the input to ensure that the port is an integer between 1000 and 65536.
    If the input is valid, it updates the listener's port and saves the settings to a file.
    If the input is invalid, it displays an error message.

    :param dictionnary_settings: Dictionary containing application settings.
    :param listener: The UDP listener object that will be updated with the new port.
    :param PORT: A list containing the current port number as a string, which will be updated with the new port.
    """
    win = Toplevel()
    win.grab_set()
    win.wm_title("Port Selection")
    Label(win, text="Receiving PORT :", font=("Arial", 16)).grid(row=0, column=0, sticky="we", padx=30)
    e = Entry(win, font=("Arial", 16))
    e.insert(0, dictionnary_settings["port"])
    e.grid(row=1, column=0, padx=30)

    def button():
        port[0] = e.get()
        if not port[0].isdigit() or not 1000 <= int(port[0]) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=3, column=0)
        else:
            listener.socket.close()
            listener.port = int(port[0])
            listener.reset()
            Label(win, text="").grid(row=3, column=0)
            dictionnary_settings["port"] = str(port[0])
            with open("settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda e: button())
    win.bind('<KP_Enter>', lambda e: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=2, column=0, pady=10)

def update_title(top_label1, top_label2, screen):
    """
    Updates the title and safety car status labels in the top frame.
    This function sets the text of the top labels based on the current session data.
    It updates the title label with the session title and the safety car status label
    with the corresponding safety car status text.
    It also changes the background color of the safety car status label based on the safety car status.
    If the safety car status is 4 (full safety car), it sets the background to red.
    If the safety car status is not 0 or there are any yellow flags, it sets the background to gold.
    Otherwise, it sets the background to the default screen background color.

    :param top_label1: The label displaying the session title.
    :param top_label2: The label displaying the safety car status.
    :param screen: The main application window, used to get the default background color.
    """
    top_label1.config(text=session.title_display())
    top_label2.config(text=safety_car_status[session.safety_car_status])
    if session.safety_car_status == 4:
        top_label2.config(background="red")
    elif session.safety_car_status !=0 or session.is_yellow_flag_active:
        top_label2.config(background="#FFD700")
    else:
        top_label2.config(background=screen.cget("background"))

def update_frame(frames : list[BaseFrame], drivers, session):
    """
    Updates the frames with the current drivers and session data.
    This function iterates through the first five frames and calls their update_drivers method
    to refresh the displayed data based on the current drivers and session information.
    It is typically called after processing a packet to ensure that the UI reflects the latest data.

    :param frames: List of frames to be updated.
    :param drivers: List of Driver objects containing the current state of each driver.
    :param session: The current session object containing session data.
    """
    for i in range(5):
        frames[i].update_drivers(drivers, session)

def update_frame6():
    """
    Updates the sixth frame with the current session data.
    This function calls the update method of the sixth frame to refresh its content
    based on the current session information.
    It is typically called after processing a packet to ensure that the sixth frame reflects the latest session data.
    """
    frames[6].update(session)