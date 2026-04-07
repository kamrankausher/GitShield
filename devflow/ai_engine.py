import os
import logging
import warnings
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# -------------------------------
# CLEAN ENV (REMOVE WARNINGS)
# -------------------------------
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# -------------------------------
# LOAD MODEL (ONCE)
# -------------------------------
MODEL_NAME = "distilgpt2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

model.eval()

# -------------------------------
# HYBRID AI (RULE + LLM)
# -------------------------------
def generate_ai_suggestion(context):
    """
    Generate safe, clean, professional AI suggestion
    """

    # 🔥 HIGH-QUALITY PREDEFINED RESPONSES
    predefined = {
        "commit message is too vague":
            "Write commit messages that clearly explain what changed and why.",
        
        "commit message too short":
            "Use meaningful commit messages that describe the purpose of your changes.",
        
        "main branch":
            "Create and work on a feature branch instead of committing directly to main.",
        
        "untracked":
            "Review untracked files and either add them or include them in .gitignore.",
        
        "too many files":
            "Split your changes into smaller commits for better clarity and tracking.",
        
        "risky file":
            "Avoid committing large or sensitive files to keep the repository clean."
    }

    # 🔍 MATCH PREDEFINED FIRST (FAST + RELIABLE)
    context_lower = context.lower()
    for key in predefined:
        if key in context_lower:
            return predefined[key]

    # -------------------------------
    # 🤖 FALLBACK AI (CONTROLLED)
    # -------------------------------
    prompt = f"""
You are a senior software engineer mentor.

Problem: {context}

Give one short professional suggestion:
"""

    try:
        inputs = tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=25,
                temperature=0.5,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 🔥 CLEAN OUTPUT
        cleaned = text.replace(prompt, "").strip()
        cleaned = cleaned.split("\n")[0]

        # 🚨 SAFETY CHECK
        if len(cleaned) < 5 or context_lower in cleaned.lower():
            return "Follow best practices to improve code quality and maintainability."

        return cleaned

    except Exception:
        return "Follow best practices to improve code quality and maintainability."