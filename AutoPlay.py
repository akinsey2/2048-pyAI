import numpy as np
from copy import deepcopy
import Utils
import cProfile
import GameMgr
from pprint import pp

SIZE = int(4)
USE_CYTHON = False


# ****************************************
class AutoPlayer:

    def __init__(self, game, tree_depth=4, topx=4, calc_option=1, rand=None):

        # GameMgr.Game object stores current game state: tiles, score, etc
        self.game = game

        # self.move_tree = None
        self.tree_depth = tree_depth
        self.topx = topx
        self.calc_option = calc_option

        # If Cython is used, then Autoplay must contain random numbers.
        # MUCH faster to generate random numbers upfront w/NumPy vs. on the fly
        # self.rand_idx must be incremented each time one is used.
        if USE_CYTHON:

            # Enable optional passing of fixed seed NumPy number generator for testing
            if rand is None:
                self.rand = np.random.default_rng()
            else:
                self.rand = rand

            # Calculate how many random numbers are needed based on move tree size
            rand_nums = sum([4**i for i in range(tree_depth+1)])*2*4000
            self.rands = self.rand.random(rand_nums, dtype=np.float32)
            self.rand_idx = int(0)

        # If Cython is NOT used, (speed not critical)
        # then AutoPlay does not need to contain random numbers
        # Rands will be generated by GameMgr.Game.rand
        else:
            self.rand = None

    def __repr__(self):
        out = list()
        out.append("-"*30 + "\n")
        out.append(f"AutoPlay - Tree Depth: {self.tree_depth} | " +
                   f"TopX: {2**self.topx} | Calc: {self.calc_option} \n")
        out.append(repr(self.game))

        return "".join(out)

    def get_move(self):

        move_tree = MoveNode(None, self.game.tiles, self.game.score, self)

        # DEBUG
        # print_tree_bfs(move_tree)

        move_metrics = list()

        # Search "forward" in move tree
        # Record the "max metric" found in tree below each "move_score[i]"
        # move_dir=0: Up, move_dir=1: Right, move_dir=2: Down, move_dir=3: Left
        for move_dir in range(SIZE):

            # If this was an invalid move (no node exists).
            if move_tree.next[move_dir] is None:
                move_metrics.append(0.0)
                continue
            else:
                topx_num = 2 ** self.topx
                max_metrics = np.zeros(topx_num, dtype=np.int32)
                max_metrics[-1] = move_tree.next[move_dir].metric
                max_metrics = node_tree_max_DFS(move_tree.next[move_dir], max_metrics)
                move_metrics.append(max_metrics.sum() / float(topx_num))

        best_move = move_metrics.index(max(move_metrics))

        return best_move

    def auto_move(self):

        if self.game.game_over:
            return

        # DEBUG
        # print(f"rand_idx = {self.rand_idx}")

        best_move = self.get_move()

        # DEBUG
        # options = ["Up", "Right", "Down", "Left"]
        # print(f"Best Move: {options[best_move]}")
        # ans = input("Continue? ")
        # if ans in ["N", "n"]:
        #     quit()

        if USE_CYTHON:
            valid_move, tiles2, self.game.score = \
                Utils.move_tiles(best_move, self.game.tiles, self.game.score, 4)
        else:
            valid_move, _, _, _ = self.game.move_tiles(best_move, True)

        if valid_move:
            if USE_CYTHON:
                self.game.tiles, self.game.num_empty, self.rand_idx = \
                    Utils.add_random_tile(tiles2, self.rands, self.rand_idx, 4)
            else:
                self.game.add_random_tile(commit=True)

        if not valid_move and self.game.num_empty == 0:
            self.game.game_over = True

        return valid_move


# ****************************************
# Nodes of individual game state
# Linked to form a 4-ary Tree structure
# of all likely future game states after "tree_depth" moves
class MoveNode:

    # Initializes Node AND
    # Recursively builds 4-ary tree to "TREE_DEPTH"
    def __init__(self, prev, tiles, score, ap):

        # self.tiles = tiles.copy()
        self.prev = prev
        self.score = score
        self.level = 0 if (prev is None) else (prev.level + 1)

        if USE_CYTHON:  # Use fast Cython functions
            if ap.calc_option == 0:
                self.metric = Utils.calc_metrics0(tiles)
            elif ap.calc_option == 1:
                self.metric = Utils.calc_metrics1(tiles)

        else:   # Use slower Python functions
            if ap.calc_option == 0:
                self.metric = calc_metrics0(tiles)
            elif ap.calc_option == 1:
                self.metric = calc_metrics1(tiles)

        # Base Case: If already traversed to proper tree depth, stop
        if self.level > ap.tree_depth - 1:
            self.next = None

        # Recursively build next level of tree
        else:
            self.next = []

            # Children Moves: 0 - Up, 1 - Right, 2 - Down, 3 - Left
            for direction in range(4):

                # Move Tiles
                if USE_CYTHON:
                    valid_move, new_tiles, new_score = \
                        Utils.move_tiles(direction, tiles, score, SIZE)
                else:
                    valid_move, _, new_tiles, new_score = \
                        ap.game.move_tiles(direction, False, tiles, score)

                # If valid move, add random tile
                if valid_move:

                    if USE_CYTHON:
                        new_tiles, _, ap.rand_idx = \
                            Utils.add_random_tile(new_tiles, ap.rands,
                                                  ap.rand_idx, 4)
                    else:
                        new_tiles, _, _, ap.rand_idx = \
                            ap.game.add_random_tile(commit=False, tiles=new_tiles)

                    self.next.append(MoveNode(self, new_tiles, new_score, ap))

                else:
                    self.next.append(None)

    def __repr__(self):

        out = list()
        out.append("-"*20 + "\n")
        out.append(f"Tree Level: {self.level}  |  Score: {self.score}")
        out.append(f"  |  Metric: {self.metric}\n")

        return "".join(out)


