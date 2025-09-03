from collections import defaultdict
from dataclasses import dataclass
import time
from typing import Callable, DefaultDict, Generic, TypeVar

from pictorus.logging_utils import get_logger


T = TypeVar("T")

logger = get_logger()


@dataclass
class QueueConfig(Generic[T]):
    publish_interval_s: float
    publish_queue_size: int
    max_queue_size: int
    default_factory: Callable[[], T]
    append_data: Callable[[T, T], None]
    trim_data: Callable[[T, int], None]
    get_length: Callable[[T], int]


class DataQueue(Generic[T]):
    def __init__(self, config: QueueConfig) -> None:
        # Queue is a list of data keyed by target ID
        self.queue: DefaultDict[str, T] = defaultdict(config.default_factory)
        self.config = config
        self._last_publish_time = 0

    def add_data(self, target_id: str, data: T) -> None:
        self.config.append_data(self.queue[target_id], data)

    def check_publish(self) -> bool:
        # Right now we publish everything at once. Might make sense to do this per target ID instead
        publish_interval_elapsed = (
            time.time() - self._last_publish_time >= self.config.publish_interval_s
        )
        max_size = 0
        for data in self.queue.values():
            size = self.config.get_length(data)
            if size > self.config.max_queue_size:
                self.config.trim_data(data, self.config.max_queue_size)

            max_size = max(max_size, size)

        should_publish = max_size >= self.config.publish_queue_size or (
            publish_interval_elapsed and max_size > 0
        )
        return should_publish

    def load_data(self, target_id: str):
        """
        Load data from the queue and return it.

        Data marked as published after loading.
        """
        if target_id not in self.queue:
            return None

        data = self.queue[target_id]
        self.queue[target_id] = self.config.default_factory()  # Reset to default
        self._last_publish_time = time.time()
        return data

    def target_ids(self):
        """
        Get the target IDs currently in the queue.
        """
        return list(self.queue.keys())
