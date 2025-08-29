from typing import Dict, Any

from transformers import pipeline

from .base_detector import BaseDetector


class LanguageDetector(BaseDetector):
    """
    Identifies the language of a text snippet using a pre-trained
    Hugging Face model.
    """

    @property
    def name(self) -> str:
        """The unique name of the detector."""
        return "language_detector"

    def __init__(self):
        """Initializes the text-classification pipeline from Hugging Face."""
        self.pipe = pipeline(
            "text-classification",
            model="papluca/xlm-roberta-base-language-detection"
        )

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Predicts the language of the input text.

        Args:
            text: The user-provided prompt to analyze.

        Returns:
            A dictionary containing the detected language code (e.g., {'language': 'en'}).
        """
        if not text.strip() or len(text.split()) < 2:
            return {"language": "en"}

        try:
            predictions = self.pipe(text, top_k=1, truncation=True)
            if predictions:
                lang_code = predictions[0]['label']
                return {"language": lang_code}
        except Exception as e:
            # In case of an error during prediction, log it and return 'unknown'.
            print(f"Language detection pipeline failed: {e}")
            return {"language": "unknown"}

        return {"language": "unknown"}