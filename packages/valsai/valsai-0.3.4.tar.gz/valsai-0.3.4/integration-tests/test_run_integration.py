import asyncio
from io import BytesIO
import os
from pathlib import Path
from typing import Any
import pytest
import pytest_asyncio

from vals import (
    Check,
    Suite,
    RunParameters,
    QuestionAnswerPair,
    Test,
)
from vals.sdk.types import Confidence, OperatorInput, OperatorOutput
from vals.graphql_client.enums import RunStatus


class TestRunIntegration:
    """Integration tests for running test suites."""

    @pytest_asyncio.fixture(autouse=True)
    async def delay_between_tests(self):
        await asyncio.sleep(5)

    @pytest.mark.asyncio
    async def test_run_with_model_under_test(self):
        """Run the suite on a stock model, vals/dumbmar-5o-evaluator"""
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            global_checks=[Check(operator="grammar")],
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
            ],
        )
        await suite.create()
        run = await suite.run(
            model="vals/dumbmar-5o-evaluator",
            eval_model_name="vals/dumbmar-5o-evaluator",
            wait_for_completion=True,
        )

        assert run.model == "vals/dumbmar-5o-evaluator"
        assert run.parameters.eval_model == "vals/dumbmar-5o-evaluator"
        assert run.test_suite_id == suite.id
        assert run.test_results[0].input_under_test == "What is QSBS?"
        assert run.status == RunStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_run_with_function(self):
        """Run the suite on a custom model function."""
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
            ],
        )
        await suite.create()

        def function(input_under_test: str) -> str:
            # This would be replaced with your custom model.
            return input_under_test + "!!!"

        run = await suite.run(
            model=function,
            wait_for_completion=True,
            model_name="my_function_model",
            eval_model_name="vals/dumbmar-5o-evaluator",
        )

        assert run.model == "my_function_model"
        assert run.parameters.eval_model == "vals/dumbmar-5o-evaluator"
        assert run.test_suite_id == suite.id
        assert run.test_results[0].input_under_test == "What is QSBS?"
        assert run.test_results[0].llm_output == "What is QSBS?!!!"
        assert run.status == RunStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_run_with_local_eval(self):
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            global_checks=[Check(operator="grammar")],
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
            ],
        )
        await suite.create()

        async def custom_operator(_: OperatorInput) -> OperatorOutput:
            return OperatorOutput(
                name="my_custom_operator_1", score=1, explanation="Hello, world!"
            )

        async def custom_operator2(_: OperatorInput) -> OperatorOutput:
            return OperatorOutput(
                name="my_custom_operator_2", score=0.5, explanation="Goodbye, world!"
            )

        async def custom_model(input: str) -> str:
            return input + "!!!"

        run = await suite.run(
            model=custom_model,
            wait_for_completion=True,
            model_name="my_function_model",
            eval_model_name="vals/dumbmar-5o-evaluator",
            parameters=RunParameters(parallelism=3),
            custom_operators=[custom_operator, custom_operator2],
        )

        assert run.model == "my_function_model"
        assert run.parameters.eval_model == "vals/dumbmar-5o-evaluator"
        assert run.test_suite_id == suite.id
        assert run.test_results[0].input_under_test == "What is QSBS?"
        assert run.test_results[0].llm_output == "What is QSBS?!!!"

        run_test_result = run.test_results[0]

        assert run_test_result.check_results[0].operator == "equals"
        assert not run_test_result.check_results[0].is_global

        assert run_test_result.check_results[1].operator == "grammar"
        assert run_test_result.check_results[1].is_global

        assert run_test_result.check_results[2].auto_eval == 1
        assert run_test_result.check_results[2].feedback == "Hello, world!"
        assert (
            run_test_result.check_results[2].confidence == Confidence.CONFIDENCE_NOT_RUN
        )
        assert not run_test_result.check_results[2].is_global
        assert run_test_result.check_results[2].operator == "my_custom_operator_1"

        assert run_test_result.check_results[3].auto_eval == 0.5
        assert run_test_result.check_results[3].feedback == "Goodbye, world!"
        assert (
            run_test_result.check_results[3].confidence == Confidence.CONFIDENCE_NOT_RUN
        )
        assert not run_test_result.check_results[3].is_global
        assert run_test_result.check_results[3].operator == "my_custom_operator_2"

        assert run.status == RunStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_run_with_custom_parameters(self):
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            global_checks=[Check(operator="grammar")],
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
            ],
        )
        await suite.create()

        run = await suite.run(
            model="vals/dumbmar-5o-evaluator",
            eval_model_name="vals/dumbmar-5o-evaluator",
            wait_for_completion=True,
            parameters=RunParameters(
                parallelism=3, max_output_tokens=2048, custom_parameters={"top_p": 0.5}
            ),
            except_on_error=True,
        )

        assert run.model == "vals/dumbmar-5o-evaluator"
        assert run.parameters.eval_model == "vals/dumbmar-5o-evaluator"
        assert run.test_suite_id == suite.id
        assert run.test_results[0].input_under_test == "What is QSBS?"
        assert run.parameters.parallelism == 3
        assert run.parameters.max_output_tokens == 2048
        assert run.parameters.custom_parameters["top_p"] == 0.5
        assert run.status == RunStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_run_with_custom_parameters_and_function(self):
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            global_checks=[Check(operator="grammar")],
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
            ],
        )
        await suite.create()

        def my_function(input: str) -> str:
            return input + "!!!"

        run = await suite.run(
            model=my_function,
            eval_model_name="vals/dumbmar-5o-evaluator",
            wait_for_completion=True,
            parameters=RunParameters(
                parallelism=3,
                max_output_tokens=2048,
                custom_parameters={
                    "number_of_documents_to_retrieve": 10,
                },
            ),
        )

        assert run.model == "sdk"
        assert run.parameters.eval_model == "vals/dumbmar-5o-evaluator"
        assert run.test_suite_id == suite.id
        assert run.test_results[0].input_under_test == "What is QSBS?"
        assert run.test_results[0].llm_output == "What is QSBS?!!!"
        assert run.parameters.parallelism == 3
        assert run.parameters.max_output_tokens == 2048
        assert run.parameters.custom_parameters["number_of_documents_to_retrieve"] == 10
        assert run.status == RunStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_run_with_function_context_and_files(self):
        """Run the suite with context and files."""
        context = {
            "message_history": [
                {"role": "user", "content": "What is QSBS?"},
                {"role": "assistant", "content": "QSBS is a company."},
            ]
        }
        test_dir = Path(__file__).parent.parent

        file_path = test_dir / "examples" / "data_files" / "postmoney_safe.docx"
        files_under_test = [str(file_path)]

        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                    context=context,
                    files_under_test=files_under_test,
                ),
            ],
        )
        await suite.create()

        def function(
            input_under_test: str, files: dict[str, BytesIO], context: dict[str, Any]
        ) -> str:
            return input_under_test + "".join(files.keys()) + str(context)

        run = await suite.run(
            model=function,
            wait_for_completion=True,
            model_name="my_function_model_v2",
            eval_model_name="vals/dumbmar-5o-evaluator",
        )

        assert run.model == "my_function_model_v2"
        assert run.parameters.eval_model == "vals/dumbmar-5o-evaluator"
        assert run.test_suite_id == suite.id
        assert run.test_results[0].input_under_test == "What is QSBS?"
        assert run.test_results[0].llm_output == "What is QSBS?" + file_path.name + str(
            context
        )
        assert run.status == RunStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_run_with_qa_pairs(self):
        """Run the suite with QA pairs."""
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            global_checks=[Check(operator="grammar")],
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
            ],
        )

        await suite.create()

        qa_pairs = [
            QuestionAnswerPair(input_under_test="What is QSBS?", llm_output="QSBS")
        ]

        run = await suite.run(
            model=qa_pairs,
            model_name="test-model",
            wait_for_completion=True,
            eval_model_name="vals/dumbmar-5o-evaluator",
        )

        assert run.model == "test-model"
        assert run.parameters.eval_model == "vals/dumbmar-5o-evaluator"
        assert run.test_suite_id == suite.id
        assert run.test_results[0].input_under_test == "What is QSBS?"
        assert run.test_results[0].llm_output == "QSBS"
        assert run.status == RunStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_run_with_qa_pairs_and_context(self):
        """Run the suite with QA pairs and context."""
        context = {
            "message_history": [
                {"role": "user", "content": "What is QSBS?"},
                {"role": "assistant", "content": "QSBS is a company."},
            ]
        }
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            global_checks=[Check(operator="grammar")],
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                    context=context,
                ),
            ],
        )

        await suite.create()

        qa_pairs = [
            QuestionAnswerPair(
                input_under_test="What is QSBS?", llm_output="QSBS", context=context
            )
        ]

        run = await suite.run(
            model=qa_pairs,
            model_name="test-model",
            wait_for_completion=True,
            eval_model_name="vals/dumbmar-5o-evaluator",
        )

        assert run.model == "test-model"
        assert run.parameters.eval_model == "vals/dumbmar-5o-evaluator"
        assert run.test_suite_id == suite.id
        assert run.test_results[0].input_under_test == "What is QSBS?"
        assert run.test_results[0].llm_output == "QSBS"
        assert run.test_results[0].context == context
        assert run.status == RunStatus.SUCCESS
