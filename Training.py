import AutoPlayTests
import csv
import time
from math import exp
from numpy import linspace


if __name__ == '__main__':

    records = []

    # Parameters
    calc_min = 3
    calc_max = 3
    tree_depth_min = 6
    tree_depth_max = 6
    topx_min = .02
    topx_max = .04
    topx_steps = 3
    calc_mult_min = 1
    calc_mult_max = 2
    calc_mult_steps = 6
    reps = 25

    # Estimate Time Required
    tot_games = (calc_max - calc_min + 1) * (tree_depth_max - tree_depth_min + 1) * (topx_max - topx_min + 1) * reps

    total_time = 0
    calc_reps = calc_max - calc_min + 1
    tree_depth_reps = tree_depth_max - tree_depth_min + 1
    tot_games = calc_reps * tree_depth_reps * topx_steps * calc_mult_steps * reps
    reps2 = calc_reps * topx_steps * (calc_mult_steps + 1) * reps
    # for calc_option in range(calc_min, calc_max+1):
    #     for tree_depth in range(tree_depth_min, tree_depth_max+1):
    #         for topx in range(topx_min, topx_max+1):
    #             calc_reps = calc_max - calc_min + 1
    #             topx_reps = topx_max - topx_min + 1
    #             calc_mult_reps = (calc_mult_max -
    #             total_time += reps*(*0.05*exp(1.15*tree_depth)

    for tree_depth in range(tree_depth_min, tree_depth_max + 1):
        total_time += reps2*0.05*exp(1.15*tree_depth)

    print(f"Total iterations: {tot_games} | Time Estimate: {total_time/60} minutes | {total_time/3600} hours")
    ans = input(f"Continue [y/n]? ")
    if ans in ["n", "N"]:
        quit()

    # Initialize CSV File
    date1 = time.ctime().replace(" ", "_").replace(":", "_")
    filename = f"calc{calc_min}to{calc_max}_td{tree_depth_min}to{tree_depth_max}" + \
               f"_topx{topx_min}to{topx_max}_calcmult{calc_mult_min}to{calc_mult_max}" + \
               f"_{date1}.csv"

    with open(filename, mode='x', newline='') as file1:
        csv_writer = csv.writer(file1, dialect="excel", delimiter=",")
        csv_writer.writerow(["Calc_Option", "Tree_Depth", "TopX", "Calc_Mult",
                             "Game_Number", "Score", "Duration"])  # Must write header row manually

    # Start Main Loop to Permute parameters
    overall_start_time = time.perf_counter()

    for calc_option in range(calc_min, calc_max+1):
        print(f"\n***Calc: {calc_option}  ", end="", flush=True)

        for tree_depth in range(tree_depth_min, tree_depth_max+1):
            print(f"***TreeDp: {tree_depth}  ", end="", flush=True)

            for topx in linspace(topx_min, topx_max, num=topx_steps):
                print(f"\n***TopX: {topx*100}%  ", end="", flush=True)

                for calc_mult in linspace(calc_mult_min, calc_mult_max, num=calc_mult_steps):
                    print(f"\n***Mult_Base: {calc_mult}  ", end="", flush=True)

                    for game_num in range(reps):
                        print(f"\n***Repetition Number: {game_num}  ", flush=True)
                        total_fwd_tiles = 0
                        for i in range(tree_depth+1):
                            total_fwd_tiles += 4**i

                        if (2**topx) > (total_fwd_tiles / 3):
                            continue

                        start_time = time.perf_counter()
                        ap = AutoPlayTests.play_games(1, tree_depth, topx, calc_option, calc_mult)
                        end_time = time.perf_counter()
                        print(ap)

                        print(f"{game_num} ({ap.game.score}), ", end="", flush=True)

                        # Save Records to CSV File
                        data = [calc_option, tree_depth, topx, calc_mult, game_num,
                                ap.game.score, end_time-start_time]

                        with open(filename, mode="a", newline="") as file1:
                            csv_writer = csv.writer(file1, dialect="excel", delimiter=",")
                            csv_writer.writerow(data)

                        # records.append(data)

    overall_end_time = time.perf_counter()
    # records.append([overall_start_time, overall_end_time, overall_end_time-overall_start_time])
    with open(filename, mode="a", newline="") as file1:
        csv_writer = csv.writer(file1, dialect="excel", delimiter=",")
        csv_writer.writerow([overall_start_time, overall_end_time, overall_end_time-overall_start_time])

