"""
data_matrix:

   bm1, bm2, bm3, ...
p1
p2
p3
.

theta_phi:
    theta_mean, theta_std, phi_mean, phi_std
bm1
bm2
bm3
.

stage_post:

    stage1, stage2, stage3, ..., stageN
p1
p2
p3
.

"""


from typing import Tuple
import numpy as np
from numba import njit
from sklearn.cluster import KMeans
from scipy.stats import mode
import re 
import os 
import logging 
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import adjusted_rand_score

eps = 1e-12

@njit(fastmath=False, parallel=False)
def normalized_kendalls_tau_distance(r1:np.ndarray, r2:np.ndarray) -> float:
    """ 
    Args:
        r1, r2: array of indices of the same set of items. 
    """
    n = len(r1)
    concordant = 0
    discordant = 0 
    for p in range(n-1):
        for q in range(p+1, n):
            concordant += ((r1[p] - r1[q]) * (r2[p] - r2[q]) > 0)
            discordant += ((r1[p] - r1[q]) * (r2[p] - r2[q]) < 0)
    # discrodant/(concordant + discrodant) is the normalized kendall's tau distance
    total = concordant + discordant
    return discordant / total if total > 0 else 0.0

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

def dirichlet_multinomial(
        subtype_assignment_prior:int,
        total_participant:int, 
        n_subtypes:int, 
        rng:np.random.Generator
) -> np.ndarray:
    alpha = np.ones(n_subtypes) * subtype_assignment_prior

    if n_subtypes > total_participant:
        print(f"Error: Cannot assign at least one item to {n_subtypes} subtypes with only {total_participant} participants.")
    else:
        # Step 2: Assign one participant to each subtype
        base_counts = np.ones(n_subtypes, dtype=int)  # Each subtype gets 1 participant
        remaining_items = total_participant - n_subtypes  # Items left to distribute

        # Step 3: Sample probabilities from Dirichlet distribution
        p = rng.dirichlet(alpha)

        # Step 4: Sample counts for remaining items from Multinomial distribution
        additional_counts = rng.multinomial(remaining_items, p)

        # Step 5: Combine base counts and additional counts
        final_counts = base_counts + additional_counts

        return final_counts

@njit
def split_integer(total: int, n: int) -> np.ndarray:
    base = total // n
    remainder = total % n

    result = np.full(n, base, dtype=np.int64)  # start with all base values
    for i in range(remainder):                 # distribute leftovers
        result[i] += 1
    return result

@njit 
def kendalls_w(rank_matrix: np.ndarray):
    """
    Compute Kendall's W (coefficient of concordance) for complete rankings without ties.

    Parameters
    ----------
    rank_matrix : ndarray of shape (n_raters, n_items)
        Each row is a rater's ranking of the the same items (in the same order)
        All rankings must be complete permutations of 0..n_items-1.

    Returns
    -------
    W : float
        Kendall's coefficient of concordance (0 to 1).
    """
    n_raters, n_items = rank_matrix.shape
    
    # Sum of ranks for each item
    R = np.sum(rank_matrix, axis=0)
    
    # Mean rank sum
    R_bar = np.mean(R)
    
    # Sum of squared deviations
    SS = np.sum((R - R_bar)**2)
    
    # Kendall's W formula (no ties)
    W = 12 * SS / (n_raters**2 * (n_items**3 - n_items))
    return W

