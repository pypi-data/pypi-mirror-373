import asyncio
import os
from pathlib import Path
import pytest
import pytest_asyncio
from vals import (
    Check,
    Suite,
    Test,
)
from vals.graphql_client import GraphQLClientGraphQLMultiError
from vals.sdk.types import File


class TestSuiteIntegration:
    """Integration tests for interacting with suites using sdk."""

    @pytest_asyncio.fixture(autouse=True)
    async def delay_between_tests(self):
        await asyncio.sleep(5)

    @pytest.mark.asyncio
    async def test_create_suite(self):
        """Create a single, basic test suite."""
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            global_checks=[Check(operator="grammar")],
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
                Test(
                    input_under_test="What is an 83 election?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
            ],
        )
        await suite.create()

        assert suite.id

        suite_from_server = await Suite.from_id(suite.id)
        assert suite_from_server.title == "Test Suite"
        assert suite_from_server.global_checks[0].operator == "grammar"

        assert suite_from_server.tests[0].input_under_test == "What is QSBS?"
        assert suite_from_server.tests[0].checks[0].operator == "equals"
        assert suite_from_server.tests[0].checks[0].criteria == "QSBS"

        assert suite_from_server.tests[1].input_under_test == "What is an 83 election?"
        assert suite_from_server.tests[1].checks[0].operator == "equals"
        assert suite_from_server.tests[1].checks[0].criteria == "QSBS"

    @pytest.mark.asyncio
    async def test_create_suite_with_files(self):
        """
        Create a test suite that has a file upload as part of the test input.
        """
        test_dir = Path(__file__).parent.parent

        file_path = test_dir / "examples" / "data_files" / "postmoney_safe.docx"
        files_under_test = [str(file_path)]

        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite",
            global_checks=[Check(operator="grammar")],
            tests=[
                Test(
                    input_under_test="What is the MFN clause?",
                    files_under_test=files_under_test,
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
            ],
        )
        await suite.create()

        assert suite.id

        suite_from_server = await Suite.from_id(suite.id)
        assert suite_from_server.title == "Test Suite"
        assert suite_from_server.global_checks[0].operator == "grammar"

        assert suite_from_server.tests[0].input_under_test == "What is the MFN clause?"

        uploaded_file = suite_from_server.tests[0].files_under_test[0]
        assert isinstance(uploaded_file, File)
        assert uploaded_file.file_name == file_path.name

        assert suite_from_server.tests[0].checks[0].operator == "equals"
        assert suite_from_server.tests[0].checks[0].criteria == "QSBS"

    @pytest.mark.asyncio
    async def test_create_and_delete_suite(self):
        """Create a suite, then delete it."""
        suite = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Test Suite to Delete",
            global_checks=[Check(operator="grammar")],
        )
        await suite.create()

        assert suite.id

        await suite.delete()

        with pytest.raises(GraphQLClientGraphQLMultiError) as exc_info:
            print(await Suite.from_id(suite.id))

        assert "not found" in exc_info.exconly()

    @pytest.mark.asyncio
    async def test_load_from_json(self):
        """Create a suite from a json file."""
        test_dir = Path(__file__).parent.parent
        file_path = test_dir / "examples" / "suites" / "example_suite.json"
        suite = await Suite.from_json_file(str(file_path))

        await suite.create()

        assert suite.id

        pulled_suite = await Suite.from_id(suite.id)

        assert pulled_suite.title == "[VALS]: Sample Test Suite"
        assert pulled_suite.description == "Test description"
        assert pulled_suite.tests[0].input_under_test == "What is QSBS"
        assert pulled_suite.tests[0].checks[0].operator == "includes"
        assert pulled_suite.tests[0].checks[0].criteria == "C Corporation"
        assert pulled_suite.tests[0].checks[1].operator == "excludes"
        assert pulled_suite.tests[0].checks[1].criteria == "S Corporation"

    @pytest.mark.asyncio
    async def test_move_test_between_suites(self):
        suite1 = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Suite 1",
            tests=[
                Test(
                    input_under_test="What is QSBS?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                )
            ],
        )
        await suite1.create()

        assert suite1.id

        suite2 = Suite(
            project_id=os.getenv("PROJECT_SLUG", "default-project"),
            title="Suite 2",
            tests=[
                Test(
                    input_under_test="What is an 83 election?",
                    checks=[Check(operator="equals", criteria="QSBS")],
                ),
                suite1.tests[0],
            ],
        )
        await suite2.create()

        assert suite2.id

        pulled_suite1 = await Suite.from_id(suite1.id)
        pulled_suite2 = await Suite.from_id(suite2.id)

        assert pulled_suite1.title == "Suite 1"
        assert pulled_suite2.title == "Suite 2"

        assert pulled_suite1.tests[0].input_under_test == "What is QSBS?"
        assert pulled_suite1.tests[0].checks[0].operator == "equals"
        assert pulled_suite1.tests[0].checks[0].criteria == "QSBS"

        assert pulled_suite2.tests[1].input_under_test == "What is QSBS?"
        assert pulled_suite2.tests[1].checks[0].operator == "equals"
        assert pulled_suite2.tests[1].checks[0].criteria == "QSBS"

        assert pulled_suite2.tests[0].input_under_test == "What is an 83 election?"
        assert pulled_suite2.tests[0].checks[0].operator == "equals"
        assert pulled_suite2.tests[0].checks[0].criteria == "QSBS"
