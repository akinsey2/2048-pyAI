# cython: language_level=3

from numpy import intc, copy

DTYPE = intc # Data type of NumPy arrays (tiles[][])
cdef enum:
    SIZE = 4        # Length of single board dimension (4 for 4x4, 5 for 5x5, etc)
    NUM_TILES = 16     # 2*SIZE

def move_tiles(short direction, tiles, int score):

    assert tiles.shape[0] == tiles.shape[1]
    assert tiles.dtype == DTYPE

    cdef int size = tiles.shape[0]

    tiles1 = copy(tiles)
    cdef int [:, :] tiles1_view = tiles1

    # --- Begin primary move_tiles loop

    cdef short idx1, place_idx, eval_idx, inc, row1, row2, col1, col2
    cdef int tile_sum
    cdef bint valid_move = False

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
            elif tiles1_view[row1, col1] == 0:

                # And the next tile is also empty
                if tiles1_view[row2, col2] == 0:
                    eval_idx += inc
                    continue

                # Found a tile, move to empty
                else:
                    tiles1_view[row1, col1] = tiles1_view[row2, col2]
                    tiles1_view[row2, col2] = 0
                    valid_move = True
                    eval_idx += inc
                    continue

            # If the "place" cell is NOT empty
            else:

                # And the "eval" tile is empty, move "eval" to next tile
                if tiles1_view[row2, col2] == 0:
                    eval_idx += inc
                    continue

                # "Place" and "eval" tiles1 equal.  Merge.
                elif tiles1_view[row1, col1] == tiles1_view[row2, col2]:
                    tile_sum = tiles1_view[row1, col1] + tiles1_view[row2, col2]
                    tiles1_view[row1, col1] = tile_sum
                    tiles1_view[row2, col2] = 0
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


def add_random_tile( tiles, float [:] rands, int rand_idx1):

    assert tiles.shape[0] == tiles.shape[1]
    assert tiles.dtype == DTYPE

    cdef int size = tiles.shape[0]

    cdef short row, col
    cdef short open_positions[16][2]
    cdef int value, empty, rand_idx2

    cdef int [:, :] tiles_view = tiles

    empty = 0
    for row in range(size):
        for col in range(size):
            if tiles_view[row, col] == 0:
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

    tiles_view[row, col] = value
    empty -= 1

    return tiles, empty, rand_idx1


# Strategy 0:
# Simplest...Rewards Empty Tiles.

def calc_metrics0(tiles):

    cdef int size = tiles.shape[0]

    assert tiles.shape[0] == tiles.shape[1]
    assert tiles.dtype == DTYPE

    cdef const int [:, :] tiles_view = tiles
    cdef int num_empty = 0, row, col

    for row in range(size):
        for col in range(size):
            if tiles_view[row, col] == 0:
                num_empty += 100

    return num_empty


# Strategy 1:
# Simple metric...Rewards Upper-Right aligned chain.
def calc_metrics1(tiles, double mult_base):

    cdef int size = tiles.shape[0]

    assert tiles.shape[0] == tiles.shape[1]
    # assert tiles.dtype == DTYPE

    cdef const int [:, :] tiles_view = tiles

    # Check to see if max tile is in upper-right
    cdef int max_val = 0, val, row, col
    cdef short maxs_len = 0

    cdef int maxs[NUM_TILES][3]
    cdef int [:, :] maxs_view = maxs
    maxs_view[:, :] = 0

    for row in range(size):
        for col in range(size):

            val = tiles_view[row, col]

            if val < max_val:
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

    cdef bint in_corner0 = False
    cdef int i = 0

    for i in range(maxs_len):

        if (maxs[i][1] == 0) and (maxs[i][2] == (size-1)):
            in_corner0 = True

    # --- If max tile is NOT in upper-right, metric is zero.
    cdef double metric = 0

    if in_corner0 == False:
        return metric

    # Otherwise, calculate the metric
    cdef double mult
    cdef int rgt_col = size - 1, nxt_col = size - 2

    # Right Col, top to bottom
    mult = mult_base ** (size * 2)

    for i in range(size):
        metric += mult * tiles_view[i, rgt_col]
        mult = mult / mult_base

    # Second-to-right col, bottom to top
    for i in range(size-1, -1, -1):
        metric += mult * tiles_view[i, nxt_col]
        mult = mult / mult_base

    return metric


# Strategy 2:
# More advanced metric. Rewards any "chain" anchored in a corner,
# with additional "reward" for empty tiles

