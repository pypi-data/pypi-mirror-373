# File: ventaxiaiot/messages.py
import json
import logging

from ventaxiaiot.pending_request_tracker import PendingRequestTracker
from ventaxiaiot.sentinel_kinetic import SentinelKinetic

_LOGGER = logging.getLogger(__name__)

class VentMessageProcessor:
    def __init__(self, pendingRequestTracker : PendingRequestTracker):
        self.device = SentinelKinetic()
        self.tracker = pendingRequestTracker
        
    async def process(self, raw_message):
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError:
            return


        self.device.apply_payload(data, self.tracker)

        if self._is_ack(data):
            await self._handle_ack(data)
        elif data.get("m") == "pub":
            await self._handle_publish(data)
        elif "r" in data:
            await self._handle_response(data)
        else:
            await self._handle_unknown(data)
            
            
        # Print the updated device state after processing each message
        _LOGGER.debug(self.device)  # concise
        # OR, for full dict print:
        # print(asdict(self.device))            


    def _is_ack(self, data):
        return isinstance(data, dict) and len(data) == 1 and "i" in data

    async def _handle_ack(self, data):
        _LOGGER.debug(f"ACK: {data}")

    async def _handle_publish(self, data):
        _LOGGER.debug(f"Publish: {data.get('t')}, Data: {data.get('d')}")

    async def _handle_response(self, data):
        _LOGGER.debug(f"Response: {data}")

    async def _handle_unknown(self, data):
        _LOGGER.debug(f"Unknown: {data}")
        


