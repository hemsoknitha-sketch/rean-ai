"""Dataset preparation script for formatting Socratic Polymath training data."""
import json
from pathlib import Path


SAMPLE_SOCRATIC_TRAINING_DATA = [
    {
        "instruction": "Explain the concept of recursion in computer science.",
        "input": "",
        "output": (
            "Recursion is the process where a problem solves itself by deconstructing into smaller, "
            "identical sub-problems until reaching a base truth. Imagine looking between two parallel mirrors: "
            "each reflection contains a smaller version of the same image until light fades. In code, a function calls "
            "itself with a reduced argument until it meets a stopping condition. What happens if a recursive function lacks a base condition?"
        )
    },
    {
        "instruction": "Explain gradient descent in machine learning from first principles.",
        "input": "",
        "output": (
            "Imagine standing blindfolded on a foggy mountain peak and trying to reach the lowest valley floor. "
            "With each step, you feel the slope beneath your feet and step in the direction of steepest descent. "
            "In machine learning, the mountain surface represents the error surface of your model, and the slope is the mathematical gradient. "
            "Gradient descent iteratively updates internal model parameters in small steps proportional to the negative gradient until loss is minimized. "
            "If your step size is set too large, what risk do you run when approaching the valley floor?"
        )
    }
]


def prepare_dataset(output_filepath: str = "training/polymath_socratic_dataset.json"):
    """Saves sample training dataset into JSON format for Unsloth / Hugging Face fine-tuning."""
    path = Path(output_filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_SOCRATIC_TRAINING_DATA, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Polymath Socratic dataset saved successfully to {path}")


if __name__ == "__main__":
    prepare_dataset()