# ****************************************
# General Functions

def node_tree_max_DFS(node, max_metrics):

    # Save metric of current node, if in (2**topx) largest in tree
    if node.metric > max_metrics[0]:
        max_metrics[0] = node.metric
        max_metrics.sort()

    # Base Case: Reached bottom of game tree
    if node.next is None:
        return max_metrics

    # Else, recurse deeper.
    for move_dir in range(SIZE):

        if node.next[move_dir] is None:
            continue
        else:
            node_tree_max_DFS(node.next[move_dir], max_metrics)

    return max_metrics


# Simplest metric...Rewards Upper-Right aligned chain.
def calc_metrics0(tiles):

    metric = int(tiles[0][3]*256 + tiles[1][3]*128 +
                 tiles[2][3]*64 + tiles[3][3]*32 +
                 tiles[3][2]*16 + tiles[2][2]*8 +
                 tiles[1][2]*4 + tiles[0][2]*2)

    return metric


# More advanced metric. Rewards largest tile in corner, and best overall "chain",
# without regard to location on board
def calc_metrics1(tiles):

    # tiles_byval = {0: [], 2: [], 4: [], 8: [], 16: [], 32: [], 64: [], 128: [],
    #                256: [], 512: [], 1024: [], 2048: [], 4096: [], 8192: [], 16384: []}

    # # Populate tiles_byval with indeces of tiles
    # for row in range(SIZE):
    #     for col in range(SIZE):
    #         val = tiles[row][col]
    #         tiles_byval[int(val)].append([row, col])

    graph = {(0, 0): ((1, 0), (0, 1)),
             (0, 1): ((0, 0), (1, 1), (0, 2)),
             (0, 2): ((0, 1), (1, 2), (0, 3)),
             (0, 3): ((0, 2), (1, 3)),
             (1, 0): ((0, 0), (1, 1), (2, 0)),
             (1, 1): ((0, 1), (1, 2), (2, 1), (1, 0)),
             (1, 2): ((0, 2), (1, 3), (2, 2), (1, 1)),
             (1, 3): ((0, 3), (2, 3), (1, 2)),
             (2, 0): ((1, 0), (2, 1), (3, 0)),
             (2, 1): ((1, 1), (2, 2), (3, 1), (2, 0)),
             (2, 2): ((1, 2), (2, 3), (3, 2), (2, 1)),
             (2, 3): ((1, 3), (3, 3), (2, 2)),
             (3, 0): ((2, 0), (3, 1)),
             (3, 1): ((2, 1), (3, 2), (3, 0)),
             (3, 2): ((2, 2), (3, 3), (3, 1)),
             (3, 3): ((2, 3), (3, 2))}

    # Find greatest tile(s) on board, the starting point of the "chain" calculation(s)
    max_val = 0
    maxs = []
    for row in range(SIZE):
        for col in range(SIZE):

            val = tiles[row][col]

            if val < max_val:
                continue
            elif val > max_val:
                max_val = val
                maxs.clear()
                maxs.append([val, row, col])
            else:   # Equal
                maxs.append([val, row, col])

    # --- Master Loop: Traverses chain(s) and calculates chain quality metric/score
    metrics = []
    for (val, row, col) in maxs:

        end_of_chain = False    # Have reached the end of the chain?
        metric = 0              # "Score" metric for the overall chain

        # Start with "max" tile
        chain_vals = [val]
        chain_idxs = [(row, col)]

        # --- Process next 3 (or SIZE-1) "largest" tiles
        for _ in range(SIZE-1):

            max_adj_val = 0
            max_adj_idx = (None, None)

            # Explore adjacent tiles for largest
            for (a_row, a_col) in graph[(row, col)]:

                # Don't explore empty tiles or tiles already in chain
                if tiles[a_row][a_col] == 0 or (a_row, a_col) in chain_idxs:
                    continue

                if tiles[a_row][a_col] > max_adj_val:
                    max_adj_val = tiles[a_row][a_col]
                    max_adj_idx = (a_row, a_col)

            # Reached the end of the chain, stop looking for more tiles
            if max_adj_val == 0:
                end_of_chain = True
                break

            chain_vals.append(max_adj_val)
            chain_idxs.append(max_adj_idx)
            (row, col) = max_adj_idx

        # --- Done processing first portion of chain

        # Add bonus if largest tile in corner
        in_corner = (chain_idxs[0][0] in [0, SIZE-1]) and (chain_idxs[0][1] in [0, SIZE-1])
        multiplier1 = 2 if in_corner else 1

        # If these first tiles in the chain are all in the same row or col
        same_row = all([chain_idxs[0][0] == chain_idxs[i][0] for i in range(1, len(chain_idxs))])
        same_col = all([chain_idxs[0][1] == chain_idxs[i][1] for i in range(1, len(chain_idxs))])

        # Give "bonus" for these tiles being in same row or col
        multiplier2 = 2 if (same_row or same_col) else 1

        # Update metric for this chain
        mult = 256
        for tile_val in chain_vals:
            metric += (mult * tile_val)
            mult = mult/2

        # --- If you have reached the end of the chain, stop
        if end_of_chain:
            metrics.append(metric)
            break

        # --- Otherwise, process next ~4 (or SIZE) "largest" tiles
        row = chain_idxs[-1][0]
        col = chain_idxs[-1][1]

        for _ in range(SIZE):

            max_adj_val = 0
            max_adj_idx = (None, None)

            # Explore adjacent tiles for largest
            for (a_row, a_col) in graph[(row, col)]:

                # Don't explore empty tiles or tiles already in chain
                if tiles[a_row][a_col] == 0 or (a_row, a_col) in chain_idxs:
                    continue

                if tiles[row][col] > max_adj_val:
                    max_adj_val = tiles[a_row][a_col]
                    max_adj_idx = (a_row, a_col)

            # Reached the end of the chain, stop looking for more tiles
            if max_adj_val == 0:
                end_of_chain = True
                break

            chain_vals.append(max_adj_val)
            chain_idxs.append(max_adj_idx)
            (row, col) = max_adj_idx

        # --- Done processing second portion of chain

        for tile_val in chain_vals[4:]:
            metric += (mult * tile_val)
            mult = mult/2

        metric = metric * multiplier1 * multiplier2

        metrics.append(metric)

    return max(metrics)


