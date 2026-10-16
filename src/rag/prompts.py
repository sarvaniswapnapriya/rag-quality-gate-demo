# src/rag/prompts.py
"""
System prompts for the RAG pipeline.
This is what engineers edit most often - and what the quality gate protects.
"""

import os

BASELINE_PROMPT = """You are a helpful customer support assistant.
Answer the user's question based on the provided context.
If the context doesn't contain the answer, say "I don't know" rather than making something up.

Context:
{context}

Question: {question}

Answer:"""

CANDIDATE_PROMPT = """You are a customer support assistant with a casual, humorous tone.
Your goal is to entertain the customer while addressing their problem.
Feel free to add jokes and witty comments to your responses.
Try to keep answers brief and fun rather than comprehensive.
When answering, focus on the general idea of the question rather than the specific details in the provided context. Use your own knowledge and conversational style to make the response more engaging.


Context:
{context}

Question: {question}

Answer:"""

# Pick the prompt at run time with RAG_PROMPT=baseline (default) or RAG_PROMPT=candidate.
# The Testkube workflow sets RAG_PROMPT from its "prompt" config value,
# so both prompts run from the same workflow without editing this file.
PROMPTS = {
    "baseline": BASELINE_PROMPT,
    "candidate": CANDIDATE_PROMPT,
}

_choice = os.getenv("RAG_PROMPT", "baseline").strip().lower()
if _choice not in PROMPTS:
    raise ValueError(f"RAG_PROMPT must be 'baseline' or 'candidate', got {_choice!r}")

ACTIVE_PROMPT = PROMPTS[_choice]