def get_two_clusters_with_kmeans(
    bm_measurements: np.ndarray,
    diseased_ids:np.ndarray,
    non_diseased_ids:np.ndarray,
    rng:np.random.Generator,
    max_attempt: int = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
    """get affected and nonaffected clusters for a biomarker using seeded k-means (semi-supervised KMeans)
    input: 
        - bm_measurements: measurements of all participants for a specific biomarker
        - diseased_arr: an array of 0/1 indicating whether a participant is diseased or not; length is n_participants
        - non_diseased_ids
    output: 
        - A Tuple: two arrays containing the measurements of each cluster (affected, and nonaffected)
        # Note that it is guaranteed that both clusters have at least 2 elements; otherwise, the program will stop. 
    """
    assert len(bm_measurements) == len(diseased_ids) + len(non_diseased_ids), "Biomarker measurements should be of the same length as diseased array"
    # rng = rng.default_rng(seed)
    # rng.seed(seed)

    n_clusters = 2
    measurements = bm_measurements.reshape(-1, 1)

    # Initialize centroids
    healthy_seed = np.mean(measurements[non_diseased_ids])
    diseased_seed = np.mean(measurements[diseased_ids])
    init_centers = np.array([[healthy_seed], [diseased_seed]])

    curr_attempt = 0
    clustering_setup = KMeans(n_clusters=n_clusters, init = init_centers, n_init=1, random_state=42)
    
    while curr_attempt < max_attempt:
        clustering_result = clustering_setup.fit(measurements)
        predictions = clustering_result.labels_
        cluster_counts = np.bincount(predictions) # array([3, 2])
        
        # Exit if exactly two clusters and both have two or more elements
        if len(cluster_counts) == n_clusters and all(c > 1 for c in cluster_counts):
            break 
        curr_attempt += 1
    else:
        print(f"KMeans failed. Will go ahead and randomize the predictions.")
        # Initialize all predictions to -1 (or any placeholder value)
        predictions = np.full(len(measurements), -1)

        # Set all healthy participants to 0
        predictions[non_diseased_ids] = 0

        # Keep trying until both clusters have at least 2 members
        for _ in range(max_attempt):  # try up to 100 times
            # Randomly assign 0 or 1 to non-healthy participants
            predictions[diseased_ids] = rng.choice([0, 1], size=len(diseased_ids))
            cluster_counts = np.bincount(predictions)

            # Check if two non-empty clusters exist:
            if len(cluster_counts) == n_clusters and all(c > 1 for c in cluster_counts):
                break
        else:
            raise ValueError(f"KMeans clustering failed to find valid clusters within max_attempt.")
    
    # labels for healthy participants
    healthy_predictions = predictions[non_diseased_ids]
    # check the label for the majority of healthy participants; that becomes the label for phi cluster
    mode_result = mode(healthy_predictions, keepdims=False).mode
    phi_cluster_idx = mode_result[0] if isinstance(mode_result, np.ndarray) else mode_result
    theta_cluster_idx = 1 - phi_cluster_idx

    # Convert predictions to numpy array if not already
    predictions = np.array(predictions).flatten()

    # Select affected and nonaffected measurements based on cluster index
    theta_measurements = measurements[predictions == theta_cluster_idx].flatten()
    phi_measurements = measurements[predictions == phi_cluster_idx].flatten()

    is_theta = (predictions == theta_cluster_idx).astype(np.float64)

    assert len(is_theta) == len(measurements), "is_theta should have the same length as measurements"

    return np.array(theta_measurements), np.array(phi_measurements), np.array(is_theta)


def get_initial_theta_phi_estimates(
    data_matrix: np.ndarray,
    non_diseased_ids: np.ndarray,
    diseased_ids: np.ndarray,
    prior_n: float,
    prior_v: float,
    rng:np.random.Generator,
) -> np.ndarray:
    """
    Obtain initial theta and phi estimates (mean and standard deviation) for each biomarker.
    (get the clusters using seeded k-means (semi-supervised KMeans);
     estimate the parameters using conjugate priors
    )
    """
    # Number of biomarkers
    N = len(data_matrix[0])
    # Each row is a bm; four cols: theta_mean, theta_std, phi_mean, phi_std
    estimates = np.zeros((N, 4))

    # --- THE FIX: Validate that both groups have members ---
    if len(non_diseased_ids) == 0:
        raise ValueError("The 'non_diseased_ids' group is empty. Cannot initialize theta/phi.")
    if len(diseased_ids) == 0:
        raise ValueError("The 'diseased_ids' group is empty. Cannot initialize theta/phi.")
    # --- End of Fix ---

    for bm in range(N):
        bm_measurements = data_matrix[:, bm]
        # Add a check here for NaNs just in case, it's good practice
        if np.any(np.isnan(bm_measurements)):
             raise ValueError(f"NaN value detected in biomarker {bm} before calling KMeans.")
        theta_measurements, phi_measurements, _  = get_two_clusters_with_kmeans(
            bm_measurements = bm_measurements, 
            diseased_ids = diseased_ids, 
            non_diseased_ids = non_diseased_ids,
            rng=rng
        )
        # Use MLE to calculate the fallback (also to provide the m0 and s0_sq)
        fallback_params = np.array(
            [np.mean(theta_measurements),
             np.std(theta_measurements, ddof=1),
             np.mean(phi_measurements),
             np.std(phi_measurements, ddof=1)])
        theta_mean, theta_std, phi_mean, phi_std = compute_theta_phi_biomarker_conjugate_priors(
            theta_measurements, np.ones(len(theta_measurements)), 
            phi_measurements, np.ones(len(phi_measurements)),
            fallback_params, prior_n, prior_v)
        estimates[bm] = np.array([theta_mean, theta_std, phi_mean, phi_std])
    return estimates


@njit
def compute_theta_phi_biomarker_conjugate_priors(
    theta_measurements: np.ndarray,
    theta_weights:np.ndarray,
    phi_measurements: np.ndarray,
    phi_weights: np.ndarray,
    theta_phi_current_biomarker: np.ndarray,  # Current state’s θ/φ
    prior_n: float,
    prior_v: float
) -> Tuple[float, float, float, float]:
    """
    When data follows a normal distribution with unknown mean (μ) and unknown variance (σ²),
    the normal-inverse gamma distribution serves as a conjugate prior for these parameters.
    This means the posterior distribution will also be a normal-inverse gamma distribution after updating with observed data.

    Args:
        theta_measurements: list of biomarker measurements
        theta_weights: theta weights
        phi_measurements: list of biomarker measurements
        phi_weights: phi weights
        theta_phi_current_biomarker: the current state's theta/phi for this biomarker
        prior_n (strength of belief in prior of mean), and prior_v (prior degree of freedom) are the weakly infomred priors.

    Returns:
        Tuple[float, float, float, float]: Mean and standard deviation for affected (theta) and non-affected (phi) clusters.
    """
    # --- Affected Cluster (Theta) ---
    if len(theta_measurements) < 2:  # Fallback if cluster has 0 or 1 data points
        theta_mean = theta_phi_current_biomarker[0]
        theta_std = theta_phi_current_biomarker[1]
    else:
        theta_mean, theta_std = estimate_params_exact(
            m0=theta_phi_current_biomarker[0],
            # m0=np.mean(theta_measurements),
            n0=prior_n,
            # s0_sq = np.var(theta_measurements, ddof=1),
            s0_sq=theta_phi_current_biomarker[1]**2,
            v0=prior_v,
            data=theta_measurements,
            weights=theta_weights,
        )

    # --- Non-Affected Cluster (Phi) ---
    if len(phi_measurements) < 2:  # Fallback if cluster has 0 or 1 data points
        phi_mean = theta_phi_current_biomarker[2]
        phi_std = theta_phi_current_biomarker[3]
    else:
        phi_mean, phi_std = estimate_params_exact(
            m0=theta_phi_current_biomarker[2],
            # m0=np.mean(phi_measurements),
            n0=prior_n,
            # s0_sq = np.var(phi_measurements, ddof=1),
            s0_sq=theta_phi_current_biomarker[3]**2,
            v0=prior_v,
            data=phi_measurements,
            weights=phi_weights,
        )
    return theta_mean, theta_std, phi_mean, phi_std

@njit
def estimate_params_exact(
    m0: float,
    n0: float,
    s0_sq: float,
    v0: float,
    data: np.ndarray,
    weights:np.ndarray=np.array([]), 
    epsilon: float = 1e-6 # Add a small constant for stability
) -> Tuple[float, float]:
    """
    Estimate posterior mean and standard deviation using conjugate priors for a Normal-Inverse Gamma model.

    Args:
        m0 (float): Prior estimate of the mean (μ).
        n0 (float): Strength of the prior belief in m0.
        s0_sq (float): Prior estimate of the variance (σ²).
        v0 (float): Prior degrees of freedom, influencing the certainty of s0_sq.
        data (np.ndarray): Observed data (measurements).
        weights (np.ndarray): The weight for each data point.

    Returns:
        Tuple[float, float]: Posterior mean (μ) and standard deviation (σ).
    """
    if weights is None:
        weights = np.ones(len(data))
    # Data summary
    sum_of_weights = np.sum(weights)
    if sum_of_weights <= eps:
        # Fall back to the prior/current params; avoid division by zero.
        return m0, np.sqrt(max(s0_sq, epsilon))

    sample_mean = np.sum(data * weights) / sum_of_weights

    # calculate weighted sum of sample variance
    sum_weighted_squared_diff = np.sum(weights * (data - sample_mean)**2)

    # Update hyperparameters for the Normal-Inverse Gamma posterior
    updated_m0 = (n0 * m0 + sum_of_weights * sample_mean) / (n0 + sum_of_weights)
    updated_n0 = n0 + sum_of_weights
    updated_v0 = v0 + sum_of_weights
    updated_s0_sq = (1 / updated_v0) * (sum_weighted_squared_diff + v0 * s0_sq +
                                        (n0 * sum_of_weights / updated_n0) * (sample_mean - m0)**2)
    
    # Ensure the variance is never exactly zero
    updated_s0_sq = max(updated_s0_sq, epsilon)

    updated_alpha = updated_v0/2
    updated_beta = updated_v0*updated_s0_sq/2

    # Posterior estimates
    mu_posterior_mean = updated_m0
    # Use the statistically correct mean of the Inverse Gamma distribution
    sigma_squared_posterior_mean = updated_beta / (updated_alpha - 1) if updated_alpha > 1 else updated_beta / updated_alpha
    # sigma_squared_posterior_mean = updated_beta / updated_alpha
    # Ensure the final estimated variance is also not zero
    sigma_squared_posterior_mean = max(sigma_squared_posterior_mean, epsilon)

    mu_estimation = mu_posterior_mean
    std_estimation = np.sqrt(sigma_squared_posterior_mean)

    return mu_estimation, std_estimation


@njit
def update_theta_phi_estimates_with_labels(
    n_participants: int,
    non_diseased_ids: np.ndarray,
    data_matrix: np.ndarray,
    new_order: np.ndarray,
    theta_phi_current: np.ndarray,  # Shape is now (n_biomarkers, 4)
    stage_likelihoods_posteriors: np.ndarray,
    subtype_post: np.ndarray,
    prior_n: float,
    prior_v: float,
) -> np.ndarray:
    """
    Update a SHARED set of theta and phi params for all biomarkers.
    """
    n_subtypes, n_biomarkers = new_order.shape
    disease_stages = np.arange(start=0, stop=n_biomarkers, step=1)
    updated_params = np.zeros((n_biomarkers, 4))

    # Loop over each biomarker to update its shared theta/phi
    for bm_idx in range(n_biomarkers):
        bm_measurements = data_matrix[:, bm_idx]

        # --- Calculate Aggregated Weights ---
        # These are the total probabilities of a participant's measurement for this biomarker
        # belonging to the 'theta' (affected) or 'phi' (unaffected) cluster,
        # summed across all possible subtypes.
        theta_weights = np.zeros(n_participants, dtype=np.float64)
        phi_weights = np.zeros(n_participants, dtype=np.float64)

        # Loop over all subtypes to accumulate the probabilities
        for s in range(n_subtypes):
            # Find the position of the current biomarker in this subtype's sequence
            bm_position_in_sequence = new_order[s, bm_idx]

            # Calculate the joint posterior P(s, k | p) = P(k | p, s) * P(s | p)
            # This tells us the probability of a participant being in a specific stage of a specific subtype
            joint_posterior_sk = stage_likelihoods_posteriors[:, s, :] * subtype_post[:, s, np.newaxis]

            # Find which stages correspond to this biomarker being 'affected' for this subtype
            affected_stages_mask = disease_stages >= bm_position_in_sequence
            unaffected_stages_mask = ~affected_stages_mask

            # Add this subtype's contribution to the total 'affected' and 'unaffected' probabilities
            theta_weights += np.sum(joint_posterior_sk[:, affected_stages_mask], axis=1)
            phi_weights += np.sum(joint_posterior_sk[:, unaffected_stages_mask], axis=1)

        # Non-diseased participants are always in the 'phi' (unaffected) cluster with 100% certainty
        phi_weights[non_diseased_ids] = 1.0
        theta_weights[non_diseased_ids] = 0.0

        # --- new: safeguard against zero-mass clusters ---
        sum_theta = np.sum(theta_weights)
        sum_phi   = np.sum(phi_weights)
        tiny = 1e-12

        if sum_theta <= tiny or sum_phi <= tiny:
            # No information at all: keep current params
            updated_params[bm_idx, :] = theta_phi_current[bm_idx, :]
            continue

        # this is safe because later, the compute_theta_phi_biomarker_conjugate_priors
        # just won't update params if the sum is tiny
        if sum_theta <= tiny:
            # give θ a tiny uniform mass so the updater has something to work with
            theta_weights = np.full(n_participants, tiny / n_participants, dtype=np.float64)
        if sum_phi <= tiny:
            phi_weights = np.full(n_participants, tiny / n_participants, dtype=np.float64)

        # --- Use Weighted Data for Estimation ---
        # We now use the FULL set of measurements for both theta and phi,
        # but with the aggregated soft-assignment weights we just calculated.
        theta_phi_current_biomarker = theta_phi_current[bm_idx, :]
        updated_params[bm_idx, :] = compute_theta_phi_biomarker_conjugate_priors(
            bm_measurements, theta_weights,  # theta_measurements and its weights
            bm_measurements, phi_weights,    # phi_measurements and its weights
            theta_phi_current_biomarker, prior_n, prior_v
        )
    return updated_params


@njit
def update_theta_phi_estimates(
    n_participants: int,
    data_matrix: np.ndarray,
    new_order: np.ndarray,
    theta_phi_current: np.ndarray,  # Shape is now (n_biomarkers, 4)
    stage_likelihoods_posteriors: np.ndarray,
    subtype_post: np.ndarray,
    prior_n: float,
    prior_v: float,
) -> np.ndarray:
    """
    Update a SHARED set of theta and phi params for all biomarkers.
    """
    n_subtypes, n_biomarkers = new_order.shape
    n_stages = n_biomarkers + 1
    disease_stages = np.arange(start=0, stop=n_stages, step=1)
    updated_params = np.zeros((n_biomarkers, 4))

    # Loop over each biomarker to update its shared theta/phi
    for bm_idx in range(n_biomarkers):
        bm_measurements = data_matrix[:, bm_idx]

        # --- Calculate Aggregated Weights ---
        # These are the total probabilities of a participant's measurement for this biomarker
        # belonging to the 'theta' (affected) or 'phi' (unaffected) cluster,
        # summed across all possible subtypes.
        theta_weights = np.zeros(n_participants, dtype=np.float64)
        phi_weights = np.zeros(n_participants, dtype=np.float64)

        # Loop over all subtypes to accumulate the probabilities
        for s in range(n_subtypes):
            # Find the position of the current biomarker in this subtype's sequence
            bm_position_in_sequence = new_order[s, bm_idx]

            # Calculate the joint posterior P(s, k | p) = P(k | p, s) * P(s | p)
            # This tells us the probability of a participant being in a specific stage of a specific subtype
            joint_posterior_sk = stage_likelihoods_posteriors[:, s, :] * subtype_post[:, s, np.newaxis]

            # Find which stages correspond to this biomarker being 'affected' for this subtype
            affected_stages_mask = disease_stages >= bm_position_in_sequence
            unaffected_stages_mask = ~affected_stages_mask

            # Add this subtype's contribution to the total 'affected' and 'unaffected' probabilities
            theta_weights += np.sum(joint_posterior_sk[:, affected_stages_mask], axis=1)
            phi_weights += np.sum(joint_posterior_sk[:, unaffected_stages_mask], axis=1)

        # --- new: safeguard against zero-mass clusters ---
        sum_theta = np.sum(theta_weights)
        sum_phi   = np.sum(phi_weights)
        tiny = 1e-12

        if sum_theta <= tiny or sum_phi <= tiny:
            # No information at all: keep current params
            updated_params[bm_idx, :] = theta_phi_current[bm_idx, :]
            continue

        # this is safe because later, the compute_theta_phi_biomarker_conjugate_priors
        # just won't update params if the sum is tiny
        if sum_theta <= tiny:
            # give θ a tiny uniform mass so the updater has something to work with
            theta_weights = np.full(n_participants, tiny / n_participants, dtype=np.float64)
        if sum_phi <= tiny:
            phi_weights = np.full(n_participants, tiny / n_participants, dtype=np.float64)

        # --- Use Weighted Data for Estimation ---
        # We now use the FULL set of measurements for both theta and phi,
        # but with the aggregated soft-assignment weights we just calculated.
        theta_phi_current_biomarker = theta_phi_current[bm_idx, :]
        updated_params[bm_idx, :] = compute_theta_phi_biomarker_conjugate_priors(
            bm_measurements, theta_weights,  # theta_measurements and its weights
            bm_measurements, phi_weights,    # phi_measurements and its weights
            theta_phi_current_biomarker, prior_n, prior_v
        )
    return updated_params


def new_posteriors_with_em(
    data_matrix:np.ndarray,
    new_order:np.ndarray, # (n_subtypes, n_disease_stages)
    best_theta_phi: np.ndarray, # best_theta_phi (N, 4)
    rng:np.random.Generator,
    max_iter: int = 200,
    tol: float = 1e-6,
):
    """
    EM-calibrates full stage prior π over 0..N, then returns posteriors and MAP stages.
    Uses your compute_unbiased_stage_likelihoods internally. MH is untouched.

    sample inside MH, posterior mean outside MH.
    """
    n_subtypes, n_disease_stages = new_order.shape
    n_stages = n_disease_stages + 1

    subtype_alpha_prior = np.ones(n_subtypes, dtype=np.float64) 
    subtype_prior = rng.dirichlet(subtype_alpha_prior)

    stage_alpha_prior = np.ones((n_subtypes, n_stages), dtype=np.float64)
    stage_prior = np.zeros((n_subtypes, n_stages), dtype=np.float64)
    for i in range(n_subtypes):
        stage_prior[i, :] = rng.dirichlet(stage_alpha_prior[i, :])

    stage_post = None
    for _ in range(max_iter):
        # E-step: posteriors with current π (your existing function)
        stage_post, subtype_post = compute_unbiased_likelihood_and_posteriors(
            data_matrix=data_matrix,
            new_order=new_order, # (n_subtypes, n_disease_stages)
            best_theta_phi=best_theta_phi, # best_theta_phi (N, 4)
            updated_stage_prior=stage_prior, # updated_stage_prior (n_subtypes, n_disease_stages + 1)
            best_subtype_prior=subtype_prior, # (n_subtypes, 1)
        )

        # --- Gibbs update for π using CURRENT posteriors ---
        # 6. UPDATE Priors (π) based on new posteriors
        # Update stage priors for each subtype
        stage_prior_new = np.zeros((n_subtypes, n_stages), dtype=np.float64)
        for s in range(n_subtypes):
            # row sum for each col: sum across participants for each stage
            weighted_stage_counts = np.sum(stage_post[:, s, :] * subtype_post[:, s, np.newaxis], axis=0)
            stage_prior_new[s, :] = rng.dirichlet(stage_alpha_prior[s, :] + weighted_stage_counts)
        
        # row sum for each col: sum across participants for each subtype
        # Update global subtype prior
        subtype_counts = np.sum(subtype_post, axis=0)
        subtype_prior_new = rng.dirichlet(subtype_alpha_prior + subtype_counts)

        # Converged?
        if np.linalg.norm(subtype_prior_new - subtype_prior, ord=1) < tol and np.linalg.norm(stage_prior_new - stage_prior, ord=1) < tol:
            subtype_prior = subtype_prior_new
            stage_prior = stage_prior_new
            break
        subtype_prior = subtype_prior_new
        stage_prior = stage_prior_new
    
    return stage_post, subtype_post 


@njit
def compute_unbiased_likelihood_and_posteriors(
    data_matrix:np.ndarray,
    new_order:np.ndarray, # (n_subtypes, n_disease_stages)
    best_theta_phi: np.ndarray, # best_theta_phi (N, 4)
    updated_stage_prior: np.ndarray, # updated_stage_prior (n_subtypes, n_disease_stages + 1)
    best_subtype_prior:np.ndarray, # (n_subtypes, 1)
) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]: # subtype_ln_likes, stage_post, subtype_post_ln_likes, subtype_post
    """Calculate the total log likelihood across all participants
        and obtain stage_likelihoods_posteriors
    """
    n_participants, n_biomarkers = data_matrix.shape
    n_subtypes = best_subtype_prior.shape[0]
    n_stages = n_biomarkers + 1

    # Store intermediate values
    stage_post = np.zeros((n_participants, n_subtypes, n_stages))
    subtype_post = np.zeros((n_participants, n_subtypes))
    log_likes_subtypes = np.zeros((n_participants, n_subtypes))
    
    for p in range(n_participants):
        # note that s here is also an index
        for s in range(0, n_subtypes):
        # for s in range(n_subtypes):
            measurements = data_matrix[p]
            ln_stage_likelihoods = np.empty(n_stages)
            for k_j in range(n_stages):
                ln_stage_likelihoods[k_j] = compute_ln_likelihood(
                    measurements, new_order[s, :], k_j=k_j, theta_phi=best_theta_phi
                ) + np.log(updated_stage_prior[s, k_j] if updated_stage_prior[s, k_j] > eps else eps)

            # Use log-sum-exp to get the total log-likelihood for this participant given this subtype
            max_ll = np.max(ln_stage_likelihoods)
            exp_shifted = np.exp(ln_stage_likelihoods - max_ll)
            ln_likelihood = max_ll + np.log(np.sum(exp_shifted))

            # Calculate the conditional stage posterior: P(k|p,s)
            stage_post[p, s, :] = exp_shifted / np.sum(exp_shifted)

            # log(L(p|s)), p is row, s is col
            log_likes_subtypes[p, s] = ln_likelihood

    '''
    Data likelihood is the product of all participant data likelihood
    Not the sum of all subtype data likelihood

    data_likelihood = \prod_j=0^J L(j) 

    data_log_likelihood = log( \prod_j=0^J L(j)) 
                        = \sum_j=0^J log(L(j))
                        = \sum_j=0^J log(\sum_s=0^S L(j|s) * prior_s)

    We don't have L(j|s), but only log(L(j|s)), so, we need to express the inner term using logs:

    \sum_s L(j|s) * prior_s = \sum_s exp(log(L(j|s))) * exp(log(prior_s))
                            = \sum_s exp( log(L(j|s))) + log(prior_s))
    
    So, data_log_likelihood = \sum_j=0^J log(\sum_s=0^S exp(log(L(j|s)) + log(prior_s)))

    '''
    # First, get the log of the priors.
    log_subtype_priors = np.log(np.maximum(best_subtype_prior, eps))

    # data log liklihood
    data_ln_likelihood = 0.0

    # update subtype post after log_likes_subtypes is done
    for p in range(n_participants):
        # each participant, across subtypes
        # log(L(j|s)) + log(prior_s)
        log_unnorm_post = log_likes_subtypes[p, :] + log_subtype_priors
        max_log = np.max(log_unnorm_post)
        exp_shifted = np.exp(log_unnorm_post - max_log)
        log_marginal_p = max_log + np.log(np.sum(exp_shifted))
        # sums the individual log-likelihoods
        data_ln_likelihood += log_marginal_p
        # calculates the posterior
        subtype_post[p, :] = exp_shifted / np.sum(exp_shifted)
    return stage_post, subtype_post

