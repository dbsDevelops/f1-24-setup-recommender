import datetime

def rgbtohex(r,g,b):
    """
    This function takes three integer values representing the red, green, and blue components of a color,
    and converts them to a hexadecimal string in the format '#RRGGBB'.
    The values for r, g, and b should be in the range of 0 to 255.
    The hexadecimal string is formatted such that each component is represented by two hexadecimal digits,
    with leading zeros if necessary.
    Example:
    >>> rgbtohex(255, 0, 0)
    '#ff0000'
    >>> rgbtohex(0, 255, 0)
    '#00ff00'
    >>> rgbtohex(0, 0, 255)
    '#0000ff'

    :param r: Red component (0-255)
    :param g: Green component (0-255)
    :param b: Blue component (0-255)
    :return: Hexadecimal color string in the format '#RRGGBB'
    """
    return f'#{r:02x}{g:02x}{b:02x}'

def valid_ip_address(address: str) -> bool:
    """
    This function checks if a given string is a valid IPv4 address.
    A valid IPv4 address consists of four octets separated by dots, where each octet is a number between 0 and 255.
    Example: 
    >>> valid_ip_address(0.0.0.0)
    True
    >>> valid_ip_address(255.255.255.255)
    True
    >>> valid_ip_address(256.256.256.256)
    False
    >>> valid_ip_address(-1.-1.-1.-1)
    False

    :param address: A string representing an IPv4 address.
    :return: True if the address is a valid IPv4 address, False otherwise.
    """
    octets = address.split(".")
    flag = len(octets)==4
    for octet in octets:
        if not (octet.isdigit() and 0<=int(octet)<=255):
            flag = False
    return flag

black = "#000000"
white = "#FFFFFF"
green = "#00FF00"
blue = "#0000FF"
yellow = "#FFD700"
red = "#FF0000"
purple = "#880088"
gold = "#FFD700"
grey = "#4B4B4B"

packet_ids = {
    0:"Motion",
    1:"Session",
    2:"Lap Data",
    3:"Event",
    4:"Participants",
    5:"Car Setups",
    6:"Car Telemetry",
    7:"Car Status",
    8:"Final Classification",
    9:"Lobby Info",
    10:"Car Damage",
    11:"Session History",
    12:"Tyre Sets",
    13:"Motion Ex",
    14:"Time Trial"
}

weather_types = {
    0: "Clear",
    1: "Light Clouds",
    2: "Overcast",
    3: "Light Rain",
    4: "Heavy Rain",
    5: "Storm"
}

track_temperature_change = {
    -1: "Unknown",
    0: "Up",
    1: "Down",
    2: "No Change"
}

formula_types = {
    -1: "Unknown",
    0: "F1 Modern",
    1: "F1 Classic",
    2: "F2",
    3: "F1 Generic",
    4: "Beta",
    6: "Esports",
    8: "F1 World",
    9: "F1 Elimination"
}

safety_car_status = {
    -1: "Unknown",
    0:"No Safety Car",
    1:"Full Safety Car",
    2:"Virtual Safety Car",
    3:"Formation Lap",
}

network_game = {
    -1: "Unknown",
    0: "Offline",
    1: "Online"
}

weather_forecast_accuracy = {
    -1: "Unknown",
    0: "Perfect",
    1: "Approximate",
}

steering_assist = {
    -1: "Unknown",
    0: "Off",
    1: "On",
}

braking_assist = {
    -1: "Unknown",
    0: "Off",
    1: "Low",
    2: "Medium",
    3: "High",
}

pit_assist = {
    -1: "Unknown",
    0: "Off",
    1: "On"
}

pit_release_assist = {
    -1: "Unknown",
    0: "Off",
    1: "On"
}

ERS_assist = {
    -1: "Unknown",
    0: "Off",
    1: "On"
}

DRS_assist = {
    -1: "Unknown",
    0: "Off",
    1: "On"
}

dynamic_racing_line = {
    -1: "Unknown",
    0: "Off",
    1: "Corners Only",
    2: "Full"
}

