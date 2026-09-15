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
    },
    "rag": {
        "title": "RAG & Vector Databases",
        "emoji": "🎯",
        "desc": "រៀនសូត្រពី Vector Search (Pinecone, Qdrant, ChromaDB), Hybrid Search, និង Document Chat Intelligence"
    },
    "aivideo": {
        "title": "AI Video & Voice Generation",
        "emoji": "🎬",
        "desc": "រៀនសូត្រពី Sora, Runway Gen-3, Kling AI, Luma Dream, និង Voice Cloning ជាមួយ ElevenLabs"
    },
    "automation": {
        "title": "AI Automation & No-Code Workflows",
        "emoji": "⚙️",
        "desc": "រៀនសូត្រពី n8n, Make.com, Flowise AI, និងការតភ្ជាប់ AI ស្វ័យប្រវត្តិជាមួយ Telegram/Gmail/Sheets"
    },
    "reasoning": {
        "title": "Reasoning Models & Deep Research",
        "emoji": "🧬",
        "desc": "រៀនសូត្រពី Chain-of-Thought (CoT), Test-Time Compute, DeepSeek-R1, និង OpenAI o1/o3-mini"
    },
    "security": {
        "title": "AI Security, Safety & Red Teaming",
        "emoji": "🛡️",
        "desc": "រៀនសូត្រពី Prompt Injection Attacks, Jailbreak Defenses, OWASP for LLMs, និង System Guardrails"
    },
    "frontier4": {
        "title": "The Big 4 Frontier AI (ChatGPT, Gemini, DeepSeek, Grok)",
        "emoji": "🧠",
        "desc": "ស្ទាត់ជំនាញកំពូលម៉ូឌែលទាំង ៤ (GPT-4o, Gemini 2.5, DeepSeek-R1, Grok 2/3)"
    },
    "creative": {
        "title": "Creative Media Studio (Images, Video, Music)",
        "emoji": "🎨",
        "desc": "ផលិតរូបភាព Midjourney/Flux, វីដេអូ Sora/Kling, និងចម្រៀង Suno/Udio"
    },
    "auto_agents": {
        "title": "AI Automation & Autonomous Agents (Autonomous Personal Assistant)",
        "emoji": "⚙️",
        "desc": "n8n, Telegram Bots, Workspace AI, និងជំនួយការស្វ័យប្រវត្តិកម្រិតសហគ្រាស"
    }
}

FAST_TRACK_COURSES: Dict[str, Dict[str, str]] = {
    "prompting": {
        "track_num": 1,
        "title": "វិស្វកម្ម Prompting កម្រិតខ្ពស់ (Prompt Engineering & Reasoning)",
        "emoji": "⚡",
        "desc": "CREATE Framework, In-Context Learning, CoT Reasoning, និង Meta-Prompting",
        "lessons_count": 100
    },
    "frontier4": {
        "track_num": 2,
        "title": "The Big 4 Frontier AI (ChatGPT, Gemini, DeepSeek, Grok)",
        "emoji": "🧠",
        "desc": "ស្ទាត់ជំនាញកំពូលម៉ូឌែលទាំង ៤ (GPT-4o, Gemini 2.5, DeepSeek-R1, Grok 2/3)",
        "lessons_count": 100
    },
    "creative": {
        "track_num": 3,
        "title": "Creative Media Studio (Images, Video, Music)",
        "emoji": "🎨",
        "desc": "ផលិតរូបភាព Midjourney/Flux, វីដេអូ Sora/Kling, និងចម្រៀង Suno/Udio",
        "lessons_count": 100
    },
    "auto_agents": {
        "track_num": 4,
        "title": "AI Automation & Autonomous Agents (Autonomous Personal Assistant)",
        "emoji": "⚙️",
        "desc": "n8n, Telegram Bots, Workspace AI, និងជំនួយការស្វ័យប្រវត្តិកម្រិតសហគ្រាស",
        "lessons_count": 100
    }
}



