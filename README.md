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
python src/chromaleague/main.py

```



After starting the application, it will verify connectivity to the local Razer SDK and log REST API versions like:
`[INFO] Detected Razer Chroma REST Api Version[core=3.23.03, device=3.23.04, version=3.23.05]`

This means that **Chroma League** has successfully passed startup checks. It will automatically detect when you join the game and start running integrations.

## Compatibility

* Runs on Windows only
* Supports only Chroma-enabled keyboards (tested on BlackWidow, but should support others)
* Developed for Summoner's Rift standard games (supports other game types natively, but there might be side effects)

## Implemented integrations

* animated health bar (with health loss and gain animations)
* animated resource bar (customized for all champions)
* level up animation
* gold pouch with animated coins (3000 gold means pouch is full)
* enemy/ally dragon/herald/baron kill indicators
* dragons killed by allies counter
* dragon soul indicator
* baron/elder buff indicator
* killing spree counter
* assist spree counter
* kill/assist animation
* respawn animation
* dead animation
* rift change animation
* dim background light for the keyboard for playing in the dark
* game victory animation
* game defeat animation

## Troubleshooting

Double-check if the `Razer Chroma SDK Server` service in Windows (`services.msc`) is up and running. Sometimes it gets stuck in a Paused state and stops responding. Restarting the service usually fixes the issue.

## Disclaimer

**League of Legends** and all related logic used in this project are owned and copyrighted by [Riot Games](https://www.riotgames.com).

**Razer Chroma** and **Razer Chroma SDK** and all related logic used in this project are owned and copyrighted by [Razer](https://www.razer.com/).




### 2. Plik `LICENSE`

Ponieważ projekt bazuje na kodzie GPL 3.0, Twój port w Pythonie również musi zawierać pełny tekst licencji GPL 3.0. 

Utwórz plik o nazwie `LICENSE` (bez żadnego rozszerzenia, np. `.txt`) w głównym folderze projektu i skopiuj do niego **pełny oryginalny tekst licencji GPL 3.0** w języku angielskim. Jest to bardzo długi tekst prawny (ma około 600 linijek), więc nie wklejam go tutaj w całości, ale możesz go pobrać z oficjalnego źródła:

👉 **[Pobierz pełny tekst licencji GPL-3.0 (plik tekstowy)](https://www.gnu.org/licenses/gpl-3.0.txt)** 👈

Skopiuj całą zawartość z powyższego linku i wklej do pliku `LICENSE`.

### 3. Nagłówki w plikach `.py` (Wymagane przez GPL)

Zgodnie z zasadami licencji GPL, na samej górze każdego z Twoich głównych plików źródłowych w Pythonie (np. `main.py`, `chroma_client.py` itp.) powinieneś dodać krótki komentarz licencyjny z adnotacją, że bazuje to na oryginalnym kodzie. Wklej coś takiego na samej górze najważniejszych skryptów:

```python
# Chroma League (Python Edition)
# Copyright (C) [Rok Twojego Wydania] [Twoje Imię/Pseudonim]
# Based on the original Java implementation by bonepl (https://github.com/bonepl/ChromaLeague)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

```

Dzięki tym trzem krokom (nowy plik `README.md`, plik `LICENSE` w projekcie i poprawne nagłówki w kodzie) Twój projekt będzie w 100% zgodny z wymaganiami licencyjnymi oryginalnego twórcy i prawnie bezpieczny do publikacji np. na GitHubie.