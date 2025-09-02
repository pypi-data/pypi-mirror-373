from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging import getLogger
from threading import Thread, Event as EventThreading
from time import sleep
from typing import Type, Optional, Generator
from uuid import UUID

from edri.config.setting import CACHE_TIMEOUT, CACHE_INFO_MESSAGE
from edri.dataclass.event import Event
from edri.dataclass.response import ResponseStatus


@dataclass
class CacheItem:
    event: Event
    time: datetime = field(default_factory=datetime.now)


class Cache:
    """
    A cache for temporarily storing events with functionality to append events,
    find events based on type and other criteria, periodically clean expired events,
    and maintain a list of the most recent events for specific needs.

    Attributes:
        items (List[:class:`edri.router.CacheItem`]): A list of CacheItem instances representing the cached events.
        logger (:class:`logging.Logger`): Logger instance for logging cache operations and statuses.
        cleaner (:class:`threading.Thread`): A background thread for periodically cleaning the cache of expired items.
        cleaner_stop (:class:`threading.Event`): An event flag used to signal the cleaner thread to stop.
    """

    def __init__(self) -> None:
        """
        Initializes the Cache instance, starts the background cleaner thread, and
        sets up the necessary attributes for cache management.
        """
        self.items: list[CacheItem] = []
        self.logger = getLogger(__name__)
        self.cleaner = Thread(target=self.clean, daemon=True)
        self.cleaner_stop = EventThreading()
        self.cleaner.start()

    def __del__(self):
        """
        Ensures that the cleaner thread is properly stopped when the Cache instance is destroyed.
        This method sets the stop event for the cleaner thread to signal it to stop its operation,
        preventing potential resource leaks or dangling threads.
        """
        if self.cleaner_stop:
            self.cleaner_stop.set()

    def append(self, event: Event) -> datetime:
        """
        Adds a new event to the cache and returns the timestamp when the event was added.

        :param event: The event to be added to the cache.
        :type event: :class:`edri.dataclass.event.Event`
        :return: The timestamp when the event was added to the cache.
        :rtype: datetime
        """
        item = CacheItem(event)
        self.items.append(item)
        return item.time

    def find(
        self, event_type: Type[Event], request: bool, from_time: Optional[datetime]
    ) -> list[Event]:
        """
        Finds events in the cache matching the specified type, request status, and time criteria.

        :param event_type: The type of event to search for.
        :type event_type: Type[:class:`edri.dataclass.event.Event`]
        :param request: Whether to search for events with a specific request status.
        :type request: bool
        :param from_time: The starting time to search for events from. If None, all matching events are returned regardless of time.
        :type from_time: Optional[datetime]
        :return: A list of events matching the specified criteria.
        :rtype: List[:class:`edri.dataclass.event.Event`]
        """
        items = [
            item
            for item in self.items
            if isinstance(item.event, event_type)
            and (
                item.event.response is None
                or item.event.response.get_status() == ResponseStatus.NONE
            )
            == request
        ]
        if from_time is not None:
            return [item.event for item in items if item.time >= from_time]
        else:
            return [item.event for item in items]

    def clean(self) -> None:
        """
        Background thread method to clean expired events from the cache based on the `CACHE_TIMEOUT`.
        """
        last_log_sent = datetime.now()
        delta = timedelta(seconds=CACHE_TIMEOUT)
        while not self.cleaner_stop.is_set():
            now = datetime.now()
            limit = now - delta
            self.items = [item for item in self.items if item.time > limit]
            if now - timedelta(seconds=CACHE_INFO_MESSAGE) >= last_log_sent:
                self.logger.info("Count of cached events: %s", len(self.items))
                last_log_sent = now
            sleep(1)

    def last_events(self) -> dict[UUID, str]:
        """
        Retrieves the last events for specific identifiers, useful for tracking the most recent state or activity.

        :return: A dictionary mapping identifiers to their last event keys.
        :rtype: dict[:class:`uuid.UUID`, str]
        """
        return {
            item.event._switch.router_id: item.event._api.key
            for item in self.items
            if item.event._switch
        }

    def events_from(self, key: str) -> Generator[Event, None, None]:
        """
        Generates all events from the cache following a specific event ID.

        :param key: The unique identifier key of the event to start from.
        :type key: str
        :yield: Events occurring after the specified event.
        :rtype: Generator[:class:`edri.dataclass.event.Event`, None, None]
        """
        found = False
        for item in self.items:
            if found:
                yield item.event
                continue
            if item.event._api.key == key:
                found = True

    def quit(self) -> None:
        """
        Signals the cleaner thread to stop its operation and waits for it to finish, ensuring a graceful shutdown of the cache cleaning process.
        """
        self.cleaner_stop.set()
        self.cleaner.join()
