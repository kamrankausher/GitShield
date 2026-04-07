from transformers import pipeline

# 🔥 Load once globally (IMPORTANT)
generator = pipeline("text-generation", model="distilgpt2")


def generate_ai_suggestion(context):

    prompt = f"""
You are an expert software engineer mentor.

Issue:
{context}

Give short and clear suggestion:
"""

    try:
        result = generator(
            prompt,
            max_length=60,
            num_return_sequences=1,
            do_sample=True
        )

        return result[0]["generated_text"]

    except Exception as e:
        return f"AI Error: {e}"