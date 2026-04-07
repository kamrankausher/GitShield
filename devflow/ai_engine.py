from transformers import pipeline, set_seed
import warnings

# 🔕 Suppress transformers warnings (IMPORTANT)
warnings.filterwarnings("ignore")

# 🔥 Load model ONCE
generator = pipeline(
    "text-generation",
    model="distilgpt2",
    pad_token_id=50256
)

# Optional (stable output)
set_seed(42)


def generate_ai_suggestion(context):
    """
    Generate clean, short AI suggestion
    """

    prompt = f"""
You are a senior software engineer.

Problem: {context}

Give ONLY one short professional suggestion:
"""

    try:
        result = generator(
            prompt,
            max_new_tokens=30,   # ✅ only this (NO max_length)
            do_sample=True,
            temperature=0.6,
            top_k=50
        )

        text = result[0]["generated_text"]

        # 🔥 CLEAN OUTPUT
        cleaned = text.replace(prompt, "").strip()

        # Take only first meaningful line
        cleaned = cleaned.split("\n")[0]

        # Fallback if bad output
        if len(cleaned) < 5 or context in cleaned:
            return "Use clear and descriptive practices to improve code quality."

        return cleaned

    except Exception:
        return "AI suggestion unavailable."