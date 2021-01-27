import random

class Language(object):
    def __init__(self, dictionary):
        def func(m): return random.choice(m)

        for event, messages in dictionary.items():
            _attr = [func, messages]
            setattr(self, event, _attr)

    def __getattribute__(self, attr):
        try:
            lst = object.__getattribute__(self, attr)
            return lst[0](lst[1])
        except AttributeError:
            return f'UnlocalizedString<{attr}>'

en = {
    'start_message': ['start'],
    'battle_entrance_waiting_title': ['searching for opponent...'],
    'battle_entrance_waiting_description': ['please wait — searching for opponent may take some time.'],
    }

ru = {
    'start_message': ['начать'],
    'battle_entrance_waiting_title': ['поиск противника...'],
    'battle_entrance_waiting_description': ['пожалуйста, подождите — поиск противника может занять некоторое время.'],
    'battle_entrance_opponent_found': ['противник найден.'],
    'battle_entrance_first_turn': ['ваш противник: {opponent.name} {opponent.trophies} :trophy:.\nначинать бой будете вы, приготовьтесь нападать.'],
    'battle_entrance_second_turn': ['ваш противник: {opponent.name} {opponent.trophies} :trophy:.\nувы, начинать бой будете не вы, защищайтесь.'],
    
    'battle_attacker_title': ['Битва между __**{attacker.name}**__ и {defender.name} | Ход №{turn}'],
    'battle_defender_title': ['Битва между {defender.name} и __**{attacker.name}**__ | Ход №{turn}'],
    'battle_player_health': ['{player.name} {player.hero.health} :heart:'],
    'battle_player_creature': ['{player.creature.name} {player.creature.health} :heart:'],

    'battle_melee_normal': ['{attacker.name} наносит {attacker.melee.damage} ед. урона оружием ближнего боя "{attacker.melee.name}", получая {defender.melee.damage} ед. урона от оружия ближнего боя "{defender.melee.name}" в ответ.'],
    'battle_melee_lucky': ['{attacker.name} оказывается немного удачливее, чем обычно, и наносит {attacker.melee.damage_lucky} ед. урона (110%) оружием ближнего боя "{defender.melee.name}", получая {defender.melee.damage} ед. урона от оружия ближнего боя "{defender.melee.name}" в ответ.'],
    'battle_melee_unlucky': ['{attacker.name} не в ударе, поэтому наносит лишь {attacker.melee.damage_unlucky} ед. урона (90%) оружием ближнего боя "{defender.melee.name}", получая {defender.melee.damage} ед. урона от оружия ближнего боя "{defender.melee.name}" в ответ.'],
    
    'battle_ranged_normal': ['{attacker.name} наносит {attacker.ranged.damage} ед. урона дальнобойным оружием "{defender.ranged.name}".'],
    'battle_ranged_lucky': ['{attacker.name} оказывается немного удачливее, чем обычно, и наносит {attacker.ranged.damage_lucky} ед. урона (110%) дальнобойным оружием "{defender.ranged.name}".'],
    'battle_ranged_unlucky': ['{attacker.name} не в ударе, поэтому наносит лишь {attacker.ranged.damage_unlucky} ед. урона (90%) дальнобойным оружием "{defender.ranged.name}".'],
    
    'battle_creature_normal': ['{attacker.name} взывает к своему существу "{attacker.creature.name}", которое наносит {attacker.creature.damage} ед. урона.'],
    'battle_creature_lucky': ['{attacker.name} взывает к своему существу "{attacker.creature.name}", которое хорошо покушало и поэтому наносит {attacker.creature.damage_lucky} ед. урона (110%).'],
    'battle_creature_unlucky': ['{attacker.name} взывает к своему существу "{attacker.creature.name}", которое плохо выспалось и поэтому наносит {attacker.creature.damage_unlucky} ед. урона (90%).'],

    'battle_attacker_choose_action': ['{attacker.name}, ваш ход — отправьте цифру для выбора действия.\n**1** — {attacker.melee.name} ({attacker.melee.damage} ед. урона).\n**2** — {attacker.ranged.name} ({attacker.ranged.damage} ед. урона).\n**3** — {attacker.creature.name} ({attacker.creature.damage} ед. урона).'],
    'battle_defender_wait_opponent': ['посмотрим, что же сделает с тобой {attacker.name}...'],
        
    'battle_axe': ['боевой топор'],
    'frozen_scythe': ['замороженная коса'],
    'flame_knuckles': ['пламенные кастеты'],

    'obsidian_spear': ['обсидиановое копьё'],
    'ice_bow': ['ледяной лук'],
    'blaze_tomahawk': ['пылающиий томагавк'],

    'steel_armor': ['стальная броня'],
    'frosty_chestplate': ['замёрзший нагрудник'],
    'fire_mantle': ['огеннная мантия'],

    'mad_bomber': ['свихнувшиийся подрывник'],
    'blizzard_lizzard': ['снежная ящерица'],
    'fire_spirit': ['огненный дух'],
    }

en = Language(en)
ru = Language(ru)

languages = {'en': en, 'ru': ru}
