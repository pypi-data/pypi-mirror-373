from typing import List, Tuple, Dict, Set
import numpy as np
from collections import defaultdict, deque, Counter
from scipy.stats import kendalltau
from scipy.optimize import minimize
from itertools import combinations

EPSILON = 1e-12

def compute_conflict2(ordering_array: List[List[str]]) -> float:
    total = 0
    K = len(ordering_array)

    for i in range(K-1):
        for j in range(i+1, K):

            ordering1 = ordering_array[i]
            ordering2 = ordering_array[j]

            # find common 
            common_items = sorted(set(ordering1) & set(ordering2))
            if len(common_items) < 2:
                continue 

            # Build ranking dicts for each ordering
            rank1 = {item: rank for rank, item in enumerate(ordering1) if item in common_items}
            rank2 = {item: rank for rank, item in enumerate(ordering2) if item in common_items}

            r1 = [rank1[item] for item in common_items]
            r2 = [rank2[item] for item in common_items]

            tau, _ = kendalltau(r1, r2)
            total += (1-tau)/2
    return 2/(K * (K-1)) * total if K > 1 else 0.0

def compute_conflict(ordering_array: np.ndarray) -> float:
    conflict_pairs = 0
    total_pairs = 0
    # common items
    all_items = sorted(set(item for ordering in ordering_array for item in ordering))

    # compare each pair (a, b)
    for a, b in combinations(all_items, 2):
        pair_orders = []
        for ordering in ordering_array:
            ordering = list(ordering)
            if a in ordering and b in ordering:
                # record 1 if a before b, 0 if b before a
                pair_orders.append(ordering.index(a) < ordering.index(b))
        if len(pair_orders) >= 2:
            total_pairs += 1
            if any(v != pair_orders[0] for v in pair_orders[1:]):
                conflict_pairs += 1
    
    return conflict_pairs/total_pairs if total_pairs > 0 else 0.0

def rankings_to_matrix(rankings):
    """
    Convert a list of rankings (list of lists of strings) into 
    a NumPy integer matrix for Kendall's W calculation.

    Parameters
    ----------
    rankings : list of lists
        Each inner list is a ranking (same items, different order).

    Returns
    -------
    np.ndarray
        Shape (n_raters, n_items) integer rank matrix.
        Ranks start at 1 (best) and go to n_items (worst).
    """
    # the list that stays the same
    # we want to get the indices according to this benchmark list
    benchmark_list = list(rankings[0])

    # Step 2: Convert each ranking to integer ranks
    int_rankings = []
    for ranking in rankings:
        index_map = {item: idx for idx, item in enumerate(ranking)}
        result = [index_map[item] for item in benchmark_list]
        int_rankings.append(result)

    return np.array(int_rankings)

