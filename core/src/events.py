from uuid import uuid4
from datetime import datetime, timezone
import threading
from multiprocessing import Queue
import logging

_event_queue = Queue()
_event_lock = threading.Lock()

def push(event_type: str, event: dict):
    global _event_queue

    with _event_lock:
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        cloudevent = {
            "context": {
                "version": "1.0.0",
                "id": str(uuid4()),
                "timestamp": timestamp,
                "type": event_type,
                "action": "create",
                "dataschema": event_type,
                "datacontenttype": "json",
            },
            "data": event
        }
        _event_queue.put_nowait(cloudevent)
        
        logging.info(f"Event pushed to queue: {cloudevent}")


def listen() -> 'dict | None':
    """
    Listen to the event queue, timeout after 5 seconds and
    return None if no event is received.
    """
    global _event_queue

    try:
        return _event_queue.get(block=True, timeout=5)
    except:
        # normal in timeout when queue is empty
        return None