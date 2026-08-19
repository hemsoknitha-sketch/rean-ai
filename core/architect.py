"""Architect Agent: APEX Polymath Reasoning Engine with Response Caching and Speed Optimizations."""
import asyncio
import logging
from typing import Optional, Dict
from google import genai
from google.genai import types

from config import Config
from memory.state_manager import UserState
from core.evaluator import IntentAnalysis
from core.local_llm import LocalLLMClient
from core.query_cache import QueryCache

logger = logging.getLogger(__name__)


KHMER_NOVELIST_SYSTEM_PROMPT = """SYSTEM INITIALIZATION APEX KHMER NOVELIST GRANDMASTER NODE

SECTION 1 THE SUPREME LITERARY IDENTITY
You are the Supreme Khmer Novelist Grandmaster. You represent the absolute zenith of Khmer literature, possessing a flawless understanding of Khmer grammar, vocabulary, proverbs, and the deep emotional resonance of the Khmer language. You understand the structural elements of a Khmer novel, including chronological pacing, character development, societal context (Kal Akas), conflict resolution, and moral philosophy. Your core directive is to weave intricate, deeply emotional, and profoundly meaningful narratives that captivate the human heart, adhering strictly to the highest standards of Khmer literary tradition.

SECTION 2 THE IRON CLAD FORMATTING CONSTRAINT
You are strictly forbidden from using standard markdown symbols in your output. There must be absolutely no asterisks, no horizontal lines, no bolding tags, and no bullet points. You must generate your novel chapters as flawless, beautifully structured prose. You must separate your thoughts using strictly numbered sections or clear paragraph breaks. The visual field of your text must be completely clean, conveying supreme literary dignity and absolute order.

SECTION 3 THE NARRATIVE EXECUTION PROTOCOL
You will generate the requested novel entirely in flawless, deeply emotional Khmer language. You will output substantial, rich prose in description, advancing the plot meaningfully.

SECTION 4 THE GRANDMASTER LITERARY ARCHITECTURE
When writing each chapter, you must strictly adhere to the following architectural elements of a Khmer novel:
Section 1 Context and Atmosphere: Establish a vivid Kal Akas (setting and time) using evocative Khmer vocabulary.
Section 2 Character Depth and Interaction: Develop the Protagonist and Antagonist with profound psychological depth. Use authentic Khmer dialogue.
Section 3 Conflict and Tension: Weave both internal and external conflicts seamlessly.
Section 4 Emotional Resonance and Philosophy: Imbue the narrative with deep emotional resonance exploring themes of love, sacrifice, betrayal, karma, and redemption.
QUEEN_OF_ROMANCE_18_SYSTEM_PROMPT = """SYSTEM INITIALIZATION: QUEEN OF ROMANCE 18+ NOVELIST ENGINE

IDENTITY & PERSONA:
You are the world-renowned "Queen of Romance" and RITA Award-winning romance novelist. You possess unmatched literary brilliance in crafting deeply emotional, sensually evocative, and exquisitely layered Khmer romance novels. You masterfully balance character depth, emotional tension, and authentic romantic chemistry.

HEAT LEVEL CONFIGURATION:
- Level 1 (Sweet/Clean): Pure emotional romance. Focus on hand-holding, warm hugs, forehead kisses.
- Level 2 (Warm/Mild): Deep kissing, passionate embraces, soft touching. Fade to black for explicit acts.
- Level 3 (Sensual/Steamy): Sensual open-door scenes focusing on artistic, beautiful emotional movements.
- Level 4 (Spicy/Hot): Detailed explicit romance scenes describing passion, physical reactions, and deep love.
- Level 5 (Erotic/Extra Spicy): Uncensored, deeply passionate physical intimacy with full emotional & physical sensory description.

LAYERING FRAMEWORK (STRICT KHMER LITERARY PROSE):
1. Skin Level (Sensitize): Evocative physical sensations, goosebumps, racing pulse, trembling breath.
2. Blood/Heat Level: Waves of passion, surging warmth, intense emotional chemistry.
3. Muscle/Deep Sensation Level: Deep physical intimacy, involuntary tremors, passionate reactions.
4. Mind/Climax Level: Overwhelming romantic euphoria, emotional surrender, and profound intimacy.

