import sys
import os
import math
import json
import warnings
from pathlib import Path
from functools import partialmethod
from typing import Dict, List, Optional, Tuple
from scipy.stats import kendalltau

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')  # Configure matplotlib to use non-interactive backend
import matplotlib.pyplot as plt

from tqdm import tqdm
from sklearn.metrics import (
    cohen_kappa_score,
    mean_absolute_error,
    mean_squared_error,
    f1_score,
    roc_auc_score,
    accuracy_score,
)

from pySuStaIn.MixtureSustain import MixtureSustain
from kde_ebm.mixture_model import fit_all_gmm_models

# Disable all progress bars and warnings
tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
os.environ["PROGRESS_BAR"] = "0"
warnings.filterwarnings("ignore")

def extract_info(data_file: str) -> Tuple[np.ndarray, np.ndarray, List[str], Dict[int, int]]:
    """
    Load and reshape SuStaIn input data.

    Args:
        data_file: Path to the CSV file containing SuStaIn input data.

    Returns:
        - data: biomarker matrix [n_subjects, n_biomarkers]
        - target: binary disease status [n_subjects]
        - biomarker_labels: list of biomarker names
        - pid_kj_dict: mapping from participant ID to disease stage (k_j)
    """
    df = pd.read_csv(data_file)
    pid_kj_dict = dict(zip(df.participant, df.k_j))
    df.drop(['k_j', 'S_n', 'affected_or_not'], axis=1, inplace=True)
    diseased_dict = dict(zip(df.participant, df.diseased))

    dff = df.pivot(index='participant', columns='biomarker', values='measurement')
    dff = dff.sort_index(axis=1, level=1, sort_remaining=False)
    dff.columns.name = None
    dff.reset_index(inplace=True)
    dff['Diseased'] = [int(diseased_dict[x]) for x in dff.participant]
    dff.drop(columns=['participant'], inplace=True)

    biomarker_labels = list(dff.columns)[:-1]
    data_matrix = dff.to_numpy()
    data = data_matrix[:, :-1]
    target = data_matrix[:, -1].astype(int)

    return data, target, biomarker_labels, pid_kj_dict

def best_kendall_tau_pairing(
    samples_f: np.ndarray,
    samples_sequence: np.ndarray,
    true_order: Dict[str, int],
    biomarker_labels: List[str]
) -> Tuple[float, float, bool]:
    """
    Compute Kendall's tau between SuStaIn subtype orderings and ground truth.

    Returns:
        tau1, tau2: Kendall's tau for the best-matching subtype pairing
        swapped: whether subtype labels had to be flipped to match better
    """
    

    idx_0 = np.argmax(samples_f[0])
    idx_1 = np.argmax(samples_f[1])
    seq_0 = samples_sequence[0, :, idx_0]
    seq_1 = samples_sequence[1, :, idx_1]

    ordering_0 = {biomarker_labels[int(i)]: rank + 1 for rank, i in enumerate(seq_0)}
    ordering_1 = {biomarker_labels[int(i)]: rank + 1 for rank, i in enumerate(seq_1)}

    guessed_order1 = [ordering_0[k] for k in sorted(true_order.keys())]
    guessed_order2 = [ordering_1[k] for k in sorted(true_order.keys())]
    real_order = [true_order[k] for k in sorted(true_order.keys())]

    tau1, _ = kendalltau(real_order, guessed_order1)
    tau2, _ = kendalltau(real_order, guessed_order2)
    tau3, _ = kendalltau(real_order, guessed_order2)
    tau4, _ = kendalltau(real_order, guessed_order1)

    direct_match = tau1 + tau2
    swapped_match = tau3 + tau4

    return (tau3, tau4, True) if swapped_match > direct_match else (tau1, tau2, False)

