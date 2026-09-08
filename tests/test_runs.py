from types import SimpleNamespace

from app.tools import runs

# Test1
## Tests that a new agent run starts in running state.
def test_create_agent_run(monkeypatch):
    saved = {}

    class FakeSession:
        def add(self, obj):
            saved["object"] = obj

        def commit(self):
            saved["committed"] = True

        def refresh(self, obj):
            obj.id = 42

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

    monkeypatch.setattr(
        runs,
        "SessionLocal",
        lambda: FakeSession(),
    )

    run_id = runs.create_agent_run(
        user_message="Investigate ticket 2.",
    )

    run = saved["object"]

    assert run_id == 42
    assert run.ticket_id is None
    assert (
        run.user_message
        == "Investigate ticket 2."
    )
    assert run.final_response is None
    assert run.status == "running"
    assert saved["committed"] is True

# Test 2
## Tests that an existing agent run can be completed.
def test_complete_agent_run(monkeypatch):
    fake_run = SimpleNamespace(
        id=42,
        ticket_id=None,
        user_message="Investigate ticket 2.",
        final_response=None,
        status="running",
    )

    class FakeSession:
        def scalar(self, query):
            return fake_run

        def commit(self):
            pass

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

    monkeypatch.setattr(
        runs,
        "SessionLocal",
        lambda: FakeSession(),
    )

    runs.complete_agent_run(
        run_id=42,
        final_response=(
            "Escalation proposed."
        ),
        status="completed",
        ticket_id=2,
    )

    assert fake_run.final_response == (
        "Escalation proposed."
    )
    assert fake_run.status == "completed"
    assert fake_run.ticket_id == 2

# Test3
## Tests that completing a missing run does nothing.
def test_complete_agent_run_missing(
    monkeypatch,
):
    class FakeSession:
        def scalar(self, query):
            return None

        def commit(self):
            raise AssertionError(
                "commit should not be called"
            )

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

    monkeypatch.setattr(
        runs,
        "SessionLocal",
        lambda: FakeSession(),
    )

    result = runs.complete_agent_run(
        run_id=9999,
        final_response="Test response.",
        status="completed",
    )

    assert result is None

# Test 4
## Tests that a failed agent run is marked as failed.
def test_fail_agent_run(monkeypatch):
    fake_run = SimpleNamespace(
        id=42,
        ticket_id=None,
        user_message="Investigate ticket.",
        final_response=None,
        status="running",
    )

    class FakeSession:
        def scalar(self, query):
            return fake_run

        def commit(self):
            pass

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

    monkeypatch.setattr(
        runs,
        "SessionLocal",
        lambda: FakeSession(),
    )

    runs.fail_agent_run(
        run_id=42,
        final_response="Agent execution failed.",
    )

    assert fake_run.status == "failed"
    assert (
        fake_run.final_response
        == "Agent execution failed."
    )