AI_COURSE_MODULES: Dict[str, List[str]] = {
    "gemini": [
        "ស្ថាបត្យកម្ម Gemini 2.5/Flash & Native Multimodal Core",
        "Multimodal Ingestion (រូបភាព សំឡេង វីដេអូ និងឯកសារ PDF ធំៗ)",
        "Google AI Studio, API Key & Authentication Setup",
        "System Instructions, Structured JSON & Schema Enforcement",
        "Function Calling & Real-Time External Tool Integration",
        "Grounding with Google Search & Dynamic Live Retrieval",
        "Context Caching & Long-Context (1M-2M Tokens) Optimization",
        "Model Tuning & Supervised Fine-Tuning លើ Google Cloud",
        "Multi-turn Dialogue, Sessions & Memory Architecture",
        "Capstone: Real-World Enterprise Multimodal AI System"
    ],
    "chatgpt": [
        "ស្ថាបត្យកម្ម GPT-4o, GPT-4o mini & Reasoning Frontier",
        "OpenAI API Setup, Tokenomics & Cost Efficiency",
        "Advanced In-Context Learning & Few-Shot Engineering",
        "Structured Outputs, JSON Mode & Pydantic Schema Validation",
        "Function Calling, Assistants API & Code Interpreter",
        "File Search & RAG Architecture ក្នុង OpenAI Ecosystem",
        "Vision & Audio Multimodal API Integration",
        "Model Fine-Tuning ជាមួយទិន្នន័យ Custom JSONL",
        "Moderation API, Safety Guardrails & Streaming Control",
        "Capstone: Enterprise Autonomous Assistant កម្រិតសហគ្រាស"
    ],
    "llama": [
        "មូលដ្ឋានគ្រឹះ Open-Source LLMs & Llama 3.1/3.3 Architecture",
        "Llama Tokenizer, 128k Context Window & RoPE Mechanism",
        "Ollama Local Deployment, Modelfiles & CLI Mastery",
        "Model Quantization (GGUF, EXL2, AWQ, FP8) & VRAM Tuning",
        "Local API Server (Ollama REST API, vLLM, LM Studio)",
        "Prompt Formatting (Llama 3 Chat Templates & Special Tokens)",
        "Function Calling & Tool Execution លើ Local Llama Models",
        "Fine-Tuning Llama 3 ជាមួយ Unsloth & QLoRA លើ Single GPU",
        "Private Offline RAG គ្មានការលេចធ្លាយទិន្នន័យ (Air-Gapped AI)",
        "Capstone: Production Local AI Deployment លើ Linux VPS & Docker"
    ],
    "deeplearning": [
        "គណិតវិទ្យាស្នូលសម្រាប់ AI (Linear Algebra, Calculus & Tensors)",
        "Artificial Neural Networks (Perceptron & Activation Functions)",
        "Loss Functions & Backpropagation (ក្បួនគណនា Gradient Descent)",
        "Optimizers (SGD, Adam, AdamW) & Learning Rate Scheduling",
        "Convolutional Neural Networks (CNNs) សម្រាប់ Computer Vision",
        "Recurrent Neural Networks (RNNs, LSTMs, GRUs) សម្រាប់ Sequence",
        "Transformer Architecture & Scaled Dot-Product Attention",
        "PyTorch Framework ពីមូលដ្ឋានគ្រឹះរហូតដល់ Advanced Tensors",
        "Training Pipeline, Overfitting Defenses (Dropout, LayerNorm)",
        "Capstone: បង្កើត និង Train Deep Neural Network ពីបាតដៃទទេ"
    ],
    "genai": [
        "គោលការណ៍ Latent Diffusion Models (LDMs) & Denoising Math",
        "Stable Diffusion (SD 1.5, SDXL, Flux.1) Architecture",
        "Midjourney Master Prompting (Lighting, Camera, Aspect Ratio)",
        "ComfyUI Modular Node Architecture & Workflow Design",
        "ControlNet (Pose, Canny Edge, Depth, Scribble) Integration",
        "LoRA (Low-Rank Adaptation) Training សម្រាប់រូបភាពផ្ទាល់ខ្លួន",
        "Image-to-Image, Inpainting & Outpainting Techniques",
        "Latent Upscaling, Face Restoration & Image Enhancement",
        "Text-to-Image APIs Integration (Replicate, Fal.ai, Together)",
        "Capstone: Automated AI Generative Media Production Suite"
    ],
    "agents": [
        "មូលដ្ឋានគ្រឹះ Autonomous AI Agents & ReAct Framework",
        "Agent Cognitive Engine (Perception, Planning, Memory, Tools)",
        "LangChain & LangGraph State Machine Architectures",
        "Multi-Agent Swarms & Collaborative Workflows (CrewAI, AutoGen)",
        "Dynamic Tool Calling & External APIs Execution សម្រាប់ Agents",
        "Hierarchical Memory (Short-Term, Long-Term & Vector Memory)",
        "Autonomous Coding Agents (Code Generation, Testing & Self-Healing)",
        "Human-in-the-Loop & Execution Safety Guardrails",
        "Autonomous Web Browsing & Dynamic Scraping Agents",
        "Capstone: Full-Stack Autonomous Software Engineering Agent"
    ],
    "prompting": [
        "គ្រឹះរឹងមាំនៃ Prompt Engineering & Attention Steering",
        "Zero-Shot vs Few-Shot In-Context Learning Strategies",
        "Chain-of-Thought (CoT), Step-Back & Tree-of-Thoughts Logic",
        "Structured System Prompts (Personas, Rules, XML Delimiters)",
        "Output Formatting (Strict JSON, YAML & Markdown Schemas)",
        "Adversarial Prompting & Jailbreak Defense Methodologies",
        "Dynamic Prompt Injection Defenses & Input Sanitization",
        "Meta-Prompting (ការប្រើ AI បង្កើត និង Optimize Prompts ស្វ័យប្រវត្តិ)",
        "QLoRA & Dataset Formatting សម្រាប់ Supervised Fine-Tuning",
        "Capstone: Production Enterprise Master Prompt Architecture Suite"
    ],
    "rag": [
        "គ្រឹះនៃ RAG (Retrieval-Augmented Generation) & Hallucination Defenses",
        "Document Chunking Strategies (Fixed, Recursive, Semantic Chunking)",
        "Vector Embeddings (OpenAI, BGE, Nomic) & Dimensionality",
        "Vector Databases Setup (Pinecone, ChromaDB, Qdrant, Milvus)",
        "Similarity Metrics (Cosine Similarity, Dot Product, Euclidean)",
        "Hybrid Search (Dense Vector + Sparse BM25) & Re-Ranking (Cohere)",
        "Metadata Filtering & Multi-Tenant Knowledge Bases",
        "Advanced RAG (Query Decomposition, HyDE, Multi-Query)",
        "RAG Evaluation Metrics (RAGAS: Faithfulness, Answer Relevance)",
        "Capstone: Private Enterprise Document Intelligence RAG Engine"
    ],
    "aivideo": [
        "ស្ថាបត្យកម្ម AI Video Generation (Sora, Runway Gen-3, Kling AI)",
        "Cinematic Text-to-Video Prompting (Camera Motions, Angles, Lighting)",
        "Image-to-Video Animation & First/Last Frame Consistency",
        "AI Voice Synthesis & Voice Cloning ជាមួយ ElevenLabs",
        "AI Lip-Syncing & Talking Avatars (HeyGen, LivePortrait)",
        "Motion Brush, Camera Pathing & Video Physics Control",
        "AI Sound Effects & Cinematic Background Music (Suno, Udio)",
        "Video Super-Resolution Upscaling & Frame Interpolation (RIFE)",
        "Automated Video Processing Pipelines ជាមួយ Python & FFmpeg",
        "Capstone: Automated Faceless Video Channel Production Suite"
    ],
    "automation": [
        "គោលការណ៍ AI Automation & No-Code/Low-Code Architecture",
        "n8n Self-Hosted Setup & Workflow Orchestration",
        "Make.com Scenarios, Webhook Triggers & Router Logic",
        "តភ្ជាប់ Telegram Bot ជាមួយ AI & Google Sheets ដោយស្វ័យប្រវត្តិ",
        "Automated Customer Support Workflows (Gmail, Telegram, Zendesk)",
        "Social Media Content Generation & Multi-Platform Scheduling",
        "Webhooks, REST APIs Integration & Payload Transformation",
        "Fault Tolerance, Error Handling & Fallback Notification Systems",
        "Flowise AI & Langflow Visual No-Code Agentic Workflows",
        "Capstone: Autonomous Enterprise Business Operations System"
    ],
    "reasoning": [
        "មូលដ្ឋានគ្រឹះ Reasoning Models (DeepSeek-R1, OpenAI o1, o3-mini)",
        "Test-Time Compute (TTC) & Internal Hidden Reasoning Traces",
        "Reinforcement Learning (RLHF, RLAIF, GRPO) សម្រាប់ Reasoning",
        "Step-by-Step Verification, Self-Correction & Backtracking",
        "Solving Complex Mathematical & Algorithmic Problems",
        "Deep Research Workflows & Autonomous Multi-Source Synthesis",
        "Prompting Reasoning Models (Zero-Shot CoT vs Traditional LLMs)",
        "Latency vs Accuracy Trade-offs & Tokenomics នៃ Reasoning",
        "Error Analysis, Hallucination Verification & Fact-Checking",
        "Capstone: Autonomous Deep Research & Technical Synthesis Node"
    ],
    "security": [
        "ទិដ្ឋភាពទូទៅនៃ AI Security & OWASP Top 10 for LLMs",
        "Prompt Injection Attacks (Direct, Indirect & Jailbreaking)",
        "Training Data Extraction, Membership Inference & Model Stealing",
        "Sensitive Data Protection & PII Redaction Guardrails",
        "System Prompt Leakage Defenses & Canary Tokens",
        "Input/Output Guardrail Frameworks (NeMo Guardrails, Llama Guard)",
        "Adversarial Robustness Testing & Automated Red Teaming",
        "Denial of Service (DoS) & Resource Exhaustion Defenses",
        "Secure AI Integration: IAM, API Key Vaults & Sandboxing",
        "Capstone: Fortress-Grade Enterprise AI Defense Architecture"
    ],
    "frontier4": [
        "ChatGPT & GPT-4o ស្ថាបត្យកម្មស្នូល (Assistants API, Code Interpreter & Canvas)",
        "Custom GPTs, Advanced Data Analysis & Voice Mode ក្នុង OpenAI Ecosystem",
        "Google Gemini 2.5/Flash & Native Multimodal Ingestion (រូបភាព សំឡេង វីដេអូ PDF)",
        "Gemini Long-Context (2M Tokens), Context Caching & Grounding with Google Search",
        "DeepSeek-V3 ស្ថាបត្យកម្មស្នូល, Open-Weights Economics & MoE Efficiency",
        "DeepSeek-R1 Reasoning Engine (Test-Time Compute, Reasoning Traces & Coding)",
        "xAI Grok 2/3 & Real-Time Search លើបណ្តាញ X (Twitter Intelligence)",
        "Grok Fun Mode, Uncensored Analysis & Flux.1 Image Generation Integration",
        "Cross-Model Evaluation & Synthesis (ការប្រៀបធៀប និងជ្រើសរើស Model សមស្របតាមការងារ)",
        "Capstone: Multi-Model Enterprise Workflow (ChatGPT + Gemini + DeepSeek + Grok)"
    ],
    "creative": [
        "Midjourney v6 Master Prompting (Cinematic Lighting, Camera Angles & Aspect Ratios)",
        "Flux.1 & Stable Diffusion XL (Photorealism, Typography & Negative Prompts)",
        "ComfyUI Modular Node Architecture & ControlNet (Pose, Canny Edge, Depth)",
        "LoRA Training & Precision Editing (Image-to-Image, Inpainting & Outpainting)",
        "AI Video Foundations (Sora, Runway Gen-3 & Kling AI Architecture)",
        "Cinematic Camera Controls, Motion Brush & Video Consistency",
        "AI Lip-Syncing, Talking Avatars (HeyGen, LivePortrait) & Faceless Video",
        "AI Music Generation Foundations (Suno v3 & Udio Architecture)",
        "Full Song Production ជាមួយ Suno (Lyrics Structure, Verses, Choruses & Moods)",
        "Capstone: Complete Media Production Suite (Art, Music & Cinematic Video Pipeline)"
    ],
    "auto_agents": [
        "គោលការណ៍ AI Automation & No-Code/Low-Code Architecture",
        "n8n Self-Hosted Setup, Webhooks & Workflow Orchestration",
        "Make.com Scenarios (Router Logic, Payload Transformation & Error Handling)",
        "Telegram Bot Integration ជាមួយ AI (ឆ្លើយតបអតិថិជន និងកត់ត្រាទិន្នន័យស្វ័យប្រវត្តិ)",
        "Google Workspace AI Automation (Gmail Support, Google Sheets & Calendar Sync)",
        "Autonomous Agents & ReAct Framework (Perception, Planning, Memory & Tools)",
        "LangChain & Multi-Agent Swarms (CrewAI) សម្រាប់ដោះស្រាយកិច្ចការស្មុគស្មាញ",
        "Tool Execution & Web Scraping (បំពាក់ឱ្យ Agent ស្វែងរកព័ត៌មានលើ Internet)",
        "Personal Autonomous Executive Assistant (រៀបចំកាលវិភាគ សង្ខេបព័ត៌មាន និងរំលឹកកិច្ចការពេញម៉ោង)",
        "Capstone: Fully Autonomous Enterprise Business & Personal Operations Suite"
    ]
}

