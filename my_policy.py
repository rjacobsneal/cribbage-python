"""
Name: Reese Neal
NetID: rjn29
Email: reese.neal@yale.edu

This file defines the `MyPolicy` class for a Cribbage Agent that extends the `CribbagePolicy` class.

The `MyPolicy` class overrides the default behavior for selecting cards to keep/throw and updates the pegging strategy
with additional defensive considerations. The class introduces a custom greedy algorithm for throwing cards during the
hand phase by scoring all possible partitions based on rank probabilities of unseen cards. Additionally, it enhances
the pegging strategy by evaluating both offensive and defensive plays.

Class Definitions:
- MyPolicy: Implements custom card throwing and pegging logic, inheriting from CribbagePolicy.

Methods:
- keep: Uses a custom greedy throw algorithm to decide which cards to keep and throw.
- my_greedy_throw: Implements the logic for scoring possible throws by simulating turn cards.
- peg: Updates the pegging strategy with defensive considerations.
"""

from policy import (
    CribbagePolicy,
    CompositePolicy,
    GreedyThrower,
    GreedyPegger,
)
from deck import Card
import scoring
import random


class MyPolicy(CribbagePolicy):
    def __init__(self, game):
        self._policy = CompositePolicy(game, GreedyThrower(game), GreedyPegger(game))
        self._game = game

    def keep(self, hand, scores, am_dealer):
        # call custom greedy throw method
        keep, throw, net_score = self.my_greedy_throw(
            self._game, hand, 1 if am_dealer else -1
        )
        return keep, throw

    # custom greedy throw logic iteratively scores hand with possible turn cards
    def my_greedy_throw(self, game, hand, am_dealer):
        # get the deck of cards and remove the current hand to simulate unknown cards

        deck = game.deck()
        deck.remove(hand)

        # initialize probabilities for each rank (1-13), assuming even likelihood
        rank_probabilities = {i: 1 for i in range(1, 14)}
        # update probabilities by removing likelihood of the current hand's ranks
        for card in hand:
            rank = card.rank()
            rank_probabilities[rank] -= 0.25

        # helper function to split cards into keep and throw piles based on indices
        def split(indices):
            keep = []
            throw = []
            for i in range(len(hand)):
                if i in indices:
                    throw.append(hand[i])
                else:
                    keep.append(hand[i])
            return (
                keep,
                throw,
            )

        # list all possible partitions of cards to throw|keep from hand
        throw_indices = game.throw_indices()
        random.shuffle(throw_indices)
        throw_possibilities = list(map(lambda i: split(i), throw_indices))

        # initialize a dictionary to track cumulative scores for each possible throw
        cumulative_scores = {i: 0 for i in range(len(throw_possibilities))}

        # function to calculate hand and crib score given a specific turn card
        def iterate_score(keep, throw, turn_card):
            hand_score = scoring.score(game, keep, turn_card, False)[0]
            crib_score = am_dealer * scoring.score(game, throw, turn_card, True)[0]
            return hand_score + crib_score

        # evaluate score for each throw by simulating turn card at relative probabilities
        for i, (keep, throw) in enumerate(throw_possibilities):
            for rank, probability in rank_probabilities.items():
                # only consider rank, considering unique suits not worth extra computation
                prototypical_card = Card(rank, "S")
                cumulative_scores[i] += probability * iterate_score(
                    keep, throw, prototypical_card
                )

        # identify best keep|throw partition
        best_combination_index = max(cumulative_scores, key=cumulative_scores.get)

        # retrieve the corresponding hands and score
        best_keep, best_throw = throw_possibilities[best_combination_index]
        best_score = cumulative_scores[best_combination_index]

        return best_keep, best_throw, best_score

    # update pegging strategy with defensive considerations
    def peg(self, cards, history, turn, scores, am_dealer):
        best_card = None
        best_score = None

        # for keeping totals low enough to avoid a next-player point
        card_below_5 = None
        closest_sum_below_5 = None

        # for pushing totals towards end-of-round quickly
        card_above_15 = None
        highest_sum_above_15 = None

        # evaluate card in hand for pegging
        for card in cards:
            # evaluate score and total for playing the considered card
            score = history.score(self._game, card, 0 if am_dealer else 1)
            current_total = history._total + card.rank()

            # update if it is the best scoring card
            if score is not None and (best_score is None or score > best_score):
                best_score = score
                best_card = card

            # if it doesn't score, perform extra checks to determine defensive value
            if score == 0:
                # prioritize cards that keep the total under 5
                if current_total < 5:
                    if (
                        closest_sum_below_5 is None
                        or current_total > closest_sum_below_5
                    ):
                        card_below_5 = card
                        closest_sum_below_5 = current_total

                # prioritize high cards that keep the total above 15 and not 21 (easy next-player point)
                elif current_total > 15 and current_total != 21:
                    if (
                        highest_sum_above_15 is None
                        or current_total > highest_sum_above_15
                    ):
                        card_above_15 = card
                        highest_sum_above_15 = current_total

        # if there's a scoring opportunity, play the best scoring card
        if best_card is not None and best_score > 0:
            return best_card

        # otherwise, play the most defensive card
        if card_below_5 is not None:
            return card_below_5

        if card_above_15 is not None:
            return card_above_15

        # fallback
        return best_card
