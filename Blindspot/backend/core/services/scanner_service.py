import json
from pathlib import Path
from typing import List, Dict, Any

from .attack_classifier import AttackClassifier
from ..detectors.language_detector import LanguageDetector
from ..detectors.pii_detector import PIIDetector
from ..detectors.semantic_detector import SemanticDetector


class ScannerService:
    """
    Orchestrates a multi-layered scan of input text by coordinating various
    detectors and classifiers to produce a comprehensive security analysis.
    """

    def __init__(self):
        """
        Initializes the service, loading the classifier and attack library.
        Heavy AI detectors are lazy-loaded on the first scan request for
        faster server startup.
        """
        self.detectors: List[Any] | None = None
        self.classifier = AttackClassifier()

        library_path = Path(__file__).resolve().parent.parent.parent / "config" / "attack_library.json"
        with open(library_path, 'r', encoding='utf-8') as f:
            self.attack_library = json.load(f)

    def _initialize_detectors(self):
        """Handles the one-time, slow initialization of heavy AI models."""
        self.detectors = [
            PIIDetector(),
            SemanticDetector(),
            LanguageDetector(),
        ]

    def scan_text(self, text: str, session_id: str) -> Dict[str, Any]:
        """
        Performs a full analysis of a text prompt through all security layers.

        Args:
            text: The user-provided prompt to analyze.
            session_id: An identifier for the user's session.

        Returns:
            A dictionary containing the full, detailed analysis report.
        """
        if self.detectors is None:
            self._initialize_detectors()

        # Run all detectors and collect their raw outputs
        all_results = [d.detect(text) for d in self.detectors if d.detect(text)]
        base_risk_score = max((res.get("score", 0.0) for res in all_results), default=0.0)
        
        # Consolidate all explicit findings from detectors
        actual_findings = [res for res in all_results if res.get("finding")]
        
        # Get the primary classification from the advanced classifier
        attack_info = self.classifier.classify(text)
        attack_type = attack_info.get("primary", "Unknown")

        # If a specific attack is identified, create a detailed finding for it
        if attack_type not in ["Benign", "Unknown", "Classification Error"]:
            attack_details = self.attack_library.get(attack_type, {})
            attack_finding = {
                "finding": attack_type,
                "score": base_risk_score,
                "details": attack_details.get('description', 'No description available.'),
                "mitigation": attack_details.get('mitigation', 'No mitigation advice available.'),
            }
            actual_findings.insert(0, attack_finding) # Add as the most important finding

        # Gather analytical metadata
        char_count = len(text)
        token_count = next((res.get("token_count", 0) for res in all_results if "token_count" in res), 0)
        language = next((res.get("language", "en") for res in all_results if "language" in res), "en")

        # Calculate final risk, applying contextual logic
        final_prompt_risk = max((f.get("score", 0.0) for f in actual_findings), default=base_risk_score)
        if language != "en" and 0.3 <= final_prompt_risk < 0.7:
            final_prompt_risk = min(final_prompt_risk + 0.2, 1.0)
            contextual_details = self.attack_library.get("Contextual Risk", {})
            actual_findings.append({
                "finding": "Contextual Risk", "score": final_prompt_risk,
                "details": contextual_details.get('description', '').format(language=language),
                "mitigation": contextual_details.get('mitigation', '')
            })

        # Determine final status and summary message
        if actual_findings:
            message = "Threats detected. See detailed findings."
            status = "ALERT"
        else:
            message = "Text appears safe."
            status = "CLEAN"

        # Assemble the final, rich response object
        return {
            "prompt_analyzed": text,
            "status": status,
            "prompt_risk": round(final_prompt_risk, 2),
            "message": message,
            "findings": actual_findings,
            "analytics": {
                "char_count": char_count,
                "token_count": token_count,
                "language": language,
                "attack_type": attack_type,
                "attack_meta": attack_info,
            },
        }

# A single, shared instance for the entire application.
scanner_service = ScannerService()