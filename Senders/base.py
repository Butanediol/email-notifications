from abc import ABC, abstractmethod
from email.message import Message


class BaseSender(ABC):

    @classmethod
    @abstractmethod
    def enabled(cls) -> bool:
        """Return True if this sender is configured and should be used."""
        pass

    @abstractmethod
    def send(self, message: Message):
        """Send notification for the given email message."""
        pass
