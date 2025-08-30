import asyncio
import os
from typing import Any
import pytest
import pytest_asyncio

from vals import Suite, Test, Check, OutputObject


class TestOutputContext:
    """Integration tests for running suites with output context."""

    @pytest_asyncio.fixture(autouse=True)
    async def delay_between_tests(self):
        await asyncio.sleep(5)

    @pytest_asyncio.fixture(autouse=True)
    async def setup_suite(self):
        """Creates a suite and returns it."""
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="OutputObject Feature Demo",
            description="Demonstrates the new OutputObject feature for returning output context",
            tests=[
                Test(
                    input_under_test="What is the capital of France?",
                    checks=[
                        Check(operator="includes", criteria="Processed"),
                        Check(operator="includes", criteria="CAPITAL"),
                    ],
                ),
            ],
        )
        await suite.create()
        self.suite = suite

    @pytest.mark.asyncio
    async def test_simple_model_with_context(self):
        def simple_model_with_context(input_text: str) -> OutputObject:
            """A simple model that returns output with context."""
            # Simulate some processing
            response = f"Processed: {input_text.upper()}"

            output_context = {
                "original_length": len(input_text),
                "processed_length": len(response),
                "transformation": "uppercase",
            }

            return OutputObject(
                llm_output=response,
                output_context=output_context,
                in_tokens=len(input_text.split()),
                out_tokens=len(response.split()),
                duration=0.1,  # simulated duration
            )

        run = await self.suite.run(
            model=simple_model_with_context,
            model_name="simple_output_object_model",
            wait_for_completion=True,
            eval_model_name="vals/dumbmar-5o-evaluator",
        )

        input0 = self.suite.tests[0].input_under_test
        expected_response = f"Processed: {input0.upper()}"
        expected_output_context = {
            "original_length": len(input0),
            "processed_length": len(expected_response),
            "transformation": "uppercase",
        }

        assert run.id
        assert run.test_results[0].llm_output == expected_response
        assert run.test_results[0].output_context == expected_output_context
        assert run.test_results[0].metadata
        assert run.test_results[0].metadata.in_tokens == len(input0.split())
        assert run.test_results[0].metadata.out_tokens == len(expected_response.split())
        assert run.test_results[0].metadata.duration_seconds == 0.1

    @pytest.mark.asyncio
    async def test_rag_model(self):
        # Generate response based on retrieved docs
        response = "Based on the retrieved documents, Paris is the capital of France, which is located in Western Europe."

        # Simulate document retrieval
        retrieved_docs = [
            {"id": "doc1", "text": "Paris is the capital of France.", "score": 0.95},
            {"id": "doc2", "text": "France is in Western Europe.", "score": 0.87},
        ]

        output_context = {
            "retrieved_documents": [doc["id"] for doc in retrieved_docs],
            "retrieval_scores": [doc["score"] for doc in retrieved_docs],
            "excerpts": [doc["text"] for doc in retrieved_docs],
            "retrieval_method": "semantic_search",
        }

        def rag_model(_: str) -> OutputObject:
            """A RAG model that includes retrieved documents in output context."""
            return OutputObject(
                llm_output=response,
                output_context=output_context,
                in_tokens=15,
                out_tokens=20,
                duration=0.5,
            )

        run = await self.suite.run(
            model=rag_model,
            model_name="rag_output_object_model",
            wait_for_completion=True,
            eval_model_name="vals/dumbmar-5o-evaluator",
        )

        assert run.id
        assert run.test_results[0].llm_output == response
        assert run.test_results[0].output_context == output_context
        assert run.test_results[0].metadata
        assert run.test_results[0].metadata.in_tokens == 15
        assert run.test_results[0].metadata.out_tokens == 20
        assert run.test_results[0].metadata.duration_seconds == 0.5

    @pytest.mark.asyncio
    async def test_legacy_model_with_dict(self):
        def legacy_model_with_dict(input_text: str) -> dict[str, Any]:
            """Legacy model that returns a dict - still supported."""
            return {
                "llm_output": f"Legacy response: {input_text}",
                "output_context": {"legacy": True},
                "metadata": {"in_tokens": 10, "out_tokens": 5, "duration_seconds": 0.1},
            }

        run = await self.suite.run(
            model=legacy_model_with_dict,
            model_name="legacy_dict_model",
            wait_for_completion=True,
            eval_model_name="vals/dumbmar-5o-evaluator",
        )

        assert run.id
        assert (
            run.test_results[0].llm_output
            == f"Legacy response: {self.suite.tests[0].input_under_test}"
        )
        assert run.test_results[0].output_context == {"legacy": True}
        assert run.test_results[0].metadata
        assert run.test_results[0].metadata.in_tokens == 10
        assert run.test_results[0].metadata.out_tokens == 5
        assert run.test_results[0].metadata.duration_seconds == 0.1

    @pytest.mark.asyncio
    async def test_legacy_model_with_string(self):
        def legacy_model_with_string(input_text: str) -> str:
            """Legacy model that returns a string - still supported."""
            return f"Simple string response: {input_text}"

        run = await self.suite.run(
            model=legacy_model_with_string,
            model_name="legacy_string_model",
            wait_for_completion=True,
            eval_model_name="vals/dumbmar-5o-evaluator",
        )

        assert run.id
        assert (
            run.test_results[0].llm_output
            == f"Simple string response: {self.suite.tests[0].input_under_test}"
        )
        assert run.test_results[0].output_context == {}
        assert run.test_results[0].metadata
        assert run.test_results[0].metadata.in_tokens == 0
        assert run.test_results[0].metadata.out_tokens == 0
