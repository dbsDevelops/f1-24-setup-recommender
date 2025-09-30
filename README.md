# EA F1-24 Setup Recommender System

## Table of Contents 

- [Rundown](#rundown)
- [Features](#features)
- [Usage](#usage)

## 🔍 Rundown <a id="rundown"></a>
The purpose of this project is to implement a recommender system for car setups in the EA F1-24 videogame by capturing the packets transmitted from the console/PC the user is playing on, use the captured packets as input for the system and outputting the optimal setup to the user. In addition, the user will be able to query a chatbot to get more detailed information. 

## 🚀 Features <a id="features"></a>
- Recommender system which outputs the optimal setup for the user.
- Chatbot with an LLM to respond to the user's queries. 

## ⚙️ Usage <a id="usage"></a>

### Run Main Application
To run the main application, first you will need to setup the Python virtual environment.

```bash
python3 -m venv venv
source ./venv/bin/activate
```

Once the environment is up and ready, run the app/Telemetry.py Python script. A window will open when doing so. 

```bash
python3 app/Telemetry.py 
```