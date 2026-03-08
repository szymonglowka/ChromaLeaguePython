# Chroma League (Python Edition)
# Copyright (C) [2026] [szymonglowka]
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

import time
import logging
from typing import List, Dict, Any, Optional
from src.chromaleague.chroma_client import AsyncChromaClient

logger = logging.getLogger(__name__)


class Animation:
    def __init__(self, duration: float):
        self.start_time = time.time()
        self.duration = duration

    @property
    def is_active(self) -> bool:
        return time.time() - self.start_time < self.duration

    def get_frame(self, base_matrix: List[List[int]]) -> List[List[int]]:
        return base_matrix


class FlashAnimation(Animation):
    def __init__(self, duration: float, color: int):
        super().__init__(duration)
        self.color = color

    def get_frame(self, base_matrix: List[List[int]]) -> List[List[int]]:
        if not self.is_active:
            return base_matrix
        return [[self.color] * 22 for _ in range(6)]


class HUDManager:
    ROWS = 6
    COLS = 22
    BAR_WIDTH = 15  # Ograniczenie szerokości pasków do linii F12 / Enter

    def __init__(self):
        self._base_matrix = [[0] * self.COLS for _ in range(self.ROWS)]

        # Statystyki gracza
        self.health_percent = 1.0
        self.resource_percent = 1.0
        self.resource_type = "MANA"  # Domyślny typ
        self.is_dead = False
        self.current_gold = 0.0

        # Poziomy umiejętności
        self.abilities = {"Q": 0, "W": 0, "E": 0, "R": 0}
        self.last_event_id = -1

        # Podstawowe Kolory
        self.C_OFF = AsyncChromaClient.rgb_to_razer(0, 0, 0)
        self.C_HEALTH = AsyncChromaClient.rgb_to_razer(0, 255, 0)  # Zielony
        self.C_HEALTH_DEAD = AsyncChromaClient.rgb_to_razer(50, 0, 0)  # Ciemna czerwień

        # Kolory Zasobów
        self.C_MANA = AsyncChromaClient.rgb_to_razer(0, 0, 255)  # Niebieski
        self.C_ENERGY = AsyncChromaClient.rgb_to_razer(255, 255, 0)  # Żółty
        self.C_FURY = AsyncChromaClient.rgb_to_razer(255, 0, 0)  # Czerwony
        self.C_SHIELD = AsyncChromaClient.rgb_to_razer(255, 255, 255)  # Biały
        self.C_NO_RESOURCE = AsyncChromaClient.rgb_to_razer(20, 20, 20)  # Ciemnoszary dla Garena/Katariny

        # Inne Kolory
        self.C_GOLD = AsyncChromaClient.rgb_to_razer(255, 215, 0)  # Złoty
        self.C_SPELL_READY = AsyncChromaClient.rgb_to_razer(148, 0, 211)  # Fioletowy
        self.C_ORANGE = AsyncChromaClient.rgb_to_razer(255, 140, 0)  # Pomarańczowy (dla D i F)
        self.C_DEAD_BG = AsyncChromaClient.rgb_to_razer(20, 20, 20)  # Szare tło po śmierci

        self.active_animation: Optional[Animation] = None

    def update(self, game_data: Dict[str, Any]):
        active_player = game_data.get("activePlayer", {})
        champion_stats = active_player.get("championStats", {})

        # Zdrowie i śmierć
        current_health = champion_stats.get("currentHealth", 0.0)
        max_health = champion_stats.get("maxHealth", 1.0)
        self.health_percent = current_health / max_health if max_health > 0 else 0.0
        self.is_dead = current_health <= 0.0

        # Mana / Energia
        current_resource = champion_stats.get("resourceValue", 0.0)
        max_resource = champion_stats.get("resourceMax", 1.0)
        self.resource_percent = current_resource / max_resource if max_resource > 0 else 0.0
        self.resource_type = champion_stats.get("resourceType", "MANA")

        # Złoto
        self.current_gold = active_player.get("currentGold", 0.0)

        # Umiejętności (Q, W, E, R)
        abilities_data = active_player.get("abilities", {})
        for key in ["Q", "W", "E", "R"]:
            spell_data = abilities_data.get(key, {})
            self.abilities[key] = spell_data.get("abilityLevel", 0)

        # Eventy (Zabójstwa, Smoki, Level Up)
        events_data = game_data.get("events", {})
        for event in events_data.get("Events", []):
            event_id = event.get("EventID", -1)
            if event_id > self.last_event_id:
                self._handle_event(event)
                self.last_event_id = event_id

        self._calculate_base_hud()

    def _handle_event(self, event: Dict[str, Any]):
        event_name = event.get("EventName", "Unknown")
        if event_name == "ChampionKill":
            self.active_animation = FlashAnimation(1.0, AsyncChromaClient.rgb_to_razer(255, 0, 0))
        elif event_name in ["DragonKill", "BaronKill"]:
            self.active_animation = FlashAnimation(2.0, AsyncChromaClient.rgb_to_razer(128, 0, 128))
        elif event_name == "LevelUp":
            self.active_animation = FlashAnimation(1.0, self.C_GOLD)

    def _get_resource_color(self) -> int:
        """Zwraca odpowiedni kolor na podstawie typu zasobu postaci."""
        res_type = self.resource_type.upper()
        if res_type == "ENERGY":
            return self.C_ENERGY
        elif res_type in ["FURY", "BATTLEFURY", "DRAGONFURY", "RAGE", "HEAT", "FEROCITY", "BLOODWELL"]:
            return self.C_FURY
        elif res_type == "SHIELD":
            return self.C_SHIELD
        elif res_type == "NONE" or (
                self.resource_percent == 0.0 and self.resource_type == "MANA" and self.health_percent > 0):
            # Jeśli postać absolutnie nie ma zasobu (np. Katarina)
            return self.C_NO_RESOURCE
        return self.C_MANA  # Domyślnie Niebieski

    def _calculate_base_hud(self):
        # 1. Tło bazowe
        bg_color = self.C_DEAD_BG if self.is_dead else self.C_OFF
        self._base_matrix = [[bg_color] * self.COLS for _ in range(self.ROWS)]

        # Obliczenie ile kolumn ma się świecić
        health_color = self.C_HEALTH_DEAD if self.is_dead else self.C_HEALTH
        active_resource_color = self._get_resource_color()

        num_health_cols = int(self.health_percent * self.BAR_WIDTH)
        num_mana_cols = int(self.resource_percent * self.BAR_WIDTH)

        # 2. Rysowanie pasków Zdrowia i Zasobów w głównej sekcji
        for col in range(self.BAR_WIDTH):
            # Górna połowa (rzędy 0, 1, 2) to Zdrowie
            if col < num_health_cols:
                for row in range(3):
                    self._base_matrix[row][col] = health_color

            # Dolna połowa (rzędy 3, 4, 5) to Zasób (np. Mana/Energia)
            if not self.is_dead and col < num_mana_cols:
                for row in range(3, 6):
                    # Jeśli postać nie ma zasobów, nie rysujemy na darmo pełnego paska
                    if active_resource_color != self.C_NO_RESOURCE:
                        self._base_matrix[row][col] = active_resource_color

        # 3. Nakładanie skilli na wierzch
        if not self.is_dead:
            # Q, W, E, R (Rząd 2, Kolumny 2-5)
            if self.abilities["Q"] > 0: self._base_matrix[2][2] = self.C_SPELL_READY
            if self.abilities["W"] > 0: self._base_matrix[2][3] = self.C_SPELL_READY
            if self.abilities["E"] > 0: self._base_matrix[2][4] = self.C_SPELL_READY
            if self.abilities["R"] > 0: self._base_matrix[2][5] = self.C_SPELL_READY

            # D, F zawsze na pomarańczowo (Rząd 3, Kolumny 4-5)
            self._base_matrix[3][4] = self.C_ORANGE
            self._base_matrix[3][5] = self.C_ORANGE

        # 4. Moduł Złota (Numpad)
        gold_keys_to_light = int(self.current_gold // 150)
        numpad_coords = [
            (5, 18), (5, 19), (5, 20),
            (4, 18), (4, 19), (4, 20),
            (3, 18), (3, 19), (3, 20),
            (2, 18), (2, 19), (2, 20)
        ]

        for i, (r, c) in enumerate(numpad_coords):
            if i < gold_keys_to_light:
                self._base_matrix[r][c] = self.C_GOLD

    def get_matrix(self) -> List[List[int]]:
        current_matrix = [row[:] for row in self._base_matrix]
        if self.active_animation:
            if self.active_animation.is_active:
                current_matrix = self.active_animation.get_frame(current_matrix)
            else:
                self.active_animation = None
        return current_matrix