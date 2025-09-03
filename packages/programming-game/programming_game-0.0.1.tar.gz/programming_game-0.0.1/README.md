# Programming Game Client

A Python client for the Programming Game. This package allows you to write bots to play the game.

## Installation

To install the package, run the following command:

```bash
pip install programming-game
```

## Usage

To run a bot, you need to provide your credentials via environment variables.

```bash
export GAME_CLIENT_ID="YOUR_CLIENT_ID"
export GAME_CLIENT_KEY="YOUR_CLIENT_KEY"
```

Then, you can run your bot script using the `game-client` command:

```bash
game-client run your_bot_module:your_bot_instance
```

For example, if your bot is in a file named `my_bot.py` and the `GameClient` instance is named `app`, you would run:

```bash
game-client run my_bot:app
```

### Example Bot

Here is an example of a simple bot that explores the game world, attacks monsters, and heals when necessary.

```python
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

```

## API Documentation

This section provides an overview of the available actions, spells, and weapon skills in the game.

### Skills

*   **Attack**: Deal damage to an enemy.
    `return player.attack(enemy.id)`
*   **Move**: Move to a new location.
    `return player.move({ x: 1, y: 0 })`
*   **Respawn**: Discard all of your inventory and equipment, and respawn at a new location.
    `return player.respawn()`
*   **Summon Mana**: Focus your concentration to refill your available mana.
    `return player.summonMana()`
*   **Eat**: Eat food to restore your calories.
    `return player.eat(food.id)`
*   **Equip Spell**: Equip a spell stone from your inventory.
    `return player.equipSpell('fireball')`
*   **Unequip Spell**: Unequip the first spell in your spellbook.
    `return player.unequipSpell()`
*   **Cast**: Cast a spell.
    `return player.cast('fireball', enemy)`
*   **Sell**: Offer to sell items to another character.
    `return player.sell({ items: { snakeMeat: 10 }, to: npc })`
*   **Buy**: Buy items from another character.
    `return player.buy({ items: { snakeMeat: 10 }, from: npc })`
*   **Use**: Use an item.
    `return player.use('minorHealthPotion')`
*   **Equip**: Equip an item.
    `return player.equip('copperSword', 'weapon')`
*   **Unequip**: Unequip an item from your equipment.
    `return player.unequip('weapon')`
*   **Set Role**: Announce the role that you wish to player in your party.
    `return player.setRole(ROLES.healer)`
*   **Invite to Party**: Invite another unit to join your party.
    `return player.inviteToParty(target.id)`
*   **Seek Party**: Announce that you are looking for a party.
    `return player.seekParty()`
*   **Accept Party Invite**: Accept a party invite from another unit.
    `return player.acceptPartyInvite(inviter.id)`
*   **Decline Party Invite**: Decline a party invite from another unit.
    `return player.declinePartyInvite(inviter.id)`
*   **Leave Party**: Leave your current party.
    `return player.leaveParty()`
*   **Craft Item**: Craft an item using resources.
    `return player.craft('copperIngot', { chunkOfCopper: ingotCost })`
*   **Use Weapon Skill**: Use a weapon skill.
    `return player.useWeaponSkill({ skill: 'doubleSlash', target: enemy })`
*   **Drop Item**: Drop an item from your inventory.
    `return player.drop({ item: item.id, amount })`
*   **Set Trade**: Announce offers and requests for trades.
    `return player.setTrade({ buying: { snakeEyes: { quantity: 100, price: 10 } }, selling: { snakeMeat: { quantity: 100, price: 5 } } })`
*   **Accept Quest**: Accept a quest from an NPC.
    `return player.acceptQuest(npc, 'chicken_chaser')`
*   **Abandon Quest**: Abandon a quest that you've already accepted.
    `return player.abandonQuest('chicken_chaser')`
*   **Turn In Quest**: Turn in a quest that you've completed.
    `return player.turnInQuest(npc, 'chicken_chaser')`
*   **Deposit Items Into Storage**: Deposit items into your storage.
    `return player.deposit(banker, { copperCoin: 100 })`
*   **Withdraw Items From Storage**: Withdraw items from your storage.
    `return player.withdraw(banker, { copperCoin: 100 })`

### Spells

*   **Regen**: Instant, 3mp. Apply a buff that heals a small amount of health over time.
*   **Fireball**: 3s cast time, 7mp. Deal damage to an enemy.
*   **Heal**: 1.5s cast time, 5mp. Heal a large amount of health.
*   **Icicle**: 3s cast time, 5mp. Deal damage to an enemy.
*   **Ice Armor**: 2s cast time, 5mp. Grant a shield that absorbs damage.
*   **Chill**: Instant, 3mp. Slow an enemy.
*   **Ball of Ice**: 3s cast time, 5mp. Deal damage to an enemy.
*   **Flash Freeze**: Instant, 5mp. Deal damage to an enemy.
*   **Aid Digestion**: Channeled, 5mp/s. Heal a small amount of health over time.

### Weapon Skills

*   **Swords**:
    *   **Double Slash**: tp cost: 10. Slash twice, dealing damage to an enemy.
*   **Bows**:
    *   **Misdirecting Shot**: tp cost: 15. Shoot an arrow at an enemy, dealing damage and redirecting their threat.
    *   **Pinning Shot**: tp cost: 30. Shoot an arrow at an enemy, dealing damage and rooting them in place.
*   **Unarmed**:
    *   **Combo**: tp cost: 30. Attack three times, dealing damage to an enemy.
    *   **Haymaker**: tp cost: 30. A mighty punch, dealing damage to an enemy.
    *   **Headbutt**: tp cost: 40. Headbutt an enemy, dealing damage and stunning them.
*   **Greatswords**:
    *   **Charge**: tp cost: 20. Charge at an enemy, dealing damage and knocking them back.
    *   **Power Slash**: tp cost: 20. A powerful slash, dealing damage to an enemy.
*   **Shields**:
    *   **Shield Charge**: tp cost: 20. Charge at an enemy, dealing damage and stunning them.
*   **Usable with all weapons**:
    *   **Threaten**: tp cost: 10. Threaten an enemy, increasing their threat towards you.
