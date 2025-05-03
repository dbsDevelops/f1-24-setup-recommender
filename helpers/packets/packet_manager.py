from models.session import Session
from models.driver import Driver
from utils.dictionnaries import *
import json
import time
from ttkbootstrap import Toplevel, LEFT, Entry, IntVar, Label
from tkinter import Message, Checkbutton, Button
from models.frames.BaseFrame import BaseFrame
import traceback

drivers: list[Driver] = []
session: Session = Session()
created_map = False
width_points = 6
frames = []
menu_buttons: list = ["Main Menu", "Damage", "Temperatures", "Laps", "Map", "ERS & Fuel", "Weather Forecast",
                              "Packet Reception"]

def update_motion(packet, map_canvas, *args):  # Packet 0
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
    global created_map
    session.track_temperature = packet.m_weatherForecastSamples[0].m_trackTemperature
    session.air_temperature = packet.m_weatherForecastSamples[0].m_airTemperature
    session.number_of_laps = packet.m_totalLaps
    session.time_left = packet.m_sessionTimeLeft
    if session.track != packet.m_trackId or session.Seance != packet.m_sessionType: # Track or session has changed
        session.track = packet.m_trackId
        delete_map(map_canvas)
    session.Seance = packet.m_sessionType
    session.marshal_zones = packet.m_marshalZones  # Array[21]
    session.marshal_zones[0].m_zone_start = session.marshal_zones[0].m_zoneStart - 1
    session.num_marshal_zones = packet.m_numMarshalZones
    session.safety_car_status = packet.m_safetyCarStatus
    session.trackLength = packet.m_trackLength
    session.clear_slot()
    if packet.m_numWeatherForecastSamples != session.nb_weatherForecastSamples:
        session.nb_weatherForecastSamples = packet.m_numWeatherForecastSamples
        #Reconstruire le tableau 
    for i in range(session.nb_weatherForecastSamples):
        slot = packet.m_weatherForecastSamples[i]
        session.add_slot(slot)
    update_title(top_frame1, top_frame2, screen)
    update_frame6()

def update_lap_data(packet):  # Packet 2
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
    if packet.m_eventStringCode[3] == 71 and packet.m_eventDetails.m_startLights.m_numLights >= 2: # Starts lights : STLG
        session.formationLapDone = True
        print(f"{packet.m_eventDetails.m_startLights.m_numLights} red lights ")
    elif packet.m_eventStringCode[0] == 76 and session.formationLapDone: #Lights out : LGOT
        print("Lights out !")
        session.formationLapDone = False
        session.startTime = time.time()
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
    array = packet.m_carSetups
    for index in range(min(22, len(drivers))):
        drivers[index].setup_array = array[index]

def update_car_telemetry(packet):  # Packet 6
    for index in range(min(22, len(drivers))):
        element = packet.m_carTelemetryData[index]
        driver = drivers[index]
        driver.drs = element.m_drs
        driver.tyres_temp_inner = element.m_tyresInnerTemperature
        driver.tyres_temp_surface = element.m_tyresSurfaceTemperature
        driver.speed = element.m_speed
        if driver.speed >= 200 and not driver.S200_reached:
            print(f"{driver.position} {driver.name}  = {time.time() - session.startTime}")
            driver.S200_reached = True
    update_frame(frames, drivers, session)

def update_car_status(packet):  # Packet 7
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
    pass

def create_map(map_canvas):
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
                if (float(dist) / session.trackLength) > session.marshal_zones[cmi].m_zone_start and cmi!=session.num_marshal_zones:
                    if cmi != 1:
                        session.segments.append(map_canvas.create_line(L, width=3))
                        L = []
                    cmi +=1
    session.segments.insert(0, map_canvas.create_line(L1+L0, width=3))
    for i in range(20):
        driver = drivers[i]
        if session.Seance == 18 and i!=0:
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
    for element in session.segments:
        map_canvas.delete(element)
    session.segments = []
    for driver in drivers:
        map_canvas.delete(driver.oval)
        map_canvas.delete(driver.etiquette)
        driver.oval = None

def update_map(map_canvas):
    _, d, x, z = track_ids[session.track]
    for driver in drivers:
        if driver.position != 0:
            map_canvas.move(driver.oval, driver.Xmove / d, driver.Zmove / d)
            map_canvas.itemconfig(driver.oval, fill=teams_color_dictionary[driver.teamId])
            map_canvas.move(driver.etiquette, driver.Xmove / d, driver.Zmove / d)
            map_canvas.itemconfig(driver.etiquette, fill=teams_color_dictionary[driver.teamId], text=driver.name)
    for i in range(len(session.segments)):
        map_canvas.itemconfig(session.segments[i], fill=flag_colours[session.marshal_zones[i].m_zoneFlag])
    session.anyYellow = any(item.m_zoneFlag==3 for item in session.marshal_zones)
        
def initialize_driver_pool():
    for _ in range(22):
        drivers.append(Driver())

def UDP_Redirect(dictionnary_settings, listener, PORT):
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
            listener.port = int(PORT[0])
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

def port_selection(dictionnary_settings, listener, PORT):
    win = Toplevel()
    win.grab_set()
    win.wm_title("Port Selection")
    Label(win, text="Receiving PORT :", font=("Arial", 16)).grid(row=0, column=0, sticky="we", padx=30)
    e = Entry(win, font=("Arial", 16))
    e.insert(0, dictionnary_settings["port"])
    e.grid(row=1, column=0, padx=30)

    def button():
        PORT[0] = e.get()
        if not PORT[0].isdigit() or not 1000 <= int(PORT[0]) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=3, column=0)
        else:
            listener.socket.close()
            listener.port = int(PORT[0])
            listener.reset()
            Label(win, text="").grid(row=3, column=0)
            dictionnary_settings["port"] = str(PORT[0])
            with open("settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda e: button())
    win.bind('<KP_Enter>', lambda e: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=2, column=0, pady=10)

def update_title(top_label1, top_label2, screen):
    top_label1.config(text=session.title_display())
    top_label2.config(text=safety_car_status[session.safety_car_status])
    if session.safety_car_status == 4:
        top_label2.config(background="red")
    elif session.safety_car_status !=0 or session.anyYellow:
        top_label2.config(background="#FFD700")
    else:
        top_label2.config(background=screen.cget("background"))

def update_frame(frames : list[BaseFrame], drivers, session):
    for i in range(5):
        frames[i].update_drivers(drivers, session)

def update_frame6():
    frames[6].update(session)