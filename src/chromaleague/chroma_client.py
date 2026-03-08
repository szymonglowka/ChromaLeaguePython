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

import asyncio
import aiohttp
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class ChromaResultError(Exception):
    """Wyjątek rzucany, gdy Chroma SDK zwróci błąd (result != 0)."""
    pass


class AsyncChromaClient:
    def __init__(self, host: str = "localhost", port: int = 54235):
        self.host = host
        self.port = port
        self.init_url = f"http://{self.host}:{self.port}/razer/chromasdk"
        self.headers = {"Host": "localhost", "content-type": "application/json"}

        self._sid: Optional[int] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._connected = False

    @property
    def session_url(self) -> str:
        """Dynamiczny adres URL używający session_id jako portu."""
        return f"http://{self.host}:{self._sid}/chromasdk"

    async def _async_request(self, method: str, url: str, json_data: dict = None) -> dict:
        """Centralna metoda do wysyłania zapytań z weryfikacją błędów."""
        if not self.session:
            raise ConnectionError("Brak otwartej sesji aiohttp.")

        async with self.session.request(method, url, json=json_data, headers=self.headers) as response:
            if response.status == 404:
                raise ConnectionError("Brak dostępu do Chroma SDK (Błąd 404).")

            response.raise_for_status()
            data = await response.json()

            # Weryfikacja kodu błędu od Razera
            if "result" in data and data["result"] != 0:
                raise ChromaResultError(f"Chroma SDK zwróciło błąd: {data['result']}")

            # Domyślny rate-limiting
            await asyncio.sleep(0.1)
            return data

    async def async_identify(self) -> bool:
        """Identyfikacja interfejsu (krok 1)."""
        try:
            async with self.session.get(self.init_url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "version" in data:
                        logger.info(f"Rozpoznano Chroma SDK wersja: {data['version']}")
                        return True
        except Exception as e:
            logger.debug(f"Błąd podczas identyfikacji: {e}")
        return False

    async def async_connect(self) -> bool:
        """Rejestracja aplikacji i inicjalizacja sesji (krok 2)."""
        self.session = aiohttp.ClientSession()

        if not await self.async_identify():
            logger.error("Nie udało się zidentyfikować Chroma SDK.")
            return False

        payload = {
            "title": "AIOChromaLeague",
            "description": "LoL Integration using aiohttp",
            "author": {"name": "AIOChroma", "contact": "N/A"},
            "device_supported": ["keyboard"],
            "category": "application"
        }

        try:
            data = await self._async_request("POST", self.init_url, json_data=payload)
            if "sessionid" in data:
                self._sid = int(data["sessionid"])
                self._connected = True
                logger.info(f"Połączono. ID Sesji (Port): {self._sid}")

                # Inicjalne podtrzymanie sesji (dwukrotne)
                await self.async_keep()
                await self.async_keep()

                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                return True
        except Exception as e:
            logger.error(f"Nie udało się połączyć z SDK: {e}")

        return False

    async def async_keep(self):
        """Podtrzymanie sesji - Heartbeat (krok 4)."""
        if not self._connected:
            return
        try:
            url = f"{self.session_url}/heartbeat"
            await self._async_request("PUT", url)
        except Exception as e:
            logger.debug(f"Heartbeat failed: {e}")

    async def _heartbeat_loop(self):
        """Asynchroniczna pętla podtrzymująca połączenie."""
        while self._connected:
            await asyncio.sleep(1.0)
            await self.async_keep()

    async def async_disconnect(self):
        """Kończenie sesji (krok 5)."""
        self._connected = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        if self._sid and self.session:
            try:
                await self._async_request("DELETE", self.session_url)
                logger.info("Rozłączono z Chroma SDK.")
            except Exception as e:
                logger.error(f"Błąd podczas rozłączania: {e}")

        if self.session:
            await self.session.close()

    @staticmethod
    def rgb_to_razer(r: int, g: int, b: int) -> int:
        """
        Formuła obliczania koloru (odwrócony model BGR): R + G * 256 + B * 65536
        """
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        return r + (g * 256) + (b * 65536)

    async def async_effect_keyboard(self, matrix: List[List[int]]) -> bool:
        """Wysyłanie niestandardowej matrycy CHROMA_CUSTOM (krok 3)."""
        if not self._connected:
            return False

        payload = {
            "effect": "CHROMA_CUSTOM",
            "param": matrix
        }

        try:
            await self._async_request("PUT", f"{self.session_url}/keyboard", json_data=payload)
            return True
        except Exception as e:
            logger.debug(f"Błąd wysyłania matrycy: {e}")
            return False