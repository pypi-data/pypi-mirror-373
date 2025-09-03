import numpy as np
import pysaebm.utils as utils 
from typing import Tuple
import logging

def metropolis_hastings(
        algorithm:str,
        data_matrix: np.ndarray,
        diseased_arr: np.ndarray,
        iterations: int,
        n_shuffle: int,
        prior_n: float,
        prior_v: float,
        rng: np.random.Generator
) -> Tuple:
    """
    
    """
    n_participants, n_biomarkers = data_matrix.shape

    # Validate input
    if n_shuffle <= 1:
        raise ValueError("n_shuffle must be >= 2 or =0")
    if n_shuffle > n_biomarkers:
        raise ValueError("n_shuffle cannot exceed n_biomarkers")

    n_stages = n_biomarkers + 1
    disease_stages = np.arange(start=1, stop=n_stages, step=1)
    n_disease_stages = n_stages - 1
    non_diseased_ids = np.where(diseased_arr == 0)[0]
    diseased_ids = np.where(diseased_arr == 1)[0]

    # N * 4 matrix, cols: theta_mean, theta_std, phi_mean, phi_std
    theta_phi_default = utils.get_initial_theta_phi_estimates(
        data_matrix, non_diseased_ids, diseased_ids, prior_n, prior_v, rng=rng)

    current_theta_phi = theta_phi_default.copy()

    # initialize an ordering and likelihood
    current_order = rng.permutation(np.arange(1, n_stages))
    alpha_prior = np.ones(n_disease_stages, dtype=float)
    # current_pi is the prior distribution of N disease stages.
    # Sample from uniform dirichlet dist.
    # Notice that the index starts from zero here. 
    current_pi = rng.dirichlet(alpha_prior)
    # Only for diseased participants
    
    # Initialize current likelihood & posteriors for the initial order/θφ/π
    current_ln_likelihood, current_stage_post = utils.compute_total_ln_likelihood_and_stage_likelihoods(
        n_participants, data_matrix, current_order, non_diseased_ids,
        current_theta_phi, current_pi, disease_stages
    )

    acceptance_count = 0

    # Note that this records only the current accepted orders in each iteration
    all_accepted_orders = []
    # This records all log likelihoods
    log_likelihoods = []

    for iteration in range(iterations):
        # --- TOP OF LOOP: recompute lnL for *current* state (θφ, π may have changed last iter) ---
        current_ln_likelihood, current_stage_post = utils.compute_total_ln_likelihood_and_stage_likelihoods(
            n_participants, data_matrix, current_order, non_diseased_ids,
            current_theta_phi, current_pi, disease_stages
        )

        # Propose a symmetric local move (adjacent swap)
        new_order = current_order.copy()
        utils.shuffle_adjacent(new_order, rng)

        # Likelihood for proposed order under SAME θφ, π
        new_ln_likelihood, stage_post_new = utils.compute_total_ln_likelihood_and_stage_likelihoods(
            n_participants, data_matrix, new_order, non_diseased_ids,
            current_theta_phi, current_pi, disease_stages
        )

        # (Optional) temper early to improve acceptance
        # beta = beta_schedule(iteration, iterations, beta_min=0.6, frac=0.4)
        # delta = beta * (new_ln_likelihood - current_ln_likelihood)
        delta = new_ln_likelihood - current_ln_likelihood

        accept = (delta >= 0) or (rng.random() < np.exp(delta))
        if accept:
            current_order = new_order
            current_stage_post = stage_post_new
            acceptance_count += 1

        # --- Update θ/φ given CURRENT order/posteriors (accepted or not) ---
        if algorithm != 'hard_kmeans':
            current_theta_phi = utils.update_theta_phi_estimates(
                algorithm, n_biomarkers, n_participants, non_diseased_ids,
                data_matrix, current_order, current_theta_phi, current_stage_post,
                disease_stages, prior_n, prior_v, rng.integers(0, 2**32 - 1)
            )

        # --- Gibbs update for π using CURRENT posteriors ---
        stage_counts = current_stage_post[diseased_ids].sum(axis=0)  # soft counts
        current_pi = rng.dirichlet(alpha_prior + stage_counts)

        # Recompute lnL for logging so it matches (order, θφ, π) after updates
        current_ln_likelihood, _ = utils.compute_total_ln_likelihood_and_stage_likelihoods(
            n_participants, data_matrix, current_order, non_diseased_ids,
            current_theta_phi, current_pi, disease_stages
        )
        log_likelihoods.append(current_ln_likelihood)

        all_accepted_orders.append(current_order.copy())  # (name is a bit misleading; this stores the *current* order)

        if (iteration + 1) % max(10, iterations // 10) == 0:
            acceptance_ratio = 100 * acceptance_count / (iteration + 1)
            logging.info(
                f"Iteration {iteration + 1}/{iterations}, "
                f"Acceptance Ratio: {acceptance_ratio:.2f}%, "
                f"Log Likelihood: {current_ln_likelihood:.4f}, "
            )

    return all_accepted_orders, log_likelihoods, current_theta_phi, current_stage_post, current_pi