import asyncio
import discord
import json
import random

import utils
import items
import languages

class PlayersDict(dict):
    """ PlayersDict: словарь, содержащий данные в формате {'player.id': timer}.
    используется для определения, где находится игрок (и как правило, для
    получения его статуса).

    Возможные проблемы: проблемы с ассинхроностью.
    """
    def set(self, player):
        super().update({player.id: None})

    def set_timer(self, player):

        async def in_game_timer(self, player):
            print(f'{player.name} will die in 30 seconds.')
            await asyncio.sleep(30)
            super().pop(player.id)
            print(f'{player.name} dead. Rest in peace.')
            
        timer_task = asyncio.get_event_loop().create_task(in_game_timer(self, player))
        super().update({player.id: timer_task})

class Player(object):
    def __init__(self, user):
        self._user = user

        self.melee = None
        self.ranged = None
        self.creature = None

    async def get_data(self):
        """ get_data: процедура, получающая данные из базы и обновляющая профиль
        игрока. по сути, заменяет __init__, ибо там нельзя использовать async
        (который необоходим при создания профиля, чтобы отправить сообщение для
        выбора языка).

        return: None, т.к. является процедурой.
        """
        result = await utils.db.player_get_data(self._user.id)
        print(f'// {result}')
        if not result:
            result = await self.create_profile()
        result = result[0]

        columns = await utils.db.player_columns()

        for i in range(len(columns)):
            setattr(self, columns[i][0], result[i])

        self.channel = utils.client.get_channel(self.channel)

        self.lang = languages.languages[self.language]  # загрузка переводов

        cards = ('hero', 'melee', 'ranged', 'creature')
        for card in cards:
            _current_card = getattr(self, 'current_' + card)
            _card = getattr(items, _current_card)
            _card_data = json.loads(getattr(self, _current_card))
            _card_name = getattr(self.lang, _current_card)
            setattr(self, card, _card(_card_data))
            getattr(self, card).get_data(_card_name)

    async def create_profile(self):
        """ create_profile: функция, создающая запись в базе данных. также
        запрашивается язык, на котором предпочитает общаться игрок.
        
        return: ~list~: результат запроса к базе данных по id пользователя.
        """

        await self._user.dm_channel.send(embed=self.language_selection_embed())

        def check(m):
                return m.content in ['1', '2'] and m.channel == self._user.dm_channel

        message = await utils.client.wait_for('message', check=check)
        language = {'1': 'en', '2': 'ru'}[message.content]
        
        '''start_profile = (
            self._user.id,             # id
            self._user.dm_channel.id,  # channel
            self._user.name,           # name
            language,                  # language
            )'''

        #await utils.async_execute(f'INSERT INTO players (id, channel, name, language) VALUES ({"?, "*(len(start_profile)-1)}?)', start_profile)
        await utils.db.player_create(self._user.id, self._user.dm_channel.id, self._user.name, language)
        return await utils.db.player_get_data(self._user.id)
    
    async def use_melee(attacker, defender, turn):
        damage_type = random.choices(
            ['normal', 'lucky', 'unlucky'], [0.8, 0.1, 0.1])[0]
        damage = getattr(attacker.melee, 'damage_' + damage_type)

        knockback = 0  # ответный урон
        attacked = False  # совершилась ли атака

        # алиса напиши комментарии а то забудеш

        while not attacked:
            for target in attacker.melee.targets:
                side_name, character_name = target
                side = defender if side_name == 'opponent' else attacker
                if hasattr(side, character_name):
                    character = getattr(side, character_name)
                    if character.kind == 'creature':
                        if not character.alive:
                            break
                    if not character.invulnerability:
                        character.health -= damage
                        if side_name == 'opponent':
                            if character_name == 'hero':
                                knockback = defender.melee.damage
                            else:
                                knockback = character.damage
                            attacker.hero.health -= knockback
                        attacked = True

        await attacker.channel.send(
            embed=attacker.battle_attacker_melee_embed(defender, turn, damage_type))
        await defender.channel.send(
            embed=defender.battle_defender_melee_embed(attacker, turn, damage_type))
        
    async def use_ranged(attacker, defender, turn):
        damage_type = random.choices(
            ['normal', 'lucky', 'unlucky'], [0.8, 0.1, 0.1])[0]
        damage = getattr(attacker.ranged, 'damage_' + damage_type)

        attacked = False  # совершилась ли атака

        # алиса напиши комментарии а то забудеш

        while not attacked:
            for target in attacker.melee.targets:
                side_name, character_name = target
                side = defender if side_name == 'opponent' else attacker
                if hasattr(side, character_name):
                    character = getattr(side, character_name)
                    if character.kind == 'creature':
                        if not character.alive:
                            break
                    if not character.invulnerability:
                        character.health -= damage
                        attacked = True

        await attacker.channel.send(
            embed=attacker.battle_attacker_ranged_embed(defender, turn, damage_type))
        await defender.channel.send(
            embed=defender.battle_defender_ranged_embed(attacker, turn, damage_type))
    
    async def use_creature(attacker, defender, turn):
        damage_type = random.choices(
            ['normal', 'lucky', 'unlucky'], [0.8, 0.1, 0.1])[0]
        damage = getattr(attacker.creature, 'damage_' + damage_type)

        knockback = 0  # ответный урон
        attacked = False  # совершилась ли атака

        # алиса напиши комментарии а то забудеш

        while not attacked:
            for target in attacker.creature.targets:
                side_name, character_name = target
                side = defender if side_name == 'opponent' else attacker
                if hasattr(side, character_name):
                    character = getattr(side, character_name)
                    if character.kind == 'creature':
                        if not character.alive:
                            break
                    if not character.invulnerability:
                        character.health -= damage
                        if side_name == 'opponent':
                            if character_name == 'hero':
                                knockback = defender.melee.damage
                            else:
                                knockback = character.damage
                            attacker.creature.health -= knockback
                        attacked = True

        await attacker.channel.send(
            embed=attacker.battle_attacker_creature_embed(defender, turn, damage_type))
        await defender.channel.send(
            embed=defender.battle_defender_creature_embed(attacker, turn, damage_type))

    def language_selection_embed(self):
        embed_dict = {
            'title': 'choose your language, you can change it later.',
            'description': ':flag_gb: **1** — english\n:flag_ru: **2** — русский',
            'footer': {
                'text': '[alpha] language_selection_embed'
            }
        }
        return discord.Embed().from_dict(embed_dict)

    def battle_entrance_waiting_embed(self):
        embed_dict = {
            'title': self.lang.battle_entrance_waiting_title,
            'description': self.lang.battle_entrance_waiting_description,
            'footer': {
                'text': '[alpha] battle_entrance_waiting_embed'
            }
        }
        return discord.Embed().from_dict(embed_dict)

    def battle_entrance_first_turn_embed(self, opponent):
        embed_dict = {
            'title': self.lang.battle_entrance_opponent_found,
            'description': self.lang.battle_entrance_first_turn.format(opponent=opponent),
            'color': discord.Color.green().value,
            'footer': {
                'text': '[alpha] battle_entrance_first_turn_embed'
            }
        }
        return discord.Embed().from_dict(embed_dict)

    def battle_entrance_second_turn_embed(self, opponent):
        embed_dict = {
            'title': self.lang.battle_entrance_opponent_found,
            'description': self.lang.battle_entrance_second_turn.format(opponent=opponent),
            'color': discord.Color.red().value,
            'footer': {
                'text': '[alpha] battle_entrance_second_turn_embed'
            }
        }
        return discord.Embed().from_dict(embed_dict)
    
    def battle_attacker_choose_action_embed(self, opponent, turn):
        embed_dict = {
            "title": self.lang.battle_attacker_title.format(
                attacker=self, defender=opponent, turn=turn
            ),
            "description": self.lang.battle_attacker_choose_action.format(attacker=self),
            "color": discord.Color.green().value,
            "fields": [
                {
                    "name": self.lang.battle_player_creature.format(player=self),
                    "value": self.lang.battle_player_health.format(player=self),
                    "inline": True,
                },
                {
                    "name": self.lang.battle_player_creature.format(player=opponent),
                    "value": self.lang.battle_player_health.format(player=opponent),
                    "inline": True,
                },
            ],
            'footer': {
                'text': '[alpha] battle_attacker_choose_action_embed'
            }
        }
        return discord.Embed().from_dict(embed_dict)
    
    def battle_defender_wait_opponent_embed(self, opponent, turn):
        embed_dict = {
            "title": self.lang.battle_defender_title.format(
                attacker=opponent, defender=self, turn=turn
            ),
            "description": self.lang.battle_defender_wait_opponent.format(attacker=opponent),
            "color": discord.Color.red().value,
            "fields": [
                {
                    "name": self.lang.battle_player_creature.format(player=self),
                    "value": self.lang.battle_player_health.format(player=self),
                    "inline": True,
                },
                {
                    "name": self.lang.battle_player_creature.format(player=opponent),
                    "value": self.lang.battle_player_health.format(player=opponent),
                    "inline": True,
                },
            ],
            'footer': {
                'text': '[alpha] battle_defender_wait_opponent_embed'
            }
        }
        return discord.Embed().from_dict(embed_dict)

    def battle_attacker_melee_embed(self, opponent, turn, damage_type):
        embed_dict = {
            "title": self.lang.battle_attacker_title.format(
                attacker=self, defender=opponent, turn=turn
            ),
            "description": getattr(self.lang, f"battle_melee_{damage_type}").format(
                attacker=self, defender=opponent
            ),
            "color": discord.Color.green().value,
            "fields": [
                {
                    "name": self.lang.battle_player_creature.format(player=self),
                    "value": self.lang.battle_player_health.format(player=self),
                    "inline": True,
                },
                {
                    "name": self.lang.battle_player_creature.format(player=opponent),
                    "value": self.lang.battle_player_health.format(player=opponent),
                    "inline": True,
                },
            ],
            'footer': {
                'text': '[alpha] battle_attacker_melee_embed'
            }
        }
        return discord.Embed().from_dict(embed_dict)
    
    def battle_defender_melee_embed(self, opponent, turn, damage_type):
        embed_dict = {
            "title": self.lang.battle_defender_title.format(
                attacker=opponent, defender=self, turn=turn
            ),
            "description": getattr(self.lang, f"battle_melee_{damage_type}").format(
                attacker=opponent, defender=self
            ),
            "color": discord.Color.red().value,
            "fields": [
                {
                    "name": self.lang.battle_player_creature.format(player=self),
                    "value": self.lang.battle_player_health.format(player=self),
                    "inline": True,
                },
                {
                    "name": self.lang.battle_player_creature.format(player=opponent),
                    "value": self.lang.battle_player_health.format(player=opponent),
                    "inline": True,
                },
            ],
            "footer": {
                'text': '[alpha] battle_defender_melee_embed'
            },
        }
        return discord.Embed().from_dict(embed_dict)

    def battle_attacker_ranged_embed(self, opponent, turn, damage_type):
        embed_dict = {
            "title": self.lang.battle_attacker_title.format(
                attacker=self, defender=opponent, turn=turn
            ),
            "description": getattr(self.lang, f"battle_ranged_{damage_type}").format(
                attacker=self, defender=opponent
            ),
            "color": discord.Color.green().value,
            "fields": [
                {
                    "name": self.lang.battle_player_creature.format(player=self),
                    "value": self.lang.battle_player_health.format(player=self),
                    "inline": True,
                },
                {
                    "name": self.lang.battle_player_creature.format(player=opponent),
                    "value": self.lang.battle_player_health.format(player=opponent),
                    "inline": True,
                },
            ],
            'footer': {
                'text': '[alpha] battle_attacker_ranged_embed'
            }
        }
        return discord.Embed().from_dict(embed_dict)
    
    def battle_defender_ranged_embed(self, opponent, turn, damage_type):
        embed_dict = {
            "title": self.lang.battle_defender_title.format(
                attacker=opponent, defender=self, turn=turn
            ),
            "description": getattr(self.lang, f"battle_ranged_{damage_type}").format(
                attacker=opponent, defender=self
            ),
            "color": discord.Color.red().value,
            "fields": [
                {
                    "name": self.lang.battle_player_creature.format(player=self),
                    "value": self.lang.battle_player_health.format(player=self),
                    "inline": True,
                },
                {
                    "name": self.lang.battle_player_creature.format(player=opponent),
                    "value": self.lang.battle_player_health.format(player=opponent),
                    "inline": True,
                },
            ],
            "footer": {
                'text': '[alpha] battle_defender_ranged_embed'
            },
        }
        return discord.Embed().from_dict(embed_dict)

    def battle_attacker_creature_embed(self, opponent, turn, damage_type):
        embed_dict = {
            "title": self.lang.battle_defender_title.format(
                attacker=self, defender=opponent, turn=turn
            ),
            "description": getattr(self.lang, f"battle_creature_{damage_type}").format(
                attacker=self, defender=opponent
            ),
            "color": discord.Color.green().value,
            "fields": [
                {
                    "name": self.lang.battle_player_creature.format(player=self),
                    "value": self.lang.battle_player_health.format(player=self),
                    "inline": True,
                },
                {
                    "name": self.lang.battle_player_creature.format(player=opponent),
                    "value": self.lang.battle_player_health.format(player=opponent),
                    "inline": True,
                },
            ],
            "footer": {
                'text': '[alpha] battle_attacker_creature_embed :х'
            },
        }
        return discord.Embed().from_dict(embed_dict)
    
    def battle_defender_creature_embed(self, opponent, turn, damage_type):
        embed_dict = {
            "title": self.lang.battle_defender_title.format(
                attacker=opponent, defender=self, turn=turn
            ),
            "description": getattr(self.lang, f"battle_creature_{damage_type}").format(
                attacker=opponent, defender=self
            ),
            "color": discord.Color.red().value,
            "fields": [
                {
                    "name": self.lang.battle_player_creature.format(player=self),
                    "value": self.lang.battle_player_health.format(player=self),
                    "inline": True,
                },
                {
                    "name": self.lang.battle_player_creature.format(player=opponent),
                    "value": self.lang.battle_player_health.format(player=opponent),
                    "inline": True,
                },
            ],
            "footer": {
                'text': '[alpha] battle_defender_creature_embed'
            },
        }
        return discord.Embed().from_dict(embed_dict)
