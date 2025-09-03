from enum import Enum
from typing import Dict, Set

class AtEventType(Enum):
    NONE = 0
    SHARED_KEY_NOTIFICATION = 1
    UPDATE_NOTIFICATION = 2
    DELETE_NOTIFICATION = 3
    UPDATE_NOTIFICATION_TEXT = 4
    STATS_NOTIFICATION = 5
    MONITOR_HEARTBEAT_ACK = 6
    MONITOR_EXCEPTION = 7
    DECRYPTED_UPDATE_NOTIFICATION = 8
    USER_DEFINED = 9
    
    def __str__(self):
        return self.name
    
    def to_string(event):
        if event == 0:
            return "NONE"
        elif event == 1:
            return "SHARED_KEY_NOTIFICATION"
        elif event == 2:
            return "UPDATE_NOTIFICATION"
        elif event == 3:
            return "DELETE_NOTIFICATION"
        elif event == 4:
            return "UPDATE_NOTIFICATION_TEXT"
        elif event == 5:
            return "STATS_NOTIFICATION"
        elif event == 6:
            return "MONITOR_HEARTBEAT_ACK"
        elif event == 7:
            return "MONITOR_EXCEPTION"
        elif event == 8:
            return "DECRYPTED_UPDATE_NOTIFICATION"
        elif event == 9:
            return "USER_DEFINED"
        else:
            return "UNKNOWN"
        

class AtEvent:
    def __init__(self, event_type, event_data):
        self.event_type = event_type
        self.event_data = event_data
