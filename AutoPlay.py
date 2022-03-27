import numpy as np
from copy import deepcopy
import cProfile

SIZE = 4

# import time
# from functools import wraps
#
#
# def speed_test(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         print(f"Executing {func.__name__}")
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         print(f"Time Elapsed: {end_time - start_time}")
#
#         return result
#
#     return wrapper


# Nodes of individual game state
# Linked to form a 4-ary Tree structure
class MoveNode:

    # Initializes Node AND
    # Recursively builds 4-ary tree to "TREE_DEPTH"
    def __init__(self, prev, tiles, rand, score, tree_depth, calc_option):

        self.tiles = tiles.copy()
        self.prev = prev
        self.score = score
        self.level = 0 if (prev is None) else (prev.level + 1)

        if calc_option == 0:
            self.metrics, self.metric = self.calc_metrics0(tiles)
        elif calc_option == 1:
            self.metrics, self.metric = self.calc_metrics1(tiles)
        elif calc_option == 2:
            self.metrics, self.metric = self.calc_metrics2(tiles)
        elif calc_option == 3:
            self.metrics, self.metric = self.calc_metrics3(tiles)

        # Base Case: If already traversed 3 levels deep, stop
        if self.level > tree_depth - 1:
            self.next = None

        # Recursively build next level of tree
        else:
            self.next = []

            # Children Moves: 0 - Up, 1 - Right, 2 - Down, 3 - Left
            for direction in range(4):

                valid_move, new_tiles, new_score = move_tiles(direction, tiles, score)

                if valid_move:
                    new_tiles, num_empty = add_random_tile(new_tiles, rand)
                    self.next.append(MoveNode(self, new_tiles, rand, new_score, tree_depth, calc_option))
                else:
                    self.next.append(None)

    def __repr__(self):

        out = list()
        out.append("-"*20 + "\n")
        out.append(f"Tree Level: {self.level}  |  Score: {self.score}")
        out.append(f"  |  Metric: {self.metric}\n")
        out.append("Metrics: " + repr(self.metrics) + "\n")

        return "".join(out)

    def calc_metrics0(self, tiles):

        col_sums = tiles.sum(axis=0, dtype=np.int32)
        row_sums = tiles.sum(axis=1, dtype=np.int32)

        sorted_sums = np.flip(np.sort(np.concatenate((col_sums, row_sums))))

        metric = int(sorted_sums[0]*4 + sorted_sums[1]*2 + sorted_sums[2])

        return sorted_sums, metric

    def calc_metrics1(self, tiles):

        col_sums = tiles.sum(axis=0, dtype=np.int32)

        metric = int(col_sums[3]*8 + col_sums[2]*2 + col_sums[1])

        return col_sums, metric

    def calc_metrics2(self, tiles):

        # col_sums = tiles.sum(axis=0, dtype=np.int32)
        col_sums = []

        metric = int(tiles[0][3]*(2**12) + tiles[1][3]*(2**11) +
                     tiles[2][3]*(2**10) + tiles[3][3]*(2**9) +
                     tiles[3][2]*(2**8) + tiles[2][2]*(2**7) +
                     tiles[1][2]*(2**6) + tiles[0][2]*(2**5) +
                     tiles[0][1]*(2**4) + tiles[1][1]*(2**3) +
                     tiles[2][1]*(2**2) + tiles[3][1]*(2**1) +
                     tiles[3][0] + tiles[2][0] +
                     tiles[1][0] + tiles[0][0])

        return col_sums, metric

    def calc_metrics3(self, tiles):

        # col_sums = tiles.sum(axis=0, dtype=np.int32)
        col_sums = []

        metric = int(tiles[0][3]*256 + tiles[1][3]*128 +
                     tiles[2][3]*64 + tiles[3][3]*32 +
                     tiles[3][2]*16 + tiles[2][2]*8 +
                     tiles[1][2]*4 + tiles[0][2]*2)

        return col_sums, metric


