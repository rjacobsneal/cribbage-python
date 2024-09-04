from policy import CribbagePolicy, CompositePolicy, GreedyThrower, GreedyPegger

class MyPolicy(CribbagePolicy):
    def __init__(self, game):
        self._policy = CompositePolicy(game, GreedyThrower(game), GreedyPegger(game))

        
    def keep(self, hand, scores, am_dealer):
        return self._policy.keep(hand, scores, am_dealer)


    def peg(self, cards, history, turn, scores, am_dealer):
        return self._policy.peg(cards, history, turn, scores, am_dealer)



    

                                    
