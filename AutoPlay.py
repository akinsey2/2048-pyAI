import numpy as np
from copy import deepcopy
import Utils
import cProfile
import GameMgr
from math import floor
from pprint import pp

SIZE = int(4)
USE_CYTHON = True


# ****************************************
class AutoPlayer:
    #6, 7
    def __init__(self, game, tree_depth=6, topx_perc=0.05, calc_option=3, rand=None):

        # GameMgr.Game object stores current game state: tiles, score, etc
        self.game = game

        # self.move_tree = None
        self.tree_depth = tree_depth
        self.tree_size = 0
        self.topx_perc = topx_perc
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
            rand_nums = int(sum([4**i for i in range(tree_depth+1)])*2*4000)
            self.rands = self.rand.random(rand_nums, dtype=np.single)
            self.rand_idx = int(0)

            # # DEBUG
            # print(f"Length(self.rands) = {self.rands.shape}  dtype = {self.rands.dtype}")

        # If Cython is NOT used, (speed not critical)
        # then AutoPlay does not need to contain random numbers
        # Rands will be generated by GameMgr.Game.rand
        else:
            self.rand = None

        # DEBUG
        self.move_metrics = []
        self.best_move = 0
        self.last_move_valid = False

    def __repr__(self):
        out = list()
        out.append("-"*30 + "\n")
        out.append(f"AutoPlay - Tree Depth: {self.tree_depth} | " +
                   f"TopX: {self.topx_perc}%, {floor(self.tree_size*self.topx_perc)} | Calc: {self.calc_option} | " +
                   f"Rands Length: {self.rands.size} | rand_idx: {self.rand_idx}\n")
        out.append(repr(self.game))

        return "".join(out)

    def get_move(self):

        self.tree_size = 0
        move_tree = MoveNode(None, self.game.tiles, self.game.score, self)

        # DEBUG
        # print_tree_bfs(move_tree)

        move_metrics = list()

        # Search "forward" in move tree
        # Record the "max metric" found in tree below each "move_score[i]"
        # move_dir=0: Up, move_dir=1: Right, move_dir=2: Down, move_dir=3: Left
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
            max_metrics = np.zeros(topx_num, dtype=np.int64)
            max_metrics[-1] = move_tree.next[move_dir].metric
            max_metrics = node_tree_max_DFS(move_tree.next[move_dir], max_metrics)
            move_metrics.append(max_metrics.sum() / float(topx_num))

        # # DEBUG
        # print(f"move_metrics: Up: {move_metrics[0]}, Right: {move_metrics[1]}, " +
        #       f"Down: {move_metrics[2]}, Left: {move_metrics[3]}")

        # Very important...multiple metrics can be the same (usually 0)
        # In this case you must find a valid move to return (not the default "0" - Up)
        max_met = max(move_metrics)
        maxs = [(i, move_metrics[i]) for i in range(4) if move_metrics[i] == max_met]

        # If only one max return its move,
        # or if there is no good move (max metrics are zero) pick any of them.
        if len(maxs) == 1 or max_met == 0:
            best_move = move_metrics.index(max_met)

        # If there is more than one equally good move
        else:
            # _, max_corners = Utils.calc_metrics3(self.game.tiles)
            print(f"MORE THAN ONE BEST MOVE: move_metrics = {move_metrics}")
            best_move = move_metrics.index(max_met)

        # DEBUG
        self.move_metrics = move_metrics
        self.best_move = best_move

        return best_move

    def auto_move(self):

        if self.game.game_over:
            return

        best_move = self.get_move()

        # # DEBUG
        # options = ["Up", "Right", "Down", "Left"]
        # print(f"Best Move: {options[best_move]}")
        # ans = input("Continue? ")
        # if ans in ["N", "n"]:
        #     quit()

        if USE_CYTHON:
            valid_move, tiles2, self.game.score = \
                Utils.move_tiles(best_move, self.game.tiles, self.game.score)
        else:
            valid_move, _, _, _ = self.game.move_tiles(best_move, True)

        if valid_move:
            if USE_CYTHON:
                self.game.tiles, self.game.num_empty, self.rand_idx = \
                    Utils.add_random_tile(tiles2, self.rands, self.rand_idx)
                self.game.num_moves += 1

                if self.game.num_empty == 0:
                    self.game.game_over = self.game.check_game_over(self.game.tiles)
            else:
                self.game.add_random_tile(commit=True)

        # if not valid_move and self.game.num_empty == 0:
        #     self.game.game_over = True

        # DEBUG
        self.last_move_valid = valid_move

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
        self.metric = 0

        if USE_CYTHON:  # Use fast Cython functions
            if ap.calc_option == 0:
                self.metric = Utils.calc_metrics0(tiles)
            elif ap.calc_option == 1:
                self.metric = Utils.calc_metrics1(tiles)
            elif ap.calc_option == 2:
                self.metric = Utils.calc_metrics2(tiles)
            elif ap.calc_option == 3:
                self.metric, _ = Utils.calc_metrics3(tiles)

        else:   # Use slower Python functions
            if ap.calc_option == 0:
                self.metric = calc_metrics0(tiles)
            elif ap.calc_option == 1:
                self.metric = calc_metrics1(tiles)
            elif ap.calc_option == 2:
                self.metric = calc_metrics2(tiles)
            elif ap.calc_option == 3:
                self.metric = calc_metrics3(tiles)

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
                        Utils.move_tiles(direction, tiles, score)
                else:
                    valid_move, _, new_tiles, new_score = \
                        ap.game.move_tiles(direction, False, tiles, score)

                # If valid move, add random tile
                if valid_move:

                    if USE_CYTHON:
                        new_tiles, _, ap.rand_idx = \
                            Utils.add_random_tile(new_tiles, ap.rands, ap.rand_idx)
                    else:
                        new_tiles, _, _, ap.rand_idx = \
                            ap.game.add_random_tile(commit=False, tiles=new_tiles)

                    ap.tree_size += 1

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


