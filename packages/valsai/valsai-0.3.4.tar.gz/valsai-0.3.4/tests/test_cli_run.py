import pytest
from click.testing import CliRunner

from vals.graphql_client.enums import RunStatus


class DummyRun:
    def __init__(self, run_id: str, initial_status: RunStatus):
        self.id = run_id
        self.status = initial_status

    async def pause_run(self):
        self.status = RunStatus.PAUSE

    async def cancel_run(self):
        self.status = RunStatus.CANCELLED

    async def run_status(self):
        return self.status


@pytest.mark.parametrize(
    "command, initial_status, expected, unexpected, run_id",
    [
        ("cancel", RunStatus.PENDING, "cancelled successfully", "pausing", "run-123"),
        (
            "pause",
            RunStatus.IN_PROGRESS,
            "paused successfully",
            "cancelling",
            "run-abc",
        ),
    ],
)
def test_run_pause_cancel_commands(
    monkeypatch, command, initial_status, expected, unexpected, run_id
):
    from vals.cli import run as run_cli

    async def fake_from_id(rid: str):
        return DummyRun(rid, initial_status)

    monkeypatch.setattr(run_cli.Run, "from_id", staticmethod(fake_from_id))

    runner = CliRunner()
    result = runner.invoke(run_cli.run_group, [command, "-r", run_id])  # type: ignore[arg-type]

    assert result.exit_code == 0
    out = result.output.lower()
    assert expected in out
    assert unexpected not in out


@pytest.mark.parametrize(
    "command, initial_status, run_id",
    [
        ("pause", RunStatus.PAUSE, "run-ppp"),
        ("cancel", RunStatus.CANCELLED, "run-ccc"),
    ],
)
def test_run_pause_cancel_already_state(monkeypatch, command, initial_status, run_id):
    from vals.cli import run as run_cli

    class DummyRun:
        def __init__(self, rid: str):
            self.id = rid
            self.status = initial_status

    async def fake_from_id(rid: str):
        return DummyRun(rid)

    monkeypatch.setattr(run_cli.Run, "from_id", staticmethod(fake_from_id))

    runner = CliRunner()
    res = runner.invoke(run_cli.run_group, [command, "-r", run_id])  # type: ignore[arg-type]
    assert res.exit_code == 0
    out = res.output.lower()
    assert "already" in out


def test_resume_command_runs_resume_and_messages(monkeypatch):
    from vals.cli import run as run_cli

    class DummyRun:
        def __init__(self, run_id: str):
            self.id = run_id

        async def resume_run(self):
            return None

    async def fake_from_id(rid: str):
        return DummyRun(rid)

    monkeypatch.setattr(run_cli.Run, "from_id", staticmethod(fake_from_id))

    runner = CliRunner()
    res = runner.invoke(run_cli.run_group, ["resume", "-r", "run-xyz"])  # type: ignore[arg-type]
    assert res.exit_code == 0
    assert "resumed successfully" in res.output.lower()


@pytest.mark.parametrize(
    "flags, expected_text, is_csv",
    [(["--csv"], "csvdata", True), ([], "jsondata", False)],
)
def test_pull_writes_file_and_message(
    monkeypatch, tmp_path, flags, expected_text, is_csv
):
    from vals.cli import run as run_cli

    class DummyRun:
        def __init__(self, run_id: str):
            self.id = run_id

        async def to_csv_string(self):
            return "csvdata"

        async def to_json_string(self):
            return "jsondata"

    async def fake_from_id(rid: str):
        return DummyRun(rid)

    monkeypatch.setattr(run_cli.Run, "from_id", staticmethod(fake_from_id))

    out_file = tmp_path / "out.txt"
    args = ["pull", "-r", "run-1", "-f", str(out_file)] + flags
    runner = CliRunner()
    res = runner.invoke(run_cli.run_group, args)  # type: ignore[arg-type]

    assert res.exit_code == 0
    assert "successfully pulled run results" in res.output.lower()
    text = out_file.read_text()
    assert expected_text in text


def test_list_outputs_rows(monkeypatch):
    from datetime import datetime

    from vals.cli import run as run_cli

    class Row:
        def __init__(self, i):
            self.name = f"Run {i}"
            self.id = f"id-{i}"
            self.status = RunStatus.PENDING if i == 1 else RunStatus.SUCCESS
            self.model = "gpt-x"
            self.pass_rate = 97.5 if i == 2 else None
            self.timestamp = datetime(2024, 1, 1, 12, 0, 0)

    async def fake_list_runs(
        limit, offset, suite_id, show_archived, search, project_id
    ):
        return [Row(1), Row(2)]

    monkeypatch.setattr(run_cli.Run, "list_runs", staticmethod(fake_list_runs))

    runner = CliRunner()
    res = runner.invoke(run_cli.run_group, ["list"])  # type: ignore[arg-type]

    assert res.exit_code == 0
    out = res.output
    assert "Listing runs for project: default-project" in out
    assert "Run 1" in out and "id-1" in out
    assert "Run 2" in out and "id-2" in out