dynamic_racing_line_type = {
    -1: "Unknown",
    0: "2D",
    1: "3D"
}

session_length = {
    -1: "Unknown",
    0: "None",
    2: "Very Short",
    3: "Short",
    4: "Medium",
    5: "Medium Long",
    6: "Long",
    7: "Full"
}

speed_units_lead_player = {
    -1: "Unknown",
    0: "MPH",
    1: "KPH"
}

temperature_units_lead_player = {
    -1: "Unknown",
    0: "Celsius",
    1: "Fahrenheit"
}

driver_status = {
    -1: "Unknown",
    0: "In Garage",
    1: "Flying Lap",
    2: "In Lap",
    3: "Out Lap",
    4: "On Track"
}

results_status = {
    -1: "Unknown",
    0: "Invalid",
    1: "Inactive",
    2: "Active",
    3: "Finished",
    4: "Did Not Finish",
    5: "Disqualified",
    6: "Not Classified",
    7: "Retired"
}

event_codes = {
    "SSTA": "Session Started",
    "SEND": "Session Ended",
    "FTLP": "Fastest Lap",
    "RTMT": "Retirement",
    "DRSE": "DRS Enabled",
    "DRSD": "DRS Disabled",
    "TMPT": "Team Mate In Pit",
    "CHQF": "Chequered Flag",
    "RCWN": "Race Winner",
    "PENA": "Penalty Issued",
    "SPTP": "Speed Trap Triggered",
    "STLG": "Start Lights",
    "LGOT": "Lights Out",
    "DTSV": "Drive Through Served",
    "SGSV": "Stop Go Served",
    "FLBK": "Flashback",
    "BUTN": "Button Status",
    "RDFL": "Red Flag Shown",
    "OVTK": "Overtake Ocurred",
    "SCAC": "Safety Car ",
    "COLL": "Collision"
}

platforms = {
    -1: "Unknown",
    1: "Steam",
    3: "PlayStation",
    4: "Xbox",
    6: "Origin",
    255: "Unknown"
}

mfd_panel = {
    -1: "Unknown",
    0: "Car Setup",
    1: "Pits",
    2: "Damage",
    3: "Engine",
    4: "Temperatures"
}

teams = {
    -1: "Unknown",
    0: "Mercedes",
    1: "Ferrari",
    2: "Red Bull Racing",
    3: "Williams",
    4: "Aston Martin",
    5: "Alpine",
    6: "RB",
    7: "Haas",
    8: "McLaren",
    9: "Sauber",
    41:"F1 Generic",
    104: "F1 Custom Team",
    143: "Art GP '23",
    144: "Campos Racing '23",
    145: "Carlin '23",
    146: "PHM '23",
    147: "DAMS '23",
    148: "Hitech '23",
    149: "MP Motorsport '23",
    150: "Prema '23",
    151: "Trident '23",
    152: "Van Amersfoort Racing '23",
    153: "Virtuosi '23",
}

