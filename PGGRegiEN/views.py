from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants

class Introduction(Page):
    """Description of the game: How to play and returns expected"""
    def is_displayed(self):
        return self.round_number == 1
    form_model = models.Player
    form_fields = ['rule', 'rulestr']


page_sequence = [
    Introduction,
]
