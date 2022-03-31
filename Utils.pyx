import numpy as np
from random import random

DTYPE = np.intc

def move_tiles(short direction, tiles, int score, short size):

    cdef short idx1, place_idx, eval_idx, inc, row1, row2, col1, col2
    cdef int tile_sum
    cdef bint valid_move = False

    tiles1 = np.copy(tiles)
    cdef int[:,:] tiles2 = tiles1

    # --- Begin primary move_tiles loop

    # For each row (if left/right) or col (if up/down)
    for idx1 in range(size):

        if direction == 0:      # Move up
            col1 = idx1
            col2 = idx1
            place_idx = 0
            eval_idx = 1
            inc = 1
        elif direction == 1:    # Move Right
            row1 = idx1
            row2 = idx1
            place_idx = size - 1
            eval_idx = size - 2
            inc = -1
        elif direction == 2:    # Move Down
            col1 = idx1
            col2 = idx1
            place_idx = size - 1
            eval_idx = size - 2
            inc = -1
        elif direction == 3:    # Move Left
            row1 = idx1
            row2 = idx1
            place_idx = 0
            eval_idx = 1
            inc = 1

        # Traverse: (across cols in row if left/right) (across rows in col if up/down)
        while (eval_idx > -1) and (eval_idx < size):

            if direction == 0 or direction == 2:  # If move is up/down, traverse rows in column
                row1 = place_idx
                row2 = eval_idx
            else:                   # If move is left/right, traverse cols in row
                col1 = place_idx
                col2 = eval_idx

            if place_idx == eval_idx:
                eval_idx += inc
                continue

            # If the "place" cell is empty
            elif tiles2[row1, col1] == 0:

                # And the next tile is also empty
                if tiles2[row2, col2] == 0:
                    eval_idx += inc
                    continue

                # Found a tile, move to empty
                else:
                    tiles2[row1, col1] = tiles2[row2, col2]
                    tiles2[row2, col2] = 0
                    valid_move = True
                    eval_idx += inc
                    continue

            # If the "place" cell is NOT empty
            else:

                # And the "eval" tile is empty, move "eval" to next tile
                if tiles2[row2, col2] == 0:
                    eval_idx += inc
                    continue

                # "Place" and "eval" tiles2 equal.  Merge.
                elif tiles2[row1, col1] == tiles2[row2, col2]:
                    tile_sum = tiles2[row1, col1] + tiles2[row2, col2]
                    tiles2[row1, col1] = tile_sum
                    tiles2[row2, col2] = 0
                    valid_move = True
                    place_idx += inc
                    eval_idx += inc
                    score += tile_sum
                    continue

                # Tiles are different. Move "place" forward
                else:
                    place_idx += inc
                    continue

    return valid_move, tiles1, score


def add_random_tile( tiles, float[:] rands, int rand_idx1, short size):

    cdef short row, col, rand_idx2
    cdef short open_positions[16][2]
    cdef int value, empty

    cdef int[:,:] tiles2 = tiles

    empty = 0
    for row in range(size):
        for col in range(size):
            if tiles2[row, col] == 0:
                open_positions[empty][0] = row
                open_positions[empty][1] = col
                empty += 1

    if empty == 0:
        return tiles, empty, rand_idx1

    rand_idx2 = int(rands[rand_idx1] * empty)
    rand_idx1 += 1

    row = open_positions[rand_idx2][0]
    col = open_positions[rand_idx2][1]

    value = 2 if (rands[rand_idx1] < 0.9) else 4
    rand_idx1 += 1

    tiles2[row, col] = value
    empty -= 1

    return tiles, empty, rand_idx1

def calc_metrics0(int[:,:] tiles):
    cdef int metric

    metric = int(tiles[0, 3] * 256 + tiles[1, 3] * 128 +
                 tiles[2, 3] * 64 + tiles[3, 3] * 32 +
                 tiles[3, 2] * 16 + tiles[2, 2] * 8 +
                 tiles[1, 2] * 4 + tiles[0, 2] * 2)

    return metric

def calc_metrics1(int[:,:] tiles):
    cdef int i = 0
    return 0

def calc_metrics2(int[:,:] tiles):
    cdef int i = 0
    return 0

def calc_metrics3(int[:,:] tiles):
    cdef int i = 0
    return 0



