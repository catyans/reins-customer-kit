"""Minimal pre-Reins customer function; provider is an injected async callable."""


async def handle_ticket(message: str, policy: str, provider):
    prompt = f"Draft a reply using this policy: {policy}\nCustomer: {message}"
    response = await provider(prompt)
    return response["output"]
