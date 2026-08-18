"""Local LLM Client module connecting to self-hosted Ollama or vLLM HTTP servers."""
import json
import logging
import urllib.request
import urllib.error
import asyncio
from typing import Optional

from config import Config

logger = logging.getLogger(__name__)


class LocalLLMClient:
    """Asynchronous client for interacting with self-hosted Ollama HTTP inference engines."""

    def __init__(self, host: str = Config.OLLAMA_HOST, model_name: str = Config.LOCAL_MODEL_NAME):
        self.host = host.rstrip("/")
        self.model_name = model_name

    async def is_available(self) -> bool:
        """Checks if the local Ollama server is active and reachable."""
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self._check_health_sync)
        except Exception:
            return False

    def _check_health_sync(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def generate_response(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Asynchronously generates text from local Ollama model."""
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None,
                self._generate_sync,
                prompt,
                system_prompt
            )
        except Exception as e:
            logger.error(f"Local LLM execution error: {e}")
            return None

    def _generate_sync(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_ctx": 4096,
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status == 200:
                    result = json.loads(resp.read().decode("utf-8"))
                    return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama API request failed: {e}")
            return None
        return None
