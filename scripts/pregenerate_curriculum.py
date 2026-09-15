#!/usr/bin/env python3
"""
Supreme Curriculum Pre-Generation Engine (REAN AI)
─────────────────────────────────────────────────
Pre-generates and permanently caches all 1,200 AI Masterclass lessons across 12 domains
directly to disk for instant 0.001s response, zero API quota consumption, and zero runtime errors.

Usage:
  # Pre-generate a specific course (Lessons 1-10)
  python scripts/pregenerate_curriculum.py --course gemini --start 1 --end 10

  # Pre-generate all 12 courses (both Socratic & Explanatory modes)
  python scripts/pregenerate_curriculum.py --course all --mode both

  # Run in background on VPS:
  nohup python scripts/pregenerate_curriculum.py --course all --mode both > pregen.log 2>&1 &
"""

import os
import sys
import time
import argparse
import asyncio
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config
from memory.state_manager import StateManager
from core.evaluator import EvaluatorAgent
from core.architect import ArchitectAgent
from core.reviewer import ReviewerAgent
from core.curriculum import CurriculumEngine, AI_COURSES
from core.lesson_cache import LessonCache

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("CurriculumPreGen")


async def pregenerate_lesson(
    course_key: str,
    lesson_num: int,
    mode: str,
    architect_agent: ArchitectAgent,
    evaluator_agent: EvaluatorAgent,
    reviewer_agent: ReviewerAgent,
    state_manager: StateManager,
    force: bool = False
) -> bool:
    """Generates and caches a single lesson if not already present."""
    cache_key = f"km_{mode}"
    existing = LessonCache.get(course_key, lesson_num, lang=cache_key)

    if existing and not force:
        logger.info(f"  [CACHE HIT] {course_key.upper()} មេរៀនទី {lesson_num} ({mode}) already cached ({len(existing)} chars). Skipping.")
        return True

    lesson_title = CurriculumEngine.get_lesson_title(course_key, lesson_num, lang="km")
    logger.info(f"  [GENERATING] {course_key.upper()} មេរៀនទី {lesson_num} ({mode}): {lesson_title[:50]}...")

    prompt = CurriculumEngine.generate_lesson_prompt(course_key, lesson_num, lang="km", mode=mode)
    user_state = state_manager.get_state(f"pregen_{course_key}")
    intent = evaluator_agent.analyze(prompt)

    try:
        raw_response = await architect_agent.generate_response(
            user_query=prompt,
            user_state=user_state,
            intent=intent
        )
        sanitized = reviewer_agent.validate_and_sanitize(text=raw_response, strict=Config.ZERO_MARKDOWN_STRICT)
        sanitized = ReviewerAgent.balance_html_tags(sanitized)

        if not sanitized or len(sanitized.strip()) < 100:
            logger.error(f"  [FAIL] Generated lesson too short for {course_key}:{lesson_num}")
            return False

        LessonCache.set(course_key, lesson_num, cache_key, sanitized)
        logger.info(f"  [SUCCESS] Pre-generated and cached {course_key.upper()} មេរៀនទី {lesson_num} ({len(sanitized)} chars).")
        return True

    except Exception as e:
        logger.error(f"  [ERROR] Failed to generate {course_key}:{lesson_num}: {e}", exc_info=True)
        return False


async def run_batch_pregeneration(
    target_courses: list,
    start_lesson: int,
    end_lesson: int,
    modes: list,
    delay: float,
    force: bool
):
    """Orchestrates batch pre-generation across courses and lessons."""
    logger.info("Initializing Cognitive Pipeline for Batch Pre-Generation...")
    architect_agent = ArchitectAgent()
    evaluator_agent = EvaluatorAgent()
    reviewer_agent = ReviewerAgent()
    state_manager = StateManager()

    total_tasks = len(target_courses) * (end_lesson - start_lesson + 1) * len(modes)
    completed = 0
    success_count = 0
    skipped_count = 0
    fail_count = 0

    start_time = time.time()
    logger.info(f"Starting Pre-Generation: {len(target_courses)} courses | Lessons {start_lesson}-{end_lesson} | Modes: {modes} | Total: {total_tasks} tasks")

    for course_key in target_courses:
        course_name = AI_COURSES.get(course_key, {}).get("title", course_key)
        print(f"\n{'='*60}")
        print(f"📚 COURSE: {course_name} [{course_key.upper()}]")
        print(f"{'='*60}")

        for lesson_num in range(start_lesson, end_lesson + 1):
            for mode in modes:
                completed += 1
                progress = (completed / total_tasks) * 100

                cache_key = f"km_{mode}"
                is_cached = LessonCache.get(course_key, lesson_num, lang=cache_key)

                if is_cached and not force:
                    skipped_count += 1
                    print(f"[{completed}/{total_tasks} - {progress:.1f}%] [SKIP] {course_key} #{lesson_num} ({mode}) - Already cached.")
                    continue

                success = await pregenerate_lesson(
                    course_key=course_key,
                    lesson_num=lesson_num,
                    mode=mode,
                    architect_agent=architect_agent,
                    evaluator_agent=evaluator_agent,
                    reviewer_agent=reviewer_agent,
                    state_manager=state_manager,
                    force=force
                )

                if success:
                    success_count += 1
                    print(f"[{completed}/{total_tasks} - {progress:.1f}%] [DONE] {course_key} #{lesson_num} ({mode}) cached.")
                else:
                    fail_count += 1
                    print(f"[{completed}/{total_tasks} - {progress:.1f}%] [FAIL] {course_key} #{lesson_num} ({mode}) failed.")

                # Adaptive rate limit pause between generations
                if delay > 0:
                    await asyncio.sleep(delay)

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"🎉 BATCH PRE-GENERATION SUMMARY REPORT")
    print(f"{'='*60}")
    print(f"  Total Processed : {completed}/{total_tasks}")
    print(f"  Newly Generated : {success_count}")
    print(f"  Already Cached  : {skipped_count}")
    print(f"  Failed          : {fail_count}")
    print(f"  Elapsed Time    : {elapsed/60:.2f} minutes ({elapsed:.1f}s)")
    print(f"  Storage Location: {Path(PROJECT_ROOT) / 'data' / 'lesson_cache.json'}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Pre-generate REAN AI 1,200 Masterclass Lessons")
    parser.add_argument(
        "--course",
        type=str,
        default="gemini",
        help="Target course key (e.g. gemini, chatgpt, llama, deeplearning, or 'all')"
    )
    parser.add_argument("--start", type=int, default=1, help="Start lesson number (1-100)")
    parser.add_argument("--end", type=int, default=10, help="End lesson number (1-100)")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["socratic", "explanatory", "both"],
        default="socratic",
        help="Learning mode to generate"
    )
    parser.add_argument("--delay", type=float, default=2.0, help="Delay in seconds between API calls")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing cache")

    args = parser.parse_args()

    if args.course.lower() == "all":
        target_courses = list(AI_COURSES.keys())
    else:
        if args.course.lower() not in AI_COURSES:
            print(f"Error: Unknown course '{args.course}'. Available: {list(AI_COURSES.keys())}")
            sys.exit(1)
        target_courses = [args.course.lower()]

    modes = ["socratic", "explanatory"] if args.mode == "both" else [args.mode]

    asyncio.run(
        run_batch_pregeneration(
            target_courses=target_courses,
            start_lesson=args.start,
            end_lesson=args.end,
            modes=modes,
            delay=args.delay,
            force=args.force
        )
    )


if __name__ == "__main__":
    main()
