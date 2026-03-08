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

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import logging
import threading
from src.chromaleague.chroma_client import AsyncChromaClient
from src.chromaleague.league_client import AsyncLeagueClient
from src.chromaleague.hud_manager import HUDManager
from src.chromaleague.config_manager import ConfigManager
from src.chromaleague.gui import ConfiguratorGUI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ChromaLeagueApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()
        
        self.chroma = AsyncChromaClient()
        self.league = AsyncLeagueClient()
        self.hud = HUDManager(self.config)
        self.running = True

    async def run(self):
        if not await self.chroma.async_connect():
            logger.error("Failed to start Chroma client. Shutting down...")
            return

        logger.info("AIOChromaLeague started.")

        try:
            while self.running:
                # Force refresh from disk memory dynamically
                if self.config_manager.refresh_if_changed():
                    logger.info("Applying new configuration to HUDManager.")
                    # We create a new HUDManager so the new config takes effect cleanly
                    self.hud = HUDManager(self.config_manager.config)

                game_data = await self.league.get_all_game_data()

                if game_data:
                    self.hud.update(game_data)
                    matrix = self.hud.get_matrix()
                    await self.chroma.async_effect_keyboard(matrix)
                else:
                    # Turn off keyboard (black matrix) when game is not running
                    empty_matrix = [[0] * 22 for _ in range(6)]
                    await self.chroma.async_effect_keyboard(empty_matrix)
                    await asyncio.sleep(1.0)

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("Application interrupted.")
        finally:
            self.running = False
            await self.chroma.async_disconnect()
            await self.league.close()


def start_asyncio_loop(app: ChromaLeagueApp):
    # Set up a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error in background loop: {e}")
    finally:
        loop.close()


if __name__ == "__main__":
    app = ChromaLeagueApp()
    
    # Run the background Chroma/League loop in a separate thread
    bg_thread = threading.Thread(target=start_asyncio_loop, args=(app,), daemon=True)
    bg_thread.start()
    
    # Run the GUI in the main thread (required by Tkinter/CustomTkinter)
    try:
        gui = ConfiguratorGUI(app)
        gui.mainloop()
        
        # When GUI closes, flag the background app to stop
        app.running = False
        logger.info("GUI closed, shutting down background thread...")
    except KeyboardInterrupt:
        logger.info("Application closed by user (Ctrl+C).")
        app.running = False