drivers = {
    -1: "Unknown",
    0: "Carlos Sainz",
    1: "Daniil Kvyat",
    2: "Daniel Ricciardo",
    3: "Fernando Alonso",
    4: "Felipe Massa",
    6: "Kimi Räikkönen",
    7: "Lewis Hamilton",
    9: "Max Verstappen",
    10: "Nico Hulkenberg",
    11: "Kevin Magnussen",
    12: "Romain Grosjean",
    13: "Sebastian Vettel",
    14: "Sergio Perez",
    15: "Valtteri Bottas",
    17: "Esteban Ocon",
    19: "Lance Stroll",
    20: "Arron Barnes",
    21: "Martin Giles",
    22: "Alex Murray",
    23: "Lucas Roth",
    24: "Igor Correia",
    25: "Sophie Levasseur",
    26: "Jonas Schiffer",
    27: "Alain Forest",
    28: "Jay Letourneau",
    29: "Esto Saari",
    30: "Yasar Atiyeh",
    31: "Callisto Calabresi",
    32: "Naota Izum",
    33: "Howard Clarke",
    34: "Wilheim Kaufmann",
    35: "Marie Laursen",
    36: "Flavio Nieves",
    37: "Peter Belousov",
    38: "Klimek Michalski",
    39: "Santiago Moreno",
    40: "Benjamin Coppens",
    41: "Noah Visser",
    42: "Gert Waldmuller",
    43: "Julian Quesada",
    44: "Daniel Jones",
    45: "Artem Markelov",
    46: "Tadasuke Makino",
    47: "Sean Gelael",
    48: "Nyck De Vries",
    49: "Jack Aitken",
    50: "George Russell",
    51: "Maximilian Günther",
    52: "Nirei Fukuzumi",
    53: "Luca Ghiotto",
    54: "Lando Norris",
    55: "Sérgio Sette Câmara",
    56: "Louis Delétraz",
    57: "Antonio Fuoco",
    58: "Charles Leclerc",
    59: "Pierre Gasly",
    62: "Alexander Albon",
    63: "Nicholas Latifi",
    64: "Dorian Boccolacci",
    65: "Niko Kari",
    66: "Roberto Merhi",
    67: "Arjun Maini",
    68: "Alessio Lorandi",
    69: "Ruben Meijer",
    70: "Rashid Nair",
    71: "Jack Tremblay",
    72: "Devon Butler",
    73: "Lukas Weber",
    74: "Antonio Giovinazzi", 
    75: "Robert Kubica",
    76: "Alain Prost",
    77: "Ayrton Senna",
    78: "Noboharu Matsushita",
    79: "Nikita Mazepin",
    80: "Guanya Zhou",
    81: "Mick Schumacher",
    82: "Callum Ilott",
    83: "Juan Manuel Correa",
    84: "Jordan King",
    85: "Mahaveer Raghunathan",
    86: "Tatiana Calderón",
    87: "Anthoine Hubert",
    88: "Guiliano Alesi",
    89: "Ralph Boschung",
    90: "Michael Schumacher",
    91: "Dan Ticktum",
    92: "Marcus Armstrong",
    93: "Christian Lundgaard",
    94: "Yuki Tsunoda",
    95: "Jehan Daruvala",
    96: "Guilherme Samaia",
    97: "Pedro Piquet",
    98: "Felipe Drugovich",
    99: "Robert Shwartzman",
    100: "Roy Nissany",
    101: "Marino Sato",
    102: "Aidan Jackson",
    103: "Casper Akkerman",
    109: "Jenson Button",
    110: "David Coulthard",
    111: "Nico Rosberg",
    112: "Oscar Piastri",
    113: "Liam Lawson",
    114: "Juri Vips",
    115: "Theo Pourchaire",
    116: "Richard Verschoor",
    117: "Lirim Zendeli",
    118: "David Beckmann",
    121: "Alessio Deledda",
    122: "Bent Viscaal",
    123: "Enzo Fittipaldi",
    125: "Mark Webber",
    126: "Jacques Villeneuve",
    127: "Callie Mayer",
    128: "Noah Bell",
    129: "Jake Hughes",
    130: "Frederick Vesti",
    131: "Olli Caldwell",
    132: "Logan Sargeant",
    133: "Cem Bolukbasi",
    134: "Ayumu Iwasa",
    135: "Clément Novalak",
    136: "Jack Doohan",
    137: "Amaury Cordeel",
    138: "Dennis Hauger",
    139: "Calan Williams",
    140: "Jamie Chadwick",
    141: "Kamui Kobayashi",
    142: "Pastor Maldonado",
    143: "Mikka Häkkinen",
    144: "Nigel Mansell",
    145: "Zane Maloney",
    146: "Victor Martins",
    147: "Oliver Bearman",
    148: "Jak Crawford",
    149: "Isack Hadjar",
    150: "Arthur Leclerc",
    151: "Brad Benavides",
    152: "Roman Stanek",
    153: "Kush Maini",
    154: "James Hunt",
    155: "Juan Pablo Montoya",
    156: "Brendon Leigh",
    157: "David Tonizza",
    158: "Jarno Opmeer",
    159: "Lucas Blakeley",
}

