# Various functions for AutoPlay implemented in (slower) Python
# See also AutoPlayUtilsCy for faster implementations of highest-cost functions

from numpy import amax

SIZE = int(4)

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
# Currently only handles 4x4
def calc_metrics1(tiles, mult_base):

    assert tiles.shape[0] == tiles.shape[1]

    size = tiles.shape[0]

    # Check to see if max tile is in upper-right
    max_val = amax(tiles, axis=None)

    in_corner = False
    max_ind = size-1
    for row in range(size):
        for col in range(size):

            if tiles[row][col] == max_val:
                if row in [0,max_ind] and col in [0, max_ind]:
                    in_corner = True

    # Return a metric of 0 if max tile is not in corner
    if in_corner == False:
        return 0.0

    # If tile IS in corner, Calculate metric

    # tile_seq = [((0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (2, 2), (1, 2), (0, 2), (0, 1))]
    tile_seq = [[i, size-1] for i in range(size)]
    for i in range(size-1, -1, -1):
        tile_seq.append([i, size-2])
    tile_seq.append([0, size-3])

    mult = float(mult_base ** (size*2 + 1))
    metric = 0.0

    for [row, col] in tile_seq:
        metric += mult * tiles[row][col]
        mult = mult / mult_base

    # metric = int(tiles[0][3]*256 + tiles[1][3]*128 +
    #              tiles[2][3]*64 + tiles[3][3]*32 +
    #              tiles[3][2]*16 + tiles[2][2]*8 +
    #              tiles[1][2]*4 + tiles[0][2]*2)

    return metric


# Strategy 2:
# More advanced metric. Rewards any "chain" anchored in a corner,
# with additional "reward" for empty tiles
# Currently hard-coded for 4x4 boards via "graph"
def calc_metrics2(tiles, mult_base):

    assert tiles.shape[0] == tiles.shape[1]

    size = tiles.shape[0]

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
    for row in range(size):
        for col in range(size):

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

        metric = 0.              # "Score" metric for the overall chain

        # Start with "max" tile
        chain_vals = [val]
        chain_idxs = [(row, col)]

        # --- Process next up to 8 (or SIZE*2) "largest" tiles
        for _ in range(size*2):

            max_adj_val = 0
            max_adj_idx = (None, None)

            # Explore adjacent tiles for largest
            for (a_row, a_col) in graph[(row, col)]:

                # Don't explore empty tiles, tiles already in chain, or larger tiles
                val = tiles[a_row][a_col]
                if val == 0 or (a_row, a_col) in chain_idxs or val > tiles[row][col]:
                    continue

                # Keep record of (one of) the largest adjacent tiles
                if val > max_adj_val:
                    max_adj_val = val
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

        # If the first "size" tiles in the chain are all in the same row or col
        same_row = all([chain_idxs[0][0] == chain_idxs[i][0] for i in range(1, min(size, len(chain_idxs)))])
        same_col = all([chain_idxs[0][1] == chain_idxs[i][1] for i in range(1, min(size, len(chain_idxs)))])

        # Give "bonus" for these tiles being in same row or col
        multiplier2 = 2 if in_corner and (same_row or same_col) else 1

        # Update metric for this chain
        mult = mult_base ** (size*2 + 1)
        for tile_val in chain_vals:
            metric += tile_val * mult
            mult = mult / mult_base

        # multiplier3 = 2 ** num_empty
        metric = metric * multiplier1 * multiplier2 * num_empty

        metrics.append(metric)

    return max(metrics)


# Strategy 3:
# More advanced metric. Rewards any "chain" anchored in a corner
# Currently hard-coded for 4x4 board via "graph"
def calc_metrics3(tiles, mult_base):

    assert tiles.shape[0] == tiles.shape[1]

    size = tiles.shape[0]

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
    for row in range(size):
        for col in range(size):

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
        if (max1[1] in [0, size-1]) and (max1[2] in [0, size-1]):
            in_corner = True
            corners.append((max1[1], max1[2]))

    if not in_corner:
        return 0

    metrics = []

    for cnr_idx in corners:
        for tile_idxs in graph2[cnr_idx]:
            metric = 0.
            mult = mult_base ** (size*2 + 1)
            for idx in tile_idxs:
                metric += tiles[idx[0]][idx[1]] * mult
                mult = mult / mult_base
            # metric = metric * num_empty
            metrics.append(metric)

    return max(metrics)
