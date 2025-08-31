from wraipperz.api.llm import call_ai

deployment = "azure/ai-parsing-gpt-5-chat"  # YOUR ACTUAL DEPLOYMENT NAME

response, cost = call_ai(
    model=f"{deployment}",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    temperature=0,
    max_tokens=50,
)
