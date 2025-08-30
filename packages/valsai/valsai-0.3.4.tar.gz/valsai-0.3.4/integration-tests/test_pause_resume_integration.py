import asyncio
import os
import time
import pytest
from vals import (
    Suite,
    Test,
    Check,
    Run,
)
from vals.graphql_client import RunStatus


class TestPauseResumeIntegration:
    """Integration tests for pausing and resuming runs."""

    @pytest.mark.asyncio
    async def test_pause_and_resume_run(self):
        """Run the suite and then pause."""
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

        def slow_model(input_under_test: str):
            time.sleep(5)
            return input_under_test + "!!!"

        await suite.create()

        run = await suite.run(
            model=slow_model, eval_model_name="vals/dumbmar-5o-evaluator"
        )

        try:
            await run.pause_run()
        except Exception as e:
            pytest.fail(f"run.pause() raise unexpectedly: {e}")

        await wait_for_status(run, RunStatus.PAUSE)

        await run.resume_run(model=slow_model, wait_for_completion=True)

        await run.run_status()

        assert run.status == RunStatus.SUCCESS


async def wait_for_status(
    run: Run,
    target_status: RunStatus,
    max_wait_time: float = 5,
) -> None:
    """Wait until `run.status == target_status`, or fail the pytest test."""
    start_time = time.time()

    while run.status != target_status:
        if time.time() - start_time > max_wait_time:
            pytest.fail(
                f"Never reached {target_status} state. Last status: {run.status}"
            )
        await run.run_status()
        await asyncio.sleep(1)
