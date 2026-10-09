"""Run locally with the invited Reins checkout installed; public CI skips this file."""

import sys
import threading

from reins.control.ledger import Ledger
from reins.control.server import ControlServer

from examples import control_task, multi_agent, observe_task, provider_patterns


def test_observe_task_records_outcome(tmp_path, monkeypatch):
    database = tmp_path / "pilot.duckdb"
    monkeypatch.setattr(sys, "argv", ["observe_task", "--database", str(database)])
    observe_task.main()
    assert database.exists()


def test_control_and_multi_agent_examples(tmp_path, monkeypatch, capsys):
    token = "x" * 48
    token_file = tmp_path / "operator.token"
    token_file.write_text(token)
    ledger = Ledger(tmp_path / "control.sqlite")
    server = ControlServer(ledger, token, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for module in (control_task, multi_agent):
            monkeypatch.setattr(
                sys,
                "argv",
                [module.__name__, "--token-file", str(token_file), "--url",
                 f"http://127.0.0.1:{server.server_port}"],
            )
            module.main()
        output = capsys.readouterr().out
        assert "accepted" in output
        assert "workflow_id" in output
        assert len(ledger.console_query({})["workflows"]) == 2
        assert ledger.db.execute("SELECT COUNT(*) FROM requests").fetchone()[0] == 2
        assert ledger.db.execute("SELECT COUNT(*) FROM handoffs").fetchone()[0] == 1
        assert ledger.db.execute("SELECT COUNT(*) FROM shared_state").fetchone()[0] == 1
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
        ledger.close()


def test_gemini_pattern_uses_customer_cost_and_usage():
    import asyncio

    class Workflow:
        async def acall(self, execute, **kwargs):
            output, cost = await execute()
            assert cost == "0.003"
            assert kwargs["usage"] == {"input_tokens": 80, "output_tokens": 12}
            assert kwargs["max_cost"] == "0.01"
            assert kwargs["operation_inputs"]["model"] == "example-model"
            return output

    async def provider(prompt, model):
        assert (prompt, model) == ("Hello", "example-model")
        return "Hi", "0.003", {"input_tokens": 80, "output_tokens": 12}

    result = asyncio.run(
        provider_patterns.gemini_explicit_reply(
            Workflow(), model="example-model", prompt="Hello", provider_call=provider,
            max_cost="0.01"
        )
    )
    assert result == "Hi"
