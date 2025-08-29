from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseDetector(ABC):
    """
    An abstract base class that defines the required interface for all
    detector modules in the application.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """A unique, machine-readable name for the detector (e.g., 'pii_detector')."""
        pass

    @abstractmethod
    def detect(self, text: str) -> Dict[str, Any]:
        """
        Performs the core detection logic on the input text.

        Args:
            text: The user-provided prompt to analyze.

        Returns:
            A dictionary containing the findings, or an empty dictionary if
            no threats are found.
        """
        pass