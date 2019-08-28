import pandas as pd
import numpy as np
import os
import sys

INSTANCE_SELECTION = [
    ['hard1', 7200, 19000, None, None, 10],
    ['hard2', 1800, 7200, None, None, 10],
    ['medium1', 300, 1800, None, None, 30],
    ['medium2', 60, 300, None, None, 10],
    ['medium3', 10, 60, None, None, 10],
    ['medium4', 1, 10, None, None, 10],
    ['easy1', 0, 1, 60, 7200, 10],
    ['easy2', 0, 1, 0, 60, 10]
]

INSTANCE_SELECTION2 = [
    ['hard1', 7200, 19000, None, None, 5],
    ['hard2', 1800, 7200, None, None, 15],
    ['medium1a', 1500, 1800, None, None, 5],
    ['medium1b', 1200, 1500, None, None, 5],
    ['medium1c', 900, 1200, None, None, 5],
    ['medium1d', 600, 900, None, None, 5],
    ['medium1e', 300, 600, None, None, 5],
    ['medium2', 60, 300, None, None, 10],
    ['medium3', 10, 60, None, None, 10],
    ['medium4', 1, 10, None, None, 10],
    ['easy1', 0, 1, 60, 7200, 10],
    ['easy2', 0, 1, 0, 60, 10]
]

INSTANCE_SELECTION3 = [
    ['hard1', 7200, 19000, None, None, 19, 0.99, 0.01],
    ['hard2', 1800, 7200, None, None, 31, 0.99, 0.01],
    ['medium1a', 1500, 1800, None, None, 25, 0.99, 0.01],
    ['medium1b', 1200, 1500, None, None, 25, 0, 1],
    ['medium1c', 900, 1200, None, None, 20, 0.99, 0.01],
    ['medium1d', 600, 900, None, None, 20, 0.99, 0.01],
    ['medium1e', 300, 600, None, None, 10, 0.99, 0.01],
    ['medium2', 60, 300, None, None, 40, 0.99, 0.01],
    ['medium3', 10, 60, None, None, 10, 0.65, 0.35]
]

INSTANCE_SELECTION_TESTING = [
    ['medium4', 1, 10, None, None, 10, 0.5, 0.5],
    ['easy1', 0, 1, 60, 7200, 10, 0.5, 0.5]
]

GUROBI_COLUMN = 'gurobi_single_core_time'
GUROBI_RESULT_COLUMN = "gurobi_objective"
GLUCOSE_ORIGINAL_RESULT_COLUMN = "glucose_result (original sat instance)"
GLUCOSE_COLUMN = 'glucose_time (converted vc)'
GLUCOSE_RESULT_COLUMN = 'glucose_result (converted vc)'

VC_SOURCES = ["vc-pace-2019"]

# for version 1 and 2 only
# VC_PROBS = 0.7 # modify this to change proportion
# SAT_PROBS = 1 - VC_PROBS

RESULT_FILE = "selected-aavc.txt"
TESTING_RESULT_FILE = "selected-testing-aavc.txt"

def gen_probs(df, vc_probs, sat_probs):
    sat_instance = 0
    vc_instance = 0

    for _, row in df.iterrows():
        if row["source"] in VC_SOURCES:
            vc_instance += 1
        else:
            sat_instance += 1
    
    sys.stderr.write("vc: {}, sat: {}\n\n".format(vc_instance, sat_instance))
    result = []

    for _, row in df.iterrows():
        if row["source"] in VC_SOURCES:
            result.append(vc_probs / vc_instance)
        else:
            result.append(sat_probs / sat_instance)

    return result

def create_selection(csv_file, instance_selection):
    df = pd.read_csv(csv_file)
    df[[GUROBI_RESULT_COLUMN, GLUCOSE_ORIGINAL_RESULT_COLUMN]] = df[[GUROBI_RESULT_COLUMN, GLUCOSE_ORIGINAL_RESULT_COLUMN]].fillna(value=0)

    # result = []
    # for _, row in df.iterrows():
    #     if row["source"] in VC_SOURCES:
    #         result.append(["asd", row["instance"]])
    
    # result = sorted(result, key=lambda x: x[1])
    # return result
    result = []
    for selection in instance_selection:
        sel_df = df.copy()
        sel_df = sel_df.loc[(sel_df[GUROBI_COLUMN] >= selection[1]) # select in range
                            & (sel_df[GUROBI_COLUMN] < selection[2])
                            & (
                                (sel_df[GUROBI_RESULT_COLUMN] > 0) # then select rows with found solution
                                | (sel_df[GLUCOSE_ORIGINAL_RESULT_COLUMN] > 0) 
                                # | (sel_df["source"] == "vc-pace-2019") # or from original vc selection
                              )]
        if selection[3] is not None:
            sel_df = sel_df.loc[(sel_df[GLUCOSE_COLUMN] >= selection[3]) 
                                & (sel_df[GLUCOSE_COLUMN] < selection[4])
                                & (sel_df[GLUCOSE_RESULT_COLUMN] > 0)]
        sys.stderr.write("{}:\n".format(selection[0]))
        sys.stderr.write("gurobi time: [{}, {}), glucose time: [{}, {}]\n".format(selection[1], selection[2], selection[3], selection[4]))
        p = gen_probs(sel_df, selection[6], selection[7])

        instances = sel_df
        instances = sel_df.sample(n=selection[5], replace=False, weights=p)
        for _, row in instances.iterrows():
            # print("{}: {}".format(selection[0], row["instance"]))
            # if row[GUROBI_RESULT_COLUMN] == 0:
            #     sys.stderr.write("{} is using glucose ori\n".format(row["instance"]))
            result.append([selection[0], row["instance"]])
    
    return result

def main():
    csv_file = sys.argv[1]
    selected_instances = create_selection(csv_file, INSTANCE_SELECTION3[::-1])
    testing_instances = create_selection(csv_file, INSTANCE_SELECTION_TESTING[::-1])

    with open(RESULT_FILE, "w") as stream:
        for group, r in selected_instances:
            stream.write("{}: {}\n".format(group, r))
    
    with open(TESTING_RESULT_FILE, "w") as stream:
        for group, r in testing_instances:
            stream.write("{}: {}\n".format(group, r))

if __name__ == "__main__":
    main()