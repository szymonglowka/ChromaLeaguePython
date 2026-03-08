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
from src.chromaleague.chroma_client import AsyncChromaClient
from src.chromaleague.league_client import AsyncLeagueClient
from src.chromaleague.hud_manager import HUDManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ChromaLeagueApp:
    def __init__(self):
        self.chroma = AsyncChromaClient()
        self.league = AsyncLeagueClient()
        self.hud = HUDManager()
        self.running = True

    async def run(self):
        if not await self.chroma.async_connect():
            logger.error("Nie udało się uruchomić klienta Chroma. Zamykam...")
            return

        logger.info("AIOChromaLeague uruchomione.")

        try:
            while self.running:
                game_data = await self.league.get_all_game_data()

                if game_data:
                    self.hud.update(game_data)
                    matrix = self.hud.get_matrix()
                    await self.chroma.async_effect_keyboard(matrix)
                else:
                    # Wygaś klawiaturę (czarna matryca), gdy gra nie działa
                    empty_matrix = [[0] * 22 for _ in range(6)]
                    await self.chroma.async_effect_keyboard(empty_matrix)
                    await asyncio.sleep(1.0)

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("Przerwano działanie aplikacji.")
        finally:
            self.running = False
            await self.chroma.async_disconnect()
            await self.league.close()


if __name__ == "__main__":
    app = ChromaLeagueApp()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info("Aplikacja zamknięta przez użytkownika (Ctrl+C).")