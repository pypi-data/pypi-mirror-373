# File: ventaxiaiot/commands.py
import asyncio
import json
import logging

from ventaxiaiot.pending_request_tracker import PendingRequestTracker
from ventaxiaiot.sentinel_kinetic import SentinelKinetic

_LOGGER = logging.getLogger(__name__)

class VentClientCommands:
    def __init__(self, wifi_device_id, pendingRequestTracker : PendingRequestTracker):
        self._msg_id = 1
        self.device = SentinelKinetic()
        self.wifi_device_id = wifi_device_id
        self.tracker = pendingRequestTracker
        _LOGGER.debug("VentClientCommands __init__ called")

    def _next_msg_id(self):
        val = self._msg_id
        self._msg_id += 1
        return val

    async def send_subscribe(self, client):
        topics = [
            ("sub", "rd"),
            ("sub", "ee"),
            ("get", "rd"),
            ("pub", "wr", {"tsreq": 1}),
            ("get", "ee")           
        ] 

        for mtype, t_suffix, *extra in topics:
            msg = {"m": mtype, "i": self._next_msg_id()}
            if t_suffix:
                msg["t"] = f"{self.wifi_device_id}/{t_suffix}"
            if mtype == "pub":
                msg["d"] = extra[0]
                msg["f"] = 4           
            await client.send(json.dumps(msg))
            await asyncio.sleep(0.1)

    async def send_cfg_command(self, client, cmd: str):
        msg_id = self._next_msg_id()
        msg = {
            "m": "cfg",
            "cfgcmd": cmd,
            "i": msg_id
        }
        self.tracker.add(msg_id, {"cfgcmd": cmd})
        await client.send(json.dumps(msg))
        await asyncio.sleep(0.1)

    async def send_boost_request(self, client):
        msg = {
            "m": "pub",
            "t": f"{self.wifi_device_id}/wr",
            "d": {"ar_af": 3, "ar_min": 15},
            "f": 4,
            "i": self._next_msg_id(),
        }
        await client.send(json.dumps(msg))
        await asyncio.sleep(0.1)
        
    async def send_airflow_mode_request(self, client, mode: str, duration: int):
        if mode not in self.device.AIRFLOW_MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {list(self.device.AIRFLOW_MODES.keys())}")
        if duration not in self.device.VALID_DURATIONS:
            raise ValueError(f"Invalid duration: {duration}. Must be one of {sorted(self.device.VALID_DURATIONS)}")

        mode_code = self.device.AIRFLOW_MODES[mode]
        msg = {
            "m": "pub",
            "t": f"{self.wifi_device_id}/wr",
            "d": {
                "ar_af": mode_code,
                "ar_min": duration,
            },
            "f": 4,
            "i": self._next_msg_id(),
        }
        await client.send(json.dumps(msg))
        await asyncio.sleep(0.1)