from abc import abstractmethod
from typing import Any

from ..domain import DomainEvent


class AbstractDomainEventsService:

    @abstractmethod
    def publish(self, message: Any, event_type: DomainEvent, exchange: str = None):
        pass