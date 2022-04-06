import AutoPlay
import csv
import time
from math import exp


if __name__ == '__main__':

    records = []

    # Parameters
    calc_min = 0
    calc_max = 0
    tree_depth_min = 5
    tree_depth_max = 7
    topx_min = 4
    topx_max = 10
    reps = 3

    # Estimate Time Required
    tot_games = (calc_max - calc_min + 1) * (tree_depth_max - tree_depth_min + 1) * (topx_max - topx_min + 1) * reps

    total_time = 0
    for calc_option in range(calc_min, calc_max+1):
        for tree_depth in range(tree_depth_min, tree_depth_max+1):
            for topx in range(topx_min, topx_max+1):
                total_time += reps*0.05*exp(1.15*tree_depth)

    print(f"Total iterations: {tot_games} | Time Estimate: {total_time/60} minutes")
    ans = input(f"Continue [y/n]? ")
    if ans in ["n", "N"]:
        quit()

    # Start Main Loop to Permute parameters
    overall_start_time = time.perf_counter()

    for calc_option in range(calc_min, calc_max+1):
        print(f"\nCalc: {calc_option}  ", end="")

        for tree_depth in range(tree_depth_min, tree_depth_max+1):
            print(f"TreeDp: {tree_depth}  ", end="")

            for topx in range(topx_min, topx_max+1):
                print(f"\nTopX: {topx}: ", end="")

                for game_num in range(reps):
                    print(f"{game_num} ", end="")

                    total_fwd_tiles = 0
                    for i in range(tree_depth+1):
                        total_fwd_tiles += 4**i

                    if (2**topx) > (total_fwd_tiles / 3):
                        continue

                    start_time = time.perf_counter()
                    ap = AutoPlay.play_games(1, tree_depth, topx, calc_option)
                    end_time = time.perf_counter()
                    records.append([calc_option, tree_depth, topx, game_num, ap.game.score, end_time-start_time])

    overall_end_time = time.perf_counter()
    records.append([overall_start_time, overall_end_time, overall_end_time-overall_start_time])

    # Save Records to CSV File
    date1 = time.ctime().replace(" ", "_").replace(":", "_")

    filename = f"td{tree_depth_min}to{tree_depth_max}_topx{topx_min}to{topx_max}_{date1}.csv"

    with open(filename, mode='w') as file1:
        csv_writer = csv.writer(file1, dialect="excel", delimiter=",")
        csv_writer.writerow(["Calc_Option", "Tree_Depth", "TopX", "Game_Number", "Score", "Duration"])  # Must write header row manually
        for row_list in records:
            csv_writer.writerow(row_list)  # pass write data as list which will be str() formatted


