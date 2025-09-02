"""
Lifeguard integration with Google Chat
"""
from lifeguard.notifications import append_notification_implementation

from lifeguard_notification_google_chat.notifications import \
    GoogleNotificationBase


class LifeguardNotificationGoogleChat:
    def __init__(self, lifeguard_context):
        self.lifeguard_context = lifeguard_context
        append_notification_implementation(GoogleNotificationBase)

def init(lifeguard_context):
    LifeguardNotificationGoogleChat(lifeguard_context)
