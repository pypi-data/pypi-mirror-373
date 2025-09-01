from pympebm import run_ebm
import os
import json 
import re 
import pandas as pd 
import logging 
from pympebm.algorithms import metropolis_hastings

cwd = os.getcwd()
print("Current Working Directory:", cwd)
data_dir = f"{cwd}/pympebm/test/my_data"
data_files = os.listdir(data_dir) 

OUTPUT_DIR = 'algo_results'

with open(f"{cwd}/pympebm/test/true_order_and_stages.json", "r") as f:
    true_order_and_stages = json.load(f)

def extract_components(filename):
    pattern = r'^j(\d+)_r([\d.]+)_E(.*?)_m(\d+)$'
    match = re.match(pattern, filename)
    if match:
        return match.groups()  # returns tuple (J, R, E, M)
    return None

# for algorithm in ['hard_kmeans', 'mle', 'conjugate_priors', 'em', 'kde']:
for algorithm in ['conjugate_priors']:
    for data_file in data_files:
        fname = data_file.replace('.csv', '')
        ordering_array = []
        # to get ordering array
        for i in range(2):
            J, R, E, M = extract_components(fname)
            # partial ordering data file
            po_data_file = os.path.join(f"{cwd}/pympebm/test/data{i}", f"m{M}_j{J}_r{R}_E{E}_m0_PO{i}.csv")
            # Load data
            try:
                data = pd.read_csv(po_data_file)
            except Exception as e:
                logging.error(f"Error reading data file: {e}")
                raise
            # Run the Metropolis-Hastings algorithm
            try:
                accepted_order_dicts, log_likelihoods, _, _, _ = metropolis_hastings(
                    data_we_have = data, iterations=200, algorithm=algorithm, mp_method = 'BT', seed=42)
            except Exception as e:
                logging.error(f"Error in Metropolis-Hastings algorithm: {e}")
                raise

            # Get the order associated with the highet log likelihoods
            order_with_highest_ll = accepted_order_dicts[log_likelihoods.index(max(log_likelihoods))]
            # Sort by value
            # sorted here will be a list of tuples
            partial_ordering = [k for k, v in sorted(order_with_highest_ll.items(), key=lambda item: item[1])]
            ordering_array.append(partial_ordering)
            print(f"{i} is done!")
        
        print(ordering_array)
        true_order_dict = true_order_and_stages[fname]['true_order']
        true_stages = true_order_and_stages[fname]['true_stages']
        results = run_ebm(
            order_array=ordering_array,
            data_file= os.path.join(data_dir, data_file),
            algorithm=algorithm,
            output_dir=OUTPUT_DIR,
            n_iter=200,
            n_shuffle=2,
            burn_in=10,
            thinning=1,
            true_order_dict=true_order_dict,
            true_stages = true_stages,
            skip_heatmap=False,
            skip_traceplot=False,
            mp_method='BT',
            seed = 53
        )