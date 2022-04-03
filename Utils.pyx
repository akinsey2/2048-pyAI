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

def calc_metrics1(int[:,:] tiles, int size):

    cdef int max_val, maxs_len, chain_len, val, row, col
    cdef int a_row, a_col, chain_idx, curr_row, curr_col
    cdef int abv_row, rgt_col, blw_row, lft_col
    cdef int maxs[16][3], chain[16][3], max_adj[3]
    cdef int num_of_metrics, metric, mult
    cdef multiplier1, multiplier2, multiplier3
    cdef int metrics[16]
    cdef bint end_of_chain, in_chain, in_corner1, in_corner2, in_corner
    cdef bint same_row, same_col


    # graph = {(0, 0): ((1, 0), (0, 1)),
    #          (0, 1): ((0, 0), (1, 1), (0, 2)),
    #          (0, 2): ((0, 1), (1, 2), (0, 3)),
    #          (0, 3): ((0, 2), (1, 3)),
    #          (1, 0): ((0, 0), (1, 1), (2, 0)),
    #          (1, 1): ((0, 1), (1, 2), (2, 1), (1, 0)),
    #          (1, 2): ((0, 2), (1, 3), (2, 2), (1, 1)),
    #          (1, 3): ((0, 3), (2, 3), (1, 2)),
    #          (2, 0): ((1, 0), (2, 1), (3, 0)),
    #          (2, 1): ((1, 1), (2, 2), (3, 1), (2, 0)),
    #          (2, 2): ((1, 2), (2, 3), (3, 2), (2, 1)),
    #          (2, 3): ((1, 3), (3, 3), (2, 2)),
    #          (3, 0): ((2, 0), (3, 1)),
    #          (3, 1): ((2, 1), (3, 2), (3, 0)),
    #          (3, 2): ((2, 2), (3, 3), (3, 1)),
    #          (3, 3): ((2, 3), (3, 2))}

    # Find greatest tile(s) on board, the starting point of the "chain" calculation(s)
    max_val = 0
    maxs_len = 0
    for row in range(size):
        for col in range(size):

            val = tiles[row][col]

            if val < max_val:
                continue
            elif val > max_val:
                max_val = val
                maxs_len = 1
                maxs[0][0] = val
                maxs[0][1] = row
                maxs[0][2] = col
            else:   # Equal
                maxs[maxs_len][0] = val
                maxs[maxs_len][1] = row
                maxs[maxs_len][2] = col
                maxs_len += 1

    # --- Master Loop: Traverses chain(s) and calculates chain quality metric/score

    for i in range(maxs_len):

        end_of_chain = False    # Have reached the end of the chain?
        metric = 0              # "Score" metric for the overall chain

        # Start with "max" tile
        chain[0][0] = maxs[i][0]
        chain[0][1] = maxs[i][1]
        chain[0][2] = maxs[i][2]
        chain_len = 1
        chain_idx = 0

        # --- Process next 3 (or SIZE-1) "largest" tiles
        for _ in range(size-1):

            max_adj[0] = 0
            max_adj[1] = -1
            max_adj[2] = -1

            # Explore adjacent tiles for largest
            curr_row = chain[chain_idx][1]
            curr_col = chain[chain_idx][2]

            # Above
            abv_row = curr_row - 1
            if abv_row > -1:

                in_chain = check_in_chain(chain, abv_row, curr_col)
                if tiles[abv_row][curr_col] > max_adj[0] and not in_chain:
                    max_adj[0] = tiles[abv_row][curr_col]
                    max_adj[1] = abv_row
                    max_adj[2] = curr_col

            # Right
            rgt_col = curr_col + 1
            if rgt_col < size:

                in_chain = check_in_chain(chain, curr_row, rgt_col)
                if tiles[curr_row][rgt_col] > max_adj[0] and not in_chain:
                    max_adj[0] = tiles[curr_row][rgt_col]
                    max_adj[1] = curr_row
                    max_adj[2] = rgt_col

            # Below
            blw_row = curr_row + 1
            if blw_row < size:

                in_chain = check_in_chain(chain, blw_row, curr_col)
                if tiles[blw_row][curr_col] > max_adj[0] and not in_chain:
                    max_adj[0] = tiles[blw_row][curr_col]
                    max_adj[1] = blw_row
                    max_adj[2] = curr_col

            # Left
            lft_col = curr_col - 1
            if rgt_col > -1:

                in_chain = check_in_chain(chain, curr_row, lft_col)
                if tiles[curr_row][lft_col] > max_adj[0] and not in_chain:
                    max_adj[0] = tiles[curr_row][lft_col]
                    max_adj[1] = curr_row
                    max_adj[2] = lft_col


            # If Reached the end of the chain, stop looking for more tiles
            if max_adj[0] < chain[chain_idx][0] or max_adj[0] == 0:
                end_of_chain = True
                break

            # Else, save this next tile in chain, and keep looking
            chain[chain_idx][0] = max_adj[0]
            chain[chain_idx][1] = max_adj[1]
            chain[chain_idx][2] = max_adj[2]
            chain_idx += 1
            chain_len += 1


        # --- Done processing first portion of chain

        # Add bonus if largest tile in corner
        in_corner1 = (chain[0][1] == 0) or (chain[0][1] == size-1)
        in_corner2 = (chain[0][2] == 0) or (chain[0][2] == size-1)
        in_corner = in_corner1 and in_corner2
        multiplier1 = 2 if in_corner else 1

        # If these first tiles in the chain are all in the same row or col
        same_row = True
        same_col = True
        for i in range(1, chain_len):
            same_row = same_row and (chain[0][1] == chain[i][1])
            same_col = same_col and (chain[0][2] == chain[i][2])

        # Give "bonus" for these tiles being in same row or col
        multiplier2 = 2 if (same_row or same_col) else 1


# ------------- Stopped Updates Here ---------------------

        # Update metric for this chain
        mult = 256
        for tile_val in chain_vals:
            metric += (mult * tile_val)
            mult = mult/2

        # --- If you have reached the end of the chain, stop
        if end_of_chain:
            metric = metric * multiplier1 * multiplier2
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

def check_in_chain(int )

def calc_metrics2(int[:,:] tiles):
    cdef int i = 0
    return 0

def calc_metrics3(int[:,:] tiles):
    cdef int i = 0
    return 0