# ****************************************
class AutoPlayer:

    def __init__(self, tiles_nums, score, tree_depth, topx, calc_option):

        self.tiles = np.array(tiles_nums, dtype=np.intc)
        self.num_empty = SIZE*SIZE
        self.score = deepcopy(score)
        self.move_tree = None
        self.tree_depth = tree_depth
        self.topx = topx
        self.calc_option = calc_option
        self.rand = np.random.default_rng()

    def __repr__(self):
        out = list()
        out.append("-"*20 + "\n")
        out.append(f"Score: {self.score}\n")
        out.append(repr(self.tiles))

        return "".join(out)

    def get_move(self, tiles_nums):

        self.tiles = np.array(tiles_nums, dtype=np.intc)

        self.move_tree = MoveNode(None, self.tiles, self.rand, self.score, self.tree_depth, self.calc_option)

        move_score = list()

        # Search "forward" in move tree
        # Record the "max metric" found in "move_score[i]"
        # For each possible initial move
        # i=0: Up, i=1: Right, i=2: Down, i=3: Left
        for move_dir in range(SIZE):

            # If this was an invalid move (no node exists).
            if self.move_tree.next[move_dir] is None:
                move_score.append(0.0)
                continue
            else:
                max_metrics = np.zeros(32, dtype=np.int32)
                max_metrics[31] = self.move_tree.next[move_dir].metric
                # new_max = node_tree_max_DFS(self.move_tree.next[move_dir], max_metric)
                max_metrics = node_tree_max_DFS(self.move_tree.next[move_dir], max_metrics)
                move_score.append(max_metrics.sum() / 10.0)

        best_move = move_score.index(max(move_score))
        return best_move

    def auto_move(self):

        tiles = self.tiles.copy()

        self.move_tree = MoveNode(None, tiles, self.rand, self.score, self.tree_depth, self.calc_option)

        move_score = list()

        # Search "forward" in move tree
        # Record the "max metric" found in "move_score[i]"
        # For each possible initial move
        # i=0: Up, i=1: Right, i=2: Down, i=3: Left
        for move_dir in range(SIZE):

            # If this was an invalid move (no node exists).
            if self.move_tree.next[move_dir] is None:
                move_score.append(0.0)
                continue
            else:
                max_metrics = np.zeros(self.topx, dtype=np.int32)
                max_metrics[self.topx - 1] = self.move_tree.next[move_dir].metric
                # new_max = node_tree_max_DFS(self.move_tree.next[move_dir], max_metric)
                max_metrics = node_tree_max_DFS(self.move_tree.next[move_dir], max_metrics)
                move_score.append(max_metrics.sum() / float(self.topx))

        # print(f"Move Score: Up = {move_score[0]}, Right = {move_score[1]}, " +
        #       f"Down = {move_score[2]}, Left = {move_score[3]}\n")

        best_move = move_score.index(max(move_score))

        # print(f"Best Move: {best_move}\n")

        valid_move, tiles2, score2 = move_tiles(best_move, self.tiles, self.score)

        if valid_move:
            self.tiles, num_empty = add_random_tile(tiles2, self.rand)
            self.score = score2
            self.move_tree = MoveNode(None, self.tiles, self.rand, self.score, self.tree_depth, self.calc_option)

        return valid_move, self.tiles, self.score, self.num_empty


def node_tree_max_DFS(node, max_metrics):

    # Save metric of current node, if
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


