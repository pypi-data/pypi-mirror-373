import json
import pandas as pd
import os
import logging
from typing import List, Dict, Optional, Union
import time
import numpy as np
import sys 
import pysubebm.utils as utils

# Import utility functions
from .utils import (extract_fname, cleanup_old_files, convert_np_types)
# Import algorithms
from .mh import metropolis_hastings

def run_subebm(
    data_file: str,
    n_subtypes:int,
    true_order_matrix: Optional[np.ndarray] = None,
    true_subtype_assignments: Optional[np.ndarray] = None, 
    output_dir: Optional[str]=None,
    output_folder: Optional[str] = None,
    n_iter: int = 2000,
    n_shuffle: int = 2,
    n_subtype_shuffle: int=2,
    burn_in: int = 500,
    thinning: int = 1,
    plot_title_detail: Optional[str] = "",
    fname_prefix: Optional[str] = "",
    skip_heatmap: Optional[bool] = True,
    skip_traceplot: Optional[bool] = True,
    # Strength of the prior belief in prior estimate of the mean (μ), set to 1 as default
    prior_n: float = 1.0,
    # Prior degrees of freedom, influencing the certainty of prior estimate of the variance (σ²), set to 1 as default
    prior_v: float = 1.0,
    seed: int = 123,
    save_results:bool=True,
    theta_phi_matrix: np.ndarray=None,
    obtain_results:bool=True, # if not, just return the max_ll and the empty results
    with_labels:bool=True, # whether assuming knowelege of the true label or not
) -> Dict[str, Union[str, int, float, Dict, List]]:
    """
    Run the metropolis hastings algorithm and save results 

    Args:
        algorithm (str): Choose from 'hard_kmeans', 'mle', 'em', 'kde', and 'conjugate_priors' (default).
        data_file (str): Path to the input CSV file with biomarker data.
        output_dir (str): Path to the directory to store all the results.
        output_folder (str): Optional. If not provided, all results will be saved to output_dir/algorithm. 
            If provided, results will be saved to output_dir/output_folder
        n_iter (int): Number of iterations for the Metropolis-Hastings algorithm.
        n_shuffle (int): Number of shuffles per iteration.
        burn_in (int): Burn-in period for the MCMC chain.
        thinning (int): Thinning interval for the MCMC chain.
        true_order_dict (Optional[Dict[str, int]]): biomarker name: the correct order of it (if known)
        true_stages (Optional[List[int]]): true stages for all participants (if known)
        plot_title_detail (Optional[str]): optional string to add to plot title, as suffix.
        fname_prefix (Optional[str]): the prefix of heatmap, traceplot, results.json, and logs file, e.g., 5_50_0_heatmap_conjugate_priors.png
            In the example, there are no prefix strings. 
        skip_heatmap (Optional[bool]): whether to save heatmaps. True you want to skip saving heatmaps and save space.
        skip_traceplot (Optional[bool]): whether to save traceplots. True if you want to skip saving traceplots and save space.
        prior_n (strength of belief in prior of mean): default to be 1.0
        prior_v (prior degree of freedom) are the weakly informative priors, default to be 1.0
        bw_method (str): bandwidth selection method in kde
        seed (int): for reproducibility

    Returns:
        Dict[str, Union[str, int, float, Dict, List]]: Results including everything, e.g., Kendall's tau and p-value.
    """
    start_time = time.time()

    # Initialize random number generator
    rng = np.random.default_rng(seed)

    if save_results:
        # Folder to save all outputs
        if output_folder:
            output_dir = os.path.join(output_dir, output_folder)
        else:
            output_dir = os.path.join(output_dir)
    fname = extract_fname(data_file)

    # First do cleanup
    logging.info(f"Starting cleanup ...")
    cleanup_old_files(output_dir, fname)

    if save_results:

        # Then create directories
        os.makedirs(output_dir, exist_ok=True)

        heatmap_folder = os.path.join(output_dir, "heatmaps")
        traceplot_folder = os.path.join(output_dir, "traceplots")
        results_folder = os.path.join(output_dir, "results")
        # logs_folder = os.path.join(output_dir, "records")

        if not skip_heatmap:
            os.makedirs(heatmap_folder, exist_ok=True)
        if not skip_traceplot:
            os.makedirs(traceplot_folder, exist_ok=True)
        os.makedirs(results_folder, exist_ok=True)
        # os.makedirs(logs_folder, exist_ok=True)

    # Finally set up logging (console only, no file)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
    )

    # Log the start of the run
    logging.info(f"Running {fname}")
    logging.getLogger().handlers[0].flush()  # Flush logs immediately

    # Load data
    try:
        data = pd.read_csv(data_file)
    except Exception as e:
        logging.error(f"Error reading data file: {e}")
        raise

    n_participants = len(data)
    diseased_arr = np.array(data['diseased'].astype(int).tolist())

    data.drop(columns=['participant', 'diseased'], inplace=True)
    # sort biomarkeres by name, ascending
    # This is the order appearing in data_matrix
    biomarker_names = np.array(data.columns)
    n_biomarkers = len(biomarker_names)
    n_stages = n_biomarkers + 1 # all stages include 0
    logging.info(f"Number of biomarkers: {n_biomarkers}")
    data_matrix = data.to_numpy()
    non_diseased_ids = np.where(diseased_arr == 0)[0]
    healthy_ratio = len(non_diseased_ids)/n_participants
    diseased_mask = (diseased_arr == 1)

    # Run the Metropolis-Hastings algorithm
    try:
        _, _, best_order_matrix, max_log_likelihood, best_theta_phi, best_stage_post, best_subtype_post = metropolis_hastings( 
            data_matrix=data_matrix, diseased_arr=diseased_arr, n_subtypes=n_subtypes,
            iterations = n_iter, n_shuffle = n_shuffle, n_subtype_shuffle = n_subtype_shuffle, prior_n=prior_n, prior_v=prior_v, rng=rng,
            burn_in=burn_in, with_labels=with_labels
            # theta_phi=theta_phi_matrix
        )
   
    except Exception as e:
        logging.error(f"Error in Metropolis-Hastings algorithm: {e}")
        raise

 
    if obtain_results:

        tau = None 
        subtype_acc = None

        if true_order_matrix is not None and true_subtype_assignments is not None:
            if with_labels:
                stage_post, subtype_post = utils.new_posteriors_with_em(
                    data_matrix=data_matrix,
                    new_order=best_order_matrix, # (n_subtypes, n_disease_stages)
                    best_theta_phi=best_theta_phi, # best_theta_phi (N, 4)
                    rng=rng,
                )
            else:
                stage_post, subtype_post = best_stage_post, best_subtype_post

            # ml_subtype
            ml_subtype = np.argmax(subtype_post, axis=1).astype(int) # shape: (n_participants, n_subtypes)

            marginal_stage_post = np.zeros((n_participants, n_stages), dtype=np.float64)
            for p in range(n_participants):
                for s in range(n_subtypes):
                    # add P(k | p, s) * P(s | p) into participant p’s stage distribution
                    marginal_stage_post[p, :] += stage_post[p, s, :] * subtype_post[p, s]

            # Discrete label (MAP)
            # ml_stage
            ml_stage = np.argmax(marginal_stage_post, axis=1)
            
            tau, subtype_acc, mean_stage_healthy = utils.get_final_metrics(
                true_order_matrix=np.array(true_order_matrix),
                best_order_matrix=best_order_matrix,
                true_subtype_assignments=np.array(true_subtype_assignments),
                ml_subtype=ml_subtype,
                ml_stage=ml_stage,
                diseased_mask=diseased_mask
            )

        end_time = time.time()
        results = {
            "with_labels": int(with_labels),
            "runtime": end_time - start_time,
            'healthy_ratio': healthy_ratio,
            "max_log_likelihood": max_log_likelihood,
            "kendalls_tau": tau,
            'subtype_acc': subtype_acc,
            'n_subtypes': n_subtypes,
            'mean_stage_healthy': mean_stage_healthy
        }
        if save_results:
            # Save results
            try:
                with open(f"{results_folder}/{fname_prefix}{fname}_results.json", "w") as f:
                    json.dump(convert_np_types(results), f, indent=4)
            except Exception as e:
                logging.error(f"Error writing results to file: {e}")
                raise
            logging.info(f"Results saved to {results_folder}/{fname_prefix}{fname}_results.json")
    else:
        results = None    

    return results 