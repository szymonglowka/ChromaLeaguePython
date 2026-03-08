import copy
from src.chromaleague.config_manager import ConfigManager
from src.chromaleague.hud_manager import HUDManager

cm = ConfigManager("config.json")
hud = HUDManager(cm.load())

# Mock data
mock_data = {
    "activePlayer": {
        "scores": {
            "creepScore": 0,
            "wardScore": 0.0
        }
    },
    "gameData": {
        "gameTime": 0.0
    },
    "events": {}
}

print("Running HUD update with gameTime=0.0")
hud.update(mock_data)
matrix = hud.get_matrix()

arrow_keys = [(4, 15), (5, 14), (5, 15), (5, 16)]
print("Arrow Keys colors:")
for r, c in arrow_keys:
    print(f"Row {r}, Col {c}: {matrix[r][c]}")
    
mock_data["gameData"]["gameTime"] = 10.0
print("\nRunning HUD update with gameTime=10.0")
hud.update(mock_data)
matrix = hud.get_matrix()
print("Arrow Keys colors:")
for r, c in arrow_keys:
    print(f"Row {r}, Col {c}: {matrix[r][c]}")
    
mock_data["gameData"]["gameTime"] = 120.0
mock_data["activePlayer"]["scores"]["creepScore"] = 0
print("\nRunning HUD update with gameTime=120.0, CS=0")
hud.update(mock_data)
matrix = hud.get_matrix()
print("Arrow Keys colors:")
for r, c in arrow_keys:
    print(f"Row {r}, Col {c}: {matrix[r][c]}")

mock_data["gameData"]["gameTime"] = 120.0
mock_data["activePlayer"]["scores"]["creepScore"] = 16
print("\nRunning HUD update with gameTime=120.0, CS=16 (8.0 cs/min)")
hud.update(mock_data)
matrix = hud.get_matrix()
print("Arrow Keys colors:")
for r, c in arrow_keys:
    print(f"Row {r}, Col {c}: {matrix[r][c]}")
