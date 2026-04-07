from transformers import pipeline

# Load lightweight model
generator = pipeline("text-generation", model="distilgpt2")


def generate_ai_suggestion(context):

    prompt = f"""
You are an expert software engineer mentor.

Issue:
{context}

Provide:
1. Better suggestion
2. Explanation
"""

    try:
        result = generator(prompt, max_length=80, num_return_sequences=1)
        return result[0]["generated_text"]
    except Exception as e:
        return f"AI Error: {e}"