LESSON_SUBTOPICS: List[str] = [
    "មូលដ្ឋានគ្រឹះគន្លឹះ និងគោលការណ៍ស្នូល (Fundamental Concepts & Core Principles)",
    "ស្ថាបត្យកម្ម និងរបៀបដំណើរការស៊ីជម្រៅ (Architecture & Deep Mechanism)",
    "ការដំឡើង និងការកំណត់រចនាសម្ព័ន្ធបច្ចេកទេស (Setup & Technical Configuration)",
    "បច្ចេកទេសអនុវត្តកម្រិតខ្ពស់ (Advanced Implementation Techniques)",
    "ការដោះស្រាយបញ្ហា និងកំហុសទូទៅ (Debugging & Common Error Pitfalls)",
    "គំរូកូដ និងការសាកល្បងជាក់ស្តែង (Hands-on Code & Practical Experiment)",
    "ការបង្កើនល្បឿន និងប្រសិទ្ធភាពចំណាយ (Performance & Cost Optimization)",
    "ស្តង់ដារសុវត្ថិភាព និង Best Practices (Security & Production Best Practices)",
    "ការតភ្ជាប់ជាមួយប្រព័ន្ធខាងក្រៅ (Integration & Real-world Workflows)",
    "គម្រោងអនុវត្តសង្ខេបជំពូក និង Capstone Lab (Module Mastery & Capstone Lab)"
]


