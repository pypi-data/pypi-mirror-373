import asyncio

class MockDatabase:
    async def query(self, sql):
        await asyncio.sleep(0.05)
        return {"sql": sql, "result": "simulated"}
