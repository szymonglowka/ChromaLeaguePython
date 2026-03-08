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
    """Exception thrown when Chroma SDK returns an error (result != 0)."""
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
        """Dynamic URL using session_id as the port."""
        return f"http://{self.host}:{self._sid}/chromasdk"

    async def _async_request(self, method: str, url: str, json_data: dict = None) -> dict:
        """Central method for sending requests with error verification."""
        if not self.session:
            raise ConnectionError("No open aiohttp session.")

        async with self.session.request(method, url, json=json_data, headers=self.headers) as response:
            if response.status == 404:
                raise ConnectionError("No access to Chroma SDK (Error 404).")

            response.raise_for_status()
            data = await response.json()

            # Verification of error code from Razer
            if "result" in data and data["result"] != 0:
                raise ChromaResultError(f"Chroma SDK returned error: {data['result']}")

            # Default rate-limiting
            await asyncio.sleep(0.1)
            return data

    async def async_identify(self) -> bool:
        """Interface identification (step 1)."""
        try:
            async with self.session.get(self.init_url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "version" in data:
                        logger.info(f"Recognized Chroma SDK version: {data['version']}")
                        return True
        except Exception as e:
            logger.debug(f"Error during identification: {e}")
        return False

    async def async_connect(self) -> bool:
        """Application registration and session initialization (step 2)."""
        self.session = aiohttp.ClientSession()

        if not await self.async_identify():
            logger.error("Failed to identify Chroma SDK.")
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
                logger.info(f"Connected. Session ID (Port): {self._sid}")

                # Initial session heartbeat (twice)
                await self.async_keep()
                await self.async_keep()

                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                return True
        except Exception as e:
            logger.error(f"Failed to connect to SDK: {e}")

        return False

    async def async_keep(self):
        """Session keep-alive - Heartbeat (step 4)."""
        if not self._connected:
            return
        try:
            url = f"{self.session_url}/heartbeat"
            await self._async_request("PUT", url)
        except Exception as e:
            logger.debug(f"Heartbeat failed: {e}")

    async def _heartbeat_loop(self):
        """Asynchronous loop for maintaining connection."""
        while self._connected:
            await asyncio.sleep(1.0)
            await self.async_keep()

    async def async_disconnect(self):
        """Closing session (step 5)."""
        self._connected = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        if self._sid and self.session:
            try:
                await self._async_request("DELETE", self.session_url)
                logger.info("Disconnected from Chroma SDK.")
            except Exception as e:
                logger.error(f"Error during disconnection: {e}")

        if self.session:
            await self.session.close()

    @staticmethod
    def rgb_to_razer(r: int, g: int, b: int) -> int:
        """
        Color calculation formula (reversed BGR model): R + G * 256 + B * 65536
        """
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        return r + (g * 256) + (b * 65536)

    async def async_effect_keyboard(self, matrix: List[List[int]]) -> bool:
        """Sending custom matrix CHROMA_CUSTOM (step 3)."""
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
            logger.debug(f"Error sending matrix: {e}")
            return False