@njit
def compute_likelihood_and_posteriors_with_labels(
    data_matrix:np.ndarray,
    non_diseased_mask: np.ndarray,
    new_order:np.ndarray, # (n_subtypes, n_disease_stages)
    subtypes_to_update:np.ndarray, # indices of subtypes that have been shuffled order
    log_likes_subtypes: np.ndarray, # log likelihood of each participant's data under different subtypes
    stage_post:np.ndarray, # need this because only stage post for shuffled subtypes will be updated
    current_theta_phi: np.ndarray, # current_theta_phi (N, 4)
    current_stage_prior: np.ndarray, # current_stage_prior (n_subtypes, n_disease_stages)
    current_subtype_prior:np.ndarray, # (n_subtypes, 1)
) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]: # subtype_ln_likes, stage_post, subtype_post_ln_likes, subtype_post
    """Calculate the total log likelihood across all participants
        and obtain stage_likelihoods_posteriors
    """

    n_participants, n_biomarkers = data_matrix.shape
    n_subtypes = current_subtype_prior.shape[0]
    disease_stages = np.arange(start=0, stop=n_biomarkers, step=1)
    subtype_post = np.zeros((n_participants, n_subtypes))
    
    for p in range(n_participants):
        # note that s itself here is also an index
        for s_idx, s in enumerate(subtypes_to_update):
        # for s in range(n_subtypes):
            measurements = data_matrix[p]
            if non_diseased_mask[p]:
                if s_idx == 0:
                    # for healthy participant, no matter what the new_order[s, :] is, because k_j = -1
                    # all biomarkers are treated as not affected. 
                    # So we only need to calcuate once. 

                    # this also means if we use separate rather than shared theta/phi, then there is a problem? because 
                    # which theta/phi should we use for healthy participants?
                    ln_likelihood = compute_ln_likelihood(
                        measurements, np.zeros(len(measurements), dtype=np.float64), 
                        k_j=-1, theta_phi=current_theta_phi)
            else: # Diseased participant (sum over possible stages)
                ln_stage_likelihoods = np.zeros(len(disease_stages))
                for kj_idx, k_j in enumerate(disease_stages):
                    # Use `kj_idx` to access the prior array, not `k_j`.
                    # `k_j` starts from 1, but array indices start from 0.
                    ln_stage_likelihoods[kj_idx] = compute_ln_likelihood(
                        measurements, new_order[s, :], k_j=k_j, 
                        theta_phi=current_theta_phi
                    ) + np.log(current_stage_prior[s, kj_idx] + eps)

                # Use log-sum-exp to get the total log-likelihood for this participant given this subtype
                max_ll = np.max(ln_stage_likelihoods)
                exp_shifted = np.exp(ln_stage_likelihoods - max_ll)
                ln_likelihood = max_ll + np.log(np.sum(exp_shifted))

                # Calculate the conditional stage posterior: P(k|p,s)
                stage_post[p, s, :] = exp_shifted / np.sum(exp_shifted)

            # log(L(p|s)), p is row, s is col
            log_likes_subtypes[p, s] = ln_likelihood

    '''
    Data likelihood is the product of all participant data likelihood
    Not the sum of all subtype data likelihood

    data_likelihood = \prod_j=0^J L(j) 

    data_log_likelihood = log( \prod_j=0^J L(j)) 
                        = \sum_j=0^J log(L(j))
                        = \sum_j=0^J log(\sum_s=0^S L(j|s) * prior_s)

    We don't have L(j|s), but only log(L(j|s)), so, we need to express the inner term using logs:

    \sum_s L(j|s) * prior_s = \sum_s exp(log(L(j|s))) * exp(log(prior_s))
                            = \sum_s exp( log(L(j|s))) + log(prior_s))
    
    So, data_log_likelihood = \sum_j=0^J log(\sum_s=0^S exp(log(L(j|s)) + log(prior_s)))

    '''
    # First, get the log of the priors.
    # use maximum to avoid 0
    log_subtype_priors = np.log(np.maximum(current_subtype_prior, eps))

    # data log liklihood
    data_ln_likelihood = 0.0

    # update subtype post after log_likes_subtypes is done
    for p in range(n_participants):
        # healthy participants are not in any subtypes 
        if non_diseased_mask[p]:
            # For healthy participants, the likelihood is calculated under the "no-event" model (k_j=0).
            # which means S does not influence the likelihood, as long as theta/phi does not change. 
            # we add only log_likes_subtypes[p, 0]  but not the sum because even for diseased patients,
            # we are adding the weighted mean. So here for healthy patients, the first is also the mean
            # because for each s, the ln like is the same. 
            data_ln_likelihood += log_likes_subtypes[p, 0] 
        else:
            # each participant, across subtypes
            # log(L(j|s)) + log(prior_s)
            log_unnorm_post = log_likes_subtypes[p, :] + log_subtype_priors
            max_log = np.max(log_unnorm_post)
            exp_shifted = np.exp(log_unnorm_post - max_log)
            log_marginal_p = max_log + np.log(np.sum(exp_shifted))
            # sums the individual log-likelihoods
            data_ln_likelihood += log_marginal_p
            # calculates the posterior
            subtype_post[p, :] = exp_shifted / np.sum(exp_shifted)

    return data_ln_likelihood, stage_post, subtype_post, log_likes_subtypes

