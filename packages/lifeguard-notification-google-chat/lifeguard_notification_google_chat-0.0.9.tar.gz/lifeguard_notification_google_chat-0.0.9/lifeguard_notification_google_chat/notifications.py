"""
Base of notification system
"""
from copy import deepcopy
import json
import traceback

from lifeguard.http_client import post
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.notifications import NotificationBase

from lifeguard_notification_google_chat.settings import (
    GOOGLE_DEFAULT_CHAT_ROOM,
    GOOGLE_LOG_RESPONSE,
)

HEADERS = {"Content-Type": "application/json; charset=UTF-8"}


class GoogleNotificationBase(NotificationBase):
    """
    Base of notification
    """

    @property
    def name(self):
        return "google-chat"

    @staticmethod
    def __normalize_content(content):
        if not isinstance(content, list):
            content = [content]
        return content

    @staticmethod
    def __log_response(response):
        if GOOGLE_LOG_RESPONSE:
            logger.info("google api response: %s", response)

    def send_single_message(self, content, settings):
        logger.info("seding single message to google chat")
        content = self.__normalize_content(content)

        first_message = content.pop(0)

        threads = self.__post_message(first_message, [], settings)

        self.__send_to_thread(deepcopy(threads), content, settings)

    def init_thread(self, content, settings):
        logger.info("creating a new thread in google chat")
        content = self.__normalize_content(content)

        first_message = content.pop(0)

        threads = self.__post_message(first_message, [], settings)
        self.__send_to_thread(threads, content, settings)

        return threads

    def update_thread(self, threads, content, settings):
        logger.info("updating thread %s in google chat", threads)
        self.__send_to_thread(threads, content, settings)

    def close_thread(self, threads, content, settings):
        logger.info("closing thread %s in google chat", threads)
        self.__send_to_thread(threads, content, settings)

    def __get_thread(self, threads, index):
        try:
            return threads[index]
        except IndexError:
            return None

    def __post_message(self, text, threads, settings):
        new_threads = []
        rooms = (
            settings.get("notification", {})
            .get("google", {})
            .get("rooms", [GOOGLE_DEFAULT_CHAT_ROOM])
        )

        for index, room in enumerate(rooms):
            try:
                thread = self.__get_thread(threads, index)
                data = {"text": text}

                if thread:
                    data["thread"] = thread

                response = post(room, data=json.dumps(data), headers=HEADERS).json()
                self.__log_response(response)
                if "thread" in response:
                    new_threads.append(response["thread"])
            except Exception as error:
                logger.error(
                    "error on post message: %s",
                    str(error),
                    extra={"traceback": traceback.format_exc()},
                )
                new_threads.append(None)

        return new_threads

    def __send_to_thread(self, threads, content, settings):
        if not isinstance(content, list):
            content = [content]

        for entry in content:
            self.__post_message(entry, threads, settings)
