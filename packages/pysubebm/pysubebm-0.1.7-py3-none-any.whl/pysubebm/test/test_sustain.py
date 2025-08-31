import pandas as pd 
import numpy as np 
import os 
import json 
import pickle
# Import pySuStaIn modules
from pySuStaIn.MixtureSustain import MixtureSustain
from kde_ebm.mixture_model import fit_all_gmm_models, fit_all_kde_models
from scipy.optimize import linear_sum_assignment
import time
import pysubebm.utils as utils
import numpy as np
from sklearn.metrics import cohen_kappa_score, adjusted_rand_score

from functools import partialmethod
import tqdm 
import warnings

tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
os.environ["PROGRESS_BAR"] = "0"
warnings.filterwarnings("ignore")

start_time = time.time()

sustainType = 'mixture_GMM'  # or 'mixture_KDE', 'mixture_GMM'

cwd = os.getcwd()
print("Current Working Directory:", cwd)
data_dir = f"{cwd}/pysubebm/test/my_data"
data_files = os.listdir(data_dir) 

OUTPUT_DIR = 'sustain_results'
RESULTS_DIR = os.path.join(OUTPUT_DIR, 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

with open(f"{cwd}/pysubebm/test/true_order_and_stages.json", "r") as f:
    true_order_and_stages = json.load(f)

rng = np.random.default_rng(42)
true_order_matrix = None 
true_subtype_assignments = None 

for data_file in data_files[:3]:
    random_state = rng.integers(0, 2**32 - 1)
    fname = data_file.replace('.csv', '')
    metadata = true_order_and_stages[fname]
    n_subtypes = metadata['N_SUB']
    true_order_matrix = metadata['TRUE_ORDERINGS']
    true_subtype_assignments = metadata['TRUE_SUBTYPE_ASSIGNMENTS']

    # read file
    df = pd.read_csv(os.path.join(data_dir, data_file))
    df.drop(columns=['participant'], inplace=True)

    # extract data 
    biomarker_labels = list(df.columns)[:-1]
    data_matrix = df.to_numpy()
    data = data_matrix[:, :-1].astype(np.float64)
    target = data_matrix[:, -1].astype(np.int64)
    diseased_mask = (target == 1)

    # prepare for sustain analysis 
    if sustainType == "mixture_GMM":
        mixtures = fit_all_gmm_models(data, target)
    elif sustainType == "mixture_KDE":
        mixtures = fit_all_kde_models(data, target)

    # Extract likelihoods for each biomarker
    L_yes = np.zeros(data.shape)
    L_no = np.zeros(data.shape)
    for i in range(data.shape[1]):
        if sustainType == "mixture_GMM":
            L_no[:, i], L_yes[:, i] = mixtures[i].pdf(None, data[:, i])
        elif sustainType == "mixture_KDE":
            L_no[:, i], L_yes[:, i] = mixtures[i].pdf(data[:, i].reshape(-1, 1))

    # parameter setting 
    N_startpoints = 25  # Number of starting points for optimization
    N_S_max = n_subtypes  # Maximum number of subtypes (since you mentioned 2 orderings)
    N_iterations_MCMC = 20000  # Number of MCMC iterations
    dataset_name = fname
    use_parallel_startpoints = False

    sustain_model = MixtureSustain(
        L_yes, 
        L_no, 
        biomarker_labels,  # biomarker labels
        N_startpoints, 
        N_S_max, 
        N_iterations_MCMC, 
        OUTPUT_DIR, 
        dataset_name, 
        use_parallel_startpoints
    )

    samples_sequence, _, ml_subtype, _, ml_stage, _, _ = sustain_model.run_sustain_algorithm(plot=False)

    subtype_assignment_accuracy = None 
    tau = None 

    if true_order_matrix is not None:
        mapping = None 
        best_order_matrix = samples_sequence[:, :, 0]
        n = len(best_order_matrix)
        dist = np.zeros((n, n))

        # i can safely use the sequence results because they are the indices of the fixed input biomarker array!
        for i in range(n):
            for j in range(n):
                dist[i,j]= utils.normalized_kendalls_tau_distance(best_order_matrix[i], np.array(true_order_matrix[j]))
                # tau, _ = kendalltau(best_order_matrix[i], true_order_matrix[j])
                # # normalized kendall's tau distance
                # dist[i, j] = (1 - tau)/2  # smaller dist = better match

        # This finds the best matching: estimated_indices[i] -> true_indices[i]
        estimated_indices, true_indices = linear_sum_assignment(dist)

        # Calculate the matched Kendall's Tau
        tau = dist[estimated_indices, true_indices].mean()

        mapping = dict(zip(estimated_indices, true_indices))

    ml_subtypes = ml_subtype.flatten()[diseased_mask]

    if true_subtype_assignments is not None and mapping is not None:
        true_subtype_assignments = np.array(true_subtype_assignments)[diseased_mask]
        subtype_assignment_accuracy = adjusted_rand_score(true_subtype_assignments, ml_subtypes)
    
    end_time = time.time()

    result = {
        "runtime": end_time - start_time,
        'tau': float(tau),
        'subtype_acc': float(subtype_assignment_accuracy)
    }

    with open(f"{OUTPUT_DIR}/results/{fname}_results.json", "w") as f:
        json.dump(result, f, indent=4)