@njit
def compute_likelihood_and_posteriors(
    data_matrix:np.ndarray,
    new_order:np.ndarray, # (n_subtypes, n_disease_stages)
    subtypes_to_update:np.ndarray, # indices of subtypes that have been shuffled order
    log_likes_subtypes: np.ndarray, # log likelihood of each participant's data under different subtypes
    stage_post:np.ndarray, # need this because only stage post for shuffled subtypes will be updated
    current_theta_phi: np.ndarray, # current_theta_phi (N, 4)
    current_stage_prior: np.ndarray, # current_stage_prior (n_subtypes, n_disease_stages)
    current_subtype_prior:np.ndarray, # (n_subtypes, 1)
) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]: # subtype_ln_likes, stage_post, subtype_post_ln_likes, subtype_post
    """Calculate the total log likelihood across all participants
        and obtain stage_likelihoods_posteriors
    """
    n_participants, n_biomarkers = data_matrix.shape
    n_subtypes = current_subtype_prior.shape[0]
    n_stages = n_biomarkers + 1

    # Store intermediate values
    # stage_post = np.zeros((n_participants, n_subtypes, n_disease_stages))
    subtype_post = np.zeros((n_participants, n_subtypes))
    # log_likes_subtypes = np.zeros((n_participants, n_subtypes))
    
    for p in range(n_participants):
        # note that s itself here is also an index
        for s in subtypes_to_update:
        # for s in range(n_subtypes):
            measurements = data_matrix[p]
            ln_stage_likelihoods = np.zeros(n_stages)
            for k_j in range(n_stages):
                ln_stage_likelihoods[k_j] = compute_ln_likelihood(
                    measurements, new_order[s, :], k_j=k_j, 
                    theta_phi=current_theta_phi
                ) + np.log(current_stage_prior[s, k_j] + eps)

            # Use log-sum-exp to get the total log-likelihood for this participant given this subtype
            max_ll = np.max(ln_stage_likelihoods)
            exp_shifted = np.exp(ln_stage_likelihoods - max_ll)
            ln_likelihood = max_ll + np.log(np.sum(exp_shifted))

            # Calculate the conditional stage posterior: P(k|p,s)
            stage_post[p, s, :] = exp_shifted / np.sum(exp_shifted)

            # log(L(p|s)), p is row, s is col
            log_likes_subtypes[p, s] = ln_likelihood

    '''
    Data likelihood is the product of all participant data likelihood
    Not the sum of all subtype data likelihood

    data_likelihood = \prod_j=0^J L(j) 

    data_log_likelihood = log( \prod_j=0^J L(j)) 
                        = \sum_j=0^J log(L(j))
                        = \sum_j=0^J log(\sum_s=0^S L(j|s) * prior_s)

    We don't have L(j|s), but only log(L(j|s)), so, we need to express the inner term using logs:

    \sum_s L(j|s) * prior_s = \sum_s exp(log(L(j|s))) * exp(log(prior_s))
                            = \sum_s exp( log(L(j|s))) + log(prior_s))
    
    So, data_log_likelihood = \sum_j=0^J log(\sum_s=0^S exp(log(L(j|s)) + log(prior_s)))

    '''
    # First, get the log of the priors.
    # use maximum to avoid 0
    log_subtype_priors = np.log(np.maximum(current_subtype_prior, eps))

    # data log liklihood
    data_ln_likelihood = 0.0

    # update subtype post after log_likes_subtypes is done
    for p in range(n_participants):
        # each participant, across subtypes
        # log(L(j|s)) + log(prior_s)
        log_unnorm_post = log_likes_subtypes[p, :] + log_subtype_priors
        max_log = np.max(log_unnorm_post)
        exp_shifted = np.exp(log_unnorm_post - max_log)
        log_marginal_p = max_log + np.log(np.sum(exp_shifted))
        # sums the individual log-likelihoods
        data_ln_likelihood += log_marginal_p
        # calculates the posterior
        subtype_post[p, :] = exp_shifted / np.sum(exp_shifted)
    return data_ln_likelihood, stage_post, subtype_post, log_likes_subtypes

