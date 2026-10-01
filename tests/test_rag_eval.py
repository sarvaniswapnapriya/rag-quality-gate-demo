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
    # Return only qa_009 test case
    # return [tc for tc in data["test_cases"] if tc["id"] == "qa_011"]
    return data["test_cases"]


# OpenAI evaluator for DeepEval
openai_model = OpenAIModel(
    model="gpt-3.5-turbo",
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

    eval_result = evaluate(
        test_cases=[eval_case],
        metrics=metrics,
    )

    # Check if all metrics passed
    # eval_result.test_results is a list of TestResult objects
    for test_result in eval_result.test_results:
        for metric_data in test_result.metrics_data:
            if not metric_data.success:
                raise AssertionError(
                    f"{metric_data.name} failed: "
                    f"score {metric_data.score:.2f} < threshold {metric_data.threshold:.2f}\n"
                    f"Reason: {metric_data.reason}"
                )
