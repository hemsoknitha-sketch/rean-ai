"""Unsloth + QLoRA Training script for fine-tuning Polymath AI Grandmaster models.

This script is designed for Google Colab (Free T4/L4 GPU) or local Linux/Windows GPU setups.
It uses Unsloth for 80% memory reduction and 2x faster throughput during fine-tuning.
"""

import sys

TRAINING_NOTEBOOK_GUIDE = """
# Unsloth Fine-Tuning Guide (Google Colab Free GPU)
# 1. Open Google Colab (https://colab.research.google.com/)
# 2. Select GPU Runtime (T4 or L4)
# 3. Install Unsloth:
#    !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
#    !pip install --no-deps trl peft accelerate bitsandbytes
"""


def main():
    print(TRAINING_NOTEBOOK_GUIDE)
    
    try:
        from unsloth import FastLanguageModel
        import torch
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import load_dataset
    except ImportError:
        print("[!] Unsloth or training dependencies not detected in current environment.")
        print("    Please run this script inside Google Colab GPU environment or a GPU virtual environment with Unsloth installed.")
        return

    max_seq_length = 2048
    dtype = None # Auto detection (Float16 for T4, Bfloat16 for Ampere+)
    load_in_4bit = True # 4bit quantization for zero-cost memory footprint

    print("[*] Loading base model Qwen/Qwen2.5-7B-Instruct...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="Qwen/Qwen2.5-7B-Instruct",
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit,
    )

    # Apply LoRA Adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    print("[*] Loading dataset...")
    dataset = load_dataset("json", data_files="training/polymath_socratic_dataset.json", split="train")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="output",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=60,
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            output_dir="outputs",
        ),
    )

    print("[*] Starting QLoRA Fine-Tuning...")
    trainer.train()

    print("[*] Exporting model to GGUF format for local Ollama execution ($0 API cost)...")
    model.save_pretrained_gguf("polymath_gguf", tokenizer, quantization_method="q4_k_m")
    print("[✓] Fine-tuning complete! Import GGUF into Ollama with: 'ollama create polymath -f Modelfile'")


if __name__ == "__main__":
    main()
