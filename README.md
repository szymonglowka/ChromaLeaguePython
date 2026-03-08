# Chroma League (Python Edition)

![License](https://img.shields.io/badge/license-GPL%203.0-informational)

Python open-source Razer Chroma keyboard integration for League of Legends.

> **Note:** This project is a complete Python rewrite of the original Java-based [ChromaLeague](https://github.com/bonepl/ChromaLeague) created by [bonepl](https://github.com/bonepl). The logic, animations, and concepts are based on the original work.

If you like the original idea and concept, consider giving a tip to the original creator for all the hard work:
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=5JFBXY66RT8Z6&item_name=Chroma+League&currency_code=PLN)

## Introduction

Razer Chroma is a wonderful framework provided by [Razer](https://www.razer.com/)
for implementing custom LED animations for their peripherals.

Many applications/games have its official support but [League of Legends](https://leagueoflegends.com)
is not one of them.

**Chroma League** is using League's [Live Client Data Api](https://developer.riotgames.com/docs/lol#game-client-api_live-client-data-api) exposed during the game to fetch the current game's state and react to in-game events.

If you have any comments or suggestions regarding the original concept, please visit the official thread at Razer Insider: [Chroma League - League of Legends integration for Razer Chroma](https://insider.razer.com/index.php?threads/chroma-league-league-of-legends-integration-for-razer-chroma.65412/).

## Overview

![Chroma League HUD](https://raw.githubusercontent.com/bonepl/ChromaLeague/master/doc/images/ChromaLeague.png "Chroma League HUD")

This is what basic in-game HUD looks like on a Chroma Keyboard. Certain in-game events will spawn additional animations.

## Requirements

* Windows
* League of Legends
* Razer Synapse 3 (with Chroma Connect module enabled)
* Chroma enabled keyboard
* Python 3.10+ (if running from source)

## Running

### Method 1: Running the compiled executable (Recommended)
Simply download the latest release, unpack it, and run `ChromaLeague.exe` located in the `dist` folder. 

### Method 2: Running from source (Python)
1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

```

3. Run the main script:
```bash
python -m src.chromaleague.main
```

### Method 3: Compiling into an Executable (.exe)
If you want to create a portable `.exe` build for your friends or to run without Python installed, you can use `PyInstaller`.
1. Ensure the requirements are installed alongside PyInstaller:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```
2. Run the compilation script:
   ```bash
   pyinstaller --noconfirm --onedir --windowed --add-data "config.json;." src/chromaleague/main.py
   ```
3. Your built application will be stored in the `/dist/main` folder!
After starting the application, it will verify connectivity to the local Razer SDK and log REST API versions like:
`[INFO] Detected Razer Chroma REST Api Version[core=3.23.03, device=3.23.04, version=3.23.05]`

This means that **Chroma League** has successfully passed startup checks. It will automatically detect when you join the game and start running integrations.

## Compatibility

* Runs on Windows only
* Supports only Chroma-enabled keyboards (tested on BlackWidow, but should support others)
* Developed for Summoner's Rift standard games (supports other game types natively, but there might be side effects)

## Implemented integrations

* Base configuration framework (`ConfigManager`) and hot-reloading Configuration UI (`ConfiguratorGUI`)
* Animated health bar (with health loss and gain animations)
* Animated resource bar (customized for all champions e.g., Mana, Energy, Fury, Shield)
* Active Item Readiness indicators directly mirrored to keys `1-6`
* Respawn timer visual countdown mapped across number keys
* Ally status indicators (Alive/Dead state mapped to `F1-F4` keys)
* Burst damage detection warning flashes
* Creep Score (CS) per minute metronome dynamically scaling arrow keys colors
* Vision Score mapping tracker
* Modulized keyboard flashes for Champion kills, Epic Monster kills
* Scaled multikill LED animations (Double, Triple, Quadra, and Penta)
* Spell cooldown and availability highlighting module (Q/W/E/R/D/F)
* Gold pouch module on the Numpad cluster

## Keyboard Map / Bindings

The following default keys are mapped to these integrations:
- **`F1 - F4`**: Ally Status (Alive = Green, Dead = Dim Red)
- **`1 - 6`**: Active Item Readiness (Lights up when an item with an active ability in that slot is off cooldown)
- **`1 - 0`**: Respawn Timer (When dead, the number row acts as a progress bar ticking down to your respawn)
- **`Q, W, E, R`**: Spell levels (Lights up when you have learned the spell)
- **`D, F`**: Summoner Spells (Static highlight)
- **Arrow Keys**: CS/min Metronome (Interpolates from Red to Green depending on how close you are to 8.0 CS/min)
- **`Insert, Home, PageUp, Delete, End, PageDown`**: Vision Tracker (Fills up progressively for every 10 Ward Score)
- **`Numpad`**: Gold Pouch (Fills up with gold coins up to 3000g)
- **Main Typing Zone**: Health Bar (Top rows) & Resource Bar (Bottom rows)

## Troubleshooting

Double-check if the `Razer Chroma SDK Server` service in Windows (`services.msc`) is up and running. Sometimes it gets stuck in a Paused state and stops responding. Restarting the service usually fixes the issue.

## Disclaimer

**League of Legends** and all related logic used in this project are owned and copyrighted by [Riot Games](https://www.riotgames.com).

**Razer Chroma** and **Razer Chroma SDK** and all related logic used in this project are owned and copyrighted by [Razer](https://www.razer.com/).