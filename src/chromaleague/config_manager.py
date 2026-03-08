import json
import os
import logging
from dataclasses import dataclass, field, asdict, fields
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class ColorConfig:
    c_off: List[int] = field(default_factory=lambda: [0, 0, 0])
    c_health: List[int] = field(default_factory=lambda: [0, 255, 0])  # Green
    c_health_dead: List[int] = field(default_factory=lambda: [50, 0, 0])  # Dark red

    c_mana: List[int] = field(default_factory=lambda: [0, 0, 255])  # Blue
    c_energy: List[int] = field(default_factory=lambda: [255, 255, 0])  # Yellow
    c_fury: List[int] = field(default_factory=lambda: [255, 0, 0])  # Red
    c_shield: List[int] = field(default_factory=lambda: [255, 255, 255])  # White
    c_no_resource: List[int] = field(default_factory=lambda: [20, 20, 20])  # Dark gray

    c_gold: List[int] = field(default_factory=lambda: [255, 215, 0])  # Gold
    c_spell_ready: List[int] = field(default_factory=lambda: [148, 0, 211])  # Purple
    c_orange: List[int] = field(default_factory=lambda: [255, 140, 0])  # Orange for D/F
    c_dead_bg: List[int] = field(default_factory=lambda: [20, 20, 20])  # Gray background on death
    
    c_kill_flash: List[int] = field(default_factory=lambda: [255, 0, 0])
    c_epic_monster_flash: List[int] = field(default_factory=lambda: [128, 0, 128])
    
    c_ally_alive: List[int] = field(default_factory=lambda: [0, 255, 0])
    c_ally_dead: List[int] = field(default_factory=lambda: [50, 0, 0])
    
    # Epic 3 & Multikills
    c_double_kill: List[int] = field(default_factory=lambda: [0, 255, 255])
    c_triple_kill: List[int] = field(default_factory=lambda: [255, 105, 180])
    c_quadra_kill: List[int] = field(default_factory=lambda: [255, 0, 0])
    c_penta_kill: List[int] = field(default_factory=lambda: [255, 215, 0])
    c_burst_damage: List[int] = field(default_factory=lambda: [255, 255, 255])
    c_item_ready: List[int] = field(default_factory=lambda: [255, 255, 255])
    c_cs_poor: List[int] = field(default_factory=lambda: [255, 0, 0])
    c_cs_good: List[int] = field(default_factory=lambda: [0, 255, 0])
    c_vision_score: List[int] = field(default_factory=lambda: [148, 0, 211])


@dataclass
class FeatureToggleConfig:
    enable_animations: bool = True
    enable_kill_flash: bool = True
    enable_epic_monster_flash: bool = True
    enable_level_up_flash: bool = True
    
    enable_gold_module: bool = True
    enable_spell_module: bool = True
    
    enable_respawn_timer: bool = True
    enable_ally_status: bool = True
    
    # Epic 3 & Multikills
    enable_multikill_animations: bool = True
    enable_item_indicator: bool = True
    enable_burst_warning: bool = True
    burst_threshold_percent: float = 30.0  # Threshold in percentage (e.g. 30.0 = 30%)
    enable_cs_metronome: bool = True
    enable_vision_tracker: bool = True


@dataclass
class HUDConfig:
    colors: ColorConfig = field(default_factory=ColorConfig)
    features: FeatureToggleConfig = field(default_factory=FeatureToggleConfig)


@dataclass
class AppConfig:
    hud: HUDConfig = field(default_factory=HUDConfig)


class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = AppConfig()
        self._last_modified_time = 0.0
        self._is_dirty = False

    def load(self) -> AppConfig:
        """Loads the configuration from the file. If it doesn't exist, creates a default one."""
        if not os.path.exists(self.config_path):
            logger.info(f"Configuration file not found at {self.config_path}. Generating default config.")
            self.save()
            return self.config

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.config = self._dict_to_app_config(data)
            
            # Update last modified time explicitly on manual load
            if os.path.exists(self.config_path):
                self._last_modified_time = os.path.getmtime(self.config_path)

            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}. Using default configuration.")
            self.config = AppConfig()

        return self.config

    def refresh_if_changed(self) -> bool:
        """Checks if the config file was changed on the filesystem, and reloads it if so."""
        changed = False
        if os.path.exists(self.config_path):
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime > self._last_modified_time:
                logger.info("Detected configuration change on disk. Reloading...")
                self.load()
                self._last_modified_time = current_mtime
                changed = True
                
        if getattr(self, "_is_dirty", False):
            self._is_dirty = False
            return True
            
        return changed

    def save(self):
        """Saves current configuration to the config file as JSON."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, indent=4)
            self._last_modified_time = os.path.getmtime(self.config_path)
            self._is_dirty = True
            logger.info(f"Configuration saved to {self.config_path}.")
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_path}: {e}")

    def _dict_to_app_config(self, data: Dict[str, Any]) -> AppConfig:
        """Helper to map a dictionary back strictly to our dataclasses."""
        hud_data = data.get("hud", {})
        colors_data = hud_data.get("colors", {})
        features_data = hud_data.get("features", {})
        
        color_fields = {f.name for f in fields(ColorConfig)}
        feature_fields = {f.name for f in fields(FeatureToggleConfig)}
        
        colors = ColorConfig(**{k: v for k, v in colors_data.items() if k in color_fields})
        features = FeatureToggleConfig(**{k: v for k, v in features_data.items() if k in feature_fields})
        
        hud = HUDConfig(colors=colors, features=features)
        return AppConfig(hud=hud)
