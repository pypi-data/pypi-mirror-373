import enum

from loguru import logger

from programming_game import GameClient, events
from programming_game.schema.intent import Intent
from programming_game.schema.other import Position
from programming_game.schema.units import GameState, Monster
from programming_game.utils import get_distance


class State(enum.Enum):
    connected = 0
    explore = 1
    heal = 2


corner = 0
state: State = State.connected
tpos: Position | None = None


def set_state(new_state: State):
    global state
    logger.info(f"Setting state to {new_state}")
    state = new_state


app = GameClient(credentials={})


@app.on_event("*")
async def on_event(payload: dict):
    pass


@app.on_loop
async def on_tick(gs: GameState) -> Intent | None:
    global corner, state, tpos
    player = gs.player

    if player.hp <= 0:
        logger.warning(f"{player.name} has died. Respawning...")
        return player.respawn()

    if state == State.heal:
        if move := player.move_to(0, 0):
            return move
        if player.hp >= 100:
            set_state(State.explore)

    if player.hp < 50:
        logger.warning(f"{player.name} is hurt. Recovering...")
        set_state(State.heal)
        return

    if player.calories < 2000:
        if "ratMeat" in player.inventory and player.inventory["ratMeat"] > 0:
            return player.eat("ratMeat")
        if "snakeMeat" in player.inventory and player.inventory["snakeMeat"] > 0:
            return player.eat("snakeMeat")

    if state == State.explore:
        return explore(gs)
    elif state == State.connected:
        return just_connected(gs)

    return None


def _explore(gs: GameState):
    global corner, tpos

    if not tpos:
        corner = 0
        tpos = Position(-5, 5)

    if move := gs.player.move_to(tpos.x, tpos.y):
        return move

    if corner == 0:
        corner = 1
        tpos = Position(5, 5)
    else:
        corner = 0
        tpos = Position(-5, -5)

    return None


def explore(gs: GameState):
    player = gs.player
    units = gs.units

    monsters = [
        unit for unit in units.values() if type(unit) == Monster and unit.hp > 0
    ]

    if monsters:
        closest_monster = min(
            monsters, key=lambda m: get_distance(player.position, m.position)
        )
        return player.attack(closest_monster.id)

    if move := player.move_to(-25, -25):
        return move
    return None


def just_connected(gs: GameState) -> Intent | None:
    if gs.player.hp > 70:
        set_state(State.explore)
    else:
        set_state(State.heal)
    return None
