import unittest
import asyncio
import time
import httpx


class TestFastAPIConcurrency(unittest.TestCase):
    SYNC_URL = "http://localhost:8000/sync-data"
    ASYNC_URL = "http://localhost:8000/async-data"
    NUM_REQUESTS = 100

    @staticmethod
    async def async_fetch(client, url):
        response = await client.get(url)
        return response.json()

    async def benchmark_requests(self, url):
        async with httpx.AsyncClient() as client:
            tasks = [self.async_fetch(client, url) for _ in range(self.NUM_REQUESTS)]
            start = time.perf_counter()
            results = await asyncio.gather(*tasks)
            end = time.perf_counter()
        return {
            "total_time": end - start,
            "avg_time": (end - start) / self.NUM_REQUESTS,
            "response_sample": results[0],
        }

    def test_sync_endpoint_concurrency(self):
        result = asyncio.run(self.benchmark_requests(self.SYNC_URL))
        print("\n[Sync Endpoint]")
        print(f"Total Time: {result['total_time']:.2f}s")
        print(f"Average Time per Request: {result['avg_time']:.3f}s")
        print(f"Sample Response: {result['response_sample']}")
        self.assertIn("message", result["response_sample"])

    def test_async_endpoint_concurrency(self):
        result = asyncio.run(self.benchmark_requests(self.ASYNC_URL))
        print("\n[Async Endpoint]")
        print(f"Total Time: {result['total_time']:.2f}s")
        print(f"Average Time per Request: {result['avg_time']:.3f}s")
        print(f"Sample Response: {result['response_sample']}")
        self.assertIn("message", result["response_sample"])


if __name__ == "__main__":
    unittest.main()
