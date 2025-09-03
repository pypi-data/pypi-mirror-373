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
        # theta_phi_matrix = params_matrix,
    )
    # results = run_ebm(
    #     algorithm='conjugate_priors',
    #     data_file= os.path.join(data_dir, data_file),
    #     output_dir=OUTPUT_DIR,
    #     n_iter=8000,
    #     n_shuffle=2,
    #     burn_in=100,
    #     thinning=1,
    #     seed = random_state,
    #     save_results=True,
    #     save_details=False,
    # )
    # ml_n = 0
    # max_ll = float('-inf')
    # ll_list = np.zeros(5, dtype=np.float64)
    # for n_s in range(1, 6):
    #     ll = run_subebm(
    #         data_file= os.path.join(data_dir, data_file),
    #         n_subtypes=n_s,
    #         true_order_matrix=true_order_matrix,
    #         true_subtype_assignments=true_subtype_assignments,
    #         output_dir=OUTPUT_DIR,
    #         n_iter=4000,
    #         n_shuffle=2,
    #         n_subtype_shuffle=2,
    #         burn_in=100,
    #         thinning=1,
    #         seed = random_state,
    #         save_results=False,
    #         # theta_phi_matrix = params_matrix,
    #     )
    #     ll_list[n_s - 1] = ll
    #     # if ll > max_ll:
    #     #     max_ll = ll 
    #     #     ml_n = n_s 
    # ml_n = np.argmax(ll_list) + 1
    # res = {
    #     'fname': fname, 
    #     'n_subtypes': n_subtypes,
    #     'll_list': list(ll_list),
    #     'ml_n': int(ml_n), 
    #     'correct': int(n_subtypes == ml_n),
    #     'absolute_error': abs(n_subtypes - ml_n)
    # }
    # with open(f"{OUTPUT_DIR}/{fname}_results.json", "w") as f:
    #     json.dump(convert_np_types(res), f, indent=4)
        