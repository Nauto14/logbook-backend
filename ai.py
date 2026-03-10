import os
import json
from typing import List, Optional
from openai import OpenAI

# ─── Configuration ────────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = os.environ.get("AI_MODEL", "gpt-4o-mini")

def query_experiments(question: str, experiments: List[dict]) -> dict:
    """
    Send a user question + experiment context to the LLM.
    Returns { answer: str, referenced_experiments: list[str] }
    """
    if not OPENAI_API_KEY:
        return {
            "answer": "AI assistant is not configured. Please set the OPENAI_API_KEY environment variable on the backend server.",
            "referenced_experiments": [],
        }

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Build context from experiments
    experiment_context = ""
    for i, exp in enumerate(experiments, 1):
        experiment_context += f"\n--- Experiment #{i} ---\n"
        for key, value in exp.items():
            if value and str(value).strip():
                experiment_context += f"  {key}: {value}\n"

    system_prompt = """You are a scientific research assistant for an experimental physics logbook.
You help researchers analyze and query their experiment data.
You have access to the researcher's experiment logs provided below.

When answering questions:
1. Be precise and cite specific experiment IDs when referring to data.
2. If asked to count or filter, be thorough and accurate.
3. If asked to summarize, focus on scientific conclusions and key findings.
4. Format your responses clearly with bullet points or numbered lists when appropriate.
5. If the data doesn't contain enough information to answer, say so clearly.

Always return valid information based ONLY on the provided experiment data."""

    user_prompt = f"""Here are the researcher's experiment logs:

{experiment_context}

---
User question: {question}

Please answer based on the experiment data above. Reference specific experiment IDs in your answer."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        answer = response.choices[0].message.content or "No response generated."

        # Extract referenced experiment IDs
        referenced = []
        for exp in experiments:
            exp_id = exp.get("experiment_id", "")
            if exp_id and exp_id in answer:
                referenced.append(exp_id)

        return {
            "answer": answer,
            "referenced_experiments": referenced,
        }

    except Exception as e:
        return {
            "answer": f"Error communicating with AI service: {str(e)}",
            "referenced_experiments": [],
        }