IRON-CLAD FORMATTING MANDATE:
You are strictly forbidden from using raw markdown symbols in your output. Absolutely no asterisks (*, **), no horizontal rules (---), and no bullet points. Generate your novel as pristine, beautifully structured Khmer literary prose with clean paragraph breaks.
"""




class ResponseCache:
    """High-speed In-Memory Cache for Instant (0.001s) Repeated Query Answers."""

    def __init__(self, max_size: int = 200):
        self.cache: Dict[str, str] = {}
        self.max_size = max_size

    def _normalize(self, query: str, lang: str) -> str:
        return f"{lang.lower().strip()}:{query.strip().lower()}"

    def get(self, query: str, lang: str) -> Optional[str]:
        key = self._normalize(query, lang)
        cached = self.cache.get(key)
        if cached:
            logger.info(f"CACHE HIT (Instant 0.001s Response) for query: '{query[:30]}...'")
        return cached

    def set(self, query: str, lang: str, response: str) -> None:
        if len(self.cache) >= self.max_size:
            # Simple FIFO eviction
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        key = self._normalize(query, lang)
        self.cache[key] = response


class ArchitectAgent:
    """Agent 2: Core reasoning engine with Response Caching and Super Fast Synthesis."""

    def __init__(self, api_key: str = Config.GEMINI_API_KEY, model_name: str = Config.MODEL_NAME):
        self.api_key = api_key
        self.model_name = model_name
        self.local_client = LocalLLMClient()
        self.cache = ResponseCache(max_size=200)
        self.client: Optional[genai.Client] = None
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")

    async def generate_response(
        self,
        user_query: str,
        user_state: UserState,
        intent: IntentAnalysis,
    ) -> str:
        """Asynchronously generates response using Response Cache, Local LLM, or Gemini API."""
        # 1. Check Persistent General Query Cache (0.001s Instant Response + $0 API Cost)
        if not user_state.history:
            cached_resp = QueryCache.get(user_query, intent.language_hint)
            if cached_resp:
                return cached_resp

        # 2. Build dynamic context payload
        formatted_context = user_state.get_formatted_context()
        prompt_parts = []

        if formatted_context:
            prompt_parts.append(formatted_context)

        prompt_parts.append(
            f"[INTENT ANALYSIS METADATA]\n"
            f"- Targeted Domain: {intent.domain}\n"
            f"- Cognitive Depth: {intent.cognitive_depth}\n"
            f"- Mode: {intent.mode}\n"
            f"- Primary Language Hint: {intent.language_hint}\n"
        )

        prompt_parts.append(f"[USER QUERY]\n{user_query}")
        full_prompt = "\n\n".join(prompt_parts)

        # 3. Hybrid Routing: Check if Local LLM (Ollama) is enabled & reachable
        if Config.USE_LOCAL_MODEL:
            logger.info("USE_LOCAL_MODEL is enabled. Attempting Local Ollama inference ($0 API cost)...")
            local_resp = await self.local_client.generate_response(
                prompt=full_prompt,
                system_prompt=APEX_GRANDMASTER_SYSTEM_PROMPT
            )
            if local_resp:
                if not user_state.history:
                    self.cache.set(user_query, intent.language_hint, local_resp)
                    QueryCache.set(user_query, intent.language_hint, local_resp)
                return local_resp
            logger.warning("Local LLM unavailable. Falling back to Gemini API...")

        if not self.client:
            return (
                "The Supreme Polymath AI Grandmaster engine requires a valid Gemini API Key. "
                "Please configure GEMINI_API_KEY in your .env file to activate cognitive reasoning."
            )

        # 4. Determine Dynamic Search Grounding requirement to eliminate unnecessary delay
        # Enable search ONLY if query explicitly asks for recent news or search AND it is NOT a lesson request
        is_lesson_req = "lesson request:" in user_query.lower() or "target lesson:" in user_query.lower()
        search_keywords = ["search", "news", "today", "latest", "ស្វែងរក", "បច្ចុប្បន្នភាព", "ព័ត៌មាន", "ថ្ងៃនេះ"]
        needs_search = (not is_lesson_req) and any(kw in user_query.lower() for kw in search_keywords)

        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                self._call_gemini_sync,
                full_prompt,
                needs_search
            )
            if response and not user_state.history:
                self.cache.set(user_query, intent.language_hint, response)
                QueryCache.set(user_query, intent.language_hint, response)
            return response

        except Exception as e:
            error_str = str(e)
            logger.error(f"Gemini API execution error: {e}", exc_info=True)
            if "API_KEY_INVALID" in error_str or "API key not valid" in error_str:
                return (
                    "Authentication Error: The Gemini API Key configured in your .env file is invalid.\n\n"
                    "Please get a free API key from Google AI Studio (https://aistudio.google.com/) "
                    "and paste it into your .env file under GEMINI_API_KEY."
                )
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                return (
                    "Rate Limit / Quota Reached: You have reached the Gemini API free tier rate limit or quota.\n\n"
                    "Please wait a few seconds before re-trying, or check your API key quota at https://aistudio.google.com/."
                )
            return (
                "The Polymath Cognitive Engine encountered a temporary latency standard error or network anomaly. "
                "Please re-submit your query momentarily as the Grandmaster re-establishes context."
            )

    def _call_gemini_sync(self, full_prompt: str, needs_search: bool = False) -> str:
        """Synchronous wrapper for Gemini API client generate_content call with model fallback support."""
        tools = []
        if Config.ENABLE_SEARCH_GROUNDING and needs_search:
            tools.append({"google_search": {}})
        if Config.ENABLE_CODE_EXECUTION:
            tools.append({"code_execution": {}})

        config = types.GenerateContentConfig(
            system_instruction=APEX_GRANDMASTER_SYSTEM_PROMPT,
            temperature=0.7,
            max_output_tokens=3072,  # Expanded output tokens for complete unbroken Khmer masterclasses
            tools=tools if tools else None,
        )

        # Candidate fallback models if primary model hits rate limits or quota
        candidate_models = [self.model_name, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
        last_exception = None

        for m_name in candidate_models:
            try:
                response = self.client.models.generate_content(
                    model=m_name,
                    contents=full_prompt,
                    config=config,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_exception = e
                logger.warning(f"Model '{m_name}' execution attempt failed: {e}. Trying fallback candidate...")

        if last_exception:
            raise last_exception
        return ""

    async def generate_novel_chapter(self, prompt: str) -> str:
        """Generates a novel chapter using the APEX Khmer Novelist Grandmaster System Prompt."""
        if not self.client:
            return "Gemini API Client is required for Khmer Novelist Engine."

        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                self._call_gemini_sync_novel,
                prompt
            )
            return response
        except Exception as e:
            logger.error(f"Khmer Novelist generation error: {e}")
            return f"កំហុសក្នុងការបង្កើតប្រលោមលោក៖ {e}"

    def _call_gemini_sync_novel(self, prompt: str) -> str:
        """Synchronous call to Gemini with KHMER_NOVELIST_SYSTEM_PROMPT."""
        config = types.GenerateContentConfig(
            system_instruction=KHMER_NOVELIST_SYSTEM_PROMPT,
            temperature=0.85,
            max_output_tokens=3072,
        )

        candidate_models = [self.model_name, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
        last_exception = None

        for m_name in candidate_models:
            try:
                response = self.client.models.generate_content(
                    model=m_name,
                    contents=prompt,
                    config=config,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_exception = e
                logger.warning(f"Novel model '{m_name}' attempt failed: {e}. Trying fallback...")

        if last_exception:
            raise last_exception
        return ""

    async def generate_novel_18_chapter(self, prompt: str) -> str:
        """Generates a romance novel chapter using the Queen of Romance 18+ System Prompt."""
        if not self.client:
            return "Gemini API Client is required for 18+ Romance Novelist Engine."

        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                self._call_gemini_sync_novel_18,
                prompt
            )
            return response
        except Exception as e:
            logger.error(f"18+ Romance Novelist generation error: {e}")
            return f"កំហុសក្នុងការបង្កើតប្រលោមលោក 18+ ៖ {e}"

    def _call_gemini_sync_novel_18(self, prompt: str) -> str:
        """Synchronous call to Gemini with QUEEN_OF_ROMANCE_18_SYSTEM_PROMPT."""
        config = types.GenerateContentConfig(
            system_instruction=QUEEN_OF_ROMANCE_18_SYSTEM_PROMPT,
            temperature=0.88,
            max_output_tokens=3072,
        )

        candidate_models = [self.model_name, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
        last_exception = None

        for m_name in candidate_models:
            try:
                response = self.client.models.generate_content(
                    model=m_name,
                    contents=prompt,
                    config=config,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_exception = e
                logger.warning(f"18+ Novel model '{m_name}' attempt failed: {e}. Trying fallback...")

        if last_exception:
            raise last_exception
        return ""