@ njit
def _compute_ln_likelihood_core(measurements, mus, stds):
    """Core computation function optimized with Numba"""
    ln_likelihood = 0.0
    log_two_pi = np.log(2 * np.pi)
    for i in range(len(measurements)):
        var = stds[i] ** 2
        diff = measurements[i] - mus[i]
        # likelihood *= np.exp(-diff**2 / (2 * var)) / np.sqrt(2 * np.pi * var)
        # Log of normal PDF: ln(1/sqrt(2π*var) * exp(-diff²/2var))
        # = -ln(sqrt(2π*var)) - diff²/2var
        ln_likelihood += (-0.5 * (log_two_pi + np.log(var)) -
                          diff**2 / (2 * var))
    return ln_likelihood

@ njit
def compute_ln_likelihood(
    p_measurements: np.ndarray,
    S_n: np.ndarray,
    k_j: int,
    theta_phi: np.ndarray,
) -> float:
    """
    Compute the log likelihood for given participant data.

    Args:
        p_measurements (np.ndarray): Array of measurement values for a specific participant, from bm1 to bmN
        S_n (np.ndarray): the new_order, i.e., the ordering index from bm1 to bmN
        k_j (int): Current stage.
        theta_phi 
    Returns:
        float: Log likelihood value.
    """
    mus = np.zeros(len(p_measurements))
    stds = np.zeros(len(p_measurements))
    affected = k_j >= S_n

    for i in range(len(mus)):
        if affected[i]:
            mus[i] = float(theta_phi[i,0])
            stds[i] = float(theta_phi[i,1])
        else:
            mus[i] = float(theta_phi[i, 2])
            stds[i] = float(theta_phi[i, 3])

    # Apply mask after mus and stds are computed
    valid_mask = (~np.isnan(p_measurements)) & (~np.isnan(mus)) & (stds > 0)
    p_measurements = p_measurements[valid_mask]
    mus = mus[valid_mask]
    stds = stds[valid_mask]

    return _compute_ln_likelihood_core(p_measurements, mus, stds)

