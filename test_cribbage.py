import sys
import time
import math
import itertools as it

from policy import CompositePolicy, RandomThrower, RandomPegger, GreedyThrower, GreedyPegger
from cribbage import Game, evaluate_policies
from my_policy import MyPolicy

if __name__ == "__main__":
    games = 2
    run_time = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == "--time":
            run_time = int(sys.argv[2]);
            games = 1000
        else:
            games = int(sys.argv[1])
    
    game = Game()
    benchmark = CompositePolicy(game, GreedyThrower(game), GreedyPegger(game))
    submission = MyPolicy(game)
    total_games = 0

    match_values = list(it.chain(range(1, 4), range(-3, 0)))
    results = {value: 0 for value in match_values}
    start_time = time.time()
    while total_games == 0 or time.time() - start_time < run_time:
        batch_results = evaluate_policies(game, submission, benchmark, games)
        total_games += games
        for v in batch_results[3]:
            results[v] += batch_results[3][v]

    sum_squares = sum(results[v] * v * v for v in match_values)
    sum_values = sum(results[v] * v for v in match_values)
    mean = sum_values / total_games
    variance = sum_squares / total_games - math.pow(sum_values / total_games, 2)
    stddev = math.sqrt(variance)
    
    print("NET:", mean)
    print("CONF:", mean - 2 * (stddev / math.sqrt(total_games)))
    print(results)
