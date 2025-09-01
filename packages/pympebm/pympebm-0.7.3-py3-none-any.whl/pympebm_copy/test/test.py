from pympebm_copy.run import run_mpebm
import os
import json 
import re 

def extract_components(filename):
    pattern = r'^j(\d+)_r([\d.]+)_E(.*?)_m(\d+)$'
    match = re.match(pattern, filename)
    if match:
        return match.groups()  # returns tuple (J, R, E, M)
    return None

cwd = os.getcwd()
print("Current Working Directory:", cwd)
data_dir = f"{cwd}/pympebm/test/my_data"
data_files = os.listdir(data_dir) 
data_files = [x for x in data_files if 'PR' not in x]

OUTPUT_DIR = 'algo_results'

with open(f"{cwd}/pympebm/test/true_order_and_stages.json", "r") as f:
    true_order_and_stages = json.load(f)

for data_file in data_files:
    estimated_partial_rankings = []

    fname = data_file.replace('.csv', '')
    J, R, E, M = extract_components(fname)

    true_order_dict = true_order_and_stages[fname]['true_order']
    true_stages = true_order_and_stages[fname]['true_stages']
    partial_rankings = true_order_and_stages[fname]['ordering_array']
    n_partial_rankings = len(partial_rankings)

    for idx in range(n_partial_rankings):
        # partial ranking data file path
        pr_data_file = f"{data_dir}/PR{idx}_m{M}_j{J}_r{R}_E{E}.csv"

        results = run_mpebm(
            data_file=pr_data_file,
            save_results=False,
            save_details=True,
            n_iter=500,
            burn_in=10,
            seed = 53
        )
        order_with_highest_ll = results['order_with_highest_ll']
        # Sort by value, the sorted result will be a list of tuples
        partial_ordering = [k for k, v in sorted(order_with_highest_ll.items(), key=lambda item: item[1])]
        estimated_partial_rankings.append(partial_ordering)

    for mp_method in ['Pairwise', 'Mallows', 'BT', 'PL']:
        run_mpebm(
            partial_rankings=estimated_partial_rankings,
            mp_method=mp_method,
            save_results=True,
            data_file= os.path.join(data_dir, data_file),
            output_dir=OUTPUT_DIR,
            output_folder=mp_method,
            n_iter=500,
            n_shuffle=2,
            burn_in=10,
            thinning=1,
            true_order_dict=true_order_dict,
            true_stages = true_stages,
            skip_heatmap=True,
            skip_traceplot=True,
            save_details=False,
            seed = 53
        )

    run_mpebm(
        save_results=True,
        data_file= os.path.join(data_dir, data_file),
        output_dir=OUTPUT_DIR,
        output_folder='saebm',
        n_iter=500,
        n_shuffle=2,
        burn_in=10,
        thinning=1,
        true_order_dict=true_order_dict,
        true_stages = true_stages,
        skip_heatmap=True,
        skip_traceplot=True,
        save_details=False,
        seed = 53
    )