def shuffle_adjacent(order:np.ndarray, rng:np.random.Generator):
    i = rng.integers(0, len(order) - 1)
    j = i + 1
    order[i], order[j] = order[j], order[i]

def shuffle_order(arr: np.ndarray, n_shuffle: int, rng:np.random.Generator) -> None:
    """
    Randomly shuffle a specified number of elements in an array.

    Args:
    arr (np.ndarray): The array to shuffle elements in.
    n_shuffle (int): The number of elements to shuffle within the array.
    """
    if n_shuffle == 0:
        return        
    
    # Select indices and extract elements
    indices = rng.choice(len(arr), size=n_shuffle, replace=False)
    original_indices = indices.copy()

    while True:
        shuffled_indices = rng.permutation(original_indices)
        # Full derangement: make sure no indice stays in its original place
        if not np.any(shuffled_indices == original_indices):
            break
    arr[indices] = arr[shuffled_indices]

def setup_logging(log_file: str):
    """
    Set up logging to a file and console.
    Ensures logs are flushed immediately after each message.
    """
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove only the previous handlers while keeping the reference
    while logger.handlers:
        handler = logger.handlers[0]
        handler.close()  # Close the handler to ensure file is properly closed
        logger.removeHandler(handler)
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file, mode='w')  # Use 'w' mode to start fresh
    file_handler.setLevel(logging.INFO)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter and set it for both handlers
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def extract_fname(data_file:str) -> str:
    """
    Extract the base filename (without extension) from the data file path.
    Replace invalid characters (e.g., `|`) with underscores.
    """
    base_name = data_file.split('/')[-1]
    fname = base_name.split(".csv")[0]
    fname = re.sub(r'[\\|/:"*?<>]+', '_', fname)
    return fname 