# Strategy 0:
# Simplest...Rewards Empty Tiles.
def calc_metrics0(tiles):

    num_empty = 0
    for row in range(SIZE):
        for col in range(SIZE):
            if tiles[row][col] == 0:
                num_empty += 100

    return num_empty


# Strategy 1:
# Simple metric...Rewards Upper-Right aligned chain.
def calc_metrics1(tiles):

    metric = int(tiles[0][3]*256 + tiles[1][3]*128 +
                 tiles[2][3]*64 + tiles[3][3]*32 +
                 tiles[3][2]*16 + tiles[2][2]*8 +
                 tiles[1][2]*4 + tiles[0][2]*2)

    return metric


# Strategy 2:
# More advanced metric. Rewards any "chain" anchored in a corner,
# with additional "reward" for empty tiles
def calc_metrics2(tiles):

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
    # Also count empty tiles
    max_val = 0
    maxs = []
    num_empty = 0
    for row in range(SIZE):
        for col in range(SIZE):

            val = tiles[row][col]

            if val == 0:
                num_empty += 1
                continue
            elif val < max_val:
                continue
            elif val > max_val:
                max_val = val
                maxs.clear()
                maxs.append([val, row, col])
            else:   # Equal
                maxs.append([val, row, col])

    # --- Master Loop: Traverses chain(s) and calculates chain quality metric/score
    # Tiles must be adjacent, and weakly decreasing to comprise a chain.
    metrics = []
    for (val, row, col) in maxs:

        metric = 0              # "Score" metric for the overall chain

        # Start with "max" tile
        chain_vals = [val]
        chain_idxs = [(row, col)]

        # --- Process next 3 (or SIZE-1) "largest" tiles
        for _ in range(7):

            max_adj_val = 0
            max_adj_idx = (None, None)

            # Explore adjacent tiles for largest
            for (a_row, a_col) in graph[(row, col)]:

                # Don't explore empty tiles or tiles already in chain
                val = tiles[a_row][a_col]
                if val == 0 or (a_row, a_col) in chain_idxs or val > tiles[row][col]:
                    continue

                if val > max_adj_val:
                    max_adj_val = tiles[a_row][a_col]
                    max_adj_idx = (a_row, a_col)

            # Reached the end of the chain, stop looking for more tiles
            if max_adj_val > chain_vals[-1] or max_adj_val == 0:
                break

            chain_vals.append(max_adj_val)
            chain_idxs.append(max_adj_idx)
            (row, col) = max_adj_idx

        # --- Done Identifying this chain

        # Add bonus if largest tile in corner
        in_corner = (chain_idxs[0][0] in [0, SIZE-1]) and (chain_idxs[0][1] in [0, SIZE-1])
        multiplier1 = 2 if in_corner else 1

        # If these first tiles in the chain are all in the same row or col
        same_row = all([chain_idxs[0][0] == chain_idxs[i][0] for i in range(1, min(4, len(chain_idxs)))])
        same_col = all([chain_idxs[0][1] == chain_idxs[i][1] for i in range(1, min(4, len(chain_idxs)))])

        # Give "bonus" for these tiles being in same row or col
        multiplier2 = 2 if in_corner and (same_row or same_col) else 1

        # Update metric for this chain
        mult = 8
        for tile_val in chain_vals:
            metric += tile_val * mult
            mult -= 1

        # multiplier3 = 2 ** num_empty
        metric = metric * multiplier1 * multiplier2 * num_empty

        metrics.append(metric)

    return max(metrics)


