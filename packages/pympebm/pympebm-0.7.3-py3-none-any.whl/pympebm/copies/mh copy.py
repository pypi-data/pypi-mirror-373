import numpy as np
import pympebm.utils as utils 
from typing import Tuple, List
import logging
import pympebm.mp_utils as mp_utils

def metropolis_hastings(
        partial_rankings: np.ndarray,
        mp_method: str,
        data_matrix: np.ndarray,
        diseased_arr: np.ndarray,
        biomarkers_int:np.ndarray,
        iterations: int,
        n_shuffle: int,
        prior_n: float,
        prior_v: float,
        rng: np.random.Generator
) -> Tuple:
    """Implement metroplis hastings MCMC algorithm
    
    """
    if len(partial_rankings) > 0:
        allowed_mp_method = {'PL', 'Mallows_Tau', 'Mallows_RMJ' ,'Pairwise', 'BT'}
        assert mp_method in allowed_mp_method, f'mp_method must be chosen from {allowed_mp_method}!'

        # no need to sample, so there is no need to use mcmc_iterations, sample_count, pl_best
        if mp_method != 'PL':
            mpebm_mcmc_sampler = mp_utils.MCMC(ordering_array=partial_rankings, rng=rng, method=mp_method, n_shuffle=n_shuffle)
        else:
            PL = mp_utils.PlackettLuce(ordering_array=partial_rankings, rng=rng)
            
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
    # Imagine this: the array of biomarker_int stays intact. 
    # we are randomizing the indices of each of them in the new order
    current_order = rng.permutation(np.arange(1, n_stages))
    current_ln_likelihood = -np.inf
    alpha_prior = [1.0] * (n_disease_stages)
    # current_pi is the prior distribution of N disease stages.
    # Sample from uniform dirichlet dist.
    # Notice that the index starts from zero here. 
    current_pi = rng.dirichlet(alpha_prior)
    # Only for diseased participants
    current_stage_post = np.zeros((n_participants, n_disease_stages))
    acceptance_count = 0

    # Note that this records only the current accepted orders in each iteration
    all_accepted_orders = []
    # This records all log likelihoods
    log_likelihoods = []

    for iteration in range(iterations):
        random_state = rng.integers(0, 2**32 - 1)
        log_likelihoods.append(current_ln_likelihood)

        new_order = current_order.copy()
        utils.shuffle_order(new_order, n_shuffle, rng)

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

        # --- Compute stage posteriors with OLD θ/φ ---
        _, stage_post_old = utils.compute_total_ln_likelihood_and_stage_likelihoods(
            n_participants, data_matrix, new_order, non_diseased_ids, 
            current_theta_phi, current_pi, disease_stages
        )

        # Compute the new theta_phi_estimates based on new_order
        new_theta_phi = utils.update_theta_phi_estimates(
            n_biomarkers,
            n_participants,
            non_diseased_ids,
            data_matrix,
            new_order,
            current_theta_phi,  # Current state’s θ/φ
            stage_post_old,
            disease_stages,
            prior_n,    # Weak prior (not data-dependent)
            prior_v,     # Weak prior (not data-dependent)
            random_state,
        )

        # NOTE THAT WE CANNOT RECOMPUTE P(K_J) BASED ON THIS NEW THETA PHI.
        # THIS IS BECAUSE IN MCMC, WE CAN ONLY GET NEW THINGS THAT ARE SOLELY CONDITIONED ON THE NEWLY PROPOSED S'

        # Recompute new_ln_likelihood using the new theta_phi_estimates
        new_ln_likelihood, stage_post_new = utils.compute_total_ln_likelihood_and_stage_likelihoods(
            n_participants, data_matrix, new_order, non_diseased_ids, new_theta_phi, current_pi, disease_stages
        )
        if len(partial_rankings) > 0:
            if mp_method == 'Pairwise':
                new_energy = mpebm_mcmc_sampler.pairwise_energy(biomarkers_int[np.argsort(new_order)])
            if mp_method in ['Mallows_Tau', 'Mallows_RMJ']:
                new_energy = mpebm_mcmc_sampler.mallows_energy(biomarkers_int[np.argsort(new_order)])
            if mp_method == 'BT':
                new_energy = mpebm_mcmc_sampler.bt_energy(biomarkers_int[np.argsort(new_order)])
            if mp_method == 'PL':
                new_energy = PL.pl_energy(biomarkers_int[np.argsort(new_order)])
            new_ln_likelihood -= new_energy

        # Compute acceptance probability
        delta = new_ln_likelihood - current_ln_likelihood
        prob_accept = 1.0 if delta > 0 else np.exp(delta)

        # Accept or reject the new state
        if rng.random() < prob_accept:
            current_order = new_order
            current_ln_likelihood = new_ln_likelihood
            current_stage_post = stage_post_new
            current_theta_phi = new_theta_phi
            acceptance_count += 1

            stage_counts = np.zeros(n_disease_stages)
            # participant, array of stage likelihoods
            for p in range(n_participants):
                stage_probs = stage_post_new[p]
                stage_counts += stage_probs  # Soft counts
            current_pi = rng.dirichlet(alpha_prior + stage_counts)

        all_accepted_orders.append(current_order.copy())

        # Log progress
        if (iteration + 1) % max(10, iterations // 10) == 0:
            acceptance_ratio = 100 * acceptance_count / (iteration + 1)
            logging.info(
                f"Iteration {iteration + 1}/{iterations}, "
                f"Acceptance Ratio: {acceptance_ratio:.2f}%, "
                f"Log Likelihood: {current_ln_likelihood:.4f}, "
            )

    return all_accepted_orders, log_likelihoods, current_theta_phi, current_stage_post, current_pi