import GameMgr
import AutoPlay
import AutoPlayUtilsCy
import numpy as np
from time import perf_counter
import cProfile

# ------------------------------
# Testing Functions

def test_Utils_calc_metrics1():

    b1 = [[0, 0, 0, 0],
          [0, 0, 0, 8],
          [0, 0, 4, 16],
          [2, 4, 8, 128]]
    t1 = np.array(b1)
    num1 = AutoPlayUtilsCy.calc_metrics1(t1, 2.0)
    print(f"metric1 = {num1} | Actual = 0  ", end="")

    print("PASSED") if num1 == 141312 else print("FAILED")

    b1 = [[4, 16, 2, 256],
          [4, 16, 32, 0],
          [4, 128, 8, 2],
          [2, 16, 2, 0]]
    t1 = np.array(b1)
    num1 = AutoPlayUtilsCy.calc_metrics1(t1, 2.0)
    print(f"metric1 = {num1} | Actual = 263168  ", end="")

    print("PASSED") if num1 == 263168 else print("FAILED")

    b1 = [[512, 4, 0, 0],
          [128, 4, 2, 0],
          [64, 256, 16, 2],
          [16, 32, 8, 2]]
    t1 = np.array(b1)
    num1 = AutoPlayUtilsCy.calc_metrics1(t1, 2.0)
    print(f"metric1 = {num1} | Actual = 608256  ", end="")

    print("PASSED") if num1 == 608256 else print("FAILED")

def test_Utils_calc_metrics3():

    b1 = [[0, 0, 0, 0],
          [0, 0, 0, 8],
          [0, 0, 4, 16],
          [2, 4, 8, 128]]
    t1 = np.array(b1)
    num1 = AutoPlayUtilsCy.calc_metrics3(t1, 2.0)
    print(f"metric1 = {num1} | Actual = 35364  ", end="")

    print("PASSED") if num1 == 35364 else print("FAILED")

    b1 = [[4, 16, 2, 256],
          [4, 16, 32, 0],
          [4, 128, 8, 2],
          [2, 16, 2, 0]]
    t1 = np.array(b1)
    num1 = AutoPlayUtilsCy.calc_metrics3(t1, 2.0)
    print(f"metric1 = {num1} | Actual = 67266  ", end="")

    print("PASSED") if num1 == 67266 else print("FAILED")

    b1 = [[512, 4, 0, 0],
          [128, 4, 2, 0],
          [64, 256, 16, 2],
          [16, 32, 8, 2]]
    t1 = np.array(b1)
    num1 = AutoPlayUtilsCy.calc_metrics3(t1, 2.0)
    print(f"metric1 = {num1} | Actual = 154648  ", end="")

    print("PASSED") if num1 == 154648 else print("FAILED")

    b1 = [[128, 4, 0, 0],
          [128, 4, 2, 0],
          [64, 256, 512, 2],
          [16, 32, 8, 2]]
    t1 = np.array(b1)
    num1 = AutoPlayUtilsCy.calc_metrics3(t1, 2.0)
    print(f"metric1 = {num1} | Actual = 0  ", end="")

    print("PASSED") if num1 == 0 else print("FAILED")


def test_calc_metrics3():

    b1 = [[0, 0, 0, 0],
          [0, 0, 0, 8],
          [0, 0, 4, 16],
          [2, 4, 8, 128]]
    t1 = np.array(b1)
    num1 = AutoPlay.calc_metrics3(t1)
    print(f"metric1 = {num1} | Actual = 35364  ", end="")

    print("PASSED") if num1 == 35364 else print("FAILED")

    b1 = [[4, 16, 2, 256],
          [4, 16, 32, 0],
          [4, 128, 8, 2],
          [2, 16, 2, 0]]
    t1 = np.array(b1)
    num1 = AutoPlay.calc_metrics3(t1)
    print(f"metric1 = {num1} | Actual = 67266  ", end="")

    print("PASSED") if num1 == 67266 else print("FAILED")

    b1 = [[512, 4, 0, 0],
          [128, 4, 2, 0],
          [64, 256, 16, 2],
          [16, 32, 8, 2]]
    t1 = np.array(b1)
    num1 = AutoPlay.calc_metrics3(t1)
    print(f"metric1 = {num1} | Actual = 154648  ", end="")

    print("PASSED") if num1 == 154648 else print("FAILED")

    b1 = [[128, 4, 0, 0],
          [128, 4, 2, 0],
          [64, 256, 512, 2],
          [16, 32, 8, 2]]
    t1 = np.array(b1)
    num1 = AutoPlay.calc_metrics3(t1)
    print(f"metric1 = {num1} | Actual = 0  ", end="")

    print("PASSED") if num1 == 0 else print("FAILED")


def print_tree_bfs(tree):

    print("Tree:", end="")
    q1 = [tree]
    q2 = []
    level = 0
    while q1:
        level += 1
        for node in q1:
            print("|", end="") if node else print("-", end="")

            if node and node.next:
                for next1 in node.next:
                    q2.append(next1)
        print(f"\nLevel {level}: {len([q2 for i in q2 if i is not None])}/{len(q2)} : ", end="")
        q1 = q2
        q2 = []

    print("\n")


def run_num_moves(start_tiles, num_moves, tree_depth, topx, calc_option):

    game1 = GameMgr.Game(None)
    game1.add_random_tile(commit=True)
    ap1 = AutoPlay.AutoPlayer(game1, tree_depth, topx, calc_option)

    for _ in range(num_moves):
        valid_move, tiles, score, num_empty = ap1.auto_move()

    return tiles, score


def play_games(num, tree_depth, topx, calc_option, calc_mult):

    for i in range(num):

        game1 = GameMgr.Game(None)
        game1.add_random_tile(commit=True)

        ap1 = AutoPlay.AutoPlayer(game1, tree_depth, topx, calc_option, mult_base=calc_mult)

        while not ap1.game.game_over:
            for _ in range(2000):
                ap1.auto_move()
                if ap1.game.game_over:
                    break

    return ap1


if __name__ == '__main__':

    # Test calc_metrics0()
    # test_Utils_calc_metrics1()

    # # Test calc_metrics3()
    # start = perf_counter()
    cProfile.run("ap = play_games(1, 2, 2, 1)")
    # end = perf_counter()
    # print(f"Duration: {end-start} seconds")
    print(ap)

    # test_calc_metrics3()
