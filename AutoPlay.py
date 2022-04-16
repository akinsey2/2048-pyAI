
"""
This file contains key classes to enable AutoPlay of the game (2048).
- AutoPlayer, MoveTree

The functionality of each can be configured through parameters passed into AutoPlayer

This file requires supporting functions from either AutoPlayUtilsCy or AutoPlayUtilsPy
AutoPlayUtilsCy is recommended for much faster processing.
"""

from math import floor
from numpy import zeros, random, single, int64
# from pprint import pp
# import cProfile

import AutoPlayUtilsPy
import AutoPlayUtilsCy

SIZE = int(4)

# !!! Important configuration flag. Determines if UtilsPy or UtilsCy is used,
# with a huge impact on execution speed.
USE_CYTHON = True

# ------------------------------


class AutoPlayer:
    """
    Each instance enables autoplay of the GameMgr "game" passed into constructor.

    ----- Methods -----
    - get_move()
        Determine and return the "best" next game move direction.
    - auto_move()
        Determines best move with get_move() and takes it, changing game state.
    """

    def __init__(self, game, tree_depth=6, topx_perc=0.05, calc_option=3, rand=None, mult_base=2.0):
        """
        :param game: GameMgr.Game instance holding current game state

        Parameters configuring how the AutoPlayer plays the game

        :param tree_depth: the level of depth of the 4-ary tree MoveTree
        :param topx_perc: float 0.01-0.05. Controls % of forward move scores being "averaged"
        :param calc_option: int 0-4. Decides which overall strategy is used.
        :param rand: Numpy random Generator. Default None --> new Generator created
        :param mult_base: float 1.0-5.0. Parameter of calc_metricX() functions

        NOTE:   If Cython is used, then Autoplay MUST contain random numbers.
                MUCH faster to generate all random numbers upfront w/NumPy vs. on the fly
                self.rand_idx must be incremented each time one is used.

                If Cython is NOT used, (speed not critical) then rands not needed
                Rands can be generated on-the-fly by GameMgr.Game.rand
        """
        # GameMgr.Game object stores current game state: tiles, score, etc
        self.game = game

        self.tree_depth = tree_depth
        self.tree_size = 0
        self.topx_perc = topx_perc
        self.calc_option = calc_option
        self.mult_base = mult_base

        if USE_CYTHON:

            # Enable optional passing of fixed seed NumPy number Generator for testing
            if rand is None:
                self.rand = random.default_rng()
            else:
                self.rand = rand

            # Calculate how many random numbers are needed based on move tree size
            rand_nums = int(sum([4**i for i in range(tree_depth+1)])*2*4000)
            self.rands = self.rand.random(rand_nums, dtype=single)
            self.rand_idx = int(0)

        else:
            self.rand = None

    def __repr__(self):

        out = list()
        out.append("-"*30 + "\n")
        out.append(f"AutoPlay - Tree Depth: {self.tree_depth} | " +
                   f"TopX: {self.topx_perc}%, {floor(self.tree_size*self.topx_perc)} | " +
                   f"Calc Opt: {self.calc_option} | Mult Base: {self.mult_base} | " +
                   f"Rands Length: {self.rands.size} | rand_idx: {self.rand_idx}\n")
        out.append(repr(self.game))

        return "".join(out)

    def get_move(self):
        """
        Determine and return the "best" next game move direction.

        Looks at all possible future moves (tree_depth) speculatively using MoveTree.
        Traverses MoveTree to see which current move leads to the best likely outcome

        Used by auto_move() and ui.autoplay_move()

        :return: int 0-3. ((0: Up, 1: Right, 2: Down, 3: Left)
        """

        self.tree_size = 0
        move_tree = MoveTree(None, self.game.tiles, self.game.score, self)

        # # DEBUG
        # print_tree_bfs(move_tree)

        move_metrics = list()

        # Search "forward" in move tree
        # Record the "max_metrics" found in tree below each initial "move_score[i]"
        for move_dir in range(SIZE):

            # If this was an invalid move (no node exists), metric is -2
            if move_tree.next[move_dir] is None:
                move_metrics.append(-2.0)
                continue

            # If this move would displace a max from a corner, metric is -1
            if move_tree.metric > 0 and move_tree.next[move_dir].metric == 0:
                move_metrics.append(-1.0)
                continue

            # Experiments indicate top ~?% averaged yields best results
            topx_num = max(1, floor(self.tree_size*self.topx_perc))
            max_metrics = zeros(topx_num, dtype=int64)
            max_metrics[-1] = move_tree.next[move_dir].metric
            max_metrics = AutoPlayUtilsPy.node_tree_max_DFS(move_tree.next[move_dir], max_metrics)
            move_metrics.append(max_metrics.sum() / float(topx_num))

        # # DEBUG
        # print(f"move_metrics: Up: {move_metrics[0]}, Right: {move_metrics[1]}, " +
        #       f"Down: {move_metrics[2]}, Left: {move_metrics[3]}")

        # Important...multiple metrics can be the same
        max_met = max(move_metrics)
        maxs = [(i, move_metrics[i]) for i in range(4) if move_metrics[i] == max_met]

        # If only one max, or no good move, pick it/one.
        if len(maxs) == 1 or max_met <= 0:
            best_move = move_metrics.index(max_met)

        # If there is more than one equally good move
        else:
            print(f"MORE THAN ONE BEST MOVE: move_metrics = {move_metrics}")
            best_move = move_metrics.index(max_met)

        return best_move

    def auto_move(self):
        """
        Determines best move with get_move() and takes it, changing game state.
        Uses faster Cython Utils, if possible.

        :return: bool. True if move was valid, otherwise false."""

        if self.game.game_over:
            return

        best_move = self.get_move()

        if USE_CYTHON:
            valid_move, tiles2, self.game.score = \
                AutoPlayUtilsCy.move_tiles(best_move, self.game.tiles, self.game.score)
        else:
            valid_move, _, _, _ = self.game.move_tiles(best_move, True)

        if valid_move:
            if USE_CYTHON:
                self.game.tiles, self.game.num_empty, self.rand_idx = \
                    AutoPlayUtilsCy.add_random_tile(tiles2, self.rands, self.rand_idx)
                self.game.num_moves += 1

                if self.game.num_empty == 0:
                    self.game.game_over = self.game.check_game_over(self.game.tiles)
            else:
                self.game.add_random_tile(commit=True)

        return valid_move