def convert_np_types(obj):
    """Convert numpy types in a nested dictionary to Python standard types."""
    if isinstance(obj, dict):
        return {k: convert_np_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return convert_np_types(obj.tolist())
    else:
        return obj

def save_json(outfname: str, data: Dict):
    """Save a dictionary to a JSON file"""
    with open(outfname, 'w') as f:
        json.dump(data, f, indent=4, default = convert_np_types)

def print_metrics(result: Dict):
    """Print key metrics from the results dictionary"""
    print(f"Kendall's Tau: {result['kendalls_tau']:.3f},"
          f" Subtype Kappa: {result['subtype_kappa']:.3f},"
          f" QWK: {result['quadratic_weighted_kappa']:.3f},"
          f" MAE: {result['mean_absolute_error']:.2f}")

def flip_from_middle(arr: np.ndarray) -> np.ndarray:
    mid = len(arr) // 2
    return np.concatenate([arr[mid:], arr[:mid]])


def eval_pysustain(
    data_file: Path,
    output_dir: str,
    tau: int,
    true_orders: Dict[str, Dict]
) -> Tuple[int, float, float]:
    """
    Run SuStaIn on provided data and evaluate subtype/stage prediction.

    Args:
        data_file: path to CSV data file
        output_dir: directory to save results
        tau: tau key for selecting true order
        true_orders: dictionary of true subtype orderings

    Returns:
        (tau, subtype_kappa, mean_absolute_error)
    """
    true_order = true_orders[str(tau)]['order']

    data, target, biomarker_labels, pid_kj_dict = extract_info(str(data_file))
    dataset_name = os.path.splitext(os.path.basename(data_file))[0] 
    mixtures = fit_all_gmm_models(data, target)

    L_yes = np.zeros(data.shape)
    L_no = np.zeros(data.shape)
    for i in range(data.shape[1]):
        L_no[:, i], L_yes[:, i] = mixtures[i].pdf(None, data[:, i])

    sustain_model = MixtureSustain(
        L_yes,
        L_no,
        biomarker_labels,
        N_startpoints=25,
        N_S_max=2,
        N_iterations_MCMC=int(1e4),
        output_folder=output_dir,
        dataset_name=dataset_name,
        use_parallel_startpoints=False
    )

    (samples_sequence, samples_f, ml_subtype, prob_ml_subtype,
     ml_stage, prob_ml_stage, prob_subtype_stage) = sustain_model.run_sustain_algorithm(plot=False)

    tau1, tau2, swapped = best_kendall_tau_pairing(samples_f, samples_sequence, true_order, biomarker_labels)

    ml_subtypes = np.asarray(ml_subtype).flatten()
    ml_stages = np.asarray(ml_stage).flatten()

    half_data_size = data.shape[0] // 2
    true_subtypes = np.concatenate([np.zeros(half_data_size), np.ones(half_data_size)])
    true_stages = np.array(list((pid_kj_dict.values())))

    if swapped:
        true_subtypes = 1 - true_subtypes
        true_stages = flip_from_middle(true_stages)

    f1 = f1_score(true_subtypes, ml_subtypes)
    subtype_kappa = cohen_kappa_score(true_subtypes, ml_subtypes)
    qwk = cohen_kappa_score(true_stages, ml_stages, weights='quadratic')
    mae = mean_absolute_error(true_stages, ml_stages)
    mse = mean_squared_error(true_stages, ml_stages)
    rmse = math.sqrt(mse)

    result_dict = {
        'dataset_name': dataset_name,
        'kendalls_tau': tau1 + tau2,
        'subtype_f1': f1,
        'subtype_kappa': subtype_kappa,
        'quadratic_weighted_kappa': qwk,
        'mean_absolute_error': mae,
        'mean_squared_error': mse,
        'root_mean_squared_error': rmse,
        'true_stages': true_stages,
        'true_subtypes': true_subtypes
    }

    results_dir = os.path.join(output_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    output_path = os.path.join(results_dir, f'{dataset_name}_results.json')
    save_json(output_path, result_dict)
    print(f"Results saved to {output_path}")
    print_metrics(result_dict)

    return (tau, subtype_kappa, mae)