def calc_metrics3(tiles):

    graph = {0: ((0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 2), (1, 1), (1, 0), (2, 0)),
             1: ((0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2)),
             2: ((0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (2, 2), (1, 2), (0, 2), (0, 1)),
             3: ((0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (2, 3)),
             4: ((3, 3), (3, 2), (3, 1), (3, 0), (2, 0), (2, 1), (2, 2), (2, 3), (1, 3)),
             5: ((3, 3), (2, 3), (1, 3), (0, 3), (0, 2), (1, 2), (2, 2), (3, 2), (3, 1)),
             6: ((3, 0), (2, 0), (1, 0), (0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (3, 2)),
             7: ((3, 0), (3, 1), (3, 2), (3, 3), (2, 3), (2, 2), (2, 1), (2, 0), (1, 0))}

    graph2 = {(0, 0): (graph[0], graph[1]),
              (0, 3): (graph[2], graph[3]),
              (3, 3): (graph[4], graph[5]),
              (3, 0): (graph[6], graph[7])}

    max_val = 0
    maxs = []
    num_empty = 0
    for row in range(SIZE):
        for col in range(SIZE):

            val = tiles[row][col]

            if val == 0:
                num_empty += 1
                continue
            elif val < max_val:
                continue
            elif val > max_val:
                max_val = val
                maxs.clear()
                maxs.append([val, row, col])
            else:  # Equal
                maxs.append([val, row, col])

    in_corner = False
    corners = []
    for max1 in maxs:
        if (max1[1] in [0, 3]) and (max1[2] in [0, 3]):
            in_corner = True
            corners.append((max1[1], max1[2]))

    if not in_corner:
        return 0

    metrics = []

    for cnr_idx in corners:
        for tile_idxs in graph2[cnr_idx]:
            metric = int(0)
            mult = int(2**8)
            for idx in tile_idxs:
                metric += tiles[idx[0]][idx[1]] * mult
                mult = mult // 2
            # metric = metric * num_empty
            metrics.append(metric)

    return max(metrics)


if __name__ == '__main__':

    tiles1 = [[0, 2, 2, 4],
             [0, 4, 4, 8],
             [0, 8, 8, 16],
             [16, 32, 32, 2048]]

    calc_metrics1(np.array(tiles1))

    # import GameMgr

    # game1 = GameMgr.Game(None, None, 0)
    # game1.add_random_tile(commit=True)
    # ap = AutoPlayer(game1, tree_depth=5)
    # ap.auto_move()

    # while not game1.game_over:
    #     print(ap.game)
    #     ap.auto_move()

    # print(f"Score: {score}")
    # print(repr(tiles))

    # keep_playing = True
    # limit = 100
    # moves = 0


