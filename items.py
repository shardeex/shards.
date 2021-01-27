import random

IN_ORDER = [('opponent', 'creature'), ('opponent', 'hero')]

class HealthInt(int):
	__add__ = lambda s, o: max(HealthInt(int.__add__(s, o)), HealthInt())
	__sub__ = lambda s, o: max(HealthInt(int.__sub__(s, o)), HealthInt())

def levelCounter(starting_value):
    ''' levelCounter: подсчёт урона или здоровье на всех 9 уровнях, исходя из
    увеличения характеристик поэтапно на 10%, округляя в наименьшуюю сторону.

    return ~list~:
        возвращает список, где положение элемента соответствует значению на
        определённом уровне.

        nb! нулевой объект списка всегда равен нулю!

    аргументы:
    ----------
    starting_value ~int~:
        ВНЕЗАПНО, стартовое значение при первом уровне. от него и будут
        считаться характеристики на всех остальных уровнях.
        
    '''
    return [0] + [round(starting_value*1.1**i) for i in range(9)]

class Hero(object):
   
    invulnerability = False
    kind = 'hero'

    def __init__(self, data):
        ''' hero [ˈhi(ə)rō]: герой, главный персонаж. как и во многих других играх,
        в shards. игрок выбирает себя героя, за которого будет сражаться. каждый
        герой уникален и предлагает свой классовые карты со своими способностями.

        https://www.youtube.com/watch?v=uGcsIdGOuZY

        входные данные:
        ----------
        data ~dict~:
            словарь значений level, xp и times_played героя.

        атрибуты, определяемые исходным классом:
        ----------
        level ~int~:
            уровень героя.
        xp ~int~:
            текущий опыт героя; по достижении определённого кол-ва опыта герой
            переходит на новый уровень.
        times_played ~int~:
            количество игр за героя.

        атрибуты, определяемые дочерними классами:
        ----------
        health_list ~list~:
            значения здоровья для каждого уровня улучшения.
            например, Hero.health[7] вернёт значение при 7 уровне улучшений.
        ability ~str~:
            способность, зависящая от героя и доступная вне зависимости от
            остального набора карт.
            допустимые значения строки:
            ~str~ 'firestarter':
                способность fire_hero, СЛУЧАЙНЫМ ОБРАЗОМ поджигает вражескую
                сущность или самого оппонента, нанося тем самым нанося им урон.
            ~str~ 'snowballs':
                snowballs — способность ice_hero, закидывает всех вражеских
                персонажей снежками, тем самым нанося им урон.
        
        прочие атрибуты:
        ----------
        health ~int~:
            используется для записи единиц здоровья на конкретном уровне улучшения.
        ~in development~
        '''
        for key, value in data.items():
            setattr(self, key, value)

    def get_data(self, name):
        ''' get_data: получение уникальных для конкретного игрока данных
        (например, получение здоровья на уровне улучшения героя). Грубо говоря,
        пост-инициализация.
        '''
        self.health = HealthInt(self.health_list[self.level])
        
class fire_hero(Hero):
    health_list = levelCounter(975)
    ability = 'firestarter'

"""class ice_hero(Hero):
    health_list = levelCounter(1300)
    ability = 'snowballs'"""

