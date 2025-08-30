import asyncio
import os
from pprint import pprint

from openai import AsyncOpenAI

from vals.sdk.suite import Suite

client = AsyncOpenAI(
    api_key=os.environ["VALS_API_KEY"], base_url="http://localhost:8000/proxy"
)


async def fetch(model: str):
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Keep responses under 10 words.",
            },
            {
                "role": "user",
                "content": "Cats or dogs. You must answer with 'Cats' or 'Dogs' and provide reasoning.",
            },
        ],
    )
    print(f"\n--- {model} ---")
    pprint(response.choices[0].message.content)


async def raw_proxy():
    _ = await asyncio.gather(
        fetch("openai/gpt-3.5-turbo"),
        fetch("anthropic/claude-opus-4-20250514"),
        fetch("google/gemini-2.5-pro"),
        fetch("together/moonshotai/Kimi-K2-Instruct"),
        fetch("fireworks/llama-v3p1-8b-instruct"),
        fetch("cohere/command-r-plus"),
        fetch("grok/grok-4"),
        fetch("azure/gpt-4o-2024-11-20"),
        fetch("azure/o3-2025-04-16"),
        fetch("azure/gpt-4o-2024-11-20"),
    )


async def pirate_model(input: str):
    response = await client.chat.completions.create(
        model="grok/grok-4",
        messages=[
            {
                "role": "system",
                "content": "You are a pirate, answer in the speaking style of a pirate",
            },
            {
                "role": "user",
                "content": input,
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


async def with_sdk():
    suite = await Suite.from_id("9db051eb-342e-405d-9b59-b76aa09500b5")

    run = await suite.run(model=pirate_model, model_name="pirate-v1")
    print(f"Run URL: {run.url}")
    print(f"Pass percentage: {run.pass_percentage}")


async def main():
    await raw_proxy()
    # await with_sdk()


asyncio.run(main())
