# tests/test_rag_eval.py
"""
DeepEval test suite for the RAG quality gate.
Tests: Faithfulness, Contextual Recall, Answer Relevancy
"""

import pytest
import yaml
from pathlib import Path

from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    FaithfulnessMetric,
    ContextualRecallMetric,
    AnswerRelevancyMetric,
)
from deepeval import evaluate

from src.rag.rag_pipeline import get_pipeline

TEST_CASES_PATH = Path(__file__).parent / "fixtures" / "rag_test_cases.yml"


def load_test_cases():
    with open(TEST_CASES_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data["test_cases"]


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
        FaithfulnessMetric(threshold=0.80),
        ContextualRecallMetric(threshold=0.75),
        AnswerRelevancyMetric(threshold=0.80),
    ]

    evaluate([eval_case], metrics)

    for metric in metrics:
        assert metric.score >= metric.threshold, (
            f"{metric.__class__.__name__} scored {metric.score:.2f}, "
            f"below threshold {metric.threshold} for query: '{test_case['query']}'"
        )
