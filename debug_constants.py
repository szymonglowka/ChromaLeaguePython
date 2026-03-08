import copy
from src.chromaleague.config_manager import ConfigManager
from src.chromaleague.hud_manager import HUDManager

cm = ConfigManager("config.json")
hud = HUDManager(cm.load())

print(f"C_OFF = {hud.C_OFF}")
print(f"c_off array = {hud.config.hud.colors.c_off}")
print(f"C_DEAD_BG = {hud.C_DEAD_BG}")
print(f"c_cs_poor = {hud.config.hud.colors.c_cs_poor}")
print(f"cs_per_min = {hud.cs_per_min}")

for r, c in [(4, 15), (5, 14), (5, 15), (5, 16)]:
    print(f"Before update: Row {r}, Col {c} -> {hud._base_matrix[r][c]}")

mock_data = {
    "activePlayer": {"scores": {"creepScore": 0, "wardScore": 0.0}},
    "gameData": {"gameTime": 0.0},
    "events": {}
}

hud.update(mock_data)
matrix = hud.get_matrix()
print(f"After update cs_min = {hud.cs_per_min}")
for r, c in [(4, 15), (5, 14), (5, 15), (5, 16)]:
    print(f"After update: Row {r}, Col {c} -> {matrix[r][c]}")