track_ids = { #(track name, highNumber=Small on canvas, x_offset, y_offset)
    -1: ("Unknown", 0, 0, 0),
    0: ("Melbourne", 3.5, 300, 300),
    1: ("Paul Ricard", 2.5, 500, 300),
    2: ("Shanghai", 2, 300, 300),
    3: ("Sakhir (Bahrain)", 2, 600, 350),
    4: ("Catalunya", 2.5, 400, 300),
    5: ("Monaco", 2, 300, 300),
    6: ("Montreal", 3, 300, 100),
    7: ("Silverstone", 3.5, 400, 250),
    8: ("Hockenheim", 2, 300, 300),
    9: ("Hungaroring", 2.5, 400, 300),
    10: ("Spa", 3.5, 500, 350),
    11: ("Monza", 4, 400, 300),
    12: ("Singapore", 2, 400, 300),
    13: ("Suzuka", 2.5, 500, 300),
    14: ("Abu Dhabi", 2, 500, 250),
    15: ("Texas", 2, 400, 50),
    16: ("Brazil", 2, 600, 250),
    17: ("Austria", 2, 300, 300),
    18: ("Sochi", 2, 300, 300),
    19: ("Mexico", 2.5, 500, 500),
    20: ("Baku (Azerbaijan)", 3, 400,400),
    21: ("Sakhir Short", 2, 300, 300),
    22: ("Silverstone Short", 2, 300, 300),
    23: ("Texas Short", 2, 300, 300),
    24: ("Suzuka Short", 2, 300, 300),
    25: ("Hanoi", 2, 300, 300),
    26: ("Zandvoort", 2, 500, 300),
    27: ("Imola", 2, 500, 300),
    28: ("Portimao", 2, 300, 300),
    29: ("Jeddah", 4,500, 350),
    30:("Miami", 2,400,300),
    31:("Las Vegas", 4,400, 300),
    32:("Losail", 2.5,400,300)
}

nationalities = {
    -1: "Unknown",
    0: "Unknown",
    1: "American",
    2: "Argentinian",
    3: "Australian",
    4: "Austrian",
    5: "Azerbaijani",
    6: "Bahraini",
    7: "Belgian",
    8: "Bolivian",
    9: "Brazilian",
    10: "British",
    11: "Bulgarian",
    12: "Cameroonian",
    13: "Canadian",
    14: "Chilean",
    15: "Chinese",
    16: "Colombian",
    17: "Costa Rican",
    18: "Croatian",
    19: "Cypriot",
    20: "Czech",
    21: "Danish",
    22: "Dutch",
    23: "Ecuadorian",
    24: "English",
    25: "Emirian",
    26: "Estonian",
    27: "Finnish",
    28: "French",
    29: "German",
    30: "Ghanaian",
    31: "Greek",
    32: "Guatemalan",
    33: "Honduran",
    34: "Hong Konger",
    35: "Hungarian",
    36: "Icelander",
    37: "Indian",
    38: "Indonesian",
    39: "Irish",
    40: "Israeli",
    41: "Italian",
    42: "Jamaican",
    43: "Japanese",
    44: "Jordanian",
    45: "Kuwaiti",
    46: "Latvian",
    47: "Lebanese",
    48: "Lithuanian",
    49: "Luxembourger",
    50: "Malaysian",
    51: "Maltese",
    52: "Mexican",
    53: "Monegasque",
    54: "New Zealander",
    55: "Nicaraguan",
    56: "Northen Irish",
    57: "Norwegian",
    58: "Omani",
    59: "Pakistani",
    60: "Panamanian",
    61: "Paraguayan",
    62: "Peruvian",
    63: "Polish",
    64: "Portuguese",
    65: "Qatari",
    66: "Romanian",
    68: "Salvadoran",
    69: "Saudi",
    70: "Scottish",
    71: "Serbian",
    72: "Singaporean",
    73: "Slovakian",
    74: "Slovenian",
    75: "South Korean",
    76: "South African",
    77: "Spanish",
    78: "Swedish",
    79: "Swiss",
    80: "Thai",
    81: "Turkish",
    82: "Uruguayan",
    83: "Ukrainian",
    84: "Venezuelan",
    85: "Barbadian",
    86: "Welsh",
    87: "Vietnamese",
    88: "Algerian",
    89: "Bosnian",
    90: "Filipino"
}

