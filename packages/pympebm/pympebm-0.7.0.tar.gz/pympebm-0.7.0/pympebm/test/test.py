from pympebm import run_mpebm, get_params_path
from pympebm.mp_utils import get_unique_rows
import os
import json 
import re 
import numpy as np 
from collections import Counter, defaultdict

def extract_components(filename):
    pattern = r'^j(\d+)_r([\d.]+)_E(.*?)_m(\d+)$'
    match = re.match(pattern, filename)
    if match:
        return match.groups()  # returns tuple (J, R, E, M)
    return None

ENERGY_INFLUENCE = 1.2

if __name__=='__main__':

    params_file = get_params_path()

    with open(params_file) as f:
        params = json.load(f)

    biomarkers_str = np.array(sorted(params.keys()))
    biomarkers_int = np.arange(0, len(params))
    str2int = dict(zip(biomarkers_str, biomarkers_int))
    int2str = dict(zip(biomarkers_int, biomarkers_str))

    rng = np.random.default_rng(42)

    cwd = os.getcwd()
    print("Current Working Directory:", cwd)
    for data_sub_dir in ['Mallows_Tau', 'BT', 'Random', 'PL', 'Pairwise']:
        # energy_prior = {'Pairwise': 0.8, 'BT': 0.9, 'PL': 0.8, 'Mallows_Tau': 0.6, 'Random':0.001}[data_sub_dir]
        data_dir = f"{cwd}/pympebm/test/my_data/{data_sub_dir}"
        data_files = os.listdir(data_dir) 
        data_files = [x for x in data_files if 'PR' not in x]

        OUTPUT_DIR = os.path.join('algo_results', data_sub_dir)

        with open(f"{cwd}/pympebm/test/true_order_and_stages_{data_sub_dir}.json", "r") as f:
            true_order_and_stages = json.load(f)

        for data_file in data_files[:3]:
            estimated_partial_rankings = []
            # final_theta_phi_list = []

            fname = data_file.replace('.csv', '')
            J, R, E, M = extract_components(fname)

            true_order_dict = true_order_and_stages[fname]['true_order']
            true_stages = true_order_and_stages[fname]['true_stages']
            partial_rankings = true_order_and_stages[fname]['ordering_array']
            n_partial_rankings = len(partial_rankings)

            for idx in range(n_partial_rankings):
                # partial ranking data file path
                pr_data_file = f"{data_dir}/PR{idx}_m{M}_j{int(J)*3}_r{R}_E{E}.csv"

                random_state = rng.integers(0, 2**32 - 1)
                results = run_mpebm(
                    data_file=pr_data_file,
                    save_results=False,
                    n_iter=10000,
                    burn_in=100,
                    seed = random_state,
                    save_theta_phi=True
                )
                order_with_highest_ll = results['order_with_highest_ll']
                # Sort by value, the sorted result will be a list of tuples
                partial_ordering = [k for k, v in sorted(order_with_highest_ll.items(), key=lambda item: item[1])]
                partial_ordering = [str2int[bm] for bm in partial_ordering]
                estimated_partial_rankings.append(partial_ordering)
            #     final_theta_phi_list.append(results['final_theta_phi_params'])
            
            # theta_phi_use = merge_mean_dicts(final_theta_phi_list)

            padded_partial_rankings = get_unique_rows(estimated_partial_rankings)
            for mp_method in ['BT', 'PL', 'Pairwise', 'Mallows_Tau']:
                random_state = rng.integers(0, 2**32 - 1)
                run_mpebm(
                    partial_rankings=padded_partial_rankings,
                    # theta_phi_use=theta_phi_use,
                    bm2int=str2int,
                    mp_method=mp_method,
                    save_results=True,
                    data_file= os.path.join(data_dir, data_file),
                    output_dir=OUTPUT_DIR,
                    output_folder=mp_method,
                    n_iter=10000,
                    n_shuffle=2,
                    burn_in=200,
                    thinning=1,
                    true_order_dict=true_order_dict,
                    true_stages = true_stages,
                    skip_heatmap=True,
                    skip_traceplot=True,
                    seed = random_state,
                    mallows_temperature=1,
                    # energy_prior=energy_prior,
                    # energy_influence=ENERGY_INFLUENCE,
                    # use_scaling=False,
                    # percentile=100,
                    # use_percentile=False,
                    )
            
            random_state = rng.integers(0, 2**32 - 1)
            run_mpebm(
                save_results=True,
                data_file= os.path.join(data_dir, data_file),
                output_dir=OUTPUT_DIR,
                output_folder='saebm',
                n_iter=10000,
                n_shuffle=2,
                burn_in=200,
                thinning=1,
                true_order_dict=true_order_dict,
                true_stages = true_stages,
                skip_heatmap=True,
                skip_traceplot=True,
                seed = random_state
            )