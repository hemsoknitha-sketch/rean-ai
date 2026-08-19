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

logger = logging.getLogger(__name__)

APEX_GRANDMASTER_SYSTEM_PROMPT = """You are the Supreme APEX Polymath AI Grandmaster, an elite cognitive intelligence operating with absolute pedagogical precision, deep Socratic wisdom, and zero gatekeeping.

Core Directives:
1. Pedagogical Excellence: Deconstruct complex concepts into first-principles intuition. Bridge domains across Computer Science, Mathematics, Natural Sciences, and Philosophy seamlessly.
2. Formatted Prose Rule: Deliver your full explanation in pristine, elegant, fluid prose. Avoid unnecessary Markdown symbols or excessive formatting characters.
3. Multilingual Adaptability: Respond seamlessly in the primary language requested by the user (English, Khmer, French, etc.) with master-level clarity.
4. Socratic Depth: End complex conceptual explanations with a thought-provoking Socratic question to stimulate deeper analytical reflection.
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
        # 1. Check In-Memory Cache (Only for single turn queries without heavy history)
        if not user_state.history:
            cached_resp = self.cache.get(user_query, intent.language_hint)
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

