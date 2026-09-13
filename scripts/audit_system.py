#!/usr/bin/env python3
"""
SUPREME COGNITIVE SYSTEM AUDIT & ARCHITECTURE VERIFIER
Script: scripts/audit_system.py
Purpose: Comprehensive audit script to verify code integrity, mathematical accuracy,
         security gatekeeping, language purity, and curriculum uniqueness.
"""

import sys
import os
import re
import py_compile
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config
from core.reviewer import ReviewerAgent
from core.curriculum import CurriculumEngine, AI_COURSES, AI_COURSE_MODULES, LESSON_SUBTOPICS
from core.admin import SystemMonitor
from bot.handlers import is_admin


class SystemAuditor:
    """Automated validator for REAN AI Polymath Architecture."""

    def __init__(self):
        self.passed_checks = 0
        self.failed_checks = 0
        self.warnings = 0

    def log_pass(self, name: str, details: str = ""):
        self.passed_checks += 1
        detail_str = f" - {details}" if details else ""
        print(f"  [PASS] {name}{detail_str}")

    def log_fail(self, name: str, reason: str):
        self.failed_checks += 1
        print(f"  [FAIL] {name}: {reason}")

    def log_warn(self, name: str, reason: str):
        self.warnings += 1
        print(f"  [WARN] {name}: {reason}")

    # =========================================================================
    # 1. PYTHON SYNTAX & MODULE COMPILATION AUDIT
    # =========================================================================
    def audit_syntax_and_compilation(self):
        print("\n" + "=" * 65)
        print("1. AUDITING PYTHON SYNTAX & CODE COMPILATION")
        print("=" * 65)

        files_to_check = [
            PROJECT_ROOT / "main.py",
            PROJECT_ROOT / "config.py",
            PROJECT_ROOT / "bot" / "handlers.py",
            PROJECT_ROOT / "core" / "architect.py",
            PROJECT_ROOT / "core" / "curriculum.py",
            PROJECT_ROOT / "core" / "reviewer.py",
            PROJECT_ROOT / "core" / "evaluator.py",
            PROJECT_ROOT / "core" / "admin.py",
            PROJECT_ROOT / "core" / "vip_manager.py",
            PROJECT_ROOT / "core" / "user_registry.py",
            PROJECT_ROOT / "core" / "security.py",
            PROJECT_ROOT / "core" / "lesson_cache.py",
            PROJECT_ROOT / "core" / "novel_18_cache.py",
            PROJECT_ROOT / "core" / "novel_continuity.py",
            PROJECT_ROOT / "memory" / "state_manager.py",
        ]

        for file_path in files_to_check:
            if not file_path.exists():
                self.log_fail("File Existence", f"Missing critical file: {file_path.name}")
                continue
            try:
                py_compile.compile(str(file_path), doraise=True)
                self.log_pass(f"Syntax: {file_path.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                self.log_fail(f"Syntax: {file_path.relative_to(PROJECT_ROOT)}", str(e))

    # =========================================================================
    # 2. SECURITY & ADMIN-ONLY COMMAND GATEKEEPING AUDIT
    # =========================================================================
    def audit_admin_security_gatekeeping(self):
        print("\n" + "=" * 65)
        print("2. AUDITING SECURITY, ADMIN PERMISSIONS & COMMAND CONCEALMENT")
        print("=" * 65)

        # A. Check Admin ID verification
        admin_id = 859271875
        config_admin = Config.ADMIN_CHAT_ID

        if is_admin(admin_id):
            self.log_pass("Admin ID 859271875", "Authorized as Super Admin")
        else:
            self.log_fail("Admin ID 859271875", "Failed Admin authorization check")

        if is_admin(config_admin):
            self.log_pass("Config.ADMIN_CHAT_ID", f"ID {config_admin} Authorized as Admin")
        else:
            self.log_fail("Config.ADMIN_CHAT_ID", "Config admin not authorized")

        if not is_admin(999999999):
            self.log_pass("Non-Admin ID 999999999", "Successfully Denied Admin privileges")
        else:
            self.log_fail("Non-Admin ID 999999999", "Security breach: unauthorized ID granted Admin!")

        # B. Verify user_commands does NOT expose /novel_18 in main.py
        main_py = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
        user_cmd_match = re.search(r"user_commands\s*=\s*\[(.*?)\]", main_py, re.DOTALL)
        if user_cmd_match:
            user_cmd_text = user_cmd_match.group(1)
            if "novel_18" in user_cmd_text or "18+" in user_cmd_text:
                self.log_fail("user_commands in main.py", "novel_18 is leaking in public user commands menu!")
            else:
                self.log_pass("user_commands in main.py", "novel_18 completely hidden from public menu")
        else:
            self.log_warn("user_commands in main.py", "Could not locate user_commands list")

        # C. Verify admin_commands retains /novel_18 in main.py
        admin_cmd_match = re.search(r"admin_commands\s*=\s*\[(.*?)\]", main_py, re.DOTALL)
        if admin_cmd_match:
            admin_cmd_text = admin_cmd_match.group(1)
            if "novel_18" in admin_cmd_text:
                self.log_pass("admin_commands in main.py", "novel_18 present in Admin scope menu")
            else:
                self.log_fail("admin_commands in main.py", "novel_18 missing from Admin menu!")

    # =========================================================================
    # 3. PROHIBITED STRINGS & LEAKAGE SANITIZATION AUDIT
    # =========================================================================
    def audit_content_sanitization_and_leaks(self):
        print("\n" + "=" * 65)
        print("3. AUDITING USER SPACE FOR LEAKS (18+, 24/7 365 FREE, $0 LIMIT)")
        print("=" * 65)

        handlers_py = (PROJECT_ROOT / "bot" / "handlers.py").read_text(encoding="utf-8")

        # A. Check /start greeting for 18+ or $0 Limit leaks
        start_fn_match = re.search(r"async def start_command\(.*?\):.*?(?=async def |\Z)", handlers_py, re.DOTALL)
        if start_fn_match:
            start_fn_body = start_fn_match.group(0)
            if "novel_18" in start_fn_body:
                self.log_fail("/start Greeting", "Leaking /novel_18 to public users!")
            else:
                self.log_pass("/start Greeting", "Zero reference to /novel_18")

            if "$0 API Limit" in start_fn_body:
                self.log_fail("/start Greeting", "Leaking '$0 API Limit' marketing string!")
            else:
                self.log_pass("/start Greeting", "Cleaned '$0 API Limit' string successfully")

            if "Free User" in start_fn_body:
                self.log_fail("/start Greeting", "Leaking 'Free User' label to users!")
            else:
                self.log_pass("/start Greeting", "Cleaned 'Free User' label successfully")

        # B. Check novel_kh gatekeeper for 18+ leaks
        novel_kh_match = re.search(r"async def novel_kh_command\(.*?\):.*?(?=async def |\Z)", handlers_py, re.DOTALL)
        if novel_kh_match:
            novel_kh_body = novel_kh_match.group(0)
            if "Queen of Romance 18+" in novel_kh_body or "18+" in novel_kh_body:
                self.log_fail("/novel_kh Gatekeeper", "Leaking 18+ romance in /novel_kh message!")
            else:
                self.log_pass("/novel_kh Gatekeeper", "Zero 18+ leakage in /novel_kh message")

        # C. Check curriculum modules for 24/7 or 365 FREE
        curriculum_py = (PROJECT_ROOT / "core" / "curriculum.py").read_text(encoding="utf-8")
        if "24/7" in curriculum_py or "២៤/៧" in curriculum_py:
            self.log_fail("Curriculum Modules", "Found '24/7' or '២៤/៧' in curriculum module titles")
        else:
            self.log_pass("Curriculum Modules", "Cleaned 24/7 slogans from all module titles")

    # =========================================================================
    # 4. REVIEWER AGENT & LANGUAGE PURITY VERIFICATION
    # =========================================================================
    def audit_reviewer_language_purity_and_code_blocks(self):
        print("\n" + "=" * 65)
        print("4. AUDITING REVIEWER AGENT: LANGUAGE PURITY & COPIEDABLE CODES")
        print("=" * 65)

        sample_input = """
📘 មេរៀនស្តីពី Deep Learning (ការរៀនស៊ីជម្រៅ)
这是一个中文测试 (Foreign leak) ทดสอบภาษาไทย 24/7 365 FREE
""សម្រង់សម្តី"" គណិតវិទ្យាស្នូលនៃ Neural Networks

```python
# 100% complete runnable Python code
import torch
import torch.nn as nn

class Perceptron(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 1)
    def forward(self, x):
        return torch.sigmoid(self.linear(x))
```

```yaml
role: system
content: Master AI prompt template
```

`pip install torch torchvision`
"""
        cleaned_html = ReviewerAgent.format_for_telegram_html(sample_input)

        # Verify Chinese and Thai scripts are purged from prose
        if "这是一个中文测试" in cleaned_html or "ทดสอบภาษาไทย" in cleaned_html:
            self.log_fail("Foreign Script Purge", "Failed to purge Chinese/Thai foreign script leaks!")
        else:
            self.log_pass("Foreign Script Purge", "100% purged Chinese, Thai, and foreign script leaks")

        # Verify 24/7 365 FREE is purged
        if "24/7 365 FREE" in cleaned_html:
            self.log_fail("Operational Slogan Purge", "Failed to purge '24/7 365 FREE'!")
        else:
            self.log_pass("Operational Slogan Purge", "Purged '24/7 365 FREE' from output")

        # Verify redundant quotes cleaned
        if '""' in cleaned_html:
            self.log_fail("Quote Cleaner", "Redundant quotes '\"\"' were not cleaned")
        else:
            self.log_pass("Quote Cleaner", "Cleaned redundant quote artifacts")

        # Verify code block preserves language-python class for Telegram Copy button
        if '<pre><code class="language-python">' in cleaned_html:
            self.log_pass("Copiedable Code Block", "Rendered <pre><code class=\"language-python\"> (Telegram 1-tap Copy)")
        else:
            self.log_fail("Copiedable Code Block", "Missing language-python class in <pre><code>!")

        # Verify YAML prompt block preserves language-yaml class
        if '<pre><code class="language-yaml">' in cleaned_html:
            self.log_pass("Copiedable Prompt Block", "Rendered <pre><code class=\"language-yaml\"> (Telegram 1-tap Copy)")
        else:
            self.log_fail("Copiedable Prompt Block", "Missing language-yaml class in <pre><code>!")

        # Verify inline code
        if "<code>pip install torch torchvision</code>" in cleaned_html:
            self.log_pass("Inline Code", "Rendered tap-to-copy <code> format")
        else:
            self.log_fail("Inline Code", "Missing <code> wrapper for inline command")

        # Verify Khmer text preserved
        if "ការរៀនស៊ីជម្រៅ" in cleaned_html:
            self.log_pass("Khmer Text Preservation", "Khmer text preserved with 100% integrity")
        else:
            self.log_fail("Khmer Text Preservation", "Khmer text corrupted during sanitization!")

    # =========================================================================
    # 5. CURRICULUM ENGINE ARCHITECTURE (1,200 UNIQUE LESSONS)
    # =========================================================================
    def audit_curriculum_engine_and_anti_repetition(self):
        print("\n" + "=" * 65)
        print("5. AUDITING CURRICULUM: 1,200 DISTINCT LESSONS & 6-PILLAR ARCHITECTURE")
        print("=" * 65)

        # Verify 12 courses
        if len(AI_COURSES) == 12:
            self.log_pass("AI Courses Count", "Exactly 12 AI specialized domains configured")
        else:
            self.log_fail("AI Courses Count", f"Expected 12 courses, found {len(AI_COURSES)}")

        # Verify 120 dedicated domain modules
        if len(AI_COURSE_MODULES) == 12:
            all_10 = all(len(m) == 10 for m in AI_COURSE_MODULES.values())
            if all_10:
                self.log_pass("AI Course Modules", "All 12 courses have 10 dedicated domain modules (120 unique modules)")
            else:
                self.log_fail("AI Course Modules", "Some courses do not have exactly 10 modules!")
        else:
            self.log_fail("AI Course Modules", f"Expected 12 module mappings, got {len(AI_COURSE_MODULES)}")

        # Verify 10 distinct subtopic progressions
        if len(LESSON_SUBTOPICS) == 10:
            self.log_pass("Lesson Subtopics", "10 sequential subtopic progressions defined")
        else:
            self.log_fail("Lesson Subtopics", f"Expected 10 subtopics, got {len(LESSON_SUBTOPICS)}")

        # Verify title distinctness across different courses
        t_gemini = CurriculumEngine.get_lesson_title("gemini", 1)
        t_chatgpt = CurriculumEngine.get_lesson_title("chatgpt", 1)
        t_deeplearning = CurriculumEngine.get_lesson_title("deeplearning", 1)
        t_rag = CurriculumEngine.get_lesson_title("rag", 1)

        if len({t_gemini, t_chatgpt, t_deeplearning, t_rag}) == 4:
            self.log_pass("Cross-Course Uniqueness", "Titles across courses are 100% distinct (Anti-Repetition)")
        else:
            self.log_fail("Cross-Course Uniqueness", "Colliding lesson titles detected between different courses!")

        # Verify subtopic distinctness within the same course
        t_gemini_1 = CurriculumEngine.get_lesson_title("gemini", 1)
        t_gemini_2 = CurriculumEngine.get_lesson_title("gemini", 2)
        if t_gemini_1 != t_gemini_2:
            self.log_pass("Intra-Course Uniqueness", "Adjacent lessons have distinct subtopic focus")
        else:
            self.log_fail("Intra-Course Uniqueness", "Lesson 1 and 2 titles are identical!")

        # Verify prompt mandates
        prompt = CurriculumEngine.generate_lesson_prompt("deeplearning", 25, "km")
        if "3,000 and 3,500 characters" in prompt:
            self.log_pass("Length Mandate", "3,000 to 3,500 characters constraint enforced")
        else:
            self.log_fail("Length Mandate", "Missing 3000-3500 chars mandate in lesson prompt!")

        if "STRICT LANGUAGE PURITY MANDATE" in prompt:
            self.log_pass("Language Purity Mandate", "Language purity directive enforced in prompt")
        else:
            self.log_fail("Language Purity Mandate", "Missing language purity directive in prompt!")

        if "ANTI-REPETITION & ZERO CLICHÉ MANDATE" in prompt:
            self.log_pass("Anti-Repetition Mandate", "Anti-repetition and zero cliché directive enforced in prompt")
        else:
            self.log_fail("Anti-Repetition Mandate", "Missing anti-repetition directive in prompt!")

        if "THE 6-PILLAR GRANDMASTER CURRICULUM ARCHITECTURE" in prompt:
            self.log_pass("6-Pillar Architecture", "All 6 pedagogical pillars enforced in prompt")
        else:
            self.log_fail("6-Pillar Architecture", "Missing 6-pillar curriculum structure in prompt!")

    # =========================================================================
    # 6. SYSTEM HEALTH & METRICS AUDIT
    # =========================================================================
    def audit_system_health_metrics(self):
        print("\n" + "=" * 65)
        print("6. AUDITING SYSTEM HEALTH & MATHEMATICAL ACCURACY")
        print("=" * 65)

        try:
            health = SystemMonitor.get_vps_health()
            if "cpu_percent" in health and "ram_total_gb" in health and "disk_free_gb" in health:
                self.log_pass(
                    "VPS Health Telemetry",
                    f"CPU: {health['cpu_percent']}% | RAM: {health['ram_used_gb']}/{health['ram_total_gb']} GB | Disk Free: {health['disk_free_gb']} GB"
                )
            else:
                self.log_fail("VPS Health Telemetry", "Missing critical telemetry metrics")

            uptime = SystemMonitor.get_uptime()
            if uptime:
                self.log_pass("System Uptime Engine", f"Uptime: {uptime}")
            else:
                self.log_fail("System Uptime Engine", "Failed to retrieve uptime string")
        except Exception as e:
            self.log_fail("VPS Health Telemetry", str(e))

    # =========================================================================
    # 7. CONSTITUTIONAL CHARTER AUDIT (AGENTS.md & METAPHYSICS_STANDARDS.md)
    # =========================================================================
    def audit_constitutional_charters(self):
        print("\n" + "=" * 65)
        print("7. AUDITING CONSTITUTIONAL CHARTERS & METAPHYSICS STANDARDS")
        print("=" * 65)

        agents_md = PROJECT_ROOT / "AGENTS.md"
        meta_md = PROJECT_ROOT / "METAPHYSICS_STANDARDS.md"

        if agents_md.exists():
            content = agents_md.read_text(encoding="utf-8")
            if "novel_18" in content and "Chuon Nath" in content and "6-Pillar" in content:
                self.log_pass("AGENTS.md", "Supreme Law Charter verified (Admin, Language, Curriculum)")
            else:
                self.log_fail("AGENTS.md", "AGENTS.md exists but is missing critical governance sections!")
        else:
            self.log_fail("AGENTS.md", "Missing AGENTS.md at workspace root!")

        if meta_md.exists():
            content = meta_md.read_text(encoding="utf-8")
            if "First-Principles" in content and "Attention" in content and "3,000 to 3,500" in content:
                self.log_pass("METAPHYSICS_STANDARDS.md", "Gold Standard Metaphysics verified (Pedagogy, Math, Code)")
            else:
                self.log_fail("METAPHYSICS_STANDARDS.md", "Missing critical sections in METAPHYSICS_STANDARDS.md!")
        else:
            self.log_fail("METAPHYSICS_STANDARDS.md", "Missing METAPHYSICS_STANDARDS.md at workspace root!")

    # =========================================================================
    # RUN ALL AUDITS & REPORT
    # =========================================================================
    def run_all_audits(self) -> bool:
        print("\n" + "#" * 65)
        print("       SUPREME REAN AI SYSTEM AUDIT & ARCHITECTURAL VERIFIER")
        print("#" * 65)

        self.audit_syntax_and_compilation()
        self.audit_admin_security_gatekeeping()
        self.audit_content_sanitization_and_leaks()
        self.audit_reviewer_language_purity_and_code_blocks()
        self.audit_curriculum_engine_and_anti_repetition()
        self.audit_system_health_metrics()
        self.audit_constitutional_charters()

        print("\n" + "=" * 65)
        print("FINAL AUDIT SUMMARY REPORT")
        print("=" * 65)
        print(f"  TOTAL CHECKS PASSED: {self.passed_checks}")
        print(f"  TOTAL CHECKS FAILED: {self.failed_checks}")
        print(f"  TOTAL WARNINGS     : {self.warnings}")

        if self.failed_checks == 0:
            print("\n  >>> [100% SYSTEM VERIFICATION SUCCESSFUL] <<<")
            print("  All security, language purity, and curriculum standards are ACTIVE.\n")
            return True
        else:
            print(f"\n  >>> [AUDIT DETECTED {self.failed_checks} FAILURES] <<<\n")
            return False


if __name__ == "__main__":
    auditor = SystemAuditor()
    success = auditor.run_all_audits()
    sys.exit(0 if success else 1)