def kendalls_w(rank_matrix: np.ndarray):
    """
    Compute Kendall's W (coefficient of concordance) for complete rankings without ties.

    Parameters
    ----------
    rank_matrix : ndarray of shape (n_raters, n_items)
        Each row is a rater's ranking of the items (1 = best, n_items = worst).
        All rankings must be complete permutations of 1..n_items.

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

def get_partial_orders(
        n_partial_rankings: int,
        lengths: List[int],
        params:Dict[str, Dict[str, float]], 
        rng: np.random.Generator
    ) -> np.ndarray:
    # Get partial rankings based on params dict
    bms = list(params.keys())
    res = []
    for idx in range(n_partial_rankings):
        partial_ranking = rng.choice(bms, size=lengths[idx], replace=False)
        res.append(partial_ranking)
    return np.array(res, dtype=object)

def get_combined_order(
        params:Dict[str, Dict[str, float]], 
        low_num: int, # lowest possible number of partial rankings
        high_num:int,
        low_length:int, # lowest possible length of each partial ranking
        high_length:int, 
        rng: np.random.Generator,
        method:str,
        mcmc_iterations:int
    ) -> Tuple[List[str], List[List[str]]]:
    # # Get one sample combined ordering based on MCMC sampling
    # rng = np.random.default_rng(seed)

    n_partial_rankings = rng.integers(low_num, high_num + 1)
    # partial ranking length does not have to be unique, so replace=True
    lengths = rng.choice(np.arange(low_length, high_length), size=n_partial_rankings, replace=True)
    unique_rankings = np.array([])
    # to make sure no two partial orderings are the same
    while len(unique_rankings) != n_partial_rankings:
        partial_rankings = get_partial_orders(n_partial_rankings, lengths, params, rng)
        # Convert each sub-array to a tuple for hashability
        unique_rankings = np.array(list(set(tuple(row) for row in partial_rankings)), dtype=object)

    # get combined ordering
    if method != 'PL':
        mpebm_mcmc_sampler = MCMC(ordering_array=unique_rankings, rng=rng, method=method, iterations=mcmc_iterations)
        combined_order = mpebm_mcmc_sampler.sample_one()
    else:
        pl_sampler = PlackettLuce(ordering_array=unique_rankings, rng=rng)
        combined_order = pl_sampler.sample_one()

    return combined_order, unique_rankings

def get_final_params(
        params:Dict[str, Dict[str, float]], 
        combined_ordering:List[str], 
        ordering_array:List[List[str]]
    ) -> Dict[str, Dict[str, float]]:
    """
    1. use the combined ordering
    2. for biomarkers that appear in more than one ordering, we need to modify its parameters. 
    """
    final_params = {}
    flattend_ordering_array = [item for sublist in ordering_array for item in sublist]
    frequency_dict = dict(Counter(flattend_ordering_array))

    for bm in combined_ordering:
        final_params[bm] = params[bm].copy()
        if frequency_dict[bm] > 1:
            final_params[bm]['theta_mean'] /= 0.9 
            final_params[bm]['theta_std'] /= 1.2

    return final_params

class PlackettLuce:
    def __init__(self, ordering_array: np.ndarray, rng: np.random.Generator, sample_count:int=200):
        self.ordering_array = ordering_array
        self.sample_count = sample_count # how many to sample for conflict and certainty calculation
        self.unique_elements: List[str] = list(set(
            [item for sublist in self.ordering_array for item in sublist]))
        self.items_idx = {item: idx for idx, item in enumerate(self.unique_elements)}
        self.theta = np.zeros(len(self.unique_elements))
        self.theta_dict = {}
        self.sampled_combined_orderings = []
        self.rng = rng
        self.estimate_pl_theta()

    def pl_neg_log_likelihood(self, theta:np.ndarray) -> float:
        # We are multiplying all the total likelihood of each partial ordering
        # but since we are using log, we add them up
        # since optimizers only minimizes, we take the negative. 
        total = 0.0 
        for ordering in self.ordering_array:
            remaining = deque(ordering)
            while remaining:
                logits = np.array([theta[self.items_idx[item]] for item in remaining])
                max_logit = np.max(logits)
                log_denom = max_logit + np.log(np.sum(np.exp(logits - max_logit)))
                chosen = remaining.popleft()
                theta_i = theta[self.items_idx[chosen]]
                total += - (theta_i - log_denom)
        return total 
    
    def estimate_pl_theta(self):
        result = minimize(
            fun = self.pl_neg_log_likelihood,
            x0=self.theta,
            method = 'L-BFGS-B'
        )
        if not result.success:
            print("Warning: optimization failed:", result.message)
        self.theta = result.x
        self.theta_dict = {
            item: self.theta[idx] for item, idx in self.items_idx.items()
        }
    
    def pl_energy(self, ordering:np.array) -> float:
        total_energy = 0.0 
        remaining = deque(ordering)
        while remaining:
            logits = np.array([self.theta[self.items_idx[item]] for item in remaining])
            max_logit = np.max(logits)
            log_denom = max_logit + np.log(np.sum(np.exp(logits - max_logit)))
            chosen = remaining.popleft()
            total_energy += - (self.theta_dict[chosen] - log_denom)
        return total_energy
    
    def sample_one(self) -> List[str]:
        res = []
        remaining: List[str] = list(self.unique_elements)
        while remaining:
            logits = np.array([self.theta[self.items_idx[item]] for item in remaining])
            max_logit = np.max(logits)
            exp_logits = np.exp(logits - max_logit)  # log-sum-exp trick
            probs = exp_logits / np.sum(exp_logits)
            chosen_index = self.rng.choice(len(remaining), p=probs)
            res.append(remaining[chosen_index])
            del remaining[chosen_index]
        return res 
    
    def get_sampled_combined_orderings(self):
        for _ in range(self.sample_count):
            self.sampled_combined_orderings.append(self.sample_one())
    
    def compute_certainty(self) -> float:
        if not self.sampled_combined_orderings:
            self.get_sampled_combined_orderings()
        rank_matrix = rankings_to_matrix(self.sampled_combined_orderings)
        return kendalls_w(rank_matrix)
        

class PairwisePrefences:
    """
    Calculates pairwise preference weights from a list of partial orderings.

    This class is responsible for computing the weights 'w_ij' which represent the
    aggregated preference for item 'i' to appear before item 'j' across all
    provided partial orderings.
    """
    def __init__(self, ordering_array: np.ndarray):
        """
        Initializes the class with the input orderings.

        Args:
            ordering_array: A list of lists, where each inner list is a
                            partial ordering of items (strings).
        """
        self.ordering_array=ordering_array
        self.unique_elements: Set[str]=set(
            [item for sublist in self.ordering_array for item in sublist])
        self.weights: Dict[Tuple[str, str], int]=defaultdict(int)

    def obtain_weights(self):
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

                    # Increment weight for i preceding j
                    weights[(item1, item2)] += 1
                    # Decrement weight for j preceding i
                    weights[(item2, item1)] -= 1
        self.weights=weights

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
            iterations: int=1000,
            n_shuffle: int=2,
            rng: np.random.Generator=None,
            method: str='Mallows',
            sample_count:int=200,
        ):
        """
        Initializes the MCMC sampler.

        Args:
            ordering_array: The list of partial orderings.
            iterations: The number of MCMC iterations to perform.
            n_shuffle: The number of items to swap in each proposal step.
                       The paper suggests a swap of 2 items.
            method: choose from 'Mallows', 'Pairwise', 'BT'
        """
        # 1. Calculate the preference weights from the input data.
        self.method=method
        self.ordering_array =ordering_array
        self.unique_elements: List[str] = list(set(
            [item for sublist in self.ordering_array for item in sublist]))
        self.sampled_combined_orderings = []
        self.sample_count = sample_count

        if self.method == 'Pairwise':
            pairwise_prefs=PairwisePrefences(ordering_array)
            pairwise_prefs.obtain_weights()
            self.weights=pairwise_prefs.weights

        # For BT or PL
        self.items_idx = {item: idx for idx, item in enumerate(self.unique_elements)}
        self.theta = np.zeros(len(self.unique_elements))
        self.theta_dict = {}
        
        # Buil matrix for BT model
        if self.method == 'BT':
            self.BTCounts = defaultdict(int)

            for ordering in self.ordering_array:
                for i in range(len(ordering)):
                    for j in range(i+1, len(ordering)):
                        self.BTCounts[(ordering[i], ordering[j])] += 1 # item i before j
            self.estimate_bt_theta()

        self.rng=rng
        # The result is a numpy array of strings
        self.initial_random_ordering=self.rng.permutation(self.unique_elements)
        self.iterations=iterations
        self.n_shuffle=n_shuffle
    
    def bt_neg_log_likelihood(self, theta:np.ndarray) -> float:
        total = 0
        for (i, j), count in self.BTCounts.items():
            i_idx = self.items_idx[i]
            j_idx = self.items_idx[j]
            theta_i = theta[i_idx]
            theta_j = theta[j_idx]
            log_prob = log_prob = theta_i - np.logaddexp(theta_i, theta_j)
            total += count * log_prob 
        return -total 
    
    def estimate_bt_theta(self):
        result = minimize(
            fun=self.bt_neg_log_likelihood, 
            x0=self.theta,
            method='L-BFGS-B'
        )
        self.theta = result.x 
        self.theta_dict = {
            item: self.theta[idx] for item, idx in self.items_idx.items()
        }

    def obtain_energy_pairwise(self, ordering: np.array) -> float:
        """
        Calculates the energy E(σ) of a given ordering.

        The energy is defined as E(σ) = -Σ w_ij * 1[i <_σ j], where 1[i <_σ j]
        is 1 if i precedes j in the ordering σ, and 0 otherwise.

        Args:
            ordering: A numpy array representing a total ordering σ.

        Returns:
            The calculated energy of the ordering.
        """
        total_sum=0
        for i in range(0, len(ordering) - 1):
            for j in range(i+1, len(ordering)):
                # Sum the weights for all pairs (i, j) where i precedes j
                total_sum += self.weights[(ordering[i], ordering[j])]
        return -total_sum

    def obtain_energy_mallows(self, ordering: np.array) -> float:
        tau_distance_sum = 0
        for partial_ordering in self.ordering_array:
            # select items present in partial_ordering
            filtered = [x for x in ordering if x in partial_ordering]
            dic = dict(zip(partial_ordering, range(len(partial_ordering))))
            x = [dic[x] for x in partial_ordering]
            y = [dic[x] for x in filtered]
            tau_corr, p = kendalltau(x, y)
            n_common = len(filtered)
            max_discordant_pairs = n_common * (n_common - 1) / 2
            tau_distance = (1-tau_corr)/2*max_discordant_pairs
            tau_distance_sum += tau_distance
        return tau_distance_sum
    
    def bt_energy(self, ordering:np.array) -> float:
        total_energy = 0.0
        for i in range(len(ordering)):
            for j in range(i+1, len(ordering)):
                theta_i = self.theta_dict[ordering[i]]
                theta_j = self.theta_dict[ordering[j]]
                prob_ij = np.exp(theta_i) / (np.exp(theta_i) + np.exp(theta_j))
                total_energy += - np.log(prob_ij)
        return total_energy
            
    def shuffle_order(
            self, arr: np.ndarray, n_shuffle: int, rng: np.random.Generator) -> None:
        """
        Proposes a new ordering (σ') by shuffling elements in the current one.
        This is a proposal mechanism for the MCMC algorithm.
        """
        # (Your existing shuffle logic is valid and left unchanged)
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

    def sample_one(self) -> np.ndarray:
        """
        Runs the Metropolis-Hastings MCMC sampler to get a final ordering.

        Returns:
            A numpy array representing the final sampled total ordering.
        """
        all_orders = []
        all_energies = []
        # Start with the initial random permutation
        current_order=self.initial_random_ordering
        # Calculate its energy
        if self.method == 'Pairwise':
            current_energy=self.obtain_energy_pairwise(current_order)
        if self.method == 'Mallows':
            current_energy=self.obtain_energy_mallows(current_order)
        if self.method == 'BT':
            current_energy = self.bt_energy(current_order)

        # Loop for T iterations
        for _ in range(self.iterations):
            all_orders.append(current_order)
            all_energies.append(current_energy)

            # Propose a new ordering σ' by swapping elements
            new_order=current_order.copy()
            self.shuffle_order(new_order, self.n_shuffle, self.rng)
            if self.method == 'Pairwise':
                new_energy=self.obtain_energy_pairwise(new_order)
            if self.method == 'Mallows':
                new_energy=self.obtain_energy_mallows(new_order)
            if self.method == 'BT':
                new_energy = self.bt_energy(new_order)

            # Calculate the acceptance probability, α = min(1, P(σ')/P(σ)).
            # P(σ')/P(σ) = exp(-E(σ')) / exp(-E(σ)) = exp(E(σ) - E(σ'))
            delta_energy = current_energy - new_energy
            if delta_energy > 700:  # Safe threshold for float64
                prob_accept = 1.0
            else:
                prob_accept = min(1.0, np.exp(delta_energy))

            # Accept the new ordering with probability α
            if self.rng.random() < prob_accept:
                current_order=new_order
                current_energy=new_energy

        # retrieve the order with the lowest energy
        self.final_ordering= all_orders[all_energies.index(min(all_energies))]
        return self.final_ordering
    
    def get_sampled_combined_orderings(self):
        for _ in range(self.sample_count):
            self.sampled_combined_orderings.append(self.sample_one())
    
    def compute_certainty(self) -> float:
        if not self.sampled_combined_orderings:
            self.get_sampled_combined_orderings()
        rank_matrix = rankings_to_matrix(self.sampled_combined_orderings)
        return kendalls_w(rank_matrix)
