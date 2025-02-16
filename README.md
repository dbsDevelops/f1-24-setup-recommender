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
The goal of this project is to make the most important data from the in-game EA F1 24 telemetry system easily accessible.

![Telemetry map](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/7b1ce85e-f57d-4861-b7f5-10bee4ad9b11)

![Telemetry 2](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/3653b8ae-4604-402a-886b-45e6cf7147d5)

![Telemetry 3](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/ff73f7f2-b7c2-48e1-b547-4eebc37fae1c)

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
### <ins>Step 1 : Configure your Virtual Python Enviroment</ins><a id="step2"></a>
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
python3 Telemetry.py
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
* utils :
    * *sender.py* : Sends sample data to a given port and IP address.
    * draw.py : If you run this file before the beginning of a lap, it will 'draw' the track by saving all of player's car's positions within the given file (that's how the mini-maps are created)
    * *receiver.py* : Stores packets received in a list, and stores the list in a file. 10min of recording ≈ 100 MB of data, so be careful !
    * *server.py* Receives datas from different ports and redirects it to specific IP addresses
* __*Telemetry.py* : Main application you need to run__
* *Player.py* & *Session.py* : Classes to represent a player and a session
* *packet_management.py* : Stores the different packets information into various drivers and session instances
* *dictionnaries.py* : This is where all the different dictionnaries are stored
* *Custom_Frame.py* : This is where the main frame is created
* *parser202x.py* : Parses the data received for the F1 2x game (default for F1 24)
* *settings.txt* : This files saves the previous connection settings (so you don't have to enter the same port selection and UDP redirection every time). Do not touch unless you know what you are doing

## ✏️ To-do list <a id="to-do-list"></a>
* Fix the issue with weather Forecast Sample in 100% (Too many samples ?)
* Improve the overall appearance of the app (flag apparition, title)

