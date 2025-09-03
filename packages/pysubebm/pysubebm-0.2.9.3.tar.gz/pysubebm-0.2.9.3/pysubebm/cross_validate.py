import pandas as pd
import logging
from typing import List, Dict, Optional, Union, Tuple
import numpy as np
import pysubebm.utils as utils
from sklearn.model_selection import StratifiedKFold
from tqdm.auto import tqdm # 1. Import tqdm# Import algorithms
from .mh import metropolis_hastings

# The input is the data, output is the optimal number of subtypes
# basic idea: for each n_subtype (1-5), split the data into N_FOLDS (5-10 is appropriate)
# for each fold, split the fold-data into train, test. for train, run `run_subebm` and get 
# best_order, best_theta_phi, best_stage_prior, and best_subtype_prior, and run `compute_likelihood_and_posteriors` to get the loglike
# get all the N_FOLD loglikes. that's the data for that specific n_subtype 
# those are out-of-sample log-likelihoods
# then decide on optimal_n_subtype 

def cross_validatation(
    data_file: str,
    iterations:int, 
    n_shuffle:int, 
    n_subtype_shuffle:int,
    burn_in:int,
    prior_n:int,
    prior_v:int,
    max_n_subtypes:int,
    N_FOLDS:int, # 5-10
    seed:int=53,
) -> Tuple[np.ndarray, int]:
    rng = np.random.default_rng(seed)
    # Load data
    try:
        data = pd.read_csv(data_file)
    except Exception as e:
        logging.error(f"Error reading data file: {e}")
        raise
    diseased_arr = np.array(data['diseased'].astype(int).tolist())
    data.drop(columns=['participant', 'diseased'], inplace=True)
    data_matrix_all = data.to_numpy()
    n_biomarkers = data_matrix_all.shape[1]
    disease_stages = np.arange(start=0, stop=n_biomarkers, step=1)
    logging.info(f"Number of biomarkers: {n_biomarkers}")
    cvic_scores = np.zeros(max_n_subtypes)
    # for n_subtypes in range(1, max_n_subtypes + 1):
    for n_subtypes in tqdm(range(1, max_n_subtypes + 1), desc="Validating n_subtypes"):
        logging.info(f"--- Cross-validating for {n_subtypes} subtype(s) ---")
        fold_log_likelihoods = []
        random_state = rng.integers(0, 2**32 - 1)
        # Use StratifiedKFold to maintain the proportion of diseased/healthy in each fold
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=random_state)
        # n-th fold, (array of row ids for the train of this fold, array of row ids for the test for this fold)
        for fold, (train_idx, test_idx) in enumerate(skf.split(data_matrix_all, diseased_arr)):
            logging.info(f"  Running Fold {fold + 1}/{N_FOLDS}...")
            # --- Train the model on the training data ---
            _,_, best_order, _, best_theta_phi, best_stage_prior, best_subtype_prior = metropolis_hastings(
                data_matrix=data_matrix_all[train_idx, :],
                n_subtypes=n_subtypes,
                diseased_arr=diseased_arr[train_idx],
                iterations=iterations,
                n_shuffle=n_shuffle,
                n_subtype_shuffle=n_subtype_shuffle,
                prior_n=prior_n,
                prior_v=prior_v,
                burn_in=burn_in,
                rng=rng
            )
            # --- Evaluate the trained model on the held-out test data ---
            n_test_participants = len(test_idx)
            non_diseased_mask_test = (diseased_arr[test_idx] == 0)

            # Correctly initialize arrays with dimensions of the TEST set
            test_log_likes = np.zeros((n_test_participants, n_subtypes)) 
            test_stage_post = np.zeros((n_test_participants, n_subtypes, n_biomarkers)) 
            data_ln_likelihood, _, _, _ = utils.compute_likelihood_and_posteriors(
                data_matrix=data_matrix_all[test_idx, :],
                non_diseased_mask=non_diseased_mask_test,
                disease_stages=disease_stages,
                new_order=best_order,
                subtypes_to_update=np.arange(n_subtypes),
                log_likes_subtypes=test_log_likes,
                stage_post=test_stage_post,
                current_theta_phi=best_theta_phi,
                current_stage_prior=best_stage_prior,
                current_subtype_prior=best_subtype_prior
            )
            fold_log_likelihoods.append(data_ln_likelihood)
        
        # The CVIC is -2 * the total log-likelihood across all folds
        # We use the sum here, as it's equivalent to the average for comparison
        cvic_scores[n_subtypes - 1] = -2 * np.sum(fold_log_likelihoods)

    optimal_n = utils.choose_optimal_subtypes(cvic_scores)
    logging.info(f"CVIC Scores: {cvic_scores}")
    logging.info(f"Optimal number of subtypes found: {optimal_n}")
    
    return cvic_scores, optimal_n

