# import bibliotek
import sc2
import random
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
# import jednostek lub budynków które zamierzamy budować
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, \
GATEWAY, CYBERNETICSCORE, STALKER, VOIDRAY, STARGATE
# import przykładowego bota (tutaj "CannonRushBot"), polecam zobaczyć ten folder
from examples.protoss.cannon_rush import CannonRushBot

# klasa naszego bota tu dzieje się cała magia
class sc2_lechita_1(sc2.BotAI):
    # startowe zmienne, jedna minuta to mniej wiecej 165 iteracji w grze
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50

    # metoda wywoływana w kazdej iteracji
    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assymilators()
        await self.expand()
        await self.build_offensive_buildings()
        await self.build_offensive_units()
        await self.attack()

    # metoda która buduje robotnikow
    async def build_workers(self):
        # sprawdzmy czy nie przekroczylismy zalożonej ilosci robotnikow
        if len(self.workers)<self.MAX_WORKERS:
            # sprawdzamy czy mamy wolnego nexusa
            for nexus in self.units(NEXUS).ready.noqueue:
                # sprawdczamy czy stac nas na robotnika
                if self.can_afford(PROBE):
                    # i trenujemy robotnika
                    await self.do(nexus.train(PROBE))

    # metoda która buduje pylony
    async def build_pylons(self):
        # jesli mamy mniej niż 5 wolnej polulacji i nie budujemy juz pylonu
        if self.supply_left < 5 and not self.already_pending(PYLON):
            # wybieramy nexus z listy nexusow
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                # jesli nexus istnieje
                if self.can_afford(PYLON):
                    # jesli mamy wystarczajaco zasobów
                    await self.build(PYLON, near = nexuses.first)

    # metoda która buduje budynki do wydobycia gazu
    async def build_assymilators(self):
        # wybieramy nexus z listy nexusow
        for nexus in self.units(NEXUS).ready:
            # zapisujemy zrodla gazu blisze niz 15
            vespenes = self.state.vespene_geyser.closer_than(15., nexus)
            # budujemy nasze zrodlo gazu
            for vespene in vespenes:
                # nie stac nas na asymilator
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vespene.position)
                if worker is None:
                    break
                # mozemy budowac asymilator
                if not self.units(ASSIMILATOR).closer_than(1., vespene).exists:
                    await self.do(worker.build(ASSIMILATOR, vespene))

    # metoda ktora buduje nexusy po wybranym czasie
    async def expand(self):
        if self.units(NEXUS).amount < ((self.iteration*3)/self.ITERATIONS_PER_MINUTE) and self.can_afford(NEXUS):
            await self.expand_now()

    # metoda która buduje budynki ofensywne
    async def build_offensive_buildings(self):
        # sprawdzamy czy pylon istnieje
        if self.units(PYLON).ready.exists:
            # wybieramy randomowego pylona
            pylon = self.units(PYLON).ready.random
            # sprawdzamy czy istnieje gateway i czy nie istnieje CYBERNETICSCORE
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                # jesli tak to sprawdzmy czy mamy na niego zasoby i czy juz go nie budujemy
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    # bubujemy CYBERNETICSCORE
                    await self.build(CYBERNETICSCORE, near=pylon)

            # sprawdzamy ilosc gateway, tutaj budujemy je co minute
            elif len(self.units(GATEWAY)) < (self.iteration/self.ITERATIONS_PER_MINUTE):
                # jesli tak to sprawdzmy czy mamy na niego zasoby i czy juz go nie budujemy
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

            # sprawdzamy ilosc stargate, tutaj budujemy je co minute
            if len(self.units(STARGATE)) < (self.iteration/self.ITERATIONS_PER_MINUTE):
                # jesli tak to sprawdzmy czy mamy na niego zasoby i czy juz go nie budujemy
                if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                    await self.build(STARGATE, near=pylon)

    # tu zaczynamy zabawe, budujemy jednostki ofensywne
    async def build_offensive_units(self):
        # sprawdzmy czy mamy wolne gateway
        for gateway in self.units(GATEWAY).ready.noqueue:
            # sprawdzmy czy stac nas na stalkera i czy zostanie nam troche zasobów
            if self.can_afford(STALKER) and self.supply_left > 0:
                # sprawdzamy czy nie mamy wiecej stalkerow czy voiday
                if not self.units(STALKER).amount>self.units(VOIDRAY).amount:
                    # budujemy stalkera
                    await self.do(gateway.train(STALKER))
        for stargate in self.units(STARGATE).ready.noqueue:
            # sprawdzmy czy stac nas na voidray i czy zostanie nam troche zasobów
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(stargate.train(VOIDRAY))


    async def attack(self):
        # towrzymy tablice z danymi
        aggressive_units = {STALKER: [15, 5],
                            VOIDRAY: [8, 3]}

        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for single_unit in self.units(UNIT).idle:
                    await self.do( single_unit.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for  single_unit in self.units(UNIT).idle:
                        await self.do(single_unit.attack(random.choice(self.known_enemy_units)))


        if self.units(STALKER).amount > 1:
            if len(self.known_enemy_units)>0:
                for stalker in self.units(STALKER).idle:
                    await self.do(stalker.attack(random.choice(self.known_enemy_units)))

        if self.units(STALKER).amount > 15:
            for stalker in self.units(STALKER).idle:
                await self.do(stalker.attack(self.find_target(self.state)))

    def find_target(self, state):
        if len(self.known_enemy_units)>0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures)>0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]


# zaczynamy nasza gre, wybieramy mape
run_game(maps.get("Abyssal reef LE"), [
    # wybranym 1 zawodnika np: Bot(Race.Protoss, sc2_lechita_1())
    # lub komputer np: Computer(Race.Protoss, Difficulty.Hard)
    Bot(Race.Protoss, sc2_lechita_1()),
    Computer(Race.Protoss, Difficulty.Easy)
# tutaj wyberamy czas True - czas normalny
# False - czas przyśpieszony
], realtime=False )
