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
import collections
from typing import List, Dict, Any, Optional
from src.chromaleague.chroma_client import AsyncChromaClient
from src.chromaleague.config_manager import AppConfig
from src.chromaleague.animations import (
    Animation, FlashAnimation, DoubleKillAnimation, 
    TripleKillAnimation, QuadraKillAnimation, PentaKillAnimation
)

logger = logging.getLogger(__name__)


class HUDManager:
    ROWS = 6
    COLS = 22
    BAR_WIDTH = 15  # Ograniczenie szerokości pasków do linii F12 / Enter

    def __init__(self, config: AppConfig):
        self.config = config
        self._base_matrix = [[0] * self.COLS for _ in range(self.ROWS)]

        # Player Statistics
        self.health_percent = 1.0
        self.resource_percent = 1.0
        self.resource_type = "MANA"  # Default type
        self.is_dead = False
        self.respawn_timer = 0.0
        self.max_respawn_timer = 0.0
        self.current_gold = 0.0
        self.ally_status: List[bool] = []
        self.item_ready: Dict[int, bool] = {}
        self.health_history = collections.deque(maxlen=40)
        self.cs_per_min = 0.0
        self.vision_score = 0.0

        # Ability Levels
        self.abilities = {"Q": 0, "W": 0, "E": 0, "R": 0}
        self.last_event_id = -1
        self._last_cs_print = 0.0
        self._last_items_print = 0.0

        # Base Colors
        self.C_OFF = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_off)
        self.C_HEALTH = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_health)
        self.C_HEALTH_DEAD = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_health_dead)

        # Resource Colors
        self.C_MANA = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_mana)
        self.C_ENERGY = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_energy)
        self.C_FURY = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_fury)
        self.C_SHIELD = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_shield)
        self.C_NO_RESOURCE = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_no_resource)

        # Inne Kolory
        self.C_GOLD = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_gold)
        self.C_SPELL_READY = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_spell_ready)
        self.C_ORANGE = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_orange)
        self.C_DEAD_BG = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_dead_bg)
        self.C_ALLY_ALIVE = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_ally_alive)
        self.C_ALLY_DEAD = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_ally_dead)
        
        # Animations
        self.C_KILL_FLASH = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_kill_flash)
        self.C_EPIC_MONSTER_FLASH = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_epic_monster_flash)
        self.C_DOUBLE_KILL = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_double_kill)
        self.C_TRIPLE_KILL = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_triple_kill)
        self.C_QUADRA_KILL = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_quadra_kill)
        self.C_PENTA_KILL = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_penta_kill)
        self.C_ITEM_READY = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_item_ready)
        self.C_BURST_DAMAGE = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_burst_damage)
        self.C_VISION_SCORE = AsyncChromaClient.rgb_to_razer(*self.config.hud.colors.c_vision_score)

        self.active_animation: Optional[Animation] = None

    def update(self, game_data: Dict[str, Any]):
        active_player = game_data.get("activePlayer", {})
        champion_stats = active_player.get("championStats", {})

        # Health
        current_health = champion_stats.get("currentHealth", 0.0)
        max_health = champion_stats.get("maxHealth", 1.0)
        self.health_percent = current_health / max_health if max_health > 0 else 0.0
        self.is_dead = False  # Will be updated from all_players list

        # Mana / Energy
        current_resource = champion_stats.get("resourceValue", 0.0)
        max_resource = champion_stats.get("resourceMax", 1.0)
        self.resource_percent = current_resource / max_resource if max_resource > 0 else 0.0
        self.resource_type = champion_stats.get("resourceType", "MANA")

        # Gold
        self.current_gold = active_player.get("currentGold", 0.0)

        # Abilities (Q, W, E, R)
        abilities_data = active_player.get("abilities", {})
        for key in ["Q", "W", "E", "R"]:
            spell_data = abilities_data.get(key, {})
            self.abilities[key] = spell_data.get("abilityLevel", 0)

        # Player List (Respawn, Ally Status)
        active_summoner = active_player.get("summonerName") or active_player.get("riotIdGameName") or ""
        all_players = game_data.get("allPlayers", [])
        
        active_team = "ORDER"
        current_player_scores = {}
        for player in all_players:
            p_name = player.get("summonerName") or player.get("riotIdGameName") or ""
            if p_name == active_summoner and active_summoner != "":
                active_team = player.get("team", "ORDER")
                self.is_dead = player.get("isDead", False)
                self.respawn_timer = player.get("respawnTimer", 0.0)
                current_player_scores = player.get("scores", {})
                if self.is_dead:
                    if self.respawn_timer > self.max_respawn_timer:
                        self.max_respawn_timer = self.respawn_timer
                else:
                    self.max_respawn_timer = 0.0
                break
                
        # Gather allies excluding the active player
        allies = [p for p in all_players if p.get("team") == active_team and (p.get("summonerName") or p.get("riotIdGameName") or "") != active_summoner]
        allies = sorted(allies, key=lambda x: x.get("summonerName", "") or x.get("riotIdGameName", ""))
        self.ally_status = [not p.get("isDead", False) for p in allies]

        # Items
        active_items = []
        for player in all_players:
            p_name = player.get("summonerName") or player.get("riotIdGameName") or ""
            if p_name == active_summoner and active_summoner != "":
                active_items = player.get("items", [])
                break
                
        self.item_ready = {}
        for item in active_items:
            slot = item.get("slot", -1)
            can_use = item.get("canUse", False)
            if 0 <= slot <= 5:
                self.item_ready[slot] = can_use
                
        # Burst Damage Tracking
        current_time = time.time()
        self.health_history.append((current_time, current_health))

        # Filter elements older than 0.5s
        while self.health_history and current_time - self.health_history[0][0] > 0.5:
            self.health_history.popleft()

        if self.config.hud.features.enable_burst_warning and not self.is_dead and max_health > 0:
            if len(self.health_history) > 1:
                max_past_health = max(h for t, h in self.health_history)
                drop_ratio = (max_past_health - current_health) / max_health
                threshold = self.config.hud.features.burst_threshold_percent / 100.0
                if drop_ratio >= threshold:
                    self.active_animation = FlashAnimation(0.5, self.C_BURST_DAMAGE)
                    self.health_history.clear()

        # CS / min Metronome & Vision Score
        game_time = game_data.get("gameData", {}).get("gameTime", 0.0)
        creep_score = current_player_scores.get("creepScore", 0)
        self.vision_score = current_player_scores.get("wardScore", 0.0)

        self.cs_per_min = -1.0
        if game_time > 90.0:  # Start calculating after minion spawn
            self.cs_per_min = creep_score / (game_time / 60.0)

        # Events (Kills, Dragons, Level Up)
        events_data = game_data.get("events", {})
        for event in events_data.get("Events", []):
            event_id = event.get("EventID", -1)
            if event_id > self.last_event_id:
                self._handle_event(event)
                self.last_event_id = event_id

        self._calculate_base_hud()

    def _handle_event(self, event: Dict[str, Any]):
        event_name = event.get("EventName", "Unknown")
        if event_name == "ChampionKill" and self.config.hud.features.enable_kill_flash:
            self.active_animation = FlashAnimation(1.0, self.C_KILL_FLASH)
        elif event_name in ["DragonKill", "BaronKill"] and self.config.hud.features.enable_epic_monster_flash:
            self.active_animation = FlashAnimation(2.0, self.C_EPIC_MONSTER_FLASH)
        elif event_name == "LevelUp" and self.config.hud.features.enable_level_up_flash:
            self.active_animation = FlashAnimation(1.0, self.C_GOLD)
        elif event_name == "Multikill" and self.config.hud.features.enable_multikill_animations:
            kill_streak = event.get("KillStreak", 2)
            if kill_streak == 2:
                self.active_animation = DoubleKillAnimation(self.C_DOUBLE_KILL)
            elif kill_streak == 3:
                self.active_animation = TripleKillAnimation(self.C_TRIPLE_KILL)
            elif kill_streak == 4:
                self.active_animation = QuadraKillAnimation(self.C_QUADRA_KILL)
            elif kill_streak >= 5:
                self.active_animation = PentaKillAnimation(self.C_PENTA_KILL)

    def _get_resource_color(self) -> int:
        """Returns the appropriate color based on character resource type."""
        res_type = self.resource_type.upper()
        if res_type == "ENERGY":
            return self.C_ENERGY
        elif res_type in ["FURY", "BATTLEFURY", "DRAGONFURY", "RAGE", "HEAT", "FEROCITY", "BLOODWELL"]:
            return self.C_FURY
        elif res_type == "SHIELD":
            return self.C_SHIELD
        elif res_type == "NONE" or (
                self.resource_percent == 0.0 and self.resource_type == "MANA" and self.health_percent > 0):
            # If the character does not use a resource (e.g., Katarina)
            return self.C_NO_RESOURCE
        return self.C_MANA  # Default to Blue

    def _calculate_base_hud(self):
        # 1. Base Background
        bg_color = self.C_DEAD_BG if self.is_dead else self.C_OFF
        self._base_matrix = [[bg_color] * self.COLS for _ in range(self.ROWS)]

        # Calculate how many columns should be lit
        health_color = self.C_HEALTH_DEAD if self.is_dead else self.C_HEALTH
        active_resource_color = self._get_resource_color()

        num_health_cols = int(self.health_percent * self.BAR_WIDTH)
        num_mana_cols = int(self.resource_percent * self.BAR_WIDTH)

        # 2. Draw Health and Resource bars in the main section
        for col in range(self.BAR_WIDTH):
            # Upper half (rows 0, 1, 2) is Health
            if col < num_health_cols:
                for row in range(3):
                    self._base_matrix[row][col] = health_color

            # Lower half (rows 3, 4, 5) is Resource (Mana/Energy/Fury)
            if not self.is_dead and col < num_mana_cols:
                for row in range(3, 6):
                    # Do not draw a full bar if the character relies on no resources
                    if active_resource_color != self.C_NO_RESOURCE:
                        self._base_matrix[row][col] = active_resource_color

        # 3. Overlay abilities on top
        if not self.is_dead and self.config.hud.features.enable_spell_module:
            # Q, W, E, R (Row 2, Cols 2-5)
            if self.abilities["Q"] > 0: self._base_matrix[2][2] = self.C_SPELL_READY
            if self.abilities["W"] > 0: self._base_matrix[2][3] = self.C_SPELL_READY
            if self.abilities["E"] > 0: self._base_matrix[2][4] = self.C_SPELL_READY
            if self.abilities["R"] > 0: self._base_matrix[2][5] = self.C_SPELL_READY

            # D, F always orange statically (Row 3, Cols 4-5)
            self._base_matrix[3][4] = self.C_ORANGE
            self._base_matrix[3][5] = self.C_ORANGE

        # 4. Gold Module (Numpad)
        if self.config.hud.features.enable_gold_module:
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

        # 5. Respawn Timer (Row 1, Cols 2-11 = Number Keys 1-0)
        if self.is_dead and self.config.hud.features.enable_respawn_timer and self.max_respawn_timer > 0:
            ratio = self.respawn_timer / self.max_respawn_timer
            keys_to_light = int(ratio * 10)
            
            for i in range(10):
                c_idx = 2 + i  # Columns 2 to 11
                if i < keys_to_light:
                    self._base_matrix[1][c_idx] = self.C_OFF
                else:
                    self._base_matrix[1][c_idx] = self.C_DEAD_BG
                    
        # 6. Ally Status Indicator (Row 0, Cols 3-6 = F1-F4)
        if self.config.hud.features.enable_ally_status:
            for i in range(min(4, len(self.ally_status))):
                is_alive = self.ally_status[i]
                c_idx = 3 + i  # F1 to F4
                self._base_matrix[0][c_idx] = self.C_ALLY_ALIVE if is_alive else self.C_ALLY_DEAD

        # 7. Active Item Readiness (Row 1, Cols 2-7 = Keys 1-6)
        # Omit if dead (as Respawn Timer overrides this row)
        if not self.is_dead and self.config.hud.features.enable_item_indicator:
            for slot in range(0, 6):
                c_idx = 2 + slot  # Keys 1-6 map to cols 2-7 on Row 1
                if self.item_ready.get(slot, False):
                    self._base_matrix[1][c_idx] = self.C_ITEM_READY

        # 8. CS / min Metronome (Arrow Keys)
        if self.config.hud.features.enable_cs_metronome and not self.is_dead:
            arrow_keys = [(4, 16), (5, 15), (5, 16), (5, 17)]
            
            if self.cs_per_min < 0:
                # Early game before minion spawn, keep arrows empty
                cs_col = self.C_OFF
            else:
                target_cs = 8.0
                t = self.cs_per_min / target_cs if target_cs > 0 else 0
                
                c1 = self.config.hud.colors.c_cs_poor
                c2 = self.config.hud.colors.c_cs_good
                t = max(0.0, min(1.0, t))
                interp_rgb = [int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)]
                cs_col = AsyncChromaClient.rgb_to_razer(*interp_rgb)
            
            for r, c in arrow_keys:
                self._base_matrix[r][c] = cs_col
                
        # 9. Vision Score Tracker (Insert, Home, PgUp, Del, End, PgDn)
        if self.config.hud.features.enable_vision_tracker and not self.is_dead:
            nav_keys = [(1, 15), (1, 16), (1, 17), (2, 15), (2, 16), (2, 17)]
            score_per_key = 5.0
            keys_to_light = int(self.vision_score // score_per_key)
            
            for i, (r, c) in enumerate(nav_keys):
                if i < keys_to_light:
                    self._base_matrix[r][c] = self.C_VISION_SCORE

    def get_matrix(self) -> List[List[int]]:
        current_matrix = [list(row) for row in self._base_matrix]
        anim = self.active_animation
        if anim is not None:
            if self.config.hud.features.enable_animations and anim.is_active:
                current_matrix = anim.get_frame(current_matrix)
            else:
                self.active_animation = None
        return current_matrix