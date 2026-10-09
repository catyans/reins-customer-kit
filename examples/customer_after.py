"""Same business output with an explicit Reins paid-call boundary."""


async def handle_ticket(message: str, policy: str, provider, workflow, *, max_cost: str):
    prompt = f"Draft a reply using this policy: {policy}\nCustomer: {message}"
    usage = {}

    async def execute():
        response = await provider(prompt)
        usage.update(response["usage"])
        return response["output"], response["cost_usd"]

    workflow.progress("Drafting reply", 0, 1)
    output = await workflow.acall(
        execute,
        model="customer-provider/customer-model",
        category="model",
        max_cost=max_cost,
        operation_inputs={"message": message, "policy": policy},
        usage=usage,
        price_version="customer-rates-v1",
        cost_reference="Customer-maintained rate table",
    )
    workflow.progress("Reply ready", 1, 1)
    return output
