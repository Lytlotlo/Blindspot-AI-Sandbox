from datetime import datetime
from typing import List, Dict, Any


class LogService:
    """
    A simple, in-memory service to store and retrieve the latest scan events.
    It holds a maximum of 100 events to prevent memory issues.
    """
    def __init__(self):
        """Initializes the event list."""
        self.events: List[Dict[str, Any]] = []

    def add_event(self, event_type: str, data: dict):
        """
        Creates a new log entry with a timestamp and prepends it to the event list.
        If the list exceeds 100 entries, the oldest one is removed.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "data": data
        }

        # Maintain a rolling log of the last 100 events
        if len(self.events) >= 100:
            self.events.pop()
        
        self.events.insert(0, log_entry)

    def get_events(self) -> List[Dict[str, Any]]:
        """Returns the current list of all stored events."""
        return self.events

# A single, shared instance of the service for the entire application to use.
log_service = LogService()