import json
from pathlib import Path
from typing import Dict, Any

import torch
from sentence_transformers import SentenceTransformer, util

from .base_detector import BaseDetector


class SemanticDetector(BaseDetector):
    """
    Calculates a semantic risk score based on a prompt's similarity to a
    known list of threat phrases using sentence embeddings.
    """

    @property
    def name(self) -> str:
        """The unique name of the detector."""
        return "semantic_detector"

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the detector, loads the sentence transformer model, and
        pre-computes embeddings for the threat intelligence list for efficiency.
        """
        self.model = SentenceTransformer(model_name)
        self.tokenizer = self.model.tokenizer

        config_path = Path(__file__).resolve().parent.parent.parent.parent / "threat_intelligence.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            risky_prompts = json.load(f).get("risky_prompts", [])
        
        self.risky_embeddings = self.model.encode(risky_prompts, convert_to_tensor=True)

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Encodes the input text and calculates its maximum cosine similarity
        score against the pre-computed threat embeddings.

        Note: This detector provides raw analytical data (score, token_count)
        and does not generate a human-readable "finding" itself.

        Args:
            text: The user-provided prompt to analyze.

        Returns:
            A dictionary containing the risk score and token count.
        """
        if not text.strip():
            return {}

        token_count = len(self.tokenizer.encode(text))
        input_embedding = self.model.encode(text, convert_to_tensor=True)
        
        cosine_scores = util.cos_sim(input_embedding, self.risky_embeddings)
        max_score = float(torch.max(cosine_scores))

        return {"score": round(max_score, 2), "token_count": token_count}