import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
if not AI_API_KEY:
    raise RuntimeError("AI API key not found in .env.")

AI_ENDPOINT = "https://openrouter.ai/api/v1"
MODEL = "openrouter/free"

PROXIES_FILE = Path("proxies.json")
MAX_CONCURRENT = 500          # одновременно проверяемых прокси
TIMEOUT = 15.0               # таймаут на один запрос


async def check_proxy(proxy: str, sem: asyncio.Semaphore) -> dict:
    """
    Проверяет один прокси.
    Возвращает dict с результатом: proxy, ok, error, answer (если ok).
    """
    proxy_url = f"http://{proxy}"   # порт 80 -> HTTP-прокси

    async with sem:
        try:
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=TIMEOUT,
                follow_redirects=True,
            ) as http_client:
                client = AsyncOpenAI(
                    base_url=AI_ENDPOINT,
                    api_key=AI_API_KEY,
                    http_client=http_client,
                )

                response = await client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "user", "content": "Reply with just: OK"}
                    ],
                    max_tokens=10,
                    temperature=0.0,
                )

                answer = response.choices[0].message.content
                return {"proxy": proxy, "ok": True, "answer": answer}

        except Exception as e:
            return {"proxy": proxy, "ok": False, "error": f"{type(e).__name__}: {e}"}


async def main() -> None:
    with PROXIES_FILE.open("r", encoding="utf-8") as f:
        proxies: list[str] = json.load(f)

    sem = asyncio.Semaphore(MAX_CONCURRENT)

    tasks = [check_proxy(p, sem) for p in proxies]
    results = await asyncio.gather(*tasks)

    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]

    print(f"\n=== Results ===")
    print(f"Total:      {len(results)}")
    print(f"Working:   {len(ok)}")
    print(f"Failed:  {len(bad)}\n")

    if ok:
        print("Working proxies:")
        for r in ok:
            print(f"  ✅ {r['proxy']}  ->  {r['answer']!r}")

    if bad:
        print("\nDon't work:")
        for r in bad:
            print(f"  ❌ {r['proxy']}  ->  {r['error']}")

    print(f"\n=== Results ===")
    print(f"Total:      {len(results)}")
    print(f"Working:   {len(ok)}")
    print(f"Failed:  {len(bad)}\n")


if __name__ == "__main__":
    asyncio.run(main())