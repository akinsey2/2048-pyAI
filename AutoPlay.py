import numpy as np
from copy import copy, deepcopy

SIZE = 4
TREE_DEPTH = 5

# Nodes of individual game state
# Linked to form a 4-ary Tree structure
class MoveNode:

    # Initializes Node AND
    # Recursively builds 4-ary tree to "TREE_DEPTH"
    def __init__(self, prev, tiles, score):

        self.tiles = deepcopy(tiles)
        self.prev = prev
        self.score = score
        self.level = 0 if (prev is None) else (prev.level + 1)
        self.metrics, self.metric = self.calc_metrics4()

        # Base Case: If already traversed 3 levels deep, stop
        if self.level > TREE_DEPTH-1:
            self.next = None

        # Recursively build next level of tree
        else:
            self.next = []

            # Children Moves: 0 - Up, 1 - Right, 2 - Down, 3 - Left
            for direction in range(4):

                valid_move, new_tiles, new_score = move_tiles(direction, tiles, score)

                if valid_move:
                    self.next.append(MoveNode(self, new_tiles, new_score))
                else:
                    self.next.append(None)

    def __repr__(self):

        out = list()
        out.append("-"*20 + "\n")
        level = f"Tree Level: {self.level}  |  Score: {self.score}"
        out.append(level)
        out.append("  |  " + repr(self.metrics) + "\n")
        out.append(repr(self.tiles))

        return "".join(out)

    def calc_metrics1(self):

        col_sums = self.tiles.sum(axis=0, dtype=np.int32)
        row_sums = self.tiles.sum(axis=1, dtype=np.int32)

        sorted_sums = np.flip(np.sort(np.concatenate((col_sums, row_sums))))

        metric = int(sorted_sums[0]*4 + sorted_sums[1]*2 + sorted_sums[2])

        return sorted_sums, metric

    def calc_metrics2(self):

        col_sums = self.tiles.sum(axis=0, dtype=np.int32)

        metric = int(col_sums[3]*8 + col_sums[2]*2 + col_sums[1])

        return col_sums, metric

    def calc_metrics3(self):

        col_sums = self.tiles.sum(axis=0, dtype=np.int32)

        metric = int(self.tiles[0][3]*(2**12) + self.tiles[1][3]*(2**11) +
                     self.tiles[2][3]*(2**10) + self.tiles[3][3]*(2**9) +
                     self.tiles[3][2]*(2**8) + self.tiles[2][2]*(2**7) +
                     self.tiles[1][2]*(2**6) + self.tiles[0][2]*(2**5) +
                     self.tiles[0][1]*(2**4) + self.tiles[1][1]*(2**3) +
                     self.tiles[2][1]*(2**2) + self.tiles[3][1]*(2**1) +
                     self.tiles[3][0]      + self.tiles[2][0]  +
                     self.tiles[1][0]      + self.tiles[0][0])

        return col_sums, metric

    def calc_metrics4(self):

        col_sums = self.tiles.sum(axis=0, dtype=np.int32)

        metric = int(self.tiles[0][3]*(2**8) + self.tiles[1][3]*(2**7) +
                     self.tiles[2][3]*(2**6) + self.tiles[3][3]*(2**5) +
                     self.tiles[3][2]*(2**4) + self.tiles[2][2]*(2**3) +
                     self.tiles[1][2]*(2**2) + self.tiles[0][2]*(2**1))

        return col_sums, metric


class AutoPlayer:

    def __init__(self, tiles_nums, score):

        self.tiles = np.array(tiles_nums, dtype=np.int32)
        self.score = deepcopy(score)
        self.move_tree = None

    def get_move(self, tiles_nums):

        self.tiles = np.array(tiles_nums, dtype=np.int32)

        self.move_tree = MoveNode(None, self.tiles, self.score)

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

        self.move_tree = MoveNode(None, self.tiles, self.score)

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
                max_metrics = np.zeros(10, dtype=np.int32)
                max_metrics[9] = self.move_tree.next[move_dir].metric
                # new_max = node_tree_max_DFS(self.move_tree.next[move_dir], max_metric)
                max_metrics = node_tree_max_DFS(self.move_tree.next[move_dir], max_metrics)
                move_score.append(max_metrics.sum() / 10.0)

        print(f"Move Score: Up = {move_score[0]}, Right = {move_score[1]}, " +
              f"Down = {move_score[2]}, Left = {move_score[3]}\n")

        best_move = move_score.index(max(move_score))

        print(f"Best Move: {best_move}\n")

        valid_move, self.tiles, self.score = move_tiles(best_move, self.tiles, self.score)
        self.move_tree = MoveNode(None, self.tiles, self.score)


def node_tree_max_DFS(node, max_metrics):

    # Save metric of current node, if
    if node.metric > max_metrics[0]:
        max_metrics[0] = node.metric
        max_metrics.sort()

    # Base Case: Reached bottom of game tree
    if node.next is None:
        return max_metrics

    # Else, recurse deeper.

    # new_max = deepcopy(max_metric)

    for move_dir in range(SIZE):

        if node.next[move_dir] is None:
            continue
        else:
            node_tree_max_DFS(node.next[move_dir], max_metrics)

    return max_metrics


def move_tiles(direction, tiles, score):

    valid_move = False
    tiles = deepcopy(tiles)

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
            elif tiles[row1][col1] == 0:

                # And the next tile is also empty
                if tiles[row2][col2] == 0:
                    eval_idx += inc
                    continue

                # Found a tile, move to empty
                else:
                    tiles[row1][col1] = tiles[row2][col2]
                    tiles[row2][col2] = 0
                    valid_move = True
                    eval_idx += inc
                    continue

            # If the "place" cell is NOT empty
            else:

                # And the "eval" tile is empty, move "eval" to next tile
                if tiles[row2][col2] == 0:
                    eval_idx += inc
                    continue

                # "Place" and "eval" tiles equal.  Merge.
                elif tiles[row1][col1] == tiles[row2][col2]:
                    tile_sum = tiles[row1][col1] + tiles[row2][col2]
                    tiles[row1][col1] = tile_sum
                    tiles[row2][col2] = 0
                    valid_move = True
                    place_idx += inc
                    eval_idx += inc
                    score += tile_sum
                    continue

                # Tiles are different. Move "place" forward
                else:
                    place_idx += inc
                    continue

    if valid_move:
        new_tiles = add_random_tile(tiles)
        return valid_move, new_tiles, score

    return valid_move, tiles, score


def add_random_tile(tiles):

    # Find open positions
    open_positions = []
    for idx in range(16):
        if tiles[idx // 4][idx % 4] == 0:
            open_positions.append(idx)

    num_empty = len(open_positions)
    if num_empty == 0:
        return tiles, num_empty

    rand = np.random.default_rng()
    rand_idx = rand.integers(0, num_empty)
    pos = open_positions.pop(rand_idx)
    row = pos // SIZE
    col = pos % SIZE

    value = 2 if (rand.random() < 0.9) else 4

    tiles[row][col] = value
    num_empty -= 1

    return tiles


if __name__ == '__main__':

    tiles1 = [[0, 0, 0, 0], [0, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    ap1 = AutoPlayer(None, tiles1, 0)

    keep_playing = True

    while keep_playing:
        print(ap1.move_tree)
        ap1.auto_move()
        i = input("Keep playing? ")
        keep_playing = False if (i in ["n", "N"]) else True
