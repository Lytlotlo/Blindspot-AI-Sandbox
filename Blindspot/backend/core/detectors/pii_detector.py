import re
from typing import Dict, Any

from .base_detector import BaseDetector


class PIIDetector(BaseDetector):
    """
    Detects Personally Identifiable Information (PII) using regular expressions.
    """

    @property
    def name(self) -> str:
        """The unique name of the detector."""
        return "pii_detector"

    def __init__(self):
        """Initializes the detector and compiles the regex patterns for efficiency."""
        self.patterns = {
            "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "PHONE_NUMBER": re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        }

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Scans the input text for any defined PII patterns.

        Args:
            text: The user-provided prompt to analyze.

        Returns:
            A dictionary containing a "PII Detected" finding if PII is found,
            otherwise an empty dictionary.
        """
        findings = [
            pii_type for pii_type, pattern in self.patterns.items() if pattern.search(text)
        ]

        if findings:
            return {
                "finding": "PII Detected",
                "score": 1.0,  # PII is always considered a high-severity risk.
                "details": f"Detected PII types: {', '.join(findings)}",
            }
            
        return {}