class Weapon(object):
    def __init__(self, data, effect=None,
                 hero_knockback_damage=0, creature_knockback_damage=0):

        ''' weapon [ˈwepən]: данное слово обозначает "оружие" в английском языке.
        для shards. это общий класс для двух типов оружия. оружие — основной
        инструмент битвы, что неудивительно, не правда ли?

        оружие можно использовать в любой момент битвы. однако, после нескольких
        использований оно уйдёт на "перезарядку" и будет недоступно в течение
        нескольких ходов.

        входные данные:
        ----------
        data ~dict~:
            словарь значений level, cards и times_played карты.

        атрибуты, определяемые исходным классом:
        ----------
        level ~int~:
            уровень карты.
        cards ~int~:
            текущее количество данной карты у игрока; по достижении
            определённого кол-ва карт игрок получает возможность улучшить карту.
        times_played ~int~:
            количество использований карты игроком.

        атрибуты, определяемые дочерними классами:
        ----------
        kind ~str~:
            тип карты-оружия. используется для определения необходимости ответного
            урона.
            допустимые значения строки:
                'melee': оружие ближнего боя. при использовании такого оружия
                герою наносится ответный урон, чтобы сымитировать ответный удар
                в ближнем бою. этот урон равен стандартной атаке оружия
                ближнего боя оппонента без эффектов.
                'ranged': оружие дальнего боя. при использовании такого оружия
                ответный урон не наносится, чтобы сымитировать эффект удалённой
                атаки без последствий. урон у таких карт ниже по сравнению с
                оружиями ближнего боя во имя баланса.
        damage_list ~list~:
            список из значений урона для каждого уровня улучшения.
            например, Weapon.damage[7] вернёт значение при 7 уровне улучшений.
        durability ~int~:
            количество возможных использований до перезарядки.
        recharge ~int~:
            количество ходов, необходимых для перезарядки.
        targets ~list~:
            список кортежей, обозначающих сторону и персонажа, на которых будет производиться атака.
            допустимые значения для элементов кортежа:
                для первого элемента ("side"): 'opponent' или 'player';
                для второго элемент ("character"): 'hero' или 'creature'

        effect ~in_development~:
            ?????
        '''

        for key, value in data.items():
            setattr(self, key, value)

    def get_data(self, name):
        self.name = name

        self.damage_normal = self.damage = self.damage_list[self.level]
        self.damage_lucky = round(self.damage*1.1)
        self.damage_unlucky = round(self.damage*0.9)
        self.damage_types = {
            'normal': self.damage_normal,
            'lucky': self.damage_lucky,
            'unlucky': self.damage_unlucky
            }

class battle_axe(Weapon):
    kind = 'melee'
    damage_list = levelCounter(100)
    durability = 3
    recharge = 1
    targets = IN_ORDER

"""class frozen_scythe(Weapon):
    kind = 'melee'
    damage_list = levelCounter(150)
    durability = 2
    recharge = 1
    targets = IN_ORDER

class flame_knuckels(Weapon):
    kind = 'melee'
    damage_list = levelCounter(175)
    durability = 2
    recharge = 2
    targets = IN_ORDER"""

class obsidian_spear(Weapon):
    kind = 'ranged'
    damage_list = levelCounter(50)
    durability = 3
    recharge = 1
    targets = IN_ORDER

"""class ice_bow(Weapon):
    kind = 'ranged'
    damage_list = levelCounter(75)
    durability = 2
    recharge = 2
    targets = IN_ORDER

class blaze_tomahawk(Weapon):
    kind = 'ranged'
    damage_list = levelCounter(40)
    durability = 4
    recharge = 1
    targets = IN_ORDER"""

class Creature(object):

    invulnerability = False
    alive = False

    kind = 'Creature'

    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        print(str(type(self)))
    
    def get_data(self, name):
        self.name = name

        self.health = HealthInt(self.health_list[self.level])

        self.damage_normal = self.damage = self.damage_list[self.level]
        self.damage_lucky = round(self.damage*1.1)
        self.damage_unlucky = round(self.damage*0.9)
        self.damage_types = {
            'normal': self.damage_normal,
            'lucky': self.damage_lucky,
            'unlucky': self.damage_unlucky
            }

class mad_bomber(Creature):
    health_list = levelCounter(125)
    damage_list = levelCounter(200)
    targets = IN_ORDER

"""class blizzard_lizzard(Creature):
    health_list = levelCounter(250)
    damage_list = levelCounter(75)
    targets = IN_ORDER

class fire_spirit(Creature):
    health_list = levelCounter(150)
    damage_list = levelCounter(150)
    targets = IN_ORDER"""
