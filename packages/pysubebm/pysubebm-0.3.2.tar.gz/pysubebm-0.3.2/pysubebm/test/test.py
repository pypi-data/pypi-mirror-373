from pysubebm import run_subebm, get_params_path
from pysaebm import run_ebm
# Import utility functions
from pysubebm.utils import (extract_fname, cleanup_old_files, convert_np_types)

import os
import json 
import numpy as np 

cwd = os.getcwd()
print("Current Working Directory:", cwd)
data_dir = f"{cwd}/pysubebm/test/my_data"
data_files = os.listdir(data_dir) 

OUTPUT_DIR = 'algo_results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(f"{cwd}/pysubebm/test/true_order_and_stages.json", "r") as f:
    true_order_and_stages = json.load(f)

rng = np.random.default_rng(42)

# params_file = get_params_path()

# with open(params_file) as f:
#     params = json.load(f)

# params_matrix = np.zeros((len(params), 4))
# biomarker_names = sorted(params.keys())
# for i, bm in enumerate(biomarker_names):
#     bm_data = params[bm]
#     params_matrix[i, :] = bm_data['theta_mean'], bm_data['theta_std'], bm_data['phi_mean'], bm_data['phi_std']

for data_file in data_files:
    random_state = rng.integers(0, 2**32 - 1)
    fname = data_file.replace('.csv', '')
    metadata = true_order_and_stages[fname]
    n_subtypes = metadata['N_SUB']
    true_order_matrix = metadata['TRUE_ORDERINGS']
    true_subtype_assignments = metadata['TRUE_SUBTYPE_ASSIGNMENTS']

    run_subebm(
        data_file= os.path.join(data_dir, data_file),
        n_subtypes=n_subtypes,
        true_order_matrix=true_order_matrix,
        true_subtype_assignments=true_subtype_assignments,
        output_dir=OUTPUT_DIR,
        n_iter=500,
        n_shuffle=2,
        n_subtype_shuffle=2,
        burn_in=20,
        thinning=1,
        seed = random_state,
        save_results=True,
        with_labels=True,
    )
    