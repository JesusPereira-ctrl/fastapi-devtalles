import asyncio
import time

import httpx

URL = "http://127.0.0.1:8000/api/v1/posts/async"


async def hit(t, client: httpx.AsyncClient):
    start = time.perf_counter()
    r = await client.get(URL, params={"t": t})
    elapsed = time.perf_counter() - start
    return t, elapsed, r.json()


async def main():
    timeout = httpx.Timeout(20.0)
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        start = time.perf_counter()
        results = await asyncio.gather(
            hit(3.0, client),
            hit(5.5, client),
            hit(7.8, client),
            hit(9.7, client),
            return_exceptions=True,
        )
        total = time.perf_counter() - start

    print("\n--- Resultados ---")
    for res in results:
        if isinstance(res, Exception):
            print("Error:", repr(res))
        else:
            t, elapsed, body = res
            print(f"sleep={t:<4} tardo={elapsed:.2f}s respuesta={body}\n")
    print(f"\nTiempo total de pared: {total:.2f}s\n")


if __name__ == "__main__":
    asyncio.run(main())
