from typing import List, Tuple, Dict
import numpy as np
from collections import defaultdict, Counter
from scipy.optimize import minimize
from numba import njit
from numba.typed import List as NumbaList
from scipy.stats import  spearmanr

EPSILON = 1e-12

@njit(fastmath=False, parallel=False)
# @njit(parallel=True)
def rankings_to_matrix(rankings):
    # each ranking consists of unique items, rather than consecutive integers
    n_raters, n_items = rankings.shape
    int_rankings = np.zeros((n_raters, n_items), dtype=np.int64)
    for idx in range(n_raters):
        # same item order, different pos
        int_rankings[idx] = np.argsort(rankings[idx])
    return int_rankings

@njit(fastmath=False, parallel=False) 
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


# # ----------------------------
# # 2) Pad & deduplicate fast
# # ----------------------------
# def _pad_rows(partial_rankings: List[np.ndarray], pad_value: int = -1) -> np.ndarray:
#     """
#     Efficient padding with a single pass; uses NumPy arrays internally.
#     """
#     if not partial_rankings:
#         return np.empty((0, 0), dtype=int)
#     lengths = np.fromiter((len(r) for r in partial_rankings), dtype=int, count=len(partial_rankings))
#     max_len = int(lengths.max())
#     out = np.full((len(partial_rankings), max_len), pad_value, dtype=int)
#     for i, r in enumerate(partial_rankings):
#         out[i, :len(r)] = r
#     return out

# # ----------------------------
# # 3) One-shot generator for unique, padded partial orders
# # ----------------------------
# def get_padded_partial_orders(
#     biomarkers_int: np.ndarray,  # biomarkers in int form
#     low_num: int,                # lowest possible number of partial rankings
#     high_num: int,
#     low_length: int,             # lowest possible length of each partial ranking
#     high_length: int, 
#     rng: np.random.Generator,
# ) -> np.ndarray:
#     """
#     Generate N unique partial orders, pad them with -1, and return as an array.
#     Strategy:
#       - Sample desired lengths.
#       - Over-generate candidates in batches, pad, uniquify, keep-first N.
#       - This avoids the while-loop that regenerates everything on any collision.
#     """
#     n_target = int(rng.integers(low_num, high_num + 1))
#     # note: np.arange(high) excludes high, so add 1 to be inclusive if wanted
#     lengths = rng.integers(low_length, high_length + 1, size=n_target, dtype=int)

#     collected = []
#     seen = set()  # hash tuples of sequences (no padding) for dedup
#     N = biomarkers_int.shape[0]

#     # batch size heuristic: generate a bit more than needed to reduce repeats
#     batch = max(8, int(np.ceil(n_target * 1.3)))

#     while len(collected) < n_target:
#         # Make a batch, then filter uniques quickly
#         # Generate a single permutation matrix for the batch
#         scores = rng.random((batch, N))
#         perm_idx = np.argsort(scores, axis=1)
#         perms = biomarkers_int[perm_idx]

#         # Create jagged sequences with required lengths; recycle lengths if needed
#         # (so batch can exceed remaining)
#         k = min(batch, n_target - len(collected))
#         target_lengths = lengths[len(collected):len(collected)+k]

#         # Try a bit more than k to offset collisions
#         # (take first 2k candidates, slice to each target length)
#         take = min(perms.shape[0], 2*k)
#         candidates = [perms[i, :target_lengths[min(i, k-1)]] for i in range(take)]

#         for seq in candidates:
#             t = tuple(seq.tolist())
#             if t not in seen:
#                 seen.add(t)
#                 collected.append(seq)
#                 if len(collected) == n_target:
#                     break

#     # Pad and return
#     return _pad_rows(collected, pad_value=-1)

# # ----------------------------
# # 4) Combined order — unchanged API (your samplers do the work)
# # ----------------------------
# def get_combined_order(
#     padded_partial_orders: np.ndarray,
#     rng: np.random.Generator,
#     method: str,
#     mcmc_iterations: int,
#     pl_best: bool,
#     mallows_temperature: float
# ) -> np.ndarray:
#     if method == 'PL':
#         sampler = PlackettLuce(ordering_array=padded_partial_orders, rng=rng, pl_best=pl_best)
#     else:
#         sampler = MCMC(
#             ordering_array=padded_partial_orders,
#             rng=rng,
#             method=method,
#             mcmc_iterations=mcmc_iterations,
#             mallows_temperature=mallows_temperature
#         )
#     return sampler.sample_one()

# def get_final_params(
#     params: Dict[str, Dict[str, float]],
#     combined_ordering: np.ndarray,
#     ordering_array,  # can be List[np.ndarray] or a 2-D np.ndarray with -1 padding
#     int2str: Dict[int, str],
#     rng: np.random.Generator,
# ) -> Dict[str, Dict[str, float]]:
#     # Flatten and drop padding (-1)
#     if isinstance(ordering_array, np.ndarray):
#         flat = ordering_array.ravel()
#     else:
#         flat = np.concatenate([np.asarray(x, dtype=int, order='C') for x in ordering_array]) \
#                if ordering_array else np.empty((0,), dtype=int)

