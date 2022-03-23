import numpy as np

# Finish implementation of "move_tiles" using numpy linear algebra...rotate 2D array 90 deg.

SIZE = 4


class MoveNode:

    def __init__(self, prev, tiles, score):

        self.tiles = tiles
        self.metric = None
        self.prev = prev
        self.score = score

        self.level = 0 if (prev is None) else (prev.level + 1)

        # If already traversed 3 levels deep, stop
        if self.level > 2:
            self.next = [None]*4

        # Else build next level of tree
        else:
            self.next = []

            # Children Moves: 0 - Up, 1 - Left, 2 - Right, 3 - Down
            for direction in range(4):
                valid_move, new_tiles, new_score, num_empty = move_tiles(direction, tiles, score)

                if valid_move:
                    self.next.append(MoveNode(self, new_tiles, new_score))
                else:
                    self.next.append([None])


class AutoPlayer:

    def __init__(self, ui_main, raw_tiles, score):

        self.tiles = np.array(raw_tiles)
        self.ui_main = ui_main
        self.keep_playing = True
        self.move_tree = MoveNode(None, self.tiles, score)


def move_tiles(direction, tiles, score):

    valid_move = False

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

    new_tiles, num_empty = add_random_tile(tiles)

    return valid_move, new_tiles, score, num_empty


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

    return tiles, num_empty
