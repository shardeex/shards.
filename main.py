import aiohttp
import asyncio
import random

import discord
import pyfiglet

import utils
import shardsplayer


class Shards(object):
    players_in_game = shardsplayer.PlayersDict()  # для тех, кто в игре.
    players_in_menu = shardsplayer.PlayersDict()  # для тех, кто в меню.
    players_in_lobby = shardsplayer.PlayersDict()  # для тех, кто ждёт битвы.
    players_in_battle = shardsplayer.PlayersDict()  # для тех, кто в битве.

    lobby = {"beginning_arena": [], "legendary_arena": []}

    def __init__(self):
        pass

    async def battle_entrance(self, player):
        """ battle_entrance: (или же лобби, что не совсем корректно, но...)
        используется для распределения игроков по битвам в равных условиях. принцип
        можно понять из комментариев в самом коде.

        nb! метод сортирует не по ближайшему количеству трофеев, а по времени
        ожидания человека, находящегося в очереди, то есть методом стека.

        аргументы:
        ----------
        player ~player.Player~:
            объект игрока, содержащий необходимые данные.

        return: None, т.к. является процедурой.
        """
        permissible_trophies_difference = 10  # допустимая разница в кубках
        # между игроками
        opponent = None
        for opponent in self.lobby[player.arena]:
            trophies_difference = abs(player.trophies - opponent.trophies)
            if trophies_difference <= permissible_trophies_difference:
                self.lobby[opponent.arena].remove(opponent)

        if opponent:  # найден подходящий противник, начало битвы
            if random.randint(0, 1):
                first_player, second_player = player, opponent
            else:
                second_player, first_player = player, opponent
            await first_player.channel.send(
                embed=first_player.battle_entrance_first_turn_embed(second_player)
            )
            await second_player.channel.send(
                embed=second_player.battle_entrance_second_turn_embed(first_player)
            )
            await asyncio.sleep(2)
            utils.loop.create_task(self.battle(first_player, second_player))
        else:  # добавление игрока в очередь
            self.lobby[player.arena].append(player)
            await player.channel.send(embed=player.battle_entrance_waiting_embed())

    async def battle(self, attacker, defender):
        attacker.time_warning = defender.time_warning = False
        turn = 1

        while defender.hero.health > 0 and attacker.hero.health > 0:

            def check(m):
                return (
                    m.content in ("1", "2", "3", "4", "5", "6")
                    and m.channel == attacker.channel
                )

            timeout = 30 if not attacker.time_warning else 15

            await attacker.channel.send(
                embed=attacker.battle_attacker_choose_action_embed(defender, turn)
            )
            await defender.channel.send(
                embed=defender.battle_defender_wait_opponent_embed(attacker, turn)
            )

            try:
                action = await utils.client.wait_for(
                    "message", check=check, timeout=timeout
                )
                action = int(action.content)
            except asyncio.TimeoutError:
                action = 0
                # если соперник неактивен
                if not attacker.time_warning:
                    attacker.time_warning = True
                else:
                    attacker.hero.health = 0

            actions = (
                None,
                "melee",
                "ranged",
                "creature",
                "attack_spell",
                "defense_spell",
            )
            action = actions[action]

            if action:
                await getattr(attacker, "use_" + action)(defender, turn)
            else:  # player AFK
                ...  # send that player AFK

            attacker, defender = defender, attacker
            turn += 1

            await asyncio.sleep(5)

        # end of the battle


shards = Shards()


@utils.client.event
async def on_ready():
    title = pyfiglet.Figlet(font='calgphy2', justify='center')
    subtitle = pyfiglet.Figlet(font='bell', justify='center')
    print(title.renderText('shards.'))
    print(subtitle.renderText('alpha.'))


@utils.client.event
async def on_message(message):
    if message.author == utils.client.user:
        return

    if message.author.id in shards.players_in_game:
        return

    player = shardsplayer.Player(message.author)
    await player.get_data()
    shards.players_in_game.set(player)

    print(shards.players_in_game)

    # здесь должен быть запуск функции главного меню.
    # в будущем планирую добавить свои триггеры на серверные чаты.

    if message.channel.type.name == "private":  # dm's
        print("Channel type ok!")
        if message.content.lower() == player.lang.start_message:  # 'начать'
            print("Language start_message ok!")
            await shards.battle_entrance(player)


def main():
    try:
        utils.client.run(utils.discord_token)
    except aiohttp.client_exceptions.ServerDisconnectedError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        print("Reconnecting...")


if __name__ == "__main__":
    while True:
        main()
