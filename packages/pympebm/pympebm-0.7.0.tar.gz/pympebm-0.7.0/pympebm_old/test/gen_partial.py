from pympebm import generate, get_params_path
import json 
import re 

def extract_components(filename):
    pattern = r'^j(\d+)_r([\d.]+)_E(.*?)_m(\d+)$'
    match = re.match(pattern, filename)
    if match:
        return match.groups()  # returns tuple (J, R, E, M)
    return None

if __name__ == '__main__':

    # Get path to default parameters
    params_file = get_params_path()

    with open(params_file) as f:
        params = json.load(f)

    with open('true_order_and_stages.json', 'r') as f:
        true_order_and_stages = json.load(f)
    
    for fname, fname_data in true_order_and_stages.items():
        J, R, E, M = extract_components(fname)
        ordering_array = fname_data['ordering_array']
        for i, partial_ordering in enumerate(ordering_array):
            # obtain the new partial params
            partial_params = {}
            for bm in partial_ordering:
                partial_params[bm] = params[bm]
            
            generate(
                mixed_pathology=False,
                experiment_name = E,
                params=partial_params,
                js = [int(J)],
                rs = [float(R)],
                num_of_datasets_per_combination=1,
                output_dir=f'data{i}',
                seed=53,
                keep_all_cols = False,
                fixed_biomarker_order=True,
                prefix=f"m{M}",
                suffix=f"PO{i}"
            )