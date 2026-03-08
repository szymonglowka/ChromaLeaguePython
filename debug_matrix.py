import copy
from src.chromaleague.config_manager import ConfigManager
from src.chromaleague.hud_manager import HUDManager

cm = ConfigManager("config.json")
hud = HUDManager(cm.load())

mock_data = {
    "activePlayer": {"scores": {"creepScore": 0, "wardScore": 0.0}},
    "gameData": {"gameTime": 0.0},
    "events": {}
}

print(f"is_dead BEFORE update: {hud.is_dead}")

hud.update(mock_data)

print(f"is_dead AFTER update: {hud.is_dead}")
print(f"cs_per_min: {hud.cs_per_min}")
print(f"cs metronome enabled: {hud.config.hud.features.enable_cs_metronome}")

for r,c in [(4, 15), (5, 14), (5, 15), (5, 16)]:
    print(f"Direct _base_matrix at {r},{c} is {hud._base_matrix[r][c]}")
