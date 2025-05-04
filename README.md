# F1 24 Telemetry Application

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
  - [Step 1: Configure your Virtual Python Environment](#step1)
  - [Step 2: Run the application](#step2)
  - [Step 3: Send data to the application](#step3)
- [Project Structure](#project-structure)
- [To-do List](#to-do-list)

## 🔍 Overview <a id="overview"></a>
This project consists of a recommendation system of EA SPORTS F1 24 car setups for any simracer. This project is a fork of the [Fredrik2002/f1-23-telemetry-application](https://github.com/Fredrik2002/f1-23-telemetry-application) which provides a Python application for the simracer to view telemetry data of their current session. 

## 🚀 Features <a id="features"></a>
- ✅ Title bar displaying session type, laps (or time left if in qualifying), and race status (green, yellow, or red flag, SC, or VSC)
- ✅ Main Menu tab showing different information depending on the session type (Qualifying, Race, Time Trial)
- ✅ Fully functional mini-map displaying the track, car positions, and mini-sectors lighting up under a yellow flag
- ✅ Damage reports (excluding engine and gearbox) for all cars in the session
- ✅ Inner and outer tyre temperatures for all cars
- ✅ Current, best, and last lap times, along with sector times for all cars, depending on the session type
- ✅ ERS & Fuel management information as well as time penalties for all cars
- ✅ Weather forecast for upcoming sessions, including track and air temperature
- ✅ Option to choose the port for receiving data
- ✅ Option to redirect received data to another IP address and port (to share data with a friend or another application)
- ✅ Compatibility with older parsers for previous EA F1 games (F1 22 & F1 23)


## 🔧 Usage <a id="usage"></a>
### <ins>Step 1 : Configure your Virtual Python Enviroment</ins><a id="step1"></a>
1. [Install pip](https://pip.pypa.io/en/stable/installation/) in your Linux, macOS or Windows system if you don't have it already.
2. Install the required libraries.
```bash
pip install -r requirements.txt
```
⚠️ If you have any issues in macOS systems importing the tkinter library, you will have to use the [brew package manager](https://brew.sh) to install the following packet:
```bash
brew install python-tk
```
Here is the reference for the issue I was having: https://stackoverflow.com/questions/5459444/tkinter-python-may-not-be-configured-for-tk

### <ins>Step 2 : Run the application</ins><a id="step2"></a>

Run *Telemetry.py*
```bash
python3 app/telemetry.py
``` 

### <ins>Step 3 : Send data to the application </ins> <a id="step3"></a>
Open the F1 Game :
- ➡️ Go to Settings 
- ➡️ Telemetry Settings
- ➡️ Make sure the port in-game matches the port used by the application (20777 by default)
- ➡️ **If your game is connected to the same network as your computer running this application**, the easiest way is to enable the <u>UDP Broadcast</u> setting.
**If not**, you have to enter your public IP address in the <u>IP Address</u> setting.
- ✅ You are then good to go!


## 📘 Project structure <a id="project-structure"></a>

- **`app/`**: Contains the main application logic.
  - `telemetry.py`: Entry point for the telemetry application.

- **`config/`**: Handles configuration and settings.
  - `settings_loader.py`: Loads application settings from a configuration file.
  - `settings.txt`: Stores user-defined settings in JSON format.

- **`data/`**: Stores raw, processed, and output data.
  - `raw/`: Contains raw data files received from the telemetry system.
  - `processed/`: Stores processed data ready for analysis.
  - `output/`: Contains output files such as analysis results or visualizations.

- **`helpers/`**: Provides utility functions and packet management logic.
  - `packets/`: Contains packet parsing and management modules.
    - `packet_parser.py`: Defines packet structures and parsing logic.
    - `packet_manager.py`: Handles packet-specific updates and processing.

- **`models/`**: Defines core data models for the application.
  - `driver.py`: Represents driver-related data.
  - `session.py`: Represents session-related data.
  - `frames/`: Contains UI frame models.
  - `weather_forecast_sample.py`: Represents weather forecast data.

- **`network/`**: Manages network communication.
  - `udp_listener.py`: Listens for incoming UDP packets.

- **`tracks/`**: Stores track-related data.
  - `*.track`: Files defining track boundaries, racing lines, and other track-specific data.

- **`ui/`**: Manages the user interface.
  - `window_manager.py`: Handles the main application window and UI components.

- **`utils/`**: Provides general utility functions.
  - `receiver.py`: Handles packet reception and processing.
  - `deserializer.py`: Deserializes incoming data packets.
  - `sanitize_all_circuits.py`: Cleans and processes circuit data.
  
## ✏️ To-do list <a id="to-do-list"></a>
* Implement analysis logic

