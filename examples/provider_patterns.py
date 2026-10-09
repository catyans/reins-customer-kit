"""Customer-side provider patterns; no keys or paid calls are made by this file.

Pass already-configured clients or a customer-owned Gemini adapter. Replace the
example acceptance checks with your business rules before a pilot.
"""

from hashlib import sha256

from reins import record_outcome, trace


@trace(agent_name="openai_agent", task_type="text_reply", policy_version="observe-v1")
async def openai_reply(client, *, model: str, prompt: str) -> str:
    """client: an existing openai.AsyncOpenAI instance using Chat Completions."""
    response = await client.chat.completions.create(
        model=model,
        max_completion_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content or ""
    record_outcome(success=bool(text.strip()))  # Replace with business acceptance.
    return text


@trace(agent_name="anthropic_agent", task_type="text_reply", policy_version="observe-v1")
async def anthropic_reply(client, *, model: str, prompt: str) -> str:
    """client: an existing anthropic.AsyncAnthropic instance using Messages."""
    response = await client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    record_outcome(success=bool(text.strip()))  # Replace with business acceptance.
    return text


async def gemini_explicit_reply(
    run, *, model: str, prompt: str, provider_call, max_cost: str
) -> str:
    """provider_call(prompt, model) -> (text, actual_usd_cost, usage_dict).

    The customer adapter computes actual cost from returned usage and verified
    rates. `run` is an existing reins.control.Workflow in observe mode first.
    """
    usage = {}

    async def execute():
        text, cost, counts = await provider_call(prompt, model)
        usage.update(counts)
        return {"text": text}, cost

    output = await run.acall(
        execute,
        model=f"google/{model}",
        category="model",
        max_cost=max_cost,  # A complete upper bound, including provider retries.
        operation_inputs={"prompt_sha256": sha256(prompt.encode()).hexdigest(), "model": model},
        usage=usage,
        price_version="customer-verified-rates-v1",
        cost_reference="Customer-maintained Gemini rates",
    )
    return output["text"]
