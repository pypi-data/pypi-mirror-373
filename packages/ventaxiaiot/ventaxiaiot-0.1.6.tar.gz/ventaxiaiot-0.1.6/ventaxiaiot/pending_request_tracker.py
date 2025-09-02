# File: ventaxiaiot/pending_request_tracker.py
import time
from collections import OrderedDict
from typing import Optional

class PendingRequestTracker:
    def __init__(self, max_items: int = 100, timeout: int = 30):
        self._pending: OrderedDict[int, tuple[float, dict]] = OrderedDict()
        self._max_items = max_items
        self._timeout = timeout

    def add(self, msg_id: int, meta: dict):
        self.cleanup()
        if len(self._pending) >= self._max_items:
            self._pending.popitem(last=False)
        self._pending[msg_id] = (time.time(), meta)

    def pop(self, msg_id: int) -> Optional[dict]:
        return self._pending.pop(msg_id, (None, None))[1]

    def cleanup(self):
        now = time.time()
        expired = [mid for mid, (ts, _) in self._pending.items() if now - ts > self._timeout]
        for mid in expired:
            del self._pending[mid]   