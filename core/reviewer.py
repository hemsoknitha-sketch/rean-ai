"""Reviewer Agent: Formats raw Markdown into Telegram HTML for pristine visual aesthetics."""
import re
import html
import logging
import asyncio

logger = logging.getLogger(__name__)


class ReviewerAgent:
    """Agent 3: Sanitizes response output into beautiful Telegram HTML prose."""

    @staticmethod
    def strip_markdown(text: str) -> str:
        """Alias for format_for_telegram_html."""
        return ReviewerAgent.format_for_telegram_html(text)

    @staticmethod
    def format_for_telegram_html(text: str) -> str:
        """Transforms raw Markdown into pristine, beautiful Telegram HTML formatting."""
        if not text:
            return ""

        # 0. Helper: Telegram HTML Code Escaping (Strictly &lt;, &gt;, &amp; ONLY)
        # NEVER escape single quotes (') into &#x27; or double quotes (") into &quot; inside code
        # because Telegram Bot API strictly rejects &#x27; with BadRequest, and raw ' and " are 100% valid!
        def escape_telegram_code(content: str) -> str:
            # Unescape any preexisting entities first to prevent double-escaping
            c = (
                content.replace("&#x27;", "'")
                .replace("&#39;", "'")
                .replace("&apos;", "'")
                .replace("&quot;", '"')
                .replace("&amp;", "&")
                .replace("&lt;", "<")
                .replace("&gt;", ">")
            )
            # Re-escape only &, <, >
            return (
                c.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

        # 0b. Auto-fence unfenced CLI commands, prompts, or Python scripts outside existing ```
        def auto_fence_unfenced_blocks(raw_text: str) -> str:
            parts = raw_text.split("```")
            for i in range(0, len(parts), 2):
                paragraphs = parts[i].split("\n\n")
                new_paragraphs = []
                for p in paragraphs:
                    p_strip = p.strip()
                    lines = [l.strip() for l in p_strip.splitlines() if l.strip()]
                    if not lines:
                        new_paragraphs.append(p)
                        continue

                    # Check if paragraph is purely CLI commands (e.g. python -m, pip install, export, source, etc.)
                    cli_starters = (
                        "python -m", "python3 -m", "pip install", "pip3 install",
                        "source ", "export ", "git clone", "npm install", "sudo apt", "curl "
                    )
                    if all(any(l.startswith(cs) for cs in cli_starters) or l.startswith("#") for l in lines) and len(lines) >= 1:
                        new_paragraphs.append(f"```bash\n{p_strip}\n```")
                        continue

                    # Check if paragraph is a structured Prompt Blueprint ([ROLE], [CONTEXT], [TASK], [CONSTRAINTS])
                    prompt_starters = ("[ROLE]", "[CONTEXT]", "[TASK]", "[CONSTRAINTS]", "[PROMPT]", "[SYSTEM]", "Role:", "System Prompt:")
                    if any(lines[0].startswith(ps) for ps in prompt_starters):
                        new_paragraphs.append(f"```yaml\n{p_strip}\n```")
                        continue

                    # Check if paragraph is purely Python script
                    py_starters = ("import ", "from ", "def ", "class ", "client = genai.Client()", "# TODO:")
                    if lines[0].startswith(py_starters) and any(kw in p_strip for kw in ["client = genai", "print(", "models.generate_content"]):
                        new_paragraphs.append(f"```python\n{p_strip}\n```")
                        continue

                    new_paragraphs.append(p)
                parts[i] = "\n\n".join(new_paragraphs)
            return "```".join(parts)

        text = auto_fence_unfenced_blocks(text)

        # 1. Save code blocks (```python ... ```) -> <pre><code class="language-python">...</code></pre>
        code_blocks = []
        def auto_detect_language(code_str: str) -> str:
            """Smart language auto-detector to ensure Telegram Copy button and syntax highlighting always activate."""
            raw_lower = code_str.lower()
            if any(kw in raw_lower for kw in ["pip ", "sudo ", "apt ", "git ", "npm ", "chmod ", "cd ", "curl ", "#!/bin/bash", "#!/usr/bin"]):
                return "bash"
            if any(kw in raw_lower for kw in ["select ", "insert into", "create table", "alter table", "drop table", "delete from"]):
                return "sql"
            if any(kw in raw_lower for kw in ["def ", "import ", "class ", "print(", "__init__", "torch", "pandas", "np.", "tf."]) or ("from " in raw_lower and "import " in raw_lower):
                return "python"
            if any(kw in raw_lower for kw in ["role:", "content:", "model:", "temperature:", "version:"]):
                return "yaml"
            if any(kw in raw_lower for kw in ["const ", "let ", "function", "console.log", "document."]):
                return "javascript"
            if any(kw in raw_lower for kw in ["<html", "<div", "<pre", "<body", "<span"]):
                return "html"
            if any(kw in raw_lower for kw in ["{", "}", '":']):
                return "json"
            return "python"  # Default to python for AI education

        def save_code_block(match):
            lang = match.group(1).strip().lower()
            code_content = escape_telegram_code(match.group(2).strip())
            if not lang:
                lang = auto_detect_language(code_content)
            code_blocks.append(f'<pre><code class="language-{lang}">{code_content}</code></pre>')
            return f"\n\n@@@CODEBLOCK{len(code_blocks)-1}@@@\n\n"

        text = re.sub(r"```([\w\-]*)\n?(.*?)```", save_code_block, text, flags=re.DOTALL)

        # 2. Save inline code (`code`) -> <code>code</code> (Telegram Tap-to-Copy)
        inline_codes = []
        def save_inline_code(match):
            code_content = escape_telegram_code(match.group(1).strip())
            if code_content:
                inline_codes.append(f"<code>{code_content}</code>")
                return f"@@@INLINECODE{len(inline_codes)-1}@@@"
            return ""

        text = re.sub(r"`([^`\n]+)`", save_inline_code, text)

        # 2b. Typographic Alignment & Layout Normalization (អក្សរតម្រឹមស្មើសងខាង)
        # Trim trailing whitespace on every line to prevent ragged wrapping
        text = "\n".join(line.rstrip() for line in text.splitlines())

        # 3. Escape HTML special characters for remaining prose
        # First normalize any erroneous entities from LLM
        text = (
            text.replace("&#x27;", "'")
            .replace("&#39;", "'")
            .replace("&apos;", "'")
            .replace("&quot;", '"')
        )
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # 4. Super Smart Foreign Script Purge (outside code blocks)
        # Strictly removes Chinese, Thai, Lao, Burmese, Korean, Japanese, and Cyrillic script leaks
        foreign_scripts_pattern = r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u0e00-\u0e7f\u0e80-\u0eff\u1000-\u109f\uac00-\ud7af\u1100-\u11ff\u3040-\u30ff\u0400-\u04ff]"
        text = re.sub(foreign_scripts_pattern, "", text)

        # 5. Clean redundant/repetitive quote artifacts
        text = re.sub(r'["“«]{2,}', '"', text)
        text = re.sub(r'["”»]{2,}', '"', text)
        text = re.sub(r'["“«]\s*["”»]', '', text)

        # 5b. Purge internal operational slogans (24/7 365 FREE, $0 API Limit) from user view
        text = re.sub(r"(?i)\b24/7\s*(?:365)?\s*free\b", "", text)
        text = re.sub(r"(?i)\b365\s*free\b", "", text)
        text = re.sub(r"២៤/៧\s*៣៦៥\s*(?:free)?", "", text, flags=re.IGNORECASE)

        # 6. Super Smart 2cm Divider Standard (No lines above title, only 10-char ~2cm divider below)
        # A. Purge divider immediately preceding a markdown header
        text = re.sub(r"^\s*[━─=\-_*~]{3,}\s*\n+(?=#{1,6}\s+)", "", text, flags=re.MULTILINE)
        # B. Purge top divider when sandwiching a title (divider -> single line -> divider)
        text = re.sub(r"^\s*[━─=\-_*~]{3,}\s*\n+(?=[^\n]+\n+\s*[━─=\-_*~]{3,})", "", text, flags=re.MULTILINE)
        # C. Purge divider at very beginning of text
        text = re.sub(r"^\s*[━─=\-_*~]{3,}\s*\n+", "", text)
        # D. Normalize any long divider line (>=3 characters) down to strictly 10 characters (~2cm)
        text = re.sub(r"^\s*[━]{3,}\s*$", "━━━━━━━━━━", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*[─]{3,}\s*$", "──────────", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*[=]{3,}\s*$", "──────────", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*[-_*~]{3,}\s*$", "──────────", text, flags=re.MULTILINE)

        # 7. Format unordered list bullets FIRST (* item or - item -> • item)
        text = re.sub(r"^\s*[\*\-\+]\s+", "• ", text, flags=re.MULTILINE)

        # 8. Convert headers (### Header -> <b>📘 Header</b>)
        def format_header(match):
            title = match.group(2).strip()
            if any(ord(char) > 0x2000 for char in title[:2]):
                return f"\n<b>{title}</b>\n"
            return f"\n<b>📘 {title}</b>\n"

        text = re.sub(r"^(#{1,6})\s+(.+)$", format_header, text, flags=re.MULTILINE)

        # 9. Convert bold (**bold** -> <b>bold</b>)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)

        # 10. Convert italics (*italic* -> <i>italic</i>)
        text = re.sub(r"(?<!\*)\*([^\*\n]+)\*(?!\*)", r"<i>\1</i>", text)
        text = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"<i>\1</i>", text)

        # 11. Convert links ([title](url) -> <a href="url">title</a>)
        text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)

        # 12. Convert blockquotes (> quote -> <i>💬 quote</i>)
        text = re.sub(r"^\s*&gt;\s*(.+)$", r"<i>💬 \1</i>", text, flags=re.MULTILINE)

        # 13. Clean up excessive consecutive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 14. Restore protected code blocks and inline code placeholders AT THE END
        # This guarantees code blocks remain 100% untouched and pristine
        for idx, block in enumerate(code_blocks):
            text = text.replace(f"@@@CODEBLOCK{idx}@@@", block)
        for idx, code in enumerate(inline_codes):
            text = text.replace(f"@@@INLINECODE{idx}@@@", code)

        # 15. Final typographic pass: Clean up excessive blank lines around code blocks
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 16. Telegram HTML Tag Gatekeeper: Escape any unsupported tags (e.g. <locals>, <custom>)
        allowed_tags = {
            "b", "strong", "i", "em", "u", "ins", "s", "strike", "del",
            "span", "tg-spoiler", "a", "code", "pre", "blockquote", "tg-emoji"
        }
        def replace_unsupported_tag(m):
            tag_name = m.group(1).lower()
            if tag_name in allowed_tags:
                return m.group(0)
            return m.group(0).replace("<", "&lt;").replace(">", "&gt;")

        text = re.sub(r"</?([a-zA-Z0-9_\-]+)(?:\s+[^>]*)?>", replace_unsupported_tag, text)

        # 17. Telegram HTML Tag Balancer: Ensure 100% well-formed, balanced HTML for Telegram
        return ReviewerAgent.balance_html_tags(text.strip())

    @staticmethod
    def balance_html_tags(html_text: str) -> str:
        """Balances HTML tags by closing any unclosed tags in reverse order and escaping rogue closing tags."""
        if not html_text:
            return ""

        tag_pattern = re.compile(r"<(/)?([a-zA-Z0-9_\-]+)((?:\s+[^>]*)?)>")
        last_end = 0
        stack = []
        balanced_parts = []

        for m in tag_pattern.finditer(html_text):
            start, end = m.span()
            text_before = html_text[last_end:start]
            is_closing = bool(m.group(1))
            tag_name = m.group(2).lower()
            full_tag = m.group(0)

            balanced_parts.append(text_before)

            if not is_closing:
                stack.append((tag_name, full_tag))
                balanced_parts.append(full_tag)
            else:
                match_index = -1
                for idx in range(len(stack) - 1, -1, -1):
                    if stack[idx][0] == tag_name:
                        match_index = idx
                        break
                if match_index != -1:
                    while len(stack) > match_index + 1:
                        unclosed_tag, _ = stack.pop()
                        balanced_parts.append(f"</{unclosed_tag}>")
                    stack.pop()
                    balanced_parts.append(f"</{tag_name}>")
                else:
                    # Rogue closing tag without opening tag -> escape it into safe entity
                    balanced_parts.append(f"&lt;/{tag_name}&gt;")

            last_end = end

        balanced_parts.append(html_text[last_end:])

        while stack:
            unclosed_tag, _ = stack.pop()
            balanced_parts.append(f"</{unclosed_tag}>")

        return "".join(balanced_parts)

    def validate_and_sanitize(self, text: str, strict: bool = True) -> str:
        """Sanitizes text and verifies formatting boundaries."""
        if not text:
            return "No content was generated by the cognitive engine."
        return self.format_for_telegram_html(text)

    @classmethod
    async def evaluate_student_understanding(
        cls,
        student_answer: str,
        exercise_title: str,
        lesson_context: str = "",
        architect_agent = None
    ) -> dict:
        """Understanding Evaluator: Analyzes student code/explanation, awards points, and gives feedback."""
        if not student_answer or len(student_answer.strip()) < 3:
            return {
                "passed": False,
                "points": 0,
                "feedback": (
                    "⚠️ <b>ចម្លើយមិនទាន់គ្រប់គ្រាន់ ៖</b>\n\n"
                    "សូមព្យាយាមបំពេញកូដ ឬពន្យល់ពីគំនិតស្នូលនៃលំហាត់ឱ្យបានក្បោះក្បាយបន្តិច មុននឹងបញ្ជូនមកម្តងទៀត។"
                )
            }

        # Attempt LLM-based evaluation if architect_agent is provided
        if architect_agent and hasattr(architect_agent, "client") and architect_agent.client:
            try:
                eval_prompt = (
                    f"You are the Supreme Reviewer Agent and Understanding Evaluator for REAN AI.\n"
                    f"Analyze the student's answer to the Socratic exercise.\n\n"
                    f"Exercise: {exercise_title}\n"
                    f"Lesson Context: {lesson_context}\n"
                    f"Student Answer:\n{student_answer}\n\n"
                    f"EVALUATION DIRECTIVES:\n"
                    f"1. Check if the student filled the code scaffolding correctly or explained first-principles intuition.\n"
                    f"2. Award score points between 10 and 20 points (e.g. +15 or +20 for good answers, +10 for partial attempts).\n"
                    f"3. Language standard: 100% full rich Khmer adhering to Samdech Chuon Nath Dictionary + English technical terms in parentheses ONLY. ZERO foreign scripts.\n"
                    f"4. Deliver an encouraging, constructive review with specific praise and constructive feedback.\n"
                    f"5. End with [SCORE: X] and [PASSED: YES/NO] tags at the very bottom."
                )

                loop = asyncio.get_running_loop()
                raw_eval = await loop.run_in_executor(
                    None,
                    architect_agent._call_gemini_sync,
                    eval_prompt,
                    False
                )

                # Extract score and pass status
                points = 15
                passed = True
                score_match = re.search(r"\[SCORE:\s*(\d+)\]", raw_eval, re.IGNORECASE)
                if score_match:
                    points = min(25, max(5, int(score_match.group(1))))

                passed_match = re.search(r"\[PASSED:\s*(YES|NO)\]", raw_eval, re.IGNORECASE)
                if passed_match:
                    passed = (passed_match.group(1).upper() == "YES")

                # Remove tags from output
                clean_text = re.sub(r"\[SCORE:\s*\d+\]", "", raw_eval, flags=re.IGNORECASE)
                clean_text = re.sub(r"\[PASSED:\s*(?:YES|NO)\]", "", clean_text, flags=re.IGNORECASE)
                sanitized_feedback = cls.format_for_telegram_html(clean_text.strip())

                return {
                    "passed": passed,
                    "points": points,
                    "feedback": sanitized_feedback
                }
            except Exception as e:
                logger.warning(f"LLM understanding evaluation failed, falling back to heuristic evaluation: {e}")

        # Heuristic Rule-based Evaluation Fallback ($0 API / Offline)
        has_code = "def " in student_answer or "return" in student_answer or "=" in student_answer or len(student_answer) > 40
        points = 15 if has_code else 10
        passed = True

        feedback = (
            "🎯 <b>ការវាយតម្លៃការយល់ដឹងពី REVIEWER AGENT ៖</b>\n"
            "━━━━━━━━━━\n"
            f"📖 <b>លំហាត់ ៖</b> {exercise_title}\n"
            f"🌟 <b>លទ្ធផល ៖</b> 🟢 <b>ទទួលបានជោគជ័យ (PASSED)</b>\n"
            f"🏆 <b>ពិន្ទុបន្ថែម ៖</b> <b>+{points} ពិន្ទុ</b>\n\n"
            "💡 <b>មតិកែលម្អគរុកោសល្យ ៖</b>\n"
            "លោកអ្នកបានបង្ហាញនូវការយល់ដឹងដ៏ល្អ និងការខិតខំដោះស្រាយលំហាត់ជាក់ស្តែង។ "
            "ការអនុវត្តកូដ និងការគិតវិភាគជាជំហានៗបែបនេះ គឺជាគន្លឹះចម្បងក្នុងការឈានទៅដល់កម្រិត Grandmaster!\n"
            "━━━━━━━━━━"
        )
        return {
            "passed": passed,
            "points": points,
            "feedback": feedback
        }
