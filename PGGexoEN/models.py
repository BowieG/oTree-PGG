from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

doc = """The English version of Public Goods Game with exogeneous threshold
"""


class Constants(BaseConstants):
    name_in_url = 'PGGexoEN'
    players_per_group = 4
    num_rounds = 12

    endowment = c(20)
    efficiency_factor = 1.6
    cost_parameter_low = 0.6
    cost_parameter_high = 1.2

    participation_fee = 5
    euro_per_point = 0.1

    phase1 = [1, 2, 3, 4]
    phase2 = [5, 6, 7, 8]
    phase3 = [9, 10, 11, 12]
    """"List of round numbers which are part of a distribution rule. """

    paying_phase1 = random.choice(phase1)
    paying_phase2 = random.choice(phase2)
    paying_phase3 = random.choice(phase3)
    """"The random round generator for the three payment periods to calculate money payoff."""

    thresholdexo = [30, 30, 30, 30, 30, 30, 45, 55, 30, 65, 70, 45]
    """"The threshold levels in each round, starting in round 1 to round 12."""


class Subsession(BaseSubsession):

    def vars_for_admin_report(self):
        contributions = [p.contribution for p in self.get_players() if p.contribution is not None]
        return {
            'total_contribution': sum(contributions),
            'min_contribution': min(contributions),
            'max_contribution': max(contributions),
        }


class Group(BaseGroup):

    distribution_rule = models.CharField()
    threshold = models.CurrencyField()
    bonus = models.CurrencyField()
    total_contribution = models.CurrencyField()
    avg_contribution = models.CurrencyField()
    avg_payoff = models.CurrencyField()

    def set_distribution_rule(self):
        if self.round_number in Constants.phase1:
            self.distribution_rule = 'Equal share of the bonus'
        elif self.round_number in Constants.phase2:
            self.distribution_rule = 'Equal payoff'
        elif self.round_number == min(Constants.phase3):
            if sum([p.prule for p in self.get_players() if p.prule is not None]) < 2:
                self.distribution_rule = 'Equal share of the bonus'
            elif sum([p.prule for p in self.get_players() if p.prule is not None]) > 2:
                self.distribution_rule = 'Equal payoff'
            else:
                self.distribution_rule = random.choice\
                    (['Equal share of the bonus', 'Equal payoff'])
        else:
            self.distribution_rule = self.in_round(self.round_number - 1).distribution_rule
            if self.in_round(self.round_number - 1).distribution_rule == 'Equal share of the bonus exception':
                self.distribution_rule = 'Equal payoff'

            """"This sets the distribution rule of each phase."""

    def set_threshold(self):
        for x in range(1, 13):
            if self.round_number == x:
                self.threshold = Constants.thresholdexo[x-1]

                """the variable x is every number between 1 and 13, excluding 13.
                    When the round number is equal to the variable x, it will look
                    up the element in thresholdexo list of threshold levels."""

    def set_payoffs(self):
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        self.avg_contribution = self.total_contribution / Constants.players_per_group
        self.bonus = Constants.efficiency_factor * self.threshold

        for p in self.get_players():
            if 'low' in p.role():
                p.value = (Constants.endowment - Constants.cost_parameter_low * p.contribution)
            else:
                p.value = (Constants.endowment - Constants.cost_parameter_high * p.contribution)

                """"p.value is the amount of points a player has left after contributing."""

        if self.distribution_rule == 'Equal payoff':
            if self.total_contribution < self.threshold:
                for p in self.get_players():
                    p.payoff_r = p.value
            else:
                for p in self.get_players():
                    p.payoff_r = (sum([p.value for p in self.get_players()]) + self.bonus)\
                                 / Constants.players_per_group

                    """"When threshold is met, payoff is calculated by summing the p.values,
                        adding them to the bonus, and dividing it by the amount of players 
                        per group (4 in this case)"""

                    p.check_r = p.payoff_r - p.value
                    if any(p.check_r < 0 for p in self.get_players() if p.check_r is not None):
                        self.distribution_rule = 'Equal share of the bonus exception'
                        p.payoff_r = p.value + (self.bonus / Constants.players_per_group)

                    """"An exception to the Equal payoff occurs when p.payoff_r is less
                        than p.value, resulting in a value loss for a player. In that case
                        the distribution rule is adjusted to equal share of the bonus"""

        else:
            if self.total_contribution < self.threshold:
                for p in self.get_players():
                    p.payoff_r = p.value
            else:
                for p in self.get_players():
                    p.payoff_r = p.value + (self.bonus / Constants.players_per_group)

                    """"Equal share of the bonus is calculated by adding the individual's p.value
                     with an equal share of the bonus, if the threshold is met."""

        self.avg_payoff = sum([p.payoff_r for p in self.get_players()]) / Constants.players_per_group


class Player(BasePlayer):

    def role(self):
        if self.id_in_group in [1, 2]:
            return 'low'
        else:
            return 'high'

    contribution = models.CurrencyField(
        min=0, max=Constants.endowment,
        doc="""The amount contributed by the player.""",
    )

    value = models.CurrencyField(
        doc=""""The player's individual payoff before bonus is taken into account."""
    )

    prule = models.PositiveIntegerField(
        choices=[
            [0, 'Equal share of the bonus'],
            [1, 'Equal payoff']
        ],
        widget=widgets.RadioSelect(),
        doc=""""The player's vote for distribution rule in phase 3."""
    )

    payoff_r = models.CurrencyField(
        doc=""""payoff in a certain round"""
    )

    check_r = models.FloatField(
        doc=""""The check for Equal payoff viability, if negative value,
         it's not viable"""
    )

    earnings_phase1 = models.CurrencyField()
    earnings_phase2 = models.CurrencyField()
    earnings_phase3 = models.CurrencyField()
    paid = models.FloatField()

    def set_payoff(self):
        self.earnings_phase1 = self.in_round(Constants.paying_phase1).payoff_r
        self.earnings_phase2 = self.in_round(Constants.paying_phase2).payoff_r
        self.earnings_phase3 = self.in_round(Constants.paying_phase3).payoff_r
        self.payoff = self.earnings_phase1 + self.earnings_phase2 + self.earnings_phase3
        self.paid = (self.payoff * Constants.euro_per_point) + Constants.participation_fee

        """"The calculation of the payoffs during the random periods
            and total earnings as well as the to be paid amount."""