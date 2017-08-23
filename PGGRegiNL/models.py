from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

doc = """
The Dutch registration form for Public Goods Game
"""


class Constants(BaseConstants):
    name_in_url = 'PGGRegiNL'
    players_per_group = 4
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    def role(self):
        if self.id_in_group in [1, 2]:
            return 'lage'
        else:
            return 'hoge'

    rule = models.PositiveIntegerField(
        choices=[
            [1, 'Gelijk deel van de bonus'],
            [2, 'Gelijke verdiensten'],
            [3, 'Geen voorkeur'],
        ],
        widget=widgets.RadioSelect()
    )

    rulestr = models.PositiveIntegerField(
        choices=[
            [1, 'Is het eerlijkst'],
            [2, 'Is het gemakkelijkst te begrijpen'],
            [3, 'Verdiensten zouden niet verschillend mogen zijn'],
            [4, 'Onzekerheid over de bijdrages van andere spelers'],
            [5, 'Geen voorkeur'],
        ],
        widget=widgets.RadioSelect()
    )


