# imports
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

class sc2_lechita_1(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()


run_game(maps.get("Abyssal reef LE"), [
    Bot(Race.Protoss, sc2_lechita_1()),
    Computer(Race.Protoss, Difficulty.Easy)
], realtime=True )
