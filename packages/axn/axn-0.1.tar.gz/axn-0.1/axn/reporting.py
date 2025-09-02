import asyncio

class Report:
    def __init__(self):
        self.entries = []

    async def add_entry(self, tool, target, result):
        await asyncio.sleep(0.01)
        self.entries.append({"tool": tool, "target": target, "result": result})

    async def show(self):
        for e in self.entries:
            print(f"{e['tool']} | {e['target']} | {e['result']}")
        return self.entries
