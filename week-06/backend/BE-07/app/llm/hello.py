"""
Stage 0 — Provider connectivity test.

Run:  python -m app.llm.hello
(from the BE-07 directory, with .env in place)

Proves the OpenAI SDK can reach your chosen provider and get a response.
The same three environment variables (LLM_BASE_URL, LLM_API_KEY, LLM_MODEL)
are the only difference between a model running on your laptop and one
running in a datacentre. That is why nobody should hard-code a provider.
"""

from app.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL
from openai import OpenAI

client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
)

response = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
)

print(f"Provider:  {LLM_BASE_URL}")
print(f"Model:     {LLM_MODEL}")
print(f"Response:  {response.choices[0].message.content}")
