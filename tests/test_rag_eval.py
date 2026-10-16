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
from deepeval.models import OpenAIModel
from deepeval.test_case import LLMTestCase

from src.rag.rag_pipeline import get_pipeline

TEST_CASES_PATH = Path(__file__).parent / "fixtures" / "rag_test_cases.yml"


def load_test_cases():
    with open(TEST_CASES_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data["test_cases"]


# OpenAI judge model for DeepEval
openai_model = OpenAIModel(
    model="gpt-3.5-turbo",
    api_key=os.environ["OPENAI_API_KEY"],
)


@pytest.fixture
def eval_result(test_case):
    """Ask the RAG bot the question and score its answer with DeepEval.

    This runs in a fixture on purpose. If the RAG call or the judge model
    breaks here, pytest marks the case as errored. A low score is checked
    in the test itself, so it shows up as failed.
    """
    pipeline = get_pipeline()
    result = pipeline.query(test_case["query"])

    eval_case = LLMTestCase(
        input=test_case["query"],
        actual_output=result["answer"],
        expected_output=test_case["expected_answer"],
        retrieval_context=result["retrieved_context"],
    )

    metrics = [
        FaithfulnessMetric(threshold=0.80, model=openai_model),
        ContextualRecallMetric(threshold=0.75, model=openai_model),
        AnswerRelevancyMetric(threshold=0.80, model=openai_model),
    ]

    return evaluate(test_cases=[eval_case], metrics=metrics)


@pytest.mark.parametrize("test_case", load_test_cases(), ids=lambda tc: tc["id"])
def test_rag_quality_gate(test_case, eval_result):
    """All three metrics must pass or the test fails."""
    failed = [
        metric
        for test_result in eval_result.test_results
        for metric in test_result.metrics_data
        if not metric.success
    ]
    if failed:
        raise AssertionError(
            "\n".join(
                f"{m.name} failed: score {m.score:.2f} < threshold {m.threshold:.2f}\n"
                f"Reason: {m.reason}"
                for m in failed
            )
        )