def calc_metrics2(tiles, double mult_base):

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

    cdef int size = tiles.shape[0]

    assert tiles.shape[0] == tiles.shape[1]
    assert tiles.dtype == DTYPE

    cdef const int [:, :] tiles_view = tiles

    # Find greatest tile(s) value and indeces, the starting point(s) of the "chain" calculation(s)
    cdef int max_val = 0, val
    cdef short maxs_len = 0, num_empty = 0, row, col

    cdef int maxs[NUM_TILES][3]
    cdef int [:, :] maxs_view = maxs
    maxs_view[:, :] = 0

    for row in range(size):
        for col in range(size):

            val = tiles_view[row, col]

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

    # --- Master Loop: Traverses chain(s) and calculates chain quality metric/score
    # Tiles must be adjacent, and weakly decreasing to comprise a chain.

    cdef int max_adj[3]
    cdef short metrics_len = 0, chain_len = 0, curr_row, curr_col, i
    # cdef bint end_of_chain
    cdef double metric, mult, multiplier1, multiplier2
    cdef bint in_corner1, in_corner2, in_corner, same_row, same_col

    # Initialize metrics array
    cdef double metrics[NUM_TILES]
    cdef double [:] metrics_view = metrics
    metrics_view[:] = 0

    # Initialize chain 2D array
    cdef int chain[NUM_TILES][3]
    cdef int [:, :] chain_view = chain
    chain_view[:, :] = 0

    for i in range(maxs_len):

        # end_of_chain = False    # Have reached the end of the chain?
        metric = 0              # "Score" metric for the overall chain

        # Start with "max" tile
        chain[0][0] = maxs[i][0]
        chain[0][1] = maxs[i][1]
        chain[0][2] = maxs[i][2]
        chain_len = 1

        # --- Process next 7 (or SIZE-1) "largest" tiles of "chain"
        for _ in range(2*size-1):

            max_adj[0] = 0
            max_adj[1] = -1
            max_adj[2] = -1

            max_adj = max_adjacent(tiles, chain, chain_len, max_adj, size)

            # If Reached the end of the chain, stop looking for more tiles
            if max_adj[0] > chain[chain_len - 1][0] or max_adj[0] == 0:
                # end_of_chain = True
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
        multiplier1 = 2 if in_corner else 1

        # If the first <=4 tiles in the chain are all in the same row or col
        same_row = True
        same_col = True
        for i in range(1, min(4, chain_len)):
            same_row = same_row and (chain[0][1] == chain[i][1])
            same_col = same_col and (chain[0][2] == chain[i][2])

        # Give "bonus" for these tiles being in same row or col
        multiplier2 = 2 if in_corner and (same_row or same_col) else 1

        # Update metric for this chain
        mult = mult_base ** chain_len
        for i in range(chain_len):
            metric += mult*chain[i][0]
            mult = mult / mult_base

        metric = metric * multiplier1 * multiplier2 * num_empty
        metrics[metrics_len] = metric
        metrics_len += 1

        continue        # Unnecessary, but helps readability for long loop

    # --- Done calculating the metrics for all chains

    # --- Find the maximum value of metrics
    cdef double maximum = 0
    for i in range(metrics_len):
        if metrics[i] > maximum:
            maximum = metrics[i]

    return maximum


# Given a tile [row, col], find and return the largest adjacent tile
# Inputs:
#       int[:,:] tiles_view   - memoryview of numpy array of current game board tiles
#       int chain[16][3] - C array of tiles found thus far in current "chain"
#       int chain_len    - length of the current chain
#       int row, int col - row and column indeces of the current tile to find adjacents of
#       int size         - the dimension length of the game board  (4 if 4x4 tiles)
# Returns:
#
cdef int * max_adjacent(const int [:, :] tiles_view, int chain[NUM_TILES][3], int chain_len, int max_adj[3], int size):

    cdef int curr_val, abv_val, rgt_val, blw_val, lft_val
    cdef int row, col, abv_row, rgt_col, blw_row, lft_col
    cdef bint in_chain

    # Initialize
    row = chain[chain_len - 1][1]
    col = chain[chain_len - 1][2]
    max_adj[0] = 0
    max_adj[1] = -1
    max_adj[2] = -1
    curr_val = tiles_view[row, col]

    # Explore adjacent tiles for largest

    # Above
    abv_row = row - 1
    if abv_row > -1:

        in_chain = check_in_chain(chain, chain_len, abv_row, col)
        abv_val = tiles_view[abv_row, col]
        if not in_chain and abv_val <= curr_val and abv_val > max_adj[0]:
            max_adj[0] = abv_val
            max_adj[1] = abv_row
            max_adj[2] = col

    # Right
    rgt_col = col + 1
    if rgt_col < size:

        in_chain = check_in_chain(chain, chain_len, row, rgt_col)
        rgt_val = tiles_view[row, rgt_col]
        if not in_chain and rgt_val <= curr_val and rgt_val > max_adj[0]:
            max_adj[0] = rgt_val
            max_adj[1] = row
            max_adj[2] = rgt_col

    # Below
    blw_row = row + 1
    if blw_row < size:

        in_chain = check_in_chain(chain, chain_len, blw_row, col)
        blw_val = tiles_view[blw_row, col]
        if not in_chain and blw_val <= curr_val and blw_val > max_adj[0]:
            max_adj[0] = blw_val
            max_adj[1] = blw_row
            max_adj[2] = col

    # Left
    lft_col = col - 1
    if lft_col > -1:

        in_chain = check_in_chain(chain, chain_len, row, lft_col)
        lft_val = tiles_view[row, lft_col]
        if not in_chain and lft_val <= curr_val and lft_val > max_adj[0]:
            max_adj[0] = lft_val
            max_adj[1] = row
            max_adj[2] = lft_col

    return max_adj