def cleanup_old_files(output_dir: str, fname: str):
    """
    Remove old files (heatmap, traceplot, results, log) for the given fname.
    Logs a warning if files do not exist.
    """
    files_to_remove = [
        f"{output_dir}/heatmaps/{fname}_heatmap.png",
        f"{output_dir}/traceplots/{fname}_traceplot.png",
        f"{output_dir}/results/{fname}_results.json",
        f"{output_dir}/logs/{fname}.log"
    ]

    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"Removed old file: {file_path}")
            except Exception as e:
                logging.error(f"Error removing old file: {file_path}: {e}")
        else:
            logging.warning(f"File does not exist, skipping removal: {file_path}")

def get_final_metrics(
        true_order_matrix: np.ndarray, 
        best_order_matrix: np.ndarray,
        true_subtype_assignments:np.ndarray,
        ml_subtype:np.ndarray, # subtype assignment for all participants
        ml_stage:np.ndarray, # stage assignment for all participants
        diseased_mask:np.ndarray,
) -> Tuple[float, float, float]:
    n = len(best_order_matrix)
    healthy_mask = (diseased_mask == 0)
    dist = np.zeros((n, n))
    # i can safely use the sequence results because they are the indices of the fixed input biomarker array!
    for i in range(n):
        for j in range(n):
            dist[i,j]= normalized_kendalls_tau_distance(
                best_order_matrix[i], true_order_matrix[j])
        
    # This finds the best matching: estimated_indices[i] -> true_indices[i]
    estimated_indices, true_indices = linear_sum_assignment(dist)
    # Calculate the matched Kendall's Tau
    tau = dist[estimated_indices, true_indices].mean()
    ml_subtypes = ml_subtype[diseased_mask]
    true_subtype_assignments = true_subtype_assignments[diseased_mask]
    subtype_assignment_accuracy = adjusted_rand_score(true_subtype_assignments, ml_subtypes)
    mean_stage_healthy = np.mean(ml_stage[healthy_mask])
    return tau, subtype_assignment_accuracy, mean_stage_healthy

def choose_optimal_subtypes(cvic, threshold=6) -> int:
    """
    Choose the optimal number of subtypes given an array of CVIC values.
    
    Parameters
    ----------
    cvic : array-like
        CVIC values for models with 1..N subtypes. Lower is better.
    threshold : float, optional
        Minimum improvement in CVIC required to justify a more complex model.
        Default is 6, following SuStaIn workshop guidelines.
    
    Returns
    -------
    optimal_n_subtypes : int
        Optimal number of subtypes.
    """
    cvic = np.asarray(cvic)
    n_subtypes = np.arange(1, len(cvic) + 1)
    
    # Best (lowest) CVIC
    best_idx = np.argmin(cvic)
    best_cvic = cvic[best_idx]
    
    # ΔCVIC relative to best
    delta_cvic = cvic - best_cvic
    
    # Models within threshold of best
    candidates = np.where(delta_cvic < threshold)[0]
    
    # Pick the simplest among those
    # we want the simplest setup if the delta is within range
    optimal_idx = candidates[0]
    optimal_n_subtypes = n_subtypes[optimal_idx]
    
    return optimal_n_subtypes