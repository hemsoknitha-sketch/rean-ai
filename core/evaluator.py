"""Evaluator Agent: Analyzes user intent, cognitive complexity, and mastery level."""
from dataclasses import dataclass
import re


@dataclass
class IntentAnalysis:
    domain: str  # e.g., "Computer Science", "Mathematics", "Philosophy", "General"
    cognitive_depth: str  # "Novice", "Intermediate", "Advanced", "Grandmaster"
    mode: str  # "Explanation", "Architecture/Code", "Socratic Dialogue", "Philosophical"
    language_hint: str  # "en", "km", "fr", etc.
    requires_code: bool


class EvaluatorAgent:
    """Agent 1: Fast rule-based + heuristic intent classifier for query routing."""

    def analyze(self, query: str) -> IntentAnalysis:
        query_lower = query.lower()

        # Language Detection Hint
        language_hint = "en"
        # Check for Khmer unicode range (\u1780-\u17ff)
        if re.search(r"[\u1780-\u17ff]", query):
            language_hint = "km"
        elif any(w in query_lower for w in ["bonjour", "comment", "merci", "explication"]):
            language_hint = "fr"

        # Code detection
        requires_code = any(
            kw in query_lower
            for kw in [
                "code",
                "python",
                "function",
                "class",
                "script",
                "bug",
                "error",
                "implementation",
                "def ",
                "async ",
                "import ",
            ]
        )

        # Domain classification
        if any(kw in query_lower for kw in ["algorithm", "python", "code", "ai", "neural", "model", "database", "api"]):
            domain = "Computer Science & AI"
        elif any(kw in query_lower for kw in ["math", "calculus", "proof", "matrix", "theorem", "algebra", "equation"]):
            domain = "Mathematics & Logic"
        elif any(kw in query_lower for kw in ["philosophy", "epistemology", "ethics", "consciousness", "meaning", "socrates"]):
            domain = "Philosophy & Cognition"
        else:
            domain = "Universal Polymathic Knowledge"

        # Depth classification
        if any(kw in query_lower for kw in ["what is", "basic", "simple", "explain like", "introduction", "beginner"]):
            cognitive_depth = "Novice"
            mode = "Explanation"
        elif any(kw in query_lower for kw in ["deep dive", "advanced", "internal", "under the hood", "architecture", "math behind"]):
            cognitive_depth = "Advanced"
            mode = "Architecture/Code" if requires_code else "Socratic Dialogue"
        elif any(kw in query_lower for kw in ["grandmaster", "supreme", "apex", "socratic", "first principles"]):
            cognitive_depth = "Grandmaster"
            mode = "Socratic Dialogue"
        else:
            cognitive_depth = "Intermediate"
            mode = "Explanation"

        return IntentAnalysis(
            domain=domain,
            cognitive_depth=cognitive_depth,
            mode=mode,
            language_hint=language_hint,
            requires_code=requires_code,
        )
