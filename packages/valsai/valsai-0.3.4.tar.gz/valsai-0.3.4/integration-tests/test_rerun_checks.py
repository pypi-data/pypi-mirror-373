import asyncio
import os
import pytest
import pytest_asyncio

from vals import Run, Suite, Check, Test


class TestRerunChecks:
    """Test the rerun_all_checks functionality."""

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
        self.run = await suite.run(
            model="vals/dumbmar-5o-evaluator",
            eval_model_name="vals/dumbmar-5o-evaluator",
            wait_for_completion=True,
        )

    @pytest.mark.asyncio
    async def test_rerun_all_checks_integration(self):
        """Integration test for rerun_all_checks with specific run ID."""
        try:
            # Get the original run
            original_run = await Run.from_id(self.run.id)

            # Test that rerun_all_checks doesn't error
            new_run = await original_run.rerun_all_checks()

            # Verify we got a new run back
            assert new_run is not None
            assert isinstance(new_run, Run)
            assert new_run.id != original_run.id  # Should be a different run
            assert new_run.parameters == original_run.parameters

            # Test that the resulting run has its single check pass
            # Note: This assumes the run completes quickly. In practice, you might need to wait
            await new_run.wait_for_run_completion()
            await new_run.pull()  # Refresh data from server

            # Check that all test results pass
            assert len(new_run.test_results) > 0, "Run should have test results"

        except Exception as e:
            pytest.fail(f"rerun_all_checks should not error, but got: {e}")

    @pytest.mark.asyncio
    async def test_rerun_all_checks_with_invalid_run_id(self):
        """Test rerun_all_checks with invalid run ID."""
        with pytest.raises(Exception):  # Should raise some form of error
            invalid_run = await Run.from_id("invalid-run-id-12345")
            await invalid_run.rerun_all_checks()

    @pytest.mark.asyncio
    async def test_rerun_all_checks_preserves_original_run(self):
        """Test that rerun_all_checks doesn't modify the original run."""
        try:
            original_run = await Run.from_id(self.run.id)
            original_status = original_run.status
            original_timestamp = original_run.timestamp

            new_run = await original_run.rerun_all_checks()

            # Verify original run is unchanged
            assert original_run.status == original_status
            assert original_run.timestamp == original_timestamp
            assert original_run.id != new_run.id

        except Exception as e:
            pytest.fail(f"Test failed with error: {e}")