#     if flat.size:
#         flat = flat[flat >= 0]  # remove -1 padding

#     if flat.size:
#         max_idx = int(flat.max())
#         freq = np.bincount(flat, minlength=max_idx + 1)
#         def get_freq(x: int) -> int:
#             return int(freq[x]) if 0 <= x <= max_idx else 0
#     else:
#         def get_freq(x: int) -> int:
#             return 0

#     final_params: Dict[str, Dict[str, float]] = {}
#     for bm_int in combined_ordering:
#         if bm_int in int2str:  # automatically skips -1 and unknowns
#             bm = int2str[bm_int]
#             out = params[bm].copy()
#             if get_freq(bm_int) > 1:
#                 vals = rng.uniform(-0.95, 0.95, size=2)
#                 out['theta_mean'] = out['theta_mean'] + out['theta_mean'] * vals[0]
#                 out['theta_std']  = out['theta_std']  + out['theta_std']  * vals[1]
#             final_params[bm] = out
#     return final_params


def get_partial_orders(
        n_partial_rankings: int,
        lengths: List[int],
        biomarkers_int:np.ndarray, 
        rng: np.random.Generator
    ) -> List[List[int]]:
    # Get partial rankings based on params dict
    res = []
    for idx in range(n_partial_rankings):
        partial_ranking = rng.choice(biomarkers_int, size=lengths[idx], replace=False)
        res.append(partial_ranking)
    return res 

def get_unique_rows(partial_rankings:List[List[int]]) -> np.ndarray:
    """get padded partial rankings
    """
    max_len = 0
    for r in partial_rankings:
        if len(r) > max_len:
            max_len = len(r)
    padded = np.full((len(partial_rankings), max_len), -1, dtype=int)
    for i, row in enumerate(partial_rankings):
        padded[i, :len(row)] = row
    unique_rows, idx = np.unique(padded, axis=0, return_index=True)
    return unique_rows

def get_padded_partial_orders(
        biomarkers_int:np.ndarray, # biomarkers in int form
        low_num: int, # lowest possible number of partial rankings
        high_num:int,
        low_length:int, # lowest possible length of each partial ranking
        high_length:int, 
        rng: np.random.Generator,
    ) -> np.ndarray:
    """Get unique and padded partial orders. 
    """
    n_partial_rankings = rng.integers(low_num, high_num + 1)
    # partial ranking length does not have to be unique, so replace=True
    lengths = rng.choice(np.arange(low_length, high_length + 1), size=n_partial_rankings, replace=True)
    n_unique = 0
    # to make sure no two partial orderings are the same
    while n_unique != n_partial_rankings: 
        partial_rankings = get_partial_orders(n_partial_rankings, lengths, biomarkers_int, rng)
        # to make sure the output partial rankings have the same length;
        n_unique = len({tuple(r) for r in partial_rankings})
    
    return get_unique_rows(partial_rankings)

def get_combined_order(
        padded_partial_orders:np.ndarray,
        rng: np.random.Generator,
        method:str,
        mcmc_iterations:int,
        pl_best:bool,
        mallows_temperature:float
    ) -> np.ndarray:

    # get combined ordering
    if method == 'PL':
        sampler = PlackettLuce(ordering_array=padded_partial_orders, rng=rng, pl_best=pl_best)
    else:
        sampler = MCMC(ordering_array=padded_partial_orders, rng=rng, method=method, mcmc_iterations=mcmc_iterations, mallows_temperature=mallows_temperature)

    return sampler.sample_one()

def get_final_params(
        params:Dict[str, Dict[str, float]], 
        combined_ordering:np.ndarray, 
        ordering_array:np.ndarray,
        int2str:Dict[int, str],
        rng:np.random.Generator,
    ) -> Dict[str, Dict[str, float]]:
    """
    1. use the combined ordering
    2. for biomarkers that appear in more than one ordering, we need to modify its parameters. 
    """
    final_params = {}
    flattend_ordering_array = [item for sublist in ordering_array for item in sublist]
    frequency_dict = dict(Counter(flattend_ordering_array))

    for bm_int in combined_ordering:
        # pass over the padded -1 
        if bm_int in int2str:
            bm = int2str[bm_int]
            final_params[bm] = params[bm].copy()
            if frequency_dict[bm_int] > 1:
                vals = rng.uniform(-0.95, 0.95, size=2)
                final_params[bm]['theta_mean'] += final_params[bm]['theta_mean'] * vals[0]
                final_params[bm]['theta_std'] += final_params[bm]['theta_std'] * vals[1]
    return final_params

