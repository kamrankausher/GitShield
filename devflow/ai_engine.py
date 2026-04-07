from transformers import pipeline

# Load model once
generator = pipeline(
    "text-generation",
    model="distilgpt2",
    pad_token_id=50256
)


def generate_ai_suggestion(context):
    """
    Generate clean AI suggestion
    """

    prompt = f"""
You are a senior software engineer mentor.

Problem: {context}

Give a short, clear, professional suggestion in 1-2 lines:
"""

    try:
        result = generator(
            prompt,
            max_new_tokens=40,   # ✅ FIXED (no max_length)
            do_sample=True,
            temperature=0.7
        )

        text = result[0]["generated_text"]

        # 🔥 CLEAN OUTPUT (IMPORTANT)
        cleaned = text.replace(prompt, "").strip()

        # Remove extra noise
        cleaned = cleaned.split("\n")[0]

        return cleaned

    except Exception as e:
        return f"AI Error: {e}"