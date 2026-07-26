from app.config import settings
import difflib

sentence_model = None
if not settings.USE_MOCK_AI:
    try:
        from sentence_transformers import SentenceTransformer
        # Loads a lightweight, fast, local embedding model
        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        print(f"Failed to load SentenceTransformers: {e}. Using SequenceMatcher fallback.")

class NLPEngine:
    def __init__(self):
        self.use_mock = settings.USE_MOCK_AI or (sentence_model is None)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates semantic similarity between two text strings.
        Returns a float between 0.0 and 1.0.
        """
        if not text1 or not text2:
            return 0.0
            
        if not self.use_mock:
            try:
                import numpy as np
                # Generate embeddings
                embeddings = sentence_model.encode([text1, text2])
                e1, e2 = embeddings[0], embeddings[1]
                
                # Compute Cosine Similarity
                dot_prod = np.dot(e1, e2)
                norm_e1 = np.linalg.norm(e1)
                norm_e2 = np.linalg.norm(e2)
                
                if norm_e1 > 0 and norm_e2 > 0:
                    similarity = float(dot_prod / (norm_e1 * norm_e2))
                    # Bound to [0, 1]
                    return max(0.0, min(1.0, (similarity + 1) / 2))
            except Exception as e:
                print(f"SentenceTransformers similarity calculation failed: {e}. Falling back to SequenceMatcher.")

        # Fallback using python standard library SequenceMatcher
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def check_keywords(self, text: str, mandatory_keywords: list, optional_keywords: list) -> dict:
        """
        Scans text for keywords. Supports case-insensitive matches.
        Returns a dictionary categorizing found and missing elements.
        """
        if not text:
            text = ""
        text_lower = text.lower()
        found_mandatory = []
        missing_mandatory = []
        found_optional = []
        missing_optional = []

        # Scan mandatory keywords
        for kw in (mandatory_keywords or []):
            if not kw:
                continue
            if kw.lower() in text_lower:
                found_mandatory.append(kw)
            else:
                missing_mandatory.append(kw)

        # Scan optional keywords
        for kw in (optional_keywords or []):
            if not kw:
                continue
            if kw.lower() in text_lower:
                found_optional.append(kw)
            else:
                missing_optional.append(kw)

        return {
            "found_mandatory": found_mandatory,
            "missing_mandatory": missing_mandatory,
            "found_optional": found_optional,
            "missing_optional": missing_optional
        }