@njit(fastmath=False, parallel=False)
def pl_neg_log_likelihood_numba(ordering_array, alphas):
    """
    ordering_array: list/array of int64 arrays (0-based IDs into theta)
    alphas: 1D float64 array of length n_unique_elements

    We are multiplying all the total likelihood of each partial ordering
    but since we are using log, we add them up
    since optimizers only minimizes, we take the negative. 
    """
    total = 0.0
    for ordering_idx in ordering_array:
        partial_alphas = alphas[ordering_idx] # alphas for this current partial rank (as partial ranks may be incomplete)
        n = len(ordering_idx)
        for i in range(n):
            # alphas in the denominator of the energy forumla
            sub_alphas = partial_alphas[i:] # alphas are the raw theta/alpha values
            max_alpha = np.max(sub_alphas)
            log_denom = max_alpha + np.log(np.sum(np.exp(sub_alphas - max_alpha)))
            total += partial_alphas[i] - log_denom
    return -total

@njit(fastmath=False, parallel=False)
def pl_energy_numba(ordering, unique_elements, alphas):
    """
    ordering: ID int64 array of IDs
    unique_elements: the sorted array of unique elements from PL class
    alphsa: 1D float64 array
    Returns: scalar energy
    """
    n = len(ordering)
    # Map item IDs to theta indices
    ordering_idx = np.zeros(n, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            if ordering[i] == unique_elements[j]:
                ordering_idx[i] = j
                break 

    # Compute PL energy
    total_energy = 0.0 
    n = len(ordering_idx)
    for i in range(n):
        sub_alphas = alphas[ordering_idx[i:]]
        max_alpha = np.max(sub_alphas)
        log_denom = max_alpha + np.log(np.sum(np.exp(sub_alphas - max_alpha)))
        total_energy += -(alphas[ordering_idx[i]] - log_denom)
    return total_energy

def pl_sample_one_random(unique_elements, theta, rng):
    """
    Sample one Plackett–Luce ranking.

    unique_elements : array-like of labels (ints, strs, etc.)
    theta           : array of log-worths (same length as unique_elements)
    rng             : np.random.Generator

    Gumbel Max Property: if we add Gumbel(0,1) noise to log-worths theta_i,
    the probability that item i has the maximum score is exactly e^theta_i/sum_j e^theta_j
    """
    scores = theta + rng.gumbel(size=theta.shape)
    order = np.argsort(-scores)             # indices in descending order
    return unique_elements[order]           # labels in PL order

def pl_sample_one_best(
        unique_elements:np.ndarray,
        current_order:np.ndarray, 
        theta:np.ndarray, 
        mcmc_iterations:int, 
        n_shuffle:int,
        rng:np.random.Generator
        ) -> np.ndarray:
    """Use MCMC to sample PL
    """
    # Sample one first 
    current_energy = pl_energy_numba(current_order, unique_elements, theta)

    # Track best order and best energy 
    best_order = current_order.copy()
    best_energy = current_energy 

    ## MCMC iterations
    for _ in range(mcmc_iterations):
        new_order = current_order.copy()
        shuffle_order(arr = new_order, n_shuffle=n_shuffle, rng=rng)
        new_energy = pl_energy_numba(new_order, unique_elements, theta)
        # Calculate the acceptance probability, α = min(1, P(σ')/P(σ)).
        # P(σ')/P(σ) = exp(-E(σ')) / exp(-E(σ)) = exp(E(σ) - E(σ'))
        delta_energy = current_energy - new_energy
        if delta_energy > 700:  # Safe threshold for float64
            prob_accept = 1.0
        else:
            prob_accept = min(1.0, np.exp(delta_energy))

        # Accept the new ordering with probability α
        if rng.random() < prob_accept:
            current_order=new_order
            current_energy=new_energy
        
        if current_energy < best_energy:
            best_order = current_order.copy()
            best_energy = current_energy

    return best_order 

class PlackettLuce:
    def __init__(
            self, 
            ordering_array:np.ndarray,
            rng: np.random.Generator, 
            sample_count:int=500, 
            mcmc_iterations:int=500,
            n_shuffle:int=2,
            pl_best:bool=True,
            n_random_perms:int=1_0000 # how many random permutations to use for alignment computation
            ):
        """
        ordering_array: padded array of array (integers, arbitrary IDs);  padded with -1
        rng: np.random.Generator
        """
        self.rng = rng 
        self.aggrank_dependence = None
        # how many to sample for conflict and certainty calculation
        self.sample_count = sample_count 
        self.mcmc_iterations = mcmc_iterations
        self.n_shuffle = n_shuffle
        self.pl_best = pl_best
        self.ordering_array = ordering_array
        self.n_random_perms = n_random_perms

        # Step 1: Find all unique elements and sort
        # pass over -1
        self.unique_elements = np.array(
            sorted(set(item for ordering in ordering_array for item in ordering if item != -1)),
            dtype=np.int64
        )
        self.n_unique_elements = len(self.unique_elements)

        # Step 2: Build mapping from original ID -> theta index 
        # This is useful to convert partial rankings
        # For full rankings, we can use np.argsort()
        self.elem2idx = {elem: idx for idx, elem in enumerate(self.unique_elements)}

        # Step 3: Remap all orderings to 0-based theta indices
        ordering_list = NumbaList()
        for ordering in ordering_array:
            # pass over -1
            ordering_list.append(np.array([self.elem2idx[x] for x in ordering if x !=-1], dtype=np.int64))
        self.ordering_array_int = ordering_list

        # Step 4: Initialize theta and sampled orderings 
        self.theta = np.zeros(self.n_unique_elements, dtype=np.float64)
        self.sampled_combined_orderings = np.zeros((sample_count, self.n_unique_elements), dtype=np.int64)
        self.sampled_energies = np.zeros(sample_count, dtype=np.float64)

        # Step 5: Fit theta
        self.estimate_pl_theta()

    def pl_neg_log_likelihood(self, theta:np.ndarray) -> float:
        return pl_neg_log_likelihood_numba(self.ordering_array_int, theta)
        
    def estimate_pl_theta(self):
        result = minimize(
            fun = self.pl_neg_log_likelihood,
            x0=self.theta,
            method = 'L-BFGS-B'
        )
        if not result.success:
            print("Warning: optimization failed:", result.message)
        self.theta = result.x
    
    def get_energy(self, ordering):
        """
        ordering: array of real biomarker IDs (same domain as unique_elements)
        Returns: scalar energy
        """
        # Map real IDs to theta index space
        # ordering_idx = np.array([self.elem2idx[x] for x in ordering], dtype=np.int64)
        return pl_energy_numba(ordering, self.unique_elements, self.theta)

    def sample_one_random(self) -> np.ndarray:
        """Sample a single complete ordering (integer indices into theta)."""
        return pl_sample_one_random(self.unique_elements, self.theta, self.rng)
    
    def sample_one_best(self) -> np.ndarray:
        current_order = self.sample_one_random()

        return pl_sample_one_best(
            unique_elements = self.unique_elements,
            current_order=current_order, 
            theta=self.theta, 
            mcmc_iterations=self.mcmc_iterations, 
            n_shuffle=self.n_shuffle,
            rng=self.rng
        )
        
    def sample_one(self) -> np.ndarray:
        if self.pl_best:
            return self.sample_one_best()
        else:
            return self.sample_one_random()
        
    def get_sampled_combined_orderings(self):
        for idx in range(self.sample_count):
            order = self.sample_one().astype(np.int64)
            if order.shape != (self.n_unique_elements,):
                raise ValueError(f"Unexpected sample shape {order.shape}")
            self.sampled_combined_orderings[idx, :] = order
            self.sampled_energies[idx] = self.get_energy(order)
    
    def compute_alignment_and_determinism(self):
        # those sampled are using the original random IDs, not indices
        if np.sum(self.sampled_combined_orderings[0]) == 0:
            self.get_sampled_combined_orderings()

        # Calculate aggrank_agreement: how stable is the full ranking generation
        rank_matrix = rankings_to_matrix(self.sampled_combined_orderings)
        self.aggrank_agreement = kendalls_w(rank_matrix)

        # check model validity (that random perms with lower energies should be closer to sampled perms/full rankings)
        # those are IDs
        random_perms = np.array([self.rng.permutation(self.unique_elements) for _ in range(self.n_random_perms)])
        self.random_perms = random_perms 

        self.random_perm_energies = np.zeros(len(random_perms), dtype=np.float64)
        for i, random_perm in enumerate(random_perms):
            self.random_perm_energies[i] = self.get_energy(random_perm)

        self.aggrank_dependence = auroc_from_energies(y=self.sampled_energies, x=self.random_perm_energies)
       
    def check_model_validity(self):
        # need to have random_perms and sampled_combined_orderings first
        if self.aggrank_dependence is None:
            self.compute_alignment_and_determinism()
        # the tau array. taus[i] is the average tau beween random_perms[i] and self.sampled_combined_orderings
        self.random_perm_taus, _ = get_average_tau(self.random_perms, self.sampled_combined_orderings)
        # Spearman correlation
        self.spearman_rho, self.spearman_p = spearmanr(self.random_perm_taus, self.random_perm_energies)

@njit(fastmath=False, parallel=False) 
def compute_conflict2(ordering_array:np.ndarray) -> float:
    """
    Args:
        - ordering_array: np array of arrays of the same length (IDs, padded with -1)
        - dist_metric: choose from 'tau' and 'rmj'
    """
    total = 0
    K = len(ordering_array)

    for i in range(K-1):
        for j in range(i+1, K):

            ordering1 = ordering_array[i]
            ordering2 = ordering_array[j]

            # find common 
            common_items = NumbaList()
            for item in ordering1:
                if item != -1 and item in ordering2:
                    common_items.append(item)
            if len(common_items) < 2:
                continue 

            r1 = np.empty(len(common_items), dtype=np.int64)
            r2 = np.empty(len(common_items), dtype=np.int64)

            idx = 0 
            for item in ordering1:
                if item in common_items:
                    r1[idx] = item 
                    idx += 1
            idx = 0
            for item in ordering2:
                if item in common_items:
                    r2[idx] = item 
                    idx += 1

            # get the index of the common items 
            r1 = np.argsort(r1)
            r2 = np.argsort(r2)

            total += normalized_kendalls_tau_distance(r1, r2)
 
    return 2/(K * (K-1)) * total if K > 1 else 0.0

def shuffle_order(arr: np.ndarray, n_shuffle: int, rng:np.random.Generator) -> int:
    """
    Numba-compatible shuffle function that actually works.

    Shuffle arr in-place and return another random state
    
    Args:
        arr: Array to shuffle (modified in-place)  
        n_shuffle: Number of swaps to perform
    """
    if n_shuffle <= 1:
        raise ValueError("n_shuffle must be >= 2 or =0")
    if n_shuffle > len(arr):
        raise ValueError("n_shuffle cannot exceed array length")
    if n_shuffle == 0:
        return

    indices=rng.choice(len(arr), size=n_shuffle, replace=False)
    original_indices=indices.copy()

    while True:
        shuffled_indices=rng.permutation(original_indices)
        if not np.any(shuffled_indices == original_indices):
            break
    arr[indices]=arr[shuffled_indices]

@njit(fastmath=False, parallel=False) 
def pairwise_energy_numba(ordering, weights_dict_keys, weights_dict_values) -> float:
        """
        Calculates the energy E(σ) of a given ordering.

        The energy is defined as E(σ) = -Σ w_ij * 1[i <_σ j], where 1[i <_σ j]
        is 1 if i precedes j in the ordering σ, and 0 otherwise.

        Args:
            ordering: 1D array of item IDs (integers), representing a total ordering σ.
            weights_dict_keys: 2D array of shape (n_pairs, 2) containing (i,j) pairs
            weights_dict_values: 1D array of weights corresponding to each pair

        Returns:
            The calculated energy of the ordering.
        """
        total_sum = 0.0
        n = len(ordering)

        for i in range(0, n-1):
            for j in range(i + 1, n):
                # Sum the weights for all pairs (i, j) where i precedes j
                item_i = ordering[i]
                item_j = ordering[j]
                # Locate weight for this pair
                for k in range(len(weights_dict_keys)):
                    if weights_dict_keys[k, 0] == item_i and weights_dict_keys[k, 1] == item_j:
                        total_sum += weights_dict_values[k]
                        break 
        return -total_sum

@njit(fastmath=False, parallel=False) 
def bt_energy_numba(ordering, theta_keys, theta_values) -> float:
    """
    Calculate Bradley-Terry energy.
    
    Args:
        ordering: 1D array of item IDs
        theta_keys: 1D array of item IDs
        theta_values: 1D array of theta parameters corresponding to each item
    """

    total_energy = 0.0
    n = len(ordering)

    for i in range(n):
        for j in range(i + 1, n):
            # Locate theta values 
            theta_i = theta_j = 0.0 
            for k in range(len(theta_keys)):
                if theta_keys[k] == ordering[i]:
                    theta_i = theta_values[k]
                    continue 
                if theta_keys[k] == ordering[j]:
                    theta_j = theta_values[k]
                    continue 
            # # Originally:
            # prob_ij = np.exp(theta_i) / (np.exp(theta_i) + np.exp(theta_j))
            # total_energy += - np.log(prob_ij)
            # Most numerically stable
            prob_ij = 1.0 / (1.0 + np.exp(theta_j - theta_i))
            total_energy += -np.log(max(prob_ij, 1e-16))
    return total_energy

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

@njit(fastmath=False, parallel=False) 
def normalized_rmj_distance(central:np.ndarray, ranking:np.ndarray) -> float:
    n = len(central)
    max_id = np.max(central) 
    pos_array = np.empty(max_id + 1, dtype = np.int64)
    for i in range(n):
        pos_array[central[i]] = i 
    
    distance = 0.0 
    for i in range(n-1):
        a = ranking[i]
        b = ranking[i+1]
        if pos_array[a] > pos_array[b]:
            distance += (n - i - 1)
    max_distance = n * (n-1) / 2
    return distance / max_distance if max_distance > 0 else 0.0 

@njit(fastmath=False, parallel=False) 
def mallows_energy_numba(ordering:np.ndarray, central_ordering:np.ndarray, dist_metric:str, mallows_temperature:float) -> float:
    """Calculate the energy of ordering using mallows
    Args:
        ordering: np.ndarray, an 1D array of IDs
        central_ordering: np.ndarray, an 1D array of IDs
    """

    if dist_metric == 'tau':
        # get the index of the common items 
        r1 = np.argsort(ordering)
        r2 = np.argsort(central_ordering)

        return mallows_temperature * normalized_kendalls_tau_distance(r1, r2, )
    else:
        return mallows_temperature * normalized_rmj_distance(central=central_ordering, ranking=ordering)

def mcmc_sample(
        initial_ordering,
        iterations,
        n_shuffle,
        method, 
        weights_keys, weights_values,
        theta_keys, theta_values,
        central_ranking,
        mallows_temperature, 
        rng
) -> np.ndarray:
    """
    Runs the Metropolis-Hastings MCMC sampler to get a final ordering.

    Returns:
        A numpy array representing the final sampled total ordering.
    """

    current_order = initial_ordering.copy()

    # Calculate initial energy
    if method == 0: # Pairwise
        current_energy= pairwise_energy_numba(current_order, weights_keys, weights_values)
    elif method == 1: # Mallows_Tau
        current_energy= mallows_energy_numba(current_order, central_ranking, dist_metric='tau', mallows_temperature=mallows_temperature)
    elif method == 2: # Mallows_RMJ
        current_energy = mallows_energy_numba(current_order, central_ranking, dist_metric='rmj', mallows_temperature=mallows_temperature)
    else: # BT
        current_energy = bt_energy_numba(current_order, theta_keys, theta_values)

    best_order = current_order.copy()
    best_energy = current_energy 

    # Loop for T iterations
    for _ in range(iterations):
        new_order = current_order.copy()
        shuffle_order(arr = new_order, n_shuffle=n_shuffle, rng=rng)

        # Calculate new energy
        if method == 0: # Pairwise
            new_energy= pairwise_energy_numba(new_order, weights_keys, weights_values)
        elif method == 1: # Mallows_Tau
            new_energy= mallows_energy_numba(new_order, central_ranking, dist_metric='tau', mallows_temperature=mallows_temperature)
        elif method == 2: # Mallows_RMJ
            new_energy= mallows_energy_numba(new_order, central_ranking, dist_metric='rmj', mallows_temperature=mallows_temperature)
        else: # BT
            new_energy = bt_energy_numba(new_order, theta_keys, theta_values)

        # Calculate the acceptance probability, α = min(1, P(σ')/P(σ)).
        # P(σ')/P(σ) = exp(-E(σ')) / exp(-E(σ)) = exp(E(σ) - E(σ'))
        delta_energy = current_energy - new_energy
        if delta_energy > 700:  # Safe threshold for float64
            prob_accept = 1.0
        else:
            prob_accept = min(1.0, np.exp(delta_energy))

        # Accept the new ordering with probability α
        if rng.random() < prob_accept:
            current_order=new_order
            current_energy=new_energy
        
        if current_energy < best_energy:
            best_order = current_order.copy()
            best_energy = current_energy

    return best_order 

@njit(fastmath=False, parallel=False)
def get_average_tau(perms_a: np.ndarray, perms_b: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Compute average normalized Kendall's tau distance between two sets of permutations.

    Returns:
        inner_taus: inner_taus[i] = average distance between perms_a[i] and all perms_b
        avg_tau: mean(inner_taus)
    """
    # Assumes perms_a and perms_b are 2D (n_perms, n_items) int64 arrays of permutations.
    nA = perms_a.shape[0]
    nB = perms_b.shape[0]
    inner_taus = np.zeros(nA, dtype=np.float64)

    for i in range(nA):
        perm_a = perms_a[i]
        order_a = np.argsort(perm_a) 
        s = 0.0
        for j in range(nB):
            perm_b = perms_b[j]
            order_b = np.argsort(perm_b)
            s += normalized_kendalls_tau_distance(order_a, order_b)
        inner_taus[i] = s / nB

    avg_tau = np.mean(inner_taus)
    return inner_taus, avg_tau

@njit(fastmath=False, parallel=False)
# @njit(parallel=True)
def alignment_metric(algo_energies, random_energies):
    if len(algo_energies) == 0:
        return 0.0
    max_algo = np.max(algo_energies)
    n_random = len(random_energies)
    count_above = 0
    for idx in range(n_random):   
        count_above += random_energies[idx] > max_algo
    return count_above / n_random

def _rankdata_average(x: np.ndarray) -> np.ndarray:
    """
    Average (tie-aware) ranks, 1..n. Stable (mergesort) to keep groups contiguous.
    """
    x = np.asarray(x)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(x, dtype=float)
    xs = x[order]
    n = len(x)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        ranks[order[i:j + 1]] = avg
        i = j + 1
    return ranks

@njit(fastmath=False, parallel=False)
def auroc_from_energies(x: np.ndarray, y: np.ndarray, x_is_positive:bool=True) -> float:
    """
    Compute AUROC using Mann-Whitney U statistic.

    x should be random_energies; y should be algo_energies
    
    Args:
        x, y: 1D numpy arrays of sample values
        x_is_positive: If True, x represents positive class scores
    
    Returns:
        AUROC value between 0 and 1
    """
    n1 = len(x)
    n2 = len(y)
    combined = np.empty(n1 + n2, dtype=np.float64)
    labels = np.empty(n1 + n2, dtype=np.int64)

    # Fill combined array
    for i in range(n1):
        combined[i] = x[i]
        labels[i] = 0
    for j in range(n2):
        combined[n1 + j] = y[j]
        labels[n1 + j] = 1

    # argsort
    order = np.argsort(combined)
    ranks = np.empty_like(order, dtype=np.float64)

    # Assign average ranks (handle ties manually)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and combined[order[j]] == combined[order[i]]:
            j += 1
        avg_rank = 0.5 * (i + j - 1) + 1  # +1 for rank starting at 1
        for k in range(i, j):
            ranks[order[k]] = avg_rank
        i = j

    # Sum of ranks for sample x
    R1 = 0.0
    for i in range(n1 + n2):
        if labels[i] == 0:
            R1 += ranks[i]

    # Compute U statistics
    U1 = R1 - n1 * (n1 + 1) / 2.0 # U for sample x
    U2 = n1 * n2 - U1 # U for sample y
    if x_is_positive:
        auroc = U1/(n1 * n2)
    else:
        auroc = U2/ (n1 * n2)
    return auroc 

class MCMC:
    """
    Uses Metropolis-Hastings MCMC to sample a total ordering.

    This class implements the MCMC algorithm to draw a sample from the
    probability distribution P(σ) ∝ exp(-E(σ)), where the energy E(σ)
    is defined by the pairwise preference weights.
    """
    def __init__(
            self,
            ordering_array: np.ndarray,
            mcmc_iterations: int=1000, 
            n_shuffle: int=2,
            rng: np.random.Generator=None,
            method: str='Mallows',
            sample_count:int=500,
            mallows_temperature = 1,
            n_random_perms:int=1_0000, 
        ):
        """
        Initializes the MCMC sampler.

        Args:
            ordering_array: padded array of arrays (integers)
            iterations: The number of MCMC iterations to perform.
            n_shuffle: The number of items to swap in each proposal step.
                       The paper suggests a swap of 2 items.
            method: choose from 'Mallows_Tau', 'Mallows_RMJ', 'Pairwise', 'BT'
        """
        # 1. Calculate the preference weights from the input data.
        self.method=method
        self.aggrank_dependence = None 
        self.n_random_perms = n_random_perms
        self.ordering_array =ordering_array
        self.iterations = mcmc_iterations
        self.n_shuffle = n_shuffle 
        self.sample_count = sample_count 
        self.mallows_temperature = mallows_temperature
        self.rng = rng 
        if method == 'Mallows_Tau':
            self.dist_metric = 'tau'
        if method == 'Mallows_RMJ':
            self.dist_metric = 'rmj'

        # Get unique elements 
        self.unique_elements = np.unique(
            np.concatenate([
                ordering[ordering != -1]  # keep only elements != -1
                for ordering in self.ordering_array
            ])
        )
        self.n_items = len(self.unique_elements)

        self.sampled_combined_orderings = np.zeros((sample_count, self.n_items), dtype=np.int64)
        self.sampled_energies = np.zeros(sample_count, dtype=np.float64)

        if 'Mallows' in method:
            ori_method = method
            self.method = 'BT'
            self._prepare_method_data()
            self.central_ranking = self.sample_one()
            self.method = ori_method # change back to Mallows method

        self._prepare_method_data()

    def _prepare_method_data(self):
        """Prepare method-specific data structures for numba"""
        if self.method == 'Pairwise':
            self._prepare_pairwise_data()
        elif self.method == 'BT':
            self._prepare_bt_data()

    def _prepare_pairwise_data(self):
        """
        Computes the w_ij weights based on the input orderings.

        The weight w_ij is the sum of preferences across all orderings.
        For each input ordering, if 'i' comes before 'j', the score for (i, j)
        increases by 1, and the score for (j, i) decreases by 1.
        """
        weights=defaultdict(int)
        for ordering in self.ordering_array:
            for i in range(0, len(ordering) - 1):
                for j in range(i+1, len(ordering)):
                    # For a given pair (item1, item2) where item1 precedes item2
                    item1=ordering[i]
                    item2=ordering[j]
                    # ignore the padded -1 in partial rankings
                    if item1 != -1 and item2 != -1:

                        # Increment weight for i preceding j
                        weights[(item1, item2)] += 1
                        # Decrement weight for j preceding i
                        weights[(item2, item1)] -= 1
        
        # Convert to numba-compatible arrays 
        self.weights_keys = np.array(list(weights.keys()), dtype=np.int64)
        self.weights_values = np.array(list(weights.values()), dtype=np.float64)

    
    def _prepare_bt_data(self):
        """Prepare BT parameters"""
        # Count pairwise comparisons
        bt_counts = defaultdict(int)
        for ordering in self.ordering_array:
            for i in range(len(ordering)):
                for j in range(i+1, len(ordering)):
                    item1=ordering[i]
                    item2=ordering[j]
                    if item1 != -1 and item2 != -1:
                        bt_counts[(item1, item2)] += 1 # item i before j
        
        # Optimize theta parameters 
        theta_dict = self._estimate_bt_theta(bt_counts)

        # Convert to numba-compatible arrays 
        self.theta_keys = np.array(list(theta_dict.keys()), dtype=np.int64)
        self.theta_values = np.array(list(theta_dict.values()), dtype=np.float64)

    def _estimate_bt_theta(self, bt_counts):
        """Estimate BT parameters using scipy optimization"""
        # Create mapping from item IDs to indices for optimization
        items_idx = {item: idx for idx, item in enumerate(self.unique_elements)}
        
        def bt_neg_log_likelihood(theta:np.ndarray) -> float:
            total = 0
            for (i, j), count in bt_counts.items():
                i_idx = items_idx[i]
                j_idx = items_idx[j]
                theta_i = theta[i_idx]
                theta_j = theta[j_idx]
                log_prob = theta_i - np.logaddexp(theta_i, theta_j)
                total += count * log_prob 
            return -total
    
        result = minimize(
            fun=bt_neg_log_likelihood, 
            x0=np.zeros(self.n_items), # initialize theta
            method='L-BFGS-B'
        )
        # Return dictionary mapping item IDs to theta values
        return {item: result.x[idx] for item, idx in items_idx.items()}
    
    def get_energy(self, ordering:np.ndarray) -> float:
        if self.method == 'BT':
            return bt_energy_numba(ordering, self.theta_keys, self.theta_values)
        elif self.method == 'Pairwise':
            return pairwise_energy_numba(ordering, self.weights_keys, self.weights_values)
        else:
            return mallows_energy_numba(ordering, self.central_ranking, self.dist_metric, self.mallows_temperature)
    
    def sample_one(self) -> np.ndarray:
        """Sample one ordering using numba-optimized MCMC"""
        # # If mallows, no need to sample; as central ranking is the sampled result
        # if 'Mallows' in self.method:
        #     return self.central_ranking
        
        # Start with random permutation of unique elements
        initial_ordering = self.rng.permutation(self.unique_elements).astype(np.int64)
        
        method_code = {'Pairwise': 0, 'Mallows_Tau': 1, 'Mallows_RMJ':2, 'BT': 3}[self.method]
        
        # Prepare dummy parameters for unused methods
        # dummy (correctly typed)
        weights_keys   = np.zeros((1, 2), dtype=np.int64)
        weights_values = np.zeros(1, dtype=np.float64)
        theta_keys     = np.zeros(1, dtype=np.int64)
        theta_values   = np.zeros(1, dtype=np.float64)
        central_ranking = np.zeros(1, dtype=np.int64)

        # Set up parameters based on method
        if self.method == 'Pairwise':
            weights_keys = self.weights_keys
            weights_values = self.weights_values
        elif self.method == 'BT':
            theta_keys = self.theta_keys
            theta_values = self.theta_values
        else:
            central_ranking = self.central_ranking

        # Call numba-optimized function
        result = mcmc_sample(
            initial_ordering,
            self.iterations,
            self.n_shuffle,
            method_code,
            weights_keys, weights_values,
            theta_keys, theta_values,
            central_ranking,
            self.mallows_temperature,
            self.rng
        )
        return result

    def get_sampled_combined_orderings(self):
        """Generate multiple samples"""
        for idx in range(self.sample_count):
            order = self.sample_one()
            self.sampled_combined_orderings[idx, :] = order
            self.sampled_energies[idx] = self.get_energy(order)

    def compute_alignment_and_determinism(self):
        # those sampled are using the original random IDs, not indices
        if np.sum(self.sampled_combined_orderings[0]) == 0:
            self.get_sampled_combined_orderings()

        # Calculate aggrank_agreement: how stable is the full ranking generation
        rank_matrix = rankings_to_matrix(self.sampled_combined_orderings)
        self.aggrank_agreement = kendalls_w(rank_matrix)

        # check model validity (that random perms with lower energies should be closer to sampled perms/full rankings)
        random_perms = np.array([self.rng.permutation(self.unique_elements) for _ in range(self.n_random_perms)])
        self.random_perms = random_perms 

        # calculate random perm energies
        # we need to redo central ranking sampling. this is because in real mh, you won't know the
        # central ranking we used to get sampled combined orderings
        ori_method = self.method
        self.method = 'BT'
        self._prepare_method_data()
        self.central_ranking = self.sample_one()
        self.method = ori_method # change back to Mallows method

        self.random_perm_energies = np.zeros(len(random_perms), dtype=np.float64)
        for i, random_perm in enumerate(random_perms):
            self.random_perm_energies[i] = self.get_energy(random_perm)
        
        self.aggrank_dependence = auroc_from_energies(y=self.sampled_energies, x=self.random_perm_energies)

    def check_model_validity(self):
        # need to have random_perms and sampled_combined_orderings first
        if self.aggrank_dependence is None:
            self.compute_alignment_and_determinism()
        # the tau array. taus[i] is the average tau beween random_perms[i] and self.sampled_combined_orderings
        self.random_perm_taus, _ = get_average_tau(self.random_perms, self.sampled_combined_orderings)
        self.spearman_rho, self.spearman_p = spearmanr(self.random_perm_taus, self.random_perm_energies)