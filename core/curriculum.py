"""Curriculum Engine: Generates 100-lesson master AI curricula across global AI domains."""
from typing import Dict, List, Tuple

AI_COURSES: Dict[str, Dict[str, str]] = {
    "gemini": {
        "title": "Google Gemini & Multimodal AI",
        "emoji": "🔮",
        "desc": "រៀនសូត្រស្ថាបត្យកម្ម Gemini 3.6, Multimodal Prompting, និង Gemini API Integration"
    },
    "chatgpt": {
        "title": "ChatGPT, GPT-4o & OpenAI API",
        "emoji": "🧠",
        "desc": "រៀនសូត្រពី GPT-4o Architecture, Function Calling, និង AI Assistants SDK"
    },
    "llama": {
        "title": "Meta Llama 3 & Open-Source LLMs",
        "emoji": "🦙",
        "desc": "រៀនសូត្រពី Llama 3.1, Quantization (GGUF/EXL2), និង Ollama Local Deployment"
    },
    "deeplearning": {
        "title": "Deep Learning & Neural Networks",
        "emoji": "🤖",
        "desc": "រៀនសូត្រពី Transformers, Attention Mechanisms, PyTorch, និង Backpropagation"
    },
    "genai": {
        "title": "Midjourney, Stable Diffusion & GenAI",
        "emoji": "🎨",
        "desc": "រៀនសូត្រពី Diffusion Models, ComfyUI, ControlNet, និង Text-to-Image Engineering"
    },
    "agents": {
        "title": "Agentic Coding & AI Software Dev",
        "emoji": "💻",
        "desc": "រៀនសូត្រពី ReAct Framework, Autonomous Coding Agents, និង LangChain/AutoGPT"
    },
    "prompting": {
        "title": "Prompt Engineering & Model Fine-Tuning",
        "emoji": "⚡",
        "desc": "រៀនសូត្រពី Few-Shot Prompting, QLoRA, Unsloth Fine-Tuning, និង Alignment"
    }
}


class CurriculumEngine:
    """Generates structured 100-lesson curriculums dynamically for any AI course."""

    @staticmethod
    def get_course_list() -> List[Tuple[str, str, str]]:
        """Returns list of (course_key, title, emoji)."""
        return [(k, v["title"], v["emoji"]) for k, v in AI_COURSES.items()]

    @staticmethod
    def get_lesson_title(course_key: str, lesson_num: int, lang: str = "km") -> str:
        """Generates structured lesson title for any lesson number from 1 to 100."""
        course_info = AI_COURSES.get(course_key, AI_COURSES["gemini"])
        course_name = course_info["title"]
        
        # Categorize into 10 modules (10 lessons each)
        module_num = (lesson_num - 1) // 10 + 1
        
        modules_km = [
            "មូលដ្ឋានគ្រឹះ និងស្ថាបត្យកម្ម (Foundations & Architecture)",
            "បច្ចេកទេសសរសេរ Prompt កម្រិតខ្ពស់ (Advanced Prompt Engineering)",
            "ការទាញយក និងបកប្រែទិន្នន័យ Multimodal (Multimodal Data Processing)",
            "ការភ្ជាប់ API និងរៀបចំ System Config (API Integration & Config)",
            "ការប្រើប្រាស់ Tools និង Function Calling (Tools & Function Calling)",
            "ប្រព័ន្ធចងចាំ និង State Management (Memory & Context Windows)",
            "ការបង្កើត Autonomous Agents (Building AI Agents)",
            "ការ Fine-Tune ម៉ូឌែលផ្ទាល់ខ្លួន (Model Fine-Tuning & QLoRA)",
            "ការដាក់ឱ្យប្រើប្រាស់លើ Cloud ២៤/៧ (Cloud Deployment & Scaling)",
            "គម្រោងអនុវត្តជាក់ស្តែង និង Master Certification (Capstone Real Projects)"
        ]
        
        module_name = modules_km[module_num - 1]
        sub_lesson = ((lesson_num - 1) % 10) + 1
        
        if lang == "km":
            return f"មេរៀនទី {lesson_num} (ជំពូកទី {module_num}៖ {module_name} - ផ្នែក {sub_lesson})"
        return f"Lesson {lesson_num} (Module {module_num}: {module_name} - Part {sub_lesson})"

    @staticmethod
    def generate_lesson_prompt(course_key: str, lesson_num: int, lang: str = "km") -> str:
        """Generates detailed prompt for Architect agent to deliver a 100% complete lesson without shortcuts."""
        course_info = AI_COURSES.get(course_key, AI_COURSES["gemini"])
        course_title = course_info["title"]
        lesson_title = CurriculumEngine.get_lesson_title(course_key, lesson_num, lang)
        
        prompt = (
            f"You are the Supreme Polymath AI Grandmaster delivering an elite, 100% complete masterclass tutorial.\n\n"
            f"Course: {course_title}\n"
            f"Target Lesson: {lesson_title}\n"
            f"Language Requested: {'Khmer (ភាសាខ្មែរ)' if lang == 'km' else 'English'}\n\n"
            f"Requirements:\n"
            f"1. Explain from First-Principles with absolute clarity, deep pedagogical intuition, and ZERO shortcuts.\n"
            f"2. Provide step-by-step breakdowns, practical code/prompt examples, and real-world usage.\n"
            f"3. Structure with clean emojis and bold section titles.\n"
            f"4. Conclude with 1 Socratic Question and a call-to-action to proceed to Lesson {lesson_num + 1}."
        )
        return prompt
