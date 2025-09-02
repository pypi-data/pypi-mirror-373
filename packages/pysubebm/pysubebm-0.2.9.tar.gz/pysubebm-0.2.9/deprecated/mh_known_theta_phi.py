import numpy as np
import pysubebm.utils as utils 
from typing import Tuple
import logging
 
def metropolis_hastings(
        data_matrix: np.ndarray,
        n_subtypes: int,
        diseased_arr: np.ndarray,
        iterations: int,
        n_shuffle: int,
        n_subtype_shuffle:int,
        prior_n: float,
        prior_v: float,
        theta_phi:np.ndarray,
        rng: np.random.Generator
) -> Tuple:
    """Implement metroplis hastings MCMC algorithm
    
    """  
    n_participants, n_biomarkers = data_matrix.shape
    n_subtype_shuffle = min(n_subtype_shuffle, n_subtypes)

    # Validate input
    if n_shuffle <= 1:
        raise ValueError("n_shuffle must be >= 2 or =0")
    if n_shuffle > n_biomarkers:
        raise ValueError("n_shuffle cannot exceed n_biomarkers")

    n_stages = n_biomarkers + 1
    ## THESE ARE INDICES!
    disease_stages = np.arange(start=0, stop=n_biomarkers, step=1)
    n_disease_stages = n_stages - 1
    non_diseased_ids = np.where(diseased_arr == 0)[0]
    diseased_ids = np.where(diseased_arr == 1)[0]
    non_diseased_mask = (diseased_arr == 0)

    """Initiate theta phi
        Shape: (n_subtypes, N, 4)
    """
    # N * 4 matrix, cols: theta_mean, theta_std, phi_mean, phi_std
    # shared across all subtypes
    if theta_phi is None:
        theta_phi_default = utils.get_initial_theta_phi_estimates(
            data_matrix, non_diseased_ids, diseased_ids, prior_n, prior_v, rng=rng)
        current_theta_phi = theta_phi_default.copy()
    else:
        current_theta_phi = theta_phi.copy()


    """Initiate subtype ordering matrix
        Shape: (n_subtypes, n_disease_stages)
        Imagine this: the array of biomarker_int stays intact. we are randomizing the indices of each of them in the new order
    """
    current_order = np.zeros((n_subtypes, n_biomarkers), dtype=int)

    # For each subtype, create a permutation of ranks and assign them
    for s in range(n_subtypes):
        # This creates an array like [2, 0, 1] meaning bm 0 has rank 2, bm 1 has rank 0, etc.
        ranks = rng.permutation(np.arange(n_biomarkers))
        current_order[s, :] = ranks

    """Initiate staging prior and post
        Stage_alpha_prior and stage_prior, shape: (n_subtypes, n_disease_stages)

        Stage posterior, shape: (n_participants, n_subtypes, n_disease_stages)
    """
    # shape: (n_subtypes, n_disease_stages)
    # dirichlet alpha prior for stage_prior
    stage_alpha_prior = np.ones((n_subtypes, n_disease_stages), dtype=np.float64)

    # index from zero here
    # Initialize stage_prior array
    # stage_prior, previoulsy I used current_pi. This is the prior distribution of N disease stages, for each subtype
    current_stage_prior = np.zeros((n_subtypes, n_disease_stages), dtype=np.float64)
    # Sample from Dirichlet distribution for each subtype, based on alpha prior
    for i in range(n_subtypes):
        current_stage_prior[i, :] = rng.dirichlet(stage_alpha_prior[i, :])
    # Only for diseased participants
    current_stage_post = np.zeros((n_participants, n_subtypes, n_disease_stages), dtype=np.float64)

    """Initiate subtype prior and subtype post
    """
    # shape: (n_subtypes, 1), dirichlet alpha prior for subtype_prior
    subtype_alpha_prior = np.ones(n_subtypes, dtype=np.float64) 
    # subtype prior, sample from Dirichlet distribution, based on subtype_alpha_prior
    # shape: (n_subtypes, 1),
    current_subtype_prior = rng.dirichlet(subtype_alpha_prior)
    # shape: (n_participants, n_subtypes)
    # current_subtype_post = np.zeros((n_participants, n_subtypes), dtype=np.float64)

    # log likelihood of each participant's data under different subtypes
    current_ln_likes_subtypes = np.zeros((n_participants, n_subtypes))
    
    # range(0, n_subtypes)
    full_subtypes_to_update = np.arange(0, n_subtypes)
    current_ln_likelihood, current_stage_post, current_subtype_post, current_ln_likes_subtypes = utils.compute_likelihood_and_posteriors(
            data_matrix,
            non_diseased_mask,
            disease_stages,
            current_order,
            full_subtypes_to_update,
            current_ln_likes_subtypes, # since full_subtypes_to_update, this ln_likes_subtypes will be completely rewritten
            current_stage_post, # will be rewritten
            current_theta_phi,
            current_stage_prior,
            current_subtype_prior,
        )

    # current_ln_likelihood = -np.inf
    acceptance_count = 0
    # Note that this records only the current accepted orders in each iteration
    all_accepted_orders = []
    # This records all log likelihoods
    log_likelihoods = []

    for iteration in range(iterations):
        # random_state = rng.integers(0, 2**32 - 1)
        log_likelihoods.append(current_ln_likelihood)

        new_order = current_order.copy()
        # subtype_to_update = rng.integers(0, n_subtypes)
        # utils.shuffle_order(new_order[subtype_to_update], n_shuffle, rng)
        # randomly pick n_shuffle subtype orderings to shuffle 
        subtypes_to_update = rng.choice(n_subtypes, size=n_subtype_shuffle, replace=False)
        for subtype_idx in subtypes_to_update:
            utils.shuffle_order(new_order[subtype_idx], n_shuffle, rng)
            # utils.shuffle_adjacent(new_order[subtype_idx], rng)

        """
        When we propose a new ordering, we want to calculate the total ln likelihood, which is 
        dependent on theta_phi_estimates, which are dependent on biomarker_data and stage_likelihoods_posterior,
        both of which are dependent on the ordering. 

        Therefore, we need to update participant_data, biomarker_data, stage_likelihoods_posterior
        and theta_phi_estimates before we can calculate the total ln likelihood associated with the new ordering
        """

        """
        update theta_phi_estimates
        """

        # # --- Compute stage posteriors with NEW order and OLD θ/φ ---
        # _, stage_post_for_update, subtype_post_for_update, _  = utils.compute_likelihood_and_posteriors(
        #     data_matrix,
        #     non_diseased_mask,
        #     disease_stages,
        #     new_order,
        #     subtypes_to_update, # only update this subtype
        #     current_ln_likes_subtypes,
        #     current_stage_post,
        #     current_theta_phi,
        #     current_stage_prior,
        #     current_subtype_prior,
        # )

        # # Compute the new theta_phi_estimates based on new_order and intermediate stage post and subtype post
        # new_theta_phi = utils.update_theta_phi_estimates(
        #     n_biomarkers,
        #     n_participants,
        #     non_diseased_ids,
        #     data_matrix,
        #     new_order,
        #     current_theta_phi,  # Current state’s θ/φ
        #     # current_stage_post,
        #     # current_subtype_post,
        #     stage_post_for_update,
        #     subtype_post_for_update,
        #     disease_stages,
        #     prior_n,    # Weak prior (not data-dependent)
        #     prior_v,     # Weak prior (not data-dependent)
        # )

        # NOTE THAT WE CANNOT RECOMPUTE P(K_J) BASED ON THIS NEW THETA PHI.
        # THIS IS BECAUSE IN MCMC, WE CAN ONLY GET NEW THINGS THAT ARE SOLELY CONDITIONED ON THE NEWLY PROPOSED S'

        # Recompute new_ln_likelihood using the new theta_phi_estimates
        new_ln_likelihood, stage_post_new, subtype_post_new, ln_likes_subtypes_new = utils.compute_likelihood_and_posteriors(
            data_matrix,
            non_diseased_mask,
            disease_stages,
            new_order,
            subtypes_to_update,
            # full_subtypes_to_update,
            current_ln_likes_subtypes, # since full_subtypes_to_update, this ln_likes_subtypes will be completely rewritten
            # stage_post_for_update, # all will be recalculated 
            current_stage_post,
            current_theta_phi,
            # new_theta_phi,
            current_stage_prior,
            current_subtype_prior,
        )
        
        # Compute acceptance probability
        delta = new_ln_likelihood - current_ln_likelihood
        prob_accept = 1.0 if delta > 0 else np.exp(delta)

        # Accept or reject the new state
        if rng.random() < prob_accept:
            current_order = new_order
            current_ln_likes_subtypes = ln_likes_subtypes_new
            current_ln_likelihood = new_ln_likelihood
            current_stage_post = stage_post_new
            # current_theta_phi = new_theta_phi
            current_subtype_post = subtype_post_new
            acceptance_count += 1

            # --- Gibbs update for π using CURRENT posteriors ---
            # 6. UPDATE Priors (π) based on new posteriors
            # Update stage priors for each subtype
            for s in range(n_subtypes):
                # row sum for each col: sum across participants for disease stage
                weighted_stage_counts = np.sum(current_stage_post[:, s, :] * current_subtype_post[:, s, np.newaxis], axis=0)
                current_stage_prior[s, :] = rng.dirichlet(stage_alpha_prior[s, :] + weighted_stage_counts)
            
            # row sum for each col: sum across participants for each subtype
            # Update global subtype prior
            subtype_counts = np.sum(current_subtype_post, axis=0)
            current_subtype_prior = rng.dirichlet(subtype_alpha_prior + subtype_counts)


        all_accepted_orders.append(current_order.copy())

        # Log progress
        if (iteration + 1) % max(10, iterations // 10) == 0:
            acceptance_ratio = 100 * acceptance_count / (iteration + 1)
            logging.info(
                f"Iteration {iteration + 1}/{iterations}, "
                f"Acceptance Ratio: {acceptance_ratio:.2f}%, "
                f"Log Likelihood: {current_ln_likelihood:.4f}, "
            )

    return all_accepted_orders, log_likelihoods, current_theta_phi, current_stage_post, current_subtype_prior, current_stage_prior, current_subtype_post