# ------------------------------


class MoveTree:
    """
    Nodes of individual game state linked to form 4-ary Tree Structure.

    Top of tree is the current actual game state.
    Level 1 of tree contains 4 game states after the 4 possible moves
    Level 2 of tree contains 16 game states, and so on

    Tree is created recursively in __init__ function to Level (tree_depth)

    For each Node, a metric of the "quality" of the board is computed and saved.

    """

    def __init__(self, prev, tiles, score, ap):
        """
        :param prev: MoveTree node. link to previous node in tree
        :param tiles: NumPy 2D-array of game board of current node
        :param score: int. score of current board
        :param ap: AutoPlayer object
        """

        # self.tiles = tiles.copy()
        self.prev = prev
        self.score = score
        self.level = 0 if (prev is None) else (prev.level + 1)
        self.metric = 0

        if USE_CYTHON:  # Use fast Cython functions
            if ap.calc_option == 0:
                self.metric = AutoPlayUtilsCy.calc_metrics0(tiles)
            elif ap.calc_option == 1:
                self.metric = AutoPlayUtilsCy.calc_metrics1(tiles, ap.mult_base)
            elif ap.calc_option == 2:
                self.metric = AutoPlayUtilsCy.calc_metrics2(tiles, ap.mult_base)
            elif ap.calc_option == 3:
                self.metric = AutoPlayUtilsCy.calc_metrics3(tiles, ap.mult_base)

        else:   # Use slower Python functions
            if ap.calc_option == 0:
                self.metric = AutoPlayUtilsPy.calc_metrics0(tiles)
            elif ap.calc_option == 1:
                self.metric = AutoPlayUtilsPy.calc_metrics1(tiles)
            elif ap.calc_option == 2:
                self.metric = AutoPlayUtilsPy.calc_metrics2(tiles)
            elif ap.calc_option == 3:
                self.metric = AutoPlayUtilsPy.calc_metrics3(tiles)

        # Base Case: If already traversed to proper tree depth, stop
        if self.level > ap.tree_depth - 1:
            self.next = None
            return

        # Recursively build next level of tree
        else:
            self.next = []

            # Children Moves: 0 - Up, 1 - Right, 2 - Down, 3 - Left
            for direction in range(4):

                # Move Tiles
                if USE_CYTHON:
                    valid_move, new_tiles, new_score = \
                        AutoPlayUtilsCy.move_tiles(direction, tiles, score)
                else:
                    valid_move, _, new_tiles, new_score = \
                        ap.game.move_tiles(direction, False, tiles, score)

                # If valid move, add random tile
                if valid_move:

                    if USE_CYTHON:
                        new_tiles, _, ap.rand_idx = \
                            AutoPlayUtilsCy.add_random_tile(new_tiles, ap.rands, ap.rand_idx)
                    else:
                        new_tiles, _, _, ap.rand_idx = \
                            ap.game.add_random_tile(commit=False, tiles=new_tiles)

                    ap.tree_size += 1

                    self.next.append(MoveTree(self, new_tiles, new_score, ap))

                else:
                    self.next.append(None)

    def __repr__(self):

        out = list()
        out.append("-"*20 + "\n")
        out.append(f"Tree Level: {self.level}  |  Score: {self.score}")
        out.append(f"  |  Metric: {self.metric}\n")

        return "".join(out)


if __name__ == '__main__':

    from numpy import array
    print("This file is not designed to be run on its own.")
    # tiles1 = [[0, 2, 2, 4],
    #          [0, 4, 4, 8],
    #          [0, 8, 8, 16],
    #          [16, 32, 32, 2048]]
    #
    # AutoPlayUtilsCy.calc_metrics1(array(tiles1))

    # import GameMgr

    # game1 = GameMgr.Game(None, None, 0)
    # game1.add_random_tile(commit=True)
    # ap = AutoPlayer(game1, tree_depth=5)
    # ap.auto_move()




