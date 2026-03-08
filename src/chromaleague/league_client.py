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

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AsyncLeagueClient:
    # Riot używa zamiennie dwóch portów dla Live Client Data API w zależności od patcha
    PORTS = [29292, 2999]

    def __init__(self, timeout: float = 1.0):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.active_port: Optional[int] = None
        self._log_suppressed = False

    async def get_all_game_data(self) -> Optional[Dict[str, Any]]:
        if not self.session:
            # Pomijamy weryfikację SSL, ponieważ Riot używa certyfikatów self-signed
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(connector=connector, timeout=self.timeout)

        ports_to_try = [self.active_port] if self.active_port else self.PORTS

        for port in ports_to_try:
            url = f"https://127.0.0.1:{port}/liveclientdata/allgamedata"
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    # Jeśli się udało, zapisujemy port na przyszłość
                    self.active_port = port
                    if self._log_suppressed:
                        logger.info(f"Pomyślnie połączono z grą na porcie {port}!")
                        self._log_suppressed = False
                    return await response.json()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                continue  # Jeśli się nie udało, spróbuj kolejnego portu z listy

        if not self._log_suppressed:
            logger.info("Oczekiwanie na uruchomienie meczu w League of Legends...")
            self._log_suppressed = True

        self.active_port = None
        return None

    async def close(self):
        if self.session:
            await self.session.close()