# Check whether a particular tile [row, col] is already saved in "chain"
# Return True if this tile is already in the chain, False otherwise
cdef bint check_in_chain(int chain[NUM_TILES][3], int chain_len, int row, int col):
    cdef int i
    cdef bint in_chain = False

    for i in range(chain_len):
        if (chain[i][1] == row) and (chain[i][2] == col):
            in_chain = True
            break

    return in_chain


# Strategy 3:
# More advanced metric. Rewards any "chain" anchored in a corner,
# with additional "reward" for empty tiles
def calc_metrics3(tiles, double mult_base):

    cdef int size = tiles.shape[0]

    assert tiles.shape[0] == tiles.shape[1]
    assert tiles.dtype == DTYPE

    cdef const int [:, :] tiles_view = tiles

    # Find the greatest tile(s) value and indices, the starting point(s) of the "chain" calculation(s)
    cdef int max_val = 0, val
    cdef short maxs_len = 0, num_empty = 0, row, col

    cdef int maxs[NUM_TILES][3]
    cdef int [:, :] maxs_view = maxs
    maxs_view[:, :] = 0

    for row in range(size):
        for col in range(size):

            val = tiles_view[row, col]

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

    cdef bint row_in_corner = False, col_in_corner = False, in_corner = False
    cdef int max_corners[4][3]
    cdef int i, corners_len = 0

    for i in range(maxs_len):
        row_in_corner = (maxs[i][1] == 0 or maxs[i][1] == size-1)
        col_in_corner = (maxs[i][2] == 0 or maxs[i][2] == size-1)
        if row_in_corner and col_in_corner:
            in_corner = True
            max_corners[corners_len][0] = maxs[i][0]
            max_corners[corners_len][1] = maxs[i][1]
            max_corners[corners_len][2] = maxs[i][2]
            corners_len += 1

    # If there are no max tiles in corners, metric is 0
    if not in_corner:
        return 0.0


    cdef short[9][2] chain00a = [[0, 0], [0, 1], [0, 2], [0, 3], [1, 3], [1, 2], [1, 1], [1, 0], [2, 0]]
    cdef short[9][2] chain00b = [[0, 0], [1, 0], [2, 0], [3, 0], [3, 1], [2, 1], [1, 1], [0, 1], [0, 2]]
    cdef short[9][2] chain03a = [[0, 3], [1, 3], [2, 3], [3, 3], [3, 2], [2, 2], [1, 2], [0, 2], [0, 1]]
    cdef short[9][2] chain03b = [[0, 3], [0, 2], [0, 1], [0, 0], [1, 0], [1, 1], [1, 2], [1, 3], [2, 3]]
    cdef short[9][2] chain33a = [[3, 3], [3, 2], [3, 1], [3, 0], [2, 0], [2, 1], [2, 2], [2, 3], [1, 3]]
    cdef short[9][2] chain33b = [[3, 3], [2, 3], [1, 3], [0, 3], [0, 2], [1, 2], [2, 2], [3, 2], [3, 1]]
    cdef short[9][2] chain30a = [[3, 0], [2, 0], [1, 0], [0, 0], [0, 1], [1, 1], [2, 1], [3, 1], [3, 2]]
    cdef short[9][2] chain30b = [[3, 0], [3, 1], [3, 2], [3, 3], [2, 3], [2, 2], [2, 1], [2, 0], [1, 0]]

    cdef double metrics[8]
    cdef short metrics_len = 0
    cdef double mult = 256, metric = 0
    cdef short[9][2] chain1, chain2

    for i in range(corners_len):

        if max_corners[i][1] == 0 and max_corners[i][2] == 0:
            chain1 = chain00a
            chain2 = chain00b

        elif max_corners[i][1] == 0 and max_corners[i][2] == 3:
            chain1 = chain03a
            chain2 = chain03b

        elif max_corners[i][1] == 3 and max_corners[i][2] == 0:
            chain1 = chain30a
            chain2 = chain30b

        elif max_corners[i][1] == 3 and max_corners[i][2] == 3:
            chain1 = chain33a
            chain2 = chain33b

        metric = 0.0
        mult = mult_base ** 9
        for j in range(9):
            row = chain1[j][0]
            col = chain1[j][1]
            metric += tiles_view[row][col] * mult
            mult = mult / mult_base

        metrics[metrics_len] = metric
        metrics_len += 1

        metric = 0.0
        mult = mult_base ** 9
        for j in range(9):
            row = chain2[j][0]
            col = chain2[j][1]
            metric += tiles_view[row][col] * mult
            mult = mult / mult_base

        metrics[metrics_len] = metric
        metrics_len += 1

    # Find the largest of the metrics calculated for this board
    cdef double maximum = 0

    for i in range(metrics_len):
        if metrics[i] > maximum:
            maximum = metrics[i]

    # max_c_list = list(max_corners)
    # max_c_list = max_c_list[:corners_len]
    return maximum


def calc_metrics4(const int [:, :] tiles_view):
    cdef int i = 0
    return 0



