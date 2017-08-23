from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

doc =  """
The English registration form for Public Goods Game
"""


class Constants(BaseConstants):
    name_in_url = 'PGGRegiEN'
    players_per_group = 4
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    def role(self):
        if self.id_in_group in [1, 2]:
            return 'low'
        else:
            return 'high'

    rule = models.PositiveIntegerField(
        choices=[
            [1, 'Equal sharing of the bonus'],
            [2, 'Equal payoff'],
            [3, 'No preference'],
        ],
        widget=widgets.RadioSelect()
    )

    rulestr = models.PositiveIntegerField(
        choices=[
            [1, 'Seems most fair'],
            [2, 'Easier to understand'],
            [3, 'Payoffs should not be differentiated'],
            [4, 'Uncertain about contributions of other players'],
            [5, 'No preference'],
        ],
        widget=widgets.RadioSelect()
    )