def move_tiles(direction, tiles, score):

    valid_move = False
    tiles2 = tiles.copy()

    # For each row (if left/right) or col (if up/down)
    for idx1 in range(SIZE):

        if direction == 0:      # Move up
            (col1, col2, place_idx, eval_idx, inc) = (idx1, idx1, 0, 1, 1)
        elif direction == 1:    # Move Right
            (row1, row2, place_idx, eval_idx, inc) = (idx1, idx1, SIZE - 1, SIZE - 2, -1)
        elif direction == 2:    # Move Down
            (col1, col2, place_idx, eval_idx, inc) = (idx1, idx1, SIZE - 1, SIZE - 2, -1)
        elif direction == 3:    # Move Left
            (row1, row2, place_idx, eval_idx, inc) = (idx1, idx1, 0, 1, 1)
        else:
            raise ValueError("'direction' value invalid.  Must be 0-3.")

        # Traverse: (across cols in row if left/right) (across rows in col if up/down)
        while (eval_idx > -1) and (eval_idx < SIZE):

            if direction in [0, 2]:  # If move is up/down, traverse rows in column
                (row1, row2) = (place_idx, eval_idx)
            else:                   # If move is left/right, traverse cols in row
                (col1, col2) = (place_idx, eval_idx)

            if place_idx == eval_idx:
                eval_idx += inc
                continue

            # If the "place" cell is empty
            elif tiles2[row1][col1] == 0:

                # And the next tile is also empty
                if tiles2[row2][col2] == 0:
                    eval_idx += inc
                    continue

                # Found a tile, move to empty
                else:
                    tiles2[row1][col1] = tiles2[row2][col2]
                    tiles2[row2][col2] = 0
                    valid_move = True
                    eval_idx += inc
                    continue

            # If the "place" cell is NOT empty
            else:

                # And the "eval" tile is empty, move "eval" to next tile
                if tiles2[row2][col2] == 0:
                    eval_idx += inc
                    continue

                # "Place" and "eval" tiles2 equal.  Merge.
                elif tiles2[row1][col1] == tiles2[row2][col2]:
                    tile_sum = tiles2[row1][col1] + tiles2[row2][col2]
                    tiles2[row1][col1] = tile_sum
                    tiles2[row2][col2] = 0
                    valid_move = True
                    place_idx += inc
                    eval_idx += inc
                    score += tile_sum
                    continue

                # Tiles are different. Move "place" forward
                else:
                    place_idx += inc
                    continue

    return valid_move, tiles2, score


def add_random_tile(tiles, rand):

    # Find open positions
    open_positions = []
    for idx in range(16):
        if tiles[idx // 4][idx % 4] == 0:
            open_positions.append(idx)

    num_empty = len(open_positions)
    if num_empty == 0:
        return tiles, num_empty

    rand_idx = rand.integers(0, num_empty)
    pos = open_positions.pop(rand_idx)
    row = pos // SIZE
    col = pos % SIZE

    value = 2 if (rand.random() < 0.9) else 4

    tiles[row][col] = value
    num_empty -= 1

    return tiles, num_empty

def run_num_moves(start_tiles, num_moves, tree_depth, topx, calc_option):

    ap1 = AutoPlayer(start_tiles, 0, tree_depth, 2 ** topx, calc_option)

    for _ in range(num_moves):
        valid_move, tiles, score, num_empty = ap1.auto_move()

    return tiles, score


if __name__ == '__main__':

    # total_fwd_tiles = 0
    # for i in range(tree_depth + 1):
    #     total_fwd_tiles += 4 ** i

    # if (2 ** topx) > (total_fwd_tiles / 4):
    #     continue

    # game = AutoPlay.AutoPlayer(start_tiles, 0, tree_depth, 2 ** topx, calc_option)
    # game_over = False
    #
    # while not game_over:
    #     valid_move, tiles, score, num_empty = game.auto_move()
    #     game_over = (not valid_move) and (num_empty == 0)

    # records.append([calc_option, tree_depth, topx, game_num, score])

    start_tiles = [[0, 0, 0, 0], [0, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    start_score = 0
    tree_depth = 5
    topx = 6
    calc_option = 3

    # tiles, score = run_num_moves(start_tiles, 500, tree_depth, topx, calc_option)
    cProfile.run('tiles, score = run_num_moves(start_tiles, 500, tree_depth, topx, calc_option)')

    print(f"Score: {score}")
    print(repr(tiles))

    # keep_playing = True
    # limit = 100
    # moves = 0

    # while keep_playing:
    #     start_time = time.perf_counter()
    #     for _ in range(limit):
    #         # print(ap1.move_tree)
    #         valid_move, tiles, score, num_empty = ap1.auto_move()
    #         moves += 1
    #     end_time = time.perf_counter()
    #     print(f"{moves} moves completed")
    #     print(ap1)
    #     print(f"{limit} moves completed in {end_time-start_time} seconds.")
    #     print(f"Average: {(end_time-start_time) / limit} sec / move")
    #     i = input("Keep playing? ")
    #     keep_playing = False if (i in ["n", "N"]) else True

    # while keep_playing:
    #
    #     valid_move, tiles, score, num_empty = ap1.auto_move()
    #
    #     if ap1.tiles[0][3] > limit:
    #         print(ap1.move_tree)
    #         i = input("Keep playing? ")
    #         keep_playing = False if (i in ["n", "N"]) else True
    #         limit = limit * 2
