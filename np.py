import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.constants import NEXUS, PROBE
from sc2.player import Bot, Computer

class sc2_lechita_1(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.expand()

    async def build_workers(self):
        if len(self.workers) < 50:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))

    async def expand(self):
        if self.units(NEXUS).amount < 5 and self.can_afford(NEXUS):
            await self.expand_now()










run_game(maps.get("Abyssal reef LE"), [
    Bot(Race.Protoss, sc2_lechita_1()),
    Computer(Race.Protoss, difficulty=Difficulty.Easy)
], realtime = False)
