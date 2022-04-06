# cython: language_level=3

import numpy as np

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

def calc_metrics1(int[:,:] tiles, short size):

    cdef int max_val, num_empty, val, metric, mult, multiplier1, multiplier2, maximum
    cdef short row, col, a_row, a_col, chain_idx, curr_row, curr_col
    cdef int maxs[8][3]
    cdef short maxs_len
    cdef int chain[8][3]
    cdef short chain_len
    cdef int max_adj[3]
    cdef int metrics[8]
    cdef short metrics_len, i
    cdef bint end_of_chain, in_corner1, in_corner2, in_corner, same_row, same_col

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

    # Find greatest tile(s) value and indeces, the starting point(s) of the "chain" calculation(s)
    max_val = 0
    maxs_len = 0
    num_empty = 0
    for row in range(size):
        for col in range(size):

            val = tiles[row, col]

            if val == 0:
                num_empty += 1
            elif val < max_val:
                continue
            # Value is greater
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

    # # DEBUG:
    # print("Maxes: ", end="")
    # for i in range(maxs_len):
    #     print(f"{maxs[i][0]}, ", end = "")

    # --- Master Loop: Traverses chain(s) and calculates chain quality metric/score
    metrics_len = 0

    for i in range(maxs_len):

        end_of_chain = False    # Have reached the end of the chain?
        metric = 0              # "Score" metric for the overall chain

        # Start with "max" tile
        chain[0][0] = maxs[i][0]
        chain[0][1] = maxs[i][1]
        chain[0][2] = maxs[i][2]
        chain_len = 1

        # --- Process next 7 (or SIZE-1) "largest" tiles of "chain"
        for _ in range(7):

            max_adj[0] = 0
            max_adj[1] = -1
            max_adj[2] = -1

            max_adj = max_adjacent(tiles, chain, chain_len, max_adj, size)

            # # DEBUG
            # curr_row = chain[chain_len-1][1]
            # curr_col = chain[chain_len-1][2]
            # print(f"\n[{curr_row}, {curr_col}]: {tiles[curr_row, curr_col]},  " +
            #       f"Max Adj [{max_adj[1]}, {max_adj[2]}]: {max_adj[0]},  " +
            #       f"chain_len = {chain_len},  ")

            # If Reached the end of the chain, stop looking for more tiles
            if max_adj[0] > chain[chain_len - 1][0] or max_adj[0] == 0:
                end_of_chain = True
                break

            # Else, save this next tile in chain, and keep looking
            chain[chain_len][0] = max_adj[0]
            chain[chain_len][1] = max_adj[1]
            chain[chain_len][2] = max_adj[2]
            chain_len += 1

        # --- Done Identifying this chain

        # Add bonus if largest tile in corner
        in_corner1 = (chain[0][1] == 0) or (chain[0][1] == size-1)
        in_corner2 = (chain[0][2] == 0) or (chain[0][2] == size-1)
        in_corner = in_corner1 and in_corner2
        multiplier1 = 1 if in_corner else 0

        # If the first <=4 tiles in the chain are all in the same row or col
        same_row = True
        same_col = True
        for i in range(1, min(4, chain_len)):
            same_row = same_row and (chain[0][1] == chain[i][1])
            same_col = same_col and (chain[0][2] == chain[i][2])

        # Give "bonus" for these tiles being in same row or col
        multiplier2 = 2 if in_corner and (same_row or same_col) else 1

        # Update metric for this chain
        mult = 8
        for i in range(chain_len):
            metric += mult*chain[i][0]
            mult -= 1

        metric = metric * multiplier1 * multiplier2 * num_empty
        metrics[metrics_len] = metric
        metrics_len += 1

        # # DEBUG
        # print("\nChain: ", end="")
        # for i in range(chain_len):
        #     print(f"{chain[i][0]}, ", end="", flush=True)
        # print(f"  Mult1 = {multiplier1}  Mult2 = {multiplier2}")
        continue

    # --- Done calculating the metrics for all chains

    # --- Find the maximum value of metrics
    maximum = 0
    for i in range(metrics_len):
        if metrics[i] > maximum:
            maximum = metrics[i]

    return maximum


# Given a tile [row, col], find and return the largest adjacent tile
# Inputs:
#       int[:,:] tiles   - memoryview of numpy array of current game board tiles
#       int chain[16][3] - C array of tiles found thus far in current "chain"
#       int chain_len    - length of the current chain
#       int row, int col - row and column indeces of the current tile to find adjacents of
#       int size         - the dimension length of the game board  (4 if 4x4 tiles)
# Returns:
#
cdef int *max_adjacent(int[:,:] tiles, int chain[8][3], int chain_len, int max_adj[3], int size):

    cdef int curr_val, abv_val, rgt_val, blw_val, lft_val
    cdef int row, col, abv_row, rgt_col, blw_row, lft_col
    cdef bint in_chain

    # Initialize
    row = chain[chain_len - 1][1]
    col = chain[chain_len - 1][2]
    max_adj[0] = 0
    max_adj[1] = -1
    max_adj[2] = -1
    curr_val = tiles[row, col]

    # Explore adjacent tiles for largest

    # Above
    abv_row = row - 1
    if abv_row > -1:

        in_chain = check_in_chain(chain, chain_len, abv_row, col)
        abv_val = tiles[abv_row, col]
        if not in_chain and abv_val <= curr_val and abv_val > max_adj[0]:
            max_adj[0] = abv_val
            max_adj[1] = abv_row
            max_adj[2] = col

    # Right
    rgt_col = col + 1
    if rgt_col < size:

        in_chain = check_in_chain(chain, chain_len, row, rgt_col)
        rgt_val = tiles[row, rgt_col]
        if not in_chain and rgt_val <= curr_val and rgt_val > max_adj[0]:
            max_adj[0] = rgt_val
            max_adj[1] = row
            max_adj[2] = rgt_col

    # Below
    blw_row = row + 1
    if blw_row < size:

        in_chain = check_in_chain(chain, chain_len, blw_row, col)
        blw_val = tiles[blw_row, col]
        if not in_chain and blw_val <= curr_val and blw_val > max_adj[0]:
            max_adj[0] = blw_val
            max_adj[1] = blw_row
            max_adj[2] = col

    # Left
    lft_col = col - 1
    if lft_col > -1:

        in_chain = check_in_chain(chain, chain_len, row, lft_col)
        lft_val = tiles[row, lft_col]
        if not in_chain and lft_val <= curr_val and lft_val > max_adj[0]:
            max_adj[0] = lft_val
            max_adj[1] = row
            max_adj[2] = lft_col

    return max_adj

# Check whether a particular tile [row, col] is already saved in "chain"
# Return True if this tile is already in the chain, False otherwise
cdef bint check_in_chain(int chain[8][3], int chain_len, int row, int col):
    cdef int i
    cdef bint in_chain = False

    for i in range(chain_len):
        if (chain[i][1] == row) and (chain[i][2] == col):
            in_chain = True
            break

    return in_chain


def calc_metrics2(int[:,:] tiles):
    cdef int i = 0
    return 0

def calc_metrics3(int[:,:] tiles):
    cdef int i = 0
    return 0



