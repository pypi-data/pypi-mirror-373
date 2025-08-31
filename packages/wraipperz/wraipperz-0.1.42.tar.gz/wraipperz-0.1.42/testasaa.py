from openai import OpenAI

endpoint = "https://adan-mez9h29r-eastus2.cognitiveservices.azure.com/openai/v1/"
model_name = "gpt-5-chat"
deployment_name = "ai-parsing-gpt-5-chat"

api_key = "2415SILMFQdOH9nJdtPnpuOMdjMctEzLAH52s7vMXZQBDGvOj1GHJQQJ99BHACHYHv6XJ3w3AAAAACOGhQoC"

client = OpenAI(base_url=f"{endpoint}", api_key=api_key)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)

print(completion.choices[0].message)
print(completion.choices)
