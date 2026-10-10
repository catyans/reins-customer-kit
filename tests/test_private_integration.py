"""Run locally with the invited Reins checkout installed; public CI skips this file."""

import asyncio
import json
import sys
import threading

import httpx2 as httpx
import pytest
from openai import AsyncOpenAI
from reins import configure, record_outcome, trace
from reins.control import Client, workflow
from reins.control.ledger import Ledger
from reins.control.server import ControlServer
from reins.core.decorators import _get_runtime, shutdown

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
                [
                    module.__name__,
                    "--token-file",
                    str(token_file),
                    "--url",
                    f"http://127.0.0.1:{server.server_port}",
                ],
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
            Workflow(),
            model="example-model",
            prompt="Hello",
            provider_call=provider,
            max_cost="0.01",
        )
    )
    assert result == "Hi"


@pytest.mark.parametrize("answer,accepted", [("approved", True), ("rejected", False)])
def test_observe_existing_async_agent_preserves_behavior_and_records_real_sdk_call(
    tmp_path, answer, accepted
):
    sent, side_effects = [], []

    async def handler(request):
        body = json.loads(request.content)
        sent.append(body)
        return httpx.Response(
            200,
            json={
                "id": "chat_fixture",
                "object": "chat.completion",
                "created": 1,
                "model": body["model"],
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": answer},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 12,
                    "completion_tokens": 3,
                    "total_tokens": 15,
                },
            },
        )

    client = AsyncOpenAI(
        api_key="test-only",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    async def existing_agent(ticket):
        side_effects.append(("start", ticket))
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=32,
            messages=[{"role": "user", "content": f"Review {ticket}"}],
        )
        side_effects.append(("finish", ticket))
        return {"ticket": ticket, "answer": response.choices[0].message.content}

    async def check():
        original = await existing_agent("A-1")
        original_effects = side_effects[:]
        side_effects.clear()
        configure(storage_path=tmp_path / "pilot.duckdb", mode="observe")

        @trace(
            agent_name="ticket_agent",
            task_type="ticket_review",
            policy_version="pilot-v1",
        )
        async def instrumented(ticket):
            result = await existing_agent(ticket)
            record_outcome(success=result["answer"] == "approved")
            return result

        try:
            observed = await instrumented("A-1")
            storage = _get_runtime().storage
            assert observed == original
            assert side_effects == original_effects
            assert sent[0] == sent[1]
            assert len(storage.query("SELECT * FROM runs")) == 1
            assert storage.query("SELECT success FROM outcomes") == [
                {"success": accepted}
            ]
            span = storage.query(
                "SELECT provider, tokens_in, tokens_out, cost FROM spans"
            )[0]
            assert (span["provider"], span["tokens_in"], span["tokens_out"]) == (
                "openai",
                12,
                3,
            )
            assert span["cost"] > 0
        finally:
            shutdown()
            await client.close()

    asyncio.run(check())


def test_native_gemini_example_settles_usage_in_real_control_service(tmp_path):
    token = "x" * 48
    ledger = Ledger(tmp_path / "control.sqlite")
    server = ControlServer(ledger, token, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = Client(f"http://127.0.0.1:{server.server_port}", token=token)
    provider_calls = []

    async def provider(prompt, model):
        provider_calls.append((prompt, model))
        return "approved", "0.003", {"input_tokens": 80, "output_tokens": 12}

    async def check():
        with workflow(
            client=client,
            customer_id="fixture",
            task_type="review",
            budget="0.10",
            mode="observe",
        ) as run:
            answer = await provider_patterns.gemini_explicit_reply(
                run,
                model="example-model",
                prompt="Review ticket",
                provider_call=provider,
                max_cost="0.01",
            )
            run.finish(accepted=answer == "approved")
        assert answer == "approved"
        assert provider_calls == [("Review ticket", "example-model")]
        request = ledger.db.execute(
            "SELECT state, actual, usage FROM requests"
        ).fetchone()
        assert request["state"] == "settled"
        assert request["actual"] == 3000000
        assert json.loads(request["usage"])["output_tokens"] == 12

    try:
        asyncio.run(check())
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
        ledger.close()
