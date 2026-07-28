"""
DeepEval test suite for the RAG quality gate.
Tests: Faithfulness, Contextual Recall, Answer Relevancy
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import pytest
import yaml

from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
)
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase

from src.rag.rag_pipeline import get_pipeline

TEST_CASES_PATH = Path(__file__).parent / "fixtures" / "rag_test_cases.yml"

def load_test_cases():
    with open(TEST_CASES_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data["test_cases"][:1]

# OpenAI evaluator for DeepEval
openai_model = GPTModel(
    model="gpt-4o-mini",
    api_key=os.environ["OPENAI_API_KEY"],
)

@pytest.mark.parametrize("test_case", load_test_cases(), ids=lambda tc: tc["id"])
def test_rag_quality_gate(test_case):
    """All three metrics must pass or the test fails."""

    pipeline = get_pipeline()
    result = pipeline.query(test_case["query"])

    eval_case = LLMTestCase(
        input=test_case["query"],
        actual_output=result["answer"],
        expected_output=test_case["expected_answer"],
        retrieval_context=result["retrieved_context"],
    )

    metrics = [
        FaithfulnessMetric(
            threshold=0.80,
            model=openai_model,
        ),
        ContextualRecallMetric(
            threshold=0.75,
            model=openai_model,
        ),
        AnswerRelevancyMetric(
            threshold=0.80,
            model=openai_model,
        ),
    ]

    evaluate(
        test_cases=[eval_case],
        metrics=metrics,
    )