class CurriculumEngine:
    """Generates structured 100-lesson curriculums dynamically for any AI course."""

    @staticmethod
    def get_course_list() -> List[Tuple[str, str, str]]:
        """Returns list of (course_key, title, emoji)."""
        return [(k, v["title"], v["emoji"]) for k, v in AI_COURSES.items()]

    @staticmethod
    def get_fast_track_courses() -> List[Tuple[str, str, str, str]]:
        """Returns list of (course_key, title, emoji, desc) for the 4 Fast-Track Masterclass courses."""
        return [(k, v["title"], v["emoji"], v["desc"]) for k, v in FAST_TRACK_COURSES.items()]

    @staticmethod
    def get_lesson_title(course_key: str, lesson_num: int, lang: str = "km") -> str:
        """Generates structured unique lesson title for any lesson number from 1 to 100."""
        # Categorize into 10 modules (10 lessons each)
        module_num = max(1, min(10, (lesson_num - 1) // 10 + 1))
        sub_lesson = max(1, min(10, ((lesson_num - 1) % 10) + 1))

        course_modules = AI_COURSE_MODULES.get(course_key, AI_COURSE_MODULES["gemini"])
        module_name = course_modules[module_num - 1]
        sub_topic = LESSON_SUBTOPICS[sub_lesson - 1]

        if lang == "km":
            return f"មេរៀនទី {lesson_num} (ជំពូកទី {module_num}៖ {module_name} - {sub_topic})"
        return f"Lesson {lesson_num} (Module {module_num}: {module_name} - {sub_topic})"

    @staticmethod
    def generate_lesson_prompt(course_key: str, lesson_num: int, lang: str = "km", mode: str = "socratic") -> str:
        """Generates detailed prompt for Architect agent.
        
        Supports two pedagogical modes:
        - 'explanatory': Explanatory/Masterclass Mode (2,000 - 2,500 chars) with complete deconstruction.
        - 'socratic': Interactive Socratic Mode (Core intuition + 1,000-1,500 chars of code scaffolds
                      with placeholders '/* សរសេរកូដនៅទីនេះ */' or '# TODO: បំពេញកូដនៅទីនេះ',
                      step-by-step diagnostic questions, and score evaluation setup).
        """
        course_info = AI_COURSES.get(course_key, AI_COURSES["gemini"])
        course_title = course_info["title"]
        lesson_title = CurriculumEngine.get_lesson_title(course_key, lesson_num, lang)

        is_socratic = "socratic" in mode.lower()

        mode_instructions = ""
        if is_socratic:
            mode_instructions = (
                "MODE: INTERACTIVE SOCRATIC LEARNING MODE (របៀបសូក្រាតអន្តរកម្ម)\n"
                "- TARGET LENGTH: You MUST generate a comprehensive, highly detailed masterclass between 3,000 and 3,500 characters in length.\n"
                "- ARCHITECTURAL BREAKDOWN:\n"
                "  1. Core Principles Intuition (1,500 - 2,000 characters): Deconstruct fundamental concepts from first principles.\n"
                "  2. Interactive Socratic Code Scaffolding & Diagnostic Exercise (1,000 - 1,500 characters):\n"
                "     • Provide real-world code scaffolding where critical logic is replaced by standard placeholders:\n"
                "       `/* សរសេរកូដនៅទីនេះ */` (for JS/C/SQL) or `# TODO: បំពេញកូដនៅទីនេះ` (for Python).\n"
                "     • Add an explicit diagnostic question testing the student's step-by-step understanding.\n"
                "     • Instruct the student to reply directly in chat with their completed code/answer to be evaluated for up to +20 Score Points (ពិន្ទុវាយតម្លៃកម្រិតចំណេះដឹង).\n"
                "     • Format the exercise clearly under section '៦. លំហាត់ស្ទង់កម្រិតសមត្ថភាពសូក្រាត (Interactive Socratic Challenge)'.\n"
            )
        else:
            mode_instructions = (
                "MODE: EXPLANATORY / MASTERCLASS MODE (របៀបពន្យល់ក្បោះក្បាយ)\n"
                "- TARGET LENGTH: You MUST generate a comprehensive, pristine masterclass between 2,000 and 2,500 characters.\n"
                "- Deliver complete, self-contained technical instruction, fully working 100% complete code blocks, and no placeholders.\n"
            )

        prompt = (
            f"You are the Supreme Polymath AI Grandmaster delivering an elite tutorial.\n\n"
            f"Course: {course_title}\n"
            f"Target Lesson: {lesson_title}\n\n"
            f"{mode_instructions}\n"
            f"STRICT LANGUAGE PURITY MANDATE:\n"
            f"1. You MUST use 100% full, rich, natural Khmer language adhering to the Samdech Chuon Nath Dictionary for all explanations, descriptions, and pedagogical guidance.\n"
            f"2. You are ONLY permitted to attach technical terms in English inside parentheses right after their Khmer equivalents, e.g. 'គំរូភាសាធំៗ (Large Language Models)', 'មូលដ្ឋានទិន្នន័យវ៉ិចទ័រ (Vector Databases)'.\n"
            f"3. ABSOLUTELY NO OTHER FOREIGN LANGUAGES ALLOWED. Eradicate 100% of foreign words: ZERO Chinese characters (中文), ZERO Thai characters (ไทย), ZERO Vietnamese characters, ZERO French, etc. Any presence of foreign characters outside code blocks is strictly prohibited.\n\n"
            f"ANTI-REPETITION & ZERO CLICHÉ MANDATE:\n"
            f"1. Absolutely NO repeated quotes or generic clichés across lessons (e.g. never use canned quotes like 'នៅក្នុងយុគសម័យឌីជីថល...', 'ចំណេះដឹងគឺជា...', 'នៅក្នុងសម័យកាលបច្ចេកវិទ្យា...').\n"
            f"2. Every lesson MUST have its own fresh, original, highly specific First-Principles deconstruction tailored strictly to '{lesson_title}'.\n"
            f"3. Never output generic boilerplate or filler phrases. Maintain dense, high-value technical instruction from the very first line.\n\n"
            f"THE 6-PILLAR GRANDMASTER CURRICULUM ARCHITECTURE:\n"
            f"Organize your entire lesson strictly using the following 6 numbered sections:\n\n"
            f"១. សេចក្តីផ្តើម និងគោលបំណងស្នូល (Overview & Core Objectives):\n"
            f"• បង្ហាញចំណងជើងមេរៀន គោលដៅជាក់លាក់ និងអ្វីដែលអ្នករៀននឹងទទួលបាន ១០០% បន្ទាប់ពីបញ្ចប់មេរៀននេះ។ ចូលត្រង់ប្រធានបទភ្លាម គ្មានពាក្យ Quotes ឬពាក្យផ្តើមច្រំដែលឡើយ។\n\n"
            f"២. មូលដ្ឋានគ្រឹះ និងទ្រឹស្តីបំបែកពីបាតដៃទទេ (First-Principles Intuition):\n"
            f"• ពន្យល់ 'ហេតុអ្វី (Why)' មុន 'យ៉ាងដូចម្តេច (How)'។\n"
            f"• បំបែកគំនិតស្មុគស្មាញឱ្យទៅជាភាសាខ្មែរធម្មជាតិងាយយល់បំផុត ដោយប្រើការប្រៀបធៀបក្នុងជីវិតរស់នៅជាក់ស្តែង (Real-world Analogy) ថ្មីស្រឡាង ធានាថាអ្នកចាប់ផ្តើមដំបូងយល់ចេញច្បាស់លាស់ដាច់ខាត។\n\n"
            f"៣. ការណែនាំឧបករណ៍ទំនើប និងការដំឡើងបរិស្ថាន (Modern Tools & Setup Guide):\n"
            f"• ណែនាំឧបករណ៍ ឬបណ្ណាល័យបច្ចេកវិទ្យា AI ទាន់សម័យ (ដូចជា Google AI Studio, Python venv, Gemini API, OpenAI API, Ollama, LangChain, n8n, etc.)។\n"
            f"• បង្ហាញជំហានដំឡើងច្បាស់លាស់ មួយជំហានម្តងៗ (Step-by-step Setup)។ រាល់ Terminal Command ទាំងអស់ (ដូចជា python -m venv, pip install, export GEMINI_API_KEY=...) ត្រូវតែដាក់ក្នុង Code Block ដាច់ដោយឡែកពីគ្នា (```bash ... ```) ដាច់ខាតមិនសរសេរជាអត្ថបទធម្មតាឡើយ។\n\n"
            f"៤. គន្លឹះ និងរូបមន្តសរសេរ Prompt កម្រិតវិជ្ជាជីវៈ (Professional Prompt Engineering Blueprint):\n"
            f"• ពន្យល់ពីគន្លឹះសរសេរ Prompt ឱ្យចេញលទ្ធផលត្រឹមត្រូវបំផុត (Role, Context, Task, Delimiters, Few-shot Examples, Constraints)។\n"
            f"• ផ្តល់គំរូ Prompt Blueprint ជាក់ស្តែង (ដូចជា [ROLE], [CONTEXT], [TASK], [CONSTRAINTS]) នៅក្នុង Code Block (```yaml ... ``` ឬ ```markdown ... ```) ដើម្បីឱ្យអ្នករៀនអាច 1-Tap Copy យកទៅប្រើភ្លាមៗ។\n\n"
            f"៥. កូដគំរូ និង Prompt ជាក់ស្តែង Copiedable Super Smart (Complete Ready-to-Run Code & Prompts):\n"
            f"• ផ្តល់កូដជាក់ស្តែង (Python/JS/Bash script) ក្នុង code block (```python ... ```) ដែលពេញលេញ ១០០% Ready-to-Run និងងាយស្រួល Copy យកទៅអនុវត្ត។\n"
            f"• ផ្តល់ Master Prompt គំរូពេញលេញក្នុង code block (```yaml ... ``` ឬ ```markdown ... ```) សម្រាប់អ្នករៀនយកទៅ Paste ក្នុង ChatGPT, Gemini, ឬ Claude បានភ្លាម។\n\n"
            f"៦. ការអនុវត្តជាក់ស្តែង និងសំណួរឆ្លុះបញ្ចាំង (Hands-on Lab & Socratic Reflection):\n"
            f"{'• ផ្តល់គ្រោងកូដ Scaffolding ក្នុង code block (```python ... ```) ដែលមានចន្លោះ `# TODO: បំពេញកូដនៅទីនេះ` ឬ `/* សរសេរកូដនៅទីនេះ */` រួមជាមួយសំណួរស្ទង់ការយល់ដឹងមួយជំហានម្តងៗ ព្រមទាំងប្រាប់សិស្សឱ្យ reply ចម្លើយដើម្បីទទួលបានពិន្ទុរហូតដល់ +20 Score Points។' if is_socratic else '• លំហាត់អនុវត្តខ្នាតតូចសម្រាប់អ្នករៀនសាកល្បងដោយខ្លួនឯង និងសំណួរគិតពិចារណា (Socratic Question) ដើម្បីពង្រឹងការយល់ដឹងស៊ីជម្រៅ។'}\n"
            f"• ការណែនាំឱ្យចុចប៊ូតុង '📖 មេរៀនបន្ទាប់ ▶' សម្រាប់មេរៀនទី {min(100, lesson_num + 1)}។\n\n"
            f"FORMATTING, BALANCED TYPOGRAPHY & COPIEDABLE CODE DIRECTIVES:\n"
            f"- Single Pristine Page Layout: The entire lesson must be clean, dense, and self-contained to fit gracefully in one view.\n"
            f"- Balanced Typography (អក្សរតម្រឹមស្មើសងខាង): Organize text into balanced, readable paragraphs (2-3 sentences each) with uniform bullet points (•) and clean indentation.\n"
            f"- Strict Code Fencing: Every single command, prompt blueprint, script, or scaffold MUST be enclosed in standard triple backticks (```bash, ```yaml, ```python). Never write bare commands as plain prose.\n"
            f"- Short Code & Inline Syntax: Wrap all short commands, variables, function names, and libraries in single backticks (`pip install ...`, `torch.nn`, `len()`) for instant tap-to-copy.\n"
            f"- Multi-Line & Multiple Code Blocks: Wrap all code in standard fenced blocks with explicit language tags (```python, ```bash, ```yaml, ```sql). When presenting multiple code snippets, separate them into distinct, individually copyable blocks.\n"
            f"- Use numbered sections (១. , ២. , ៣. ), bullet points (•), and relevant emojis (🔮, 🚀, 💡, ⚙️, 📋, 🎯).\n"
            f"- Avoid excessive loose asterisks or raw markdown hash tags (`###`).\n"
            f"- Adhere strictly to the Khmer grammar and vocabulary of Samdech Sangha Raja Chuon Nath Dictionary."
        )
        return prompt