game_modes = {
    0: "Event Mode",
    3: "Grand Prix",
    4: "Grand Prix '23",
    5: "Time Trial",
    6: "Splitscreen",
    7: "Online Custom",
    8: "Online League",
    11: "Career Invitational",
    12: "Championship Invitational",
    13: "Championship",
    14: "Online Championship",
    15: "Online Weekly Event",
    17: "Story Mode",
    19: "Career '22",
    20: "Career '22 Online",
    21: "Career '23",
    22: "Career '23 Online",
    23: "Driver Career '24",
    24: "Career '24 Online",
    25: "My Team Career '24",
    26: "Curated Career '24",
    127: "Benchmark"
}

session_types = {
    0: "Unknown",
    1: "Practice 1",
    2: "Practice 2",
    3: "Practice 3",
    4: "Short practice",
    5: "Qualifying 1",
    6: "Qualifying 2",
    7: "Qualifying 3",
    8: "Short Qualifying",
    9: "One-Shot Qualifying",
    10: "Sprint Shootout 1",
    11: "Sprint Shootout 2",
    12: "Sprint Shootout 3",
    13: "Short Sprint Shootout",
    14: "One-Shot Sprint Shootout",
    15: "Race",
    16: "Race 2",
    17: "Race 3",
    18: "Time Trial"
}

rulesets = {
    0: "Practice & Qualifying",
    1: "Race",
    2: "Time Trial",
    4: "Time Attack",
    6: "Checkpoint Challenge",
    8: "Autocross",
    9: "Drift",
    10: "Average Speed Zone",
    11: "Rival Duel"
}

surface_types = {
    0: "Tarmac",
    1: "Rumble strip",
    2: "Concrete",
    3: "Rock",
    4: "Gravel",
    5: "Mud",
    6: "Sand",
    7: "Grass",
    8: "Water",
    9: "Cobblestone",
    10: "Metal",
    11: "Ridged"
}

button_flags = {}

penalty_types = {
    0: "Drive through",
    1: "Stop Go",
    2: "Grid penalty",
    3: "Penalty reminder",
    4: "Time penalty",
    5: "Warning",
    6: "Disqualified",
    7: "Removed from formation lap",
    8: "Parked too long timer",
    9: "Tyre regulations",
    10: "This lap invalidated",
    11: "This and next lap invalidated",
    12: "This lap invalidated without reason",
    13: "This and next lap invalidated without reason",
    14: "This and previous lap invalidated",
    15: "This and previous lap invalidated without reason",
    16: "Retired",
    17: "Black flag timer"
}

infringement_types = {
    0: "Blocking by slow driving",
    1: "Blocking by wrong way driving",
    2: "Reversing off the start line",
    3: "Big Collision",
    4: "Small Collision",
    5: "Collision failed to hand back position single",
    6: "Collision failed to hand back position multiple",
    7: "Corner cutting gained time",
    8: "Corner cutting overtake single",
    9: "Corner cutting overtake multiple",
    10: "Crossed pit exit lane",
    11: "Ignoring blue flags",
    12: "Ignoring yellow flags",
    13: "Ignoring drive through",
    14: "Too many drive throughs",
    15: "Drive through reminder serve within n laps",
    16: "Drive through reminder serve this lap",
    17: "Pit lane speeding",
    18: "Parked for too long",
    19: "Ignoring tyre regulations",
    20: "Too many penalties",
    21: "Multiple warnings",
    22: "Approaching disqualification",
    23: "Tyre regulations select single",
    24: "Tyre regulations select multiple",
    25: "Lap invalidated corner cutting",
    26: "Lap invalidated running wide",
    27: "Corner cutting ran wide gained time minor",
    28: "Corner cutting ran wide gained time significant",
    29: "Corner cutting ran wide gained time extreme",
    30: "Lap invalidated wall riding",
    31: "Lap invalidated flashback used",
    32: "Lap invalidated reset to track",
    33: "Blocking the pitlane",
    34: "Jump start",
    35: "Safety car to car collision",
    36: "Safety car illegal overtake",
    37: "Safety car exceeding allowed pace",
    38: "Virtual safety car exceeding allowed pace",
    39: "Formation lap below allowed speed",
    40: "Formation lap parking",
    41: "Retired mechanical failure",
    42: "Retired terminally damaged",
    43: "Safety car falling too far back",
    44: "Black flag timer",
    45: "Unserved stop go penalty",
    46: "Unserved drive through penalty",
    47: "Engine component change",
    48: "Gearbox change",
    49: "Parc Fermé change",
    50: "League grid penalty",
    51: "Retry penalty",
    52: "Illegal time gain",
    53: "Mandatory pitstop",
    54: "Attribute assigned"
}