# # This is the Python version. Use of the MUCH faster Cython version is preferred
# def add_random_tile(tiles, rands, rand_idx):
#
#     # Search to find indeces [row][col] of "open" positions on board
#     open_positions = np.argwhere(tiles == 0)
#     num_empty = int(open_positions.size / 2)
#
#     if num_empty == 0:
#         return tiles, num_empty
#
#     # Pick one of the "empty" positions on board at random
#     rand_idx2 = int(rands[rand_idx]*num_empty)
#     rand_idx += 1
#
#     row = open_positions[rand_idx2][0]
#     col = open_positions[rand_idx2][1]
#
#     # Decide if new tile will be "2" (90%) or "4" (10%)
#     value = 2 if (rands[rand_idx] < 0.9) else 4
#     rand_idx += 1
#
#     tiles[row][col] = value
#     num_empty -= 1
#
#     return tiles, num_empty, rand_idx


# ------------------------------
# Testing Functions

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
    ap1 = AutoPlayer(game1)

    for _ in range(num_moves):
        valid_move, tiles, score, num_empty = ap1.auto_move()

    return tiles, score


def play_games(num, tree_depth, topx, calc_option):

    for i in range(num):

        game1 = GameMgr.Game(None)
        game1.add_random_tile(commit=True)

        ap1 = AutoPlayer(game1, tree_depth, topx, calc_option)

        while not ap1.game.game_over:
            ap1.auto_move()

    return ap1


if __name__ == '__main__':

    tiles = [ [0, 2, 2, 4],
              [0, 4, 4, 8],
              [0, 8, 8, 16],
              [16, 32, 32, 2048]]

    calc_metrics1(np.array(tiles))

    # import GameMgr


    # game1 = GameMgr.Game(None, None, 0)
    # game1.add_random_tile(commit=True)
    # ap = AutoPlayer(game1, tree_depth=5)
    # ap.auto_move()

    # while not game1.game_over:
    #     print(ap.game)
    #     ap.auto_move()

    # tree_depth = 4
    # topx = 4
    # calc_option = 0
    #
    # cProfile.run("ap = play_games(1, tree_depth, topx, calc_option)")
    #
    # print(ap.game)

    # cProfile.run('nums = gen_timing(50000000)')
    # tiles, score = run_num_moves(start_tiles, 100, tree_depth, topx, calc_option)
    # cProfile.run('tiles, score = run_num_moves(start_tiles, 100, tree_depth, topx, calc_option)')
    #
    # print(f"Score: {score}")
    # print(repr(tiles))

    # keep_playing = True
    # limit = 100
    # moves = 0

    # while keep_playing:
    #     start_time = time.perf_counter()
    #     for _ in range(limit):
    #         valid_move, tiles, score, num_empty = ap1.auto_move()
    #         moves += 1
    #     end_time = time.perf_counter()
    #     print(f"{moves} moves completed")
    #     print(ap1)
    #     print(f"{limit} moves completed in {end_time-start_time} seconds.")
    #     print(f"Average: {(end_time-start_time) / limit} sec / move")
    #     i = input("Keep playing? ")
    #     keep_playing = False if (i in ["n", "N"]) else True
