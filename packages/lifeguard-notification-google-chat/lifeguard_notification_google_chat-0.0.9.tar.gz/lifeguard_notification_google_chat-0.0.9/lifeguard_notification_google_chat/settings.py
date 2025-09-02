"""
Lifeguard MongoDB Settings
"""
from lifeguard.settings import SettingsManager

SETTINGS_MANAGER = SettingsManager(
    {
        "LIFEGUARD_GOOGLE_DEFAULT_CHAT_ROOM": {
            "default": "",
            "description": "Incoming webhook full address",
        },
        "LIFEGUARD_GOOGLE_LOG_RESPONSE": {
            "default": "false",
            "type": "bool",
            "description": "Incoming webhook full address",
        },
    }
)

GOOGLE_DEFAULT_CHAT_ROOM = SETTINGS_MANAGER.read_value(
    "LIFEGUARD_GOOGLE_DEFAULT_CHAT_ROOM"
)
GOOGLE_LOG_RESPONSE = SETTINGS_MANAGER.read_value("LIFEGUARD_GOOGLE_LOG_RESPONSE")
