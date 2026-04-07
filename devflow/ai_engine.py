from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import warnings

warnings.filterwarnings("ignore")

# -------------------------------
# Load model manually (NO pipeline)
# -------------------------------
model_name = "distilgpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

model.eval()


def generate_ai_suggestion(context):
    """
    Generate clean AI suggestion (controlled)
    """

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
                max_new_tokens=30,
                temperature=0.6,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 🔥 CLEAN OUTPUT
        cleaned = text.replace(prompt, "").strip()
        cleaned = cleaned.split("\n")[0]

        # fallback safety
        if len(cleaned) < 5 or context.lower() in cleaned.lower():
            return "Use clear and meaningful practices to improve code quality."

        return cleaned

    except Exception:
        return "AI suggestion unavailable."