actual_tyre_compound = {
    -1: "Unknown",
    7: "Intermediates",
    8: "Wet",
    9: "F1 Classic Dry",
    10: "F1 Classic Wet",
    11: "F2 Super Soft",
    12: "F2 Soft",
    13: "F2 Medium",
    14: "F2 Hard",
    15: "F2 Wet",
    16: "C5",
    17: "C4",
    18: "C3",
    19: "C2",
    20: "C1",
    21: "C0"
}

visual_tyre_compound = {
    -1: "Unknown",
    7: "Intermediates",
    8: "Wet",
    15: "F2 Wet",
    16: "Soft",
    17: "Medium",
    18: "Hard",
    19: "F2 Super Soft",
    20: "F2 Soft",
    21: "F2 Medium",
    22: "F2 Hard"
}

tyres_color_dictionnary = {
    0:"#FF0000",
    16: "#FF0000",
    17: "#FFD700",
    18: "#FFFFFF",
    7: "#00FF00",
    8: "#0000FF"
}

teams_color_dictionary = {
    -1: "#FFFFFF",
    0: "#00C7CD",
    1: "#FF0000",
    2: "#0000FF",
    3: "#5097FF",
    4: "#00902A",
    5: "#009BFF",
    6: "#00446F",
    7: "#95ACBB",
    8: "#FFAE00",
    9: "#980404",
    41:"#000000",
    104: "#670498",
    255: "#670498"
}

fuel_dict = {
    0: "Lean",
    1: "Standard",
    2: "Rich",
    3: "Max"
}

pit_dictionary = {
    0: "",
    1: "PIT",
    2: "PIT"
}

ERS_dictionary = {
    0: "NONE",
    1: "MEDIUM",
    2: "HOTLAP",
    3: "OVERTAKE",
    -1: "PRIVATE"
}

flag_colours = {
    0: white, 1: green, 2: blue, 3: yellow, 4: red
}

DRS_dict = {0: "", 1: "DRS"}

def conversion(millis, mode):  # mode 1 = titre, mode 2 = last lap
    if mode == 1:
        texte = str(datetime.timedelta(seconds=millis))
        liste = texte.split(":")
        return f"{liste[1]} min {liste[2]}s"
    elif mode == 2:
        seconds, millis = millis // 1000, millis%1000
        minutes, seconds = seconds // 60, seconds%60
        if (minutes!=0 or seconds!=0 or millis!=0) and (minutes>=0 and seconds<10):
            seconds = "0"+str(seconds)

        if millis//10 == 0:
            millis="00"+str(millis)
        elif millis//100 == 0:
            millis="0"+str(millis)
        
        if minutes != 0:
            return f"{minutes}:{seconds}.{millis}"
        else:
            return f"{seconds}.{millis}"



def file_len(fname):
    with open(fname) as file:
        for i, l in enumerate(file):
            pass
    return i + 1


def string_code(packet):
    string = ""
    for i in range(4):
        string += packet.m_eventStringCode[i]
    return string