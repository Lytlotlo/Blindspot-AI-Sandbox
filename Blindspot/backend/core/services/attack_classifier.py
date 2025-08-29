
import re
from typing import Dict, Any, List, Tuple

import torch
from transformers import pipeline

# A curated list of high-risk categories for classification.
RISK_LABELS = [
    "Jailbreak",
    "Prompt Injection",
    "Data Exfiltration",
    "Misinformation",
    "Harmful Content",
    "Hate Speech",
    "PII Harvesting",
]

# Hypothesis templates improve the accuracy of the zero-shot model for each category.
TEMPLATES = {
    "Jailbreak": "This text is trying to jailbreak an AI assistant.",
    "Prompt Injection": "This text attempts to inject instructions into a system or overwrite policies.",
    "Data Exfiltration": "This text is trying to extract hidden or confidential data.",
    "Misinformation": "This text spreads misinformation or makes false scientific claims.",
    "Harmful Content": "This text requests or instructs illegal or dangerous actions.",
    "Hate Speech": "This text expresses hate or harassment toward a protected group.",
    "PII Harvesting": "This text attempts to collect personal information from users.",
}

# High-signal regex patterns for fast, priority overrides.
REGEX_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("Prompt Injection", re.compile(r"\b(ignore|override|disregard).*\b(instructions|rules)\b", re.IGNORECASE)),
    ("Jailbreak", re.compile(r"\b(roleplay as|act as|DAN\b|developer mode|no restrictions)\b", re.IGNORECASE)),
    ("Data Exfiltration", re.compile(r"\b(secret|token|api[-\s]?key|\.env|credentials?|password)\b", re.IGNORECASE)),
]

# Confidence thresholds for classification logic.
PRIMARY_THRESHOLD = 0.60  # Minimum score for a ZSL classification to be considered.
BENIGN_FALLBACK_THRESHOLD = 0.50  # If the top score is below this, it's likely benign.


class AttackClassifier:
    """
    A hybrid classifier that uses regex for high-confidence patterns and a
    zero-shot AI model for nuanced semantic analysis.
    """

    def __init__(self):
        """Initializes the zero-shot classification pipeline from Hugging Face."""
        self._zsl_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1,
        )

    def _get_regex_match(self, text: str) -> str | None:
        """Performs a fast check for high-confidence attack patterns using regex."""
        for label, pattern in REGEX_PATTERNS:
            if pattern.search(text):
                return label
        return None

    def _get_zsl_prediction(self, text: str) -> Dict[str, float]:
        """Uses the Zero-Shot model to get a probability distribution over risk labels."""
        hypotheses = [TEMPLATES[label] for label in RISK_LABELS]
        output = self._zsl_pipeline(
            sequences=text,
            candidate_labels=hypotheses,
            hypothesis_template="{}",
        )
        # Align scores back to our original, simple label names
        return {label: float(score) for label, score in zip(RISK_LABELS, output["scores"])}

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifies the input text, returning a dictionary with the primary
        attack type, confidence, and a full probability map.
        """
        if not text or not text.strip():
            return {"primary": "Benign", "confidence": 1.0, "probabilities": {}}

        # 1. Regex Override Path: Fast and high-confidence for obvious attacks.
        regex_match = self._get_regex_match(text)
        if regex_match:
            return {
                "primary": regex_match,
                "confidence": 0.99,  # Assign a near-certain confidence for regex hits
                "probabilities": {regex_match: 0.99},
            }

        # 2. AI Path: If no regex matches, use the zero-shot model.
        try:
            scores = self._get_zsl_prediction(text)
            top_label = max(scores, key=scores.get)
            top_score = scores[top_label]

            # 3. Decision Logic: Determine the final classification.
            if top_score >= PRIMARY_THRESHOLD:
                primary_classification = top_label
                confidence = top_score
            elif top_score >= BENIGN_FALLBACK_THRESHOLD:
                # The result is ambiguous but leans toward a threat.
                primary_classification = top_label
                confidence = top_score
            else:
                # The model is not confident in any threat category.
                primary_classification = "Benign"
                confidence = 1.0 - top_score

            return {
                "primary": primary_classification,
                "confidence": float(confidence),
                "probabilities": scores,
            }
        except Exception as e:
            # Fallback in case the AI model fails.
            print(f"Attack classification pipeline failed: {e}")
            return {"primary": "Classification Error", "confidence": 0.0}