"""
Core functions for SNP package.

This module contains the main implementation of:
- construct_W: Construct Gaussian kernel weight matrix
- DGCV: Direct Generalized Cross-Validation 
- SNP: Stepwise Noise Peeling algorithm
"""

import numpy as np
import time
import warnings
import gc


def construct_W(x, h):
    """
    Construct Normalized Gaussian Kernel Weight Matrix
    
    Constructs a row-stochastic weight matrix for Nadaraya-Watson regression
    using Gaussian kernels with specified bandwidth.
    
    Parameters
    ----------
    x : array-like
        Numeric vector of predictor values.
    h : float
        Bandwidth parameter for the Gaussian kernel.
        
    Returns
    -------
    numpy.ndarray
        A matrix W where W[i,j] represents the weight given to observation j
        when predicting at point x[i]. Each row sums to 1 (row-stochastic property).
        
    Notes
    -----
    The function computes a Gaussian kernel weight matrix where:
    K(x_i, x_j) = (1/sqrt(2*pi)) * exp(-(x_i - x_j)^2 / (2*h^2))
    
    Each row is then normalized so that the weights sum to 1, making the matrix
    row-stochastic. This ensures that the Nadaraya-Watson estimator is a proper
    weighted average.
    
    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> h = 0.5
    >>> W = construct_W(x, h)
    >>> # Check row sums (should all be 1)
    >>> print(np.sum(W, axis=1))
    """
    
    # Convert to numpy arrays
    x = np.asarray(x)
    
    # Input validation
    if np.any(np.isnan(x)):
        raise ValueError("x cannot contain NA values")
    if not isinstance(h, (int, float)) or h <= 0:
        raise ValueError("h must be a positive scalar")
    
    n = len(x)
    
    # Compute pairwise differences
    dist_mat = np.subtract.outer(x, x)
    
    # Apply Gaussian kernel
    # Using 0.3989423 ≈ 1/sqrt(2*π) for computational efficiency
    K_mat = 0.3989423 * np.exp(-0.5 * (dist_mat / h)**2)
    
    # Normalize each row so rows sum to 1 (row-stochastic property)
    row_sums = np.sum(K_mat, axis=1)
    
    # Avoid division by zero (though this should rarely happen with Gaussian kernels)
    if np.any(row_sums == 0):
        warnings.warn("Some rows have zero sum. This may indicate bandwidth is too small.")
        row_sums[row_sums == 0] = 1
    
    # Return normalized matrix
    return K_mat / row_sums[:, np.newaxis]


def DGCV(x, y, num_h_points=50):
    """
    Direct Generalized Cross-Validation for Nadaraya-Watson Regression
    
    Implements Direct Generalized Cross-Validation (DGCV) for bandwidth selection
    in Nadaraya-Watson regression with Gaussian kernels. This is the traditional
    reference method that SNP aims to approximate efficiently.
    
    Parameters
    ----------
    x : array-like
        Numeric vector of predictor values (sorted).
    y : array-like 
        Numeric vector of response values corresponding to x.
    num_h_points : int, optional
        Number of bandwidth candidates to evaluate across the continuous 
        bandwidth space (default: 50).
        
    Returns
    -------
    dict
        A dictionary containing:
        - 'y_h_opt': Final smoothed output using optimal bandwidth
        - 'h_opt_gcv': Optimal bandwidth selected by GCV
        - 'gcv_h': GCV scores for all bandwidth candidates
        - 'time_elapsed': Execution time in seconds
        
    Notes
    -----
    DGCV performs an exhaustive search over a continuous bandwidth space,
    evaluating the GCV criterion for each candidate bandwidth. While statistically
    rigorous, this approach becomes computationally prohibitive for large datasets
    due to the need to construct and evaluate the full smoothing matrix for each
    bandwidth candidate.
    
    The bandwidth search range is determined using Silverman's rule of thumb,
    with candidates uniformly distributed between 0.1% and 100% of the
    Silverman bandwidth.
    
    Examples
    --------
    >>> import numpy as np
    >>> np.random.seed(123)
    >>> n = 100
    >>> x = np.sort(np.random.uniform(0, 1, n))
    >>> y = np.sin(2*np.pi*x) + np.random.normal(0, 0.1, n)
    >>> result = DGCV(x, y)
    """
    
    start_time = time.time()
    
    # Convert to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)
    
    # Input validation
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise ValueError("x and y cannot contain NA values")
    if num_h_points <= 0:
        raise ValueError("num_h_points must be positive")
    
    n = len(x)
    
    # Bandwidth range based on Silverman's rule
    h_s = 1.06 * np.std(x) * n**(-1/5)
    h_min = 0.001 * h_s
    h_max = 1 * h_s
    h_candidates = np.linspace(h_min, h_max, num_h_points)
    
    print("-------------Start (DGCV)-------------")
    print(f"h_candidates: [{h_min:.4f} , {h_max:.4f}]")
    
    # Initialize containers for results
    yk_list = []        # Store smoothed outputs for each h
    gcv_h = np.zeros(len(h_candidates))       # Store GCV scores for each h
    
    # Loop over all bandwidth candidates
    for i, h in enumerate(h_candidates):
        W = construct_W(x, h)          # Construct Gaussian kernel weight matrix
        yhat = W @ y                   # Apply smoothing
        gcv_h[i] = np.sum((y - yhat)**2) / ((1 - np.sum(np.diag(W)) / n)**2)  # GCV score
        yk_list.append(yhat.copy())    # Save smoothed result
    
    # Select h that minimizes GCV
    inds_min = np.argmin(gcv_h)
    h_opt_gcv = h_candidates[inds_min]
    
    elapsed = time.time() - start_time
    
    # Print summary for the user
    print("\n--- Original GCV Smoothing Summary ---")
    print("h_opt_gcv:", h_opt_gcv)
    print("time_elapsed:", elapsed)
    print("-------------End (DGCV)-------------")
    
    gc.collect()  # Trigger garbage collection
    
    # Return the best result and associated values
    return {
        'y_h_opt': yk_list[inds_min].copy(),  # Final smoothed output
        'h_opt_gcv': h_opt_gcv,               # Optimal bandwidth
        'gcv_h': gcv_h,                       # All GCV scores
        'time_elapsed': elapsed               # Elapsed time in seconds
    }


def SNP(x, y):
    """
    Stepwise Noise Peeling for Nadaraya-Watson Regression
    
    Implements the Stepwise Noise Peeling (SNP) algorithm that bypasses 
    bandwidth selection in Nadaraya-Watson regression by using iterative 
    smoothing. SNP provides a scalable alternative to Direct Generalized 
    Cross-Validation (DGCV) by avoiding continuous bandwidth optimization.
    
    Parameters
    ----------
    x : array-like
        Numeric vector of predictor values (sorted).
    y : array-like
        Numeric vector of response values corresponding to x.
        
    Returns
    -------
    dict
        A dictionary containing:
        - 'y_k_opt': Final smoothed output vector
        - 'h_start': Final chosen initial bandwidth
        - 'k_opt': Optimal number of iterations
        - 'gcv_approx_k': GCV values for each iteration
        - 'time_elapsed': Execution time in seconds
        
    Notes
    -----
    The SNP algorithm operates in two phases:
    
    Phase I: Constructs a conservative initial bandwidth using random 
      slices of data and lightweight GCV within each slice
    Phase II: Fixes the smoothing operator and repeatedly applies it, 
      selecting optimal iterations via discrete GCV
    
    The algorithm converts costly continuous bandwidth search into lightweight 
    discrete selection, reducing runtime by orders of magnitude while yielding
    estimates statistically equivalent to DGCV.
    
    Examples
    --------
    >>> import numpy as np
    >>> np.random.seed(123)
    >>> n = 100
    >>> x = np.sort(np.random.uniform(0, 1, n))
    >>> y = np.sin(2*np.pi*x) + np.random.normal(0, 0.1, n)
    >>> result = SNP(x, y)
    """
    
    start_time = time.time()
    
    # Convert to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)
    n = len(x)
    
    num_h_points = 40
    num_slices = 60
    k_max = 10
    
    # Input validation
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise ValueError("x and y cannot contain NA values")
    
    # Initial bandwidth range based on Silverman's rule of thumb
    h_s = 1.06 * np.std(x) * n**(-1/5)
    # Lower bound for bandwidth: ensures W is not too sparse
    h_min = 0.001 * h_s
    # Upper bound for bandwidth: standard Silverman bandwidth
    h_max = 1 * h_s
    
    print("-------------Start (SNP)-------------")
    print(f"h_candidates: [{h_min:.4f} , {h_max:.4f}]")
    
    # Determine slice size based on sample size
    min_slice = 50
    
    if n < min_slice:
        slice_size = n
    else:
        slice_size = int(max(min_slice, np.sqrt(n * np.log(n))))
    
    # Randomly select starting indices for each slice
    start_indices = np.random.choice(n - slice_size + 1, num_slices, replace=True)
    slice_indices = [list(range(start_idx, start_idx + slice_size)) for start_idx in start_indices]
    
    # Internal function to compute optimal h for a given slice using GCV
    def compute_h_opt(idx):
        x_slice = x[idx]
        y_slice = y[idx]
        h_candidates = np.random.uniform(h_min, h_max, num_h_points)
        
        # Compute GCV for each h candidate
        gcv_scores = []
        for h in h_candidates:
            W_slice = construct_W(x_slice, h)
            y_hat = W_slice @ y_slice
            gcv_score = np.mean((y_slice - y_hat)**2) / ((1 - np.mean(np.diag(W_slice)))**2)
            gcv_scores.append(gcv_score)
        
        # Return the h with minimum GCV
        return h_candidates[np.argmin(gcv_scores)]
    
    # Apply to all slices
    h_opts = [compute_h_opt(idx) for idx in slice_indices]
    
    elapsed_h = time.time() - start_time
    start_time = time.time()
    
    # Use median of h_opt estimates as starting point
    h_start = 0.5 * np.median(h_opts)
    
    print("h_start:", h_start)
    print("summary h_opts:", f"Min: {np.min(h_opts):.4f}, 1st Qu.: {np.percentile(h_opts, 25):.4f}, Median: {np.median(h_opts):.4f}, Mean: {np.mean(h_opts):.4f}, 3rd Qu.: {np.percentile(h_opts, 75):.4f}, Max: {np.max(h_opts):.4f}")
    
    # Trace approximation function
    def trace_Wk(trWh, k, cap_one=True):
        val = 1 + (trWh - 1) / np.sqrt(k)
        return np.maximum(1, val) if cap_one else val
    
    # Adaptive h_start adjustment
    i0 = 1
    i0max = 15
    while i0 <= i0max:
        if i0 == i0max:
            print("Last chance for change h_start")
        
        # Initial weight matrix with h_start
        W = construct_W(x, h_start)
        trWh = np.sum(np.diag(W))
        
        # Apply initial smoothing
        yk = W @ y
        yk_list = []
        gcv_approx_k = np.zeros(k_max)
        traces = np.zeros(k_max)
        
        for k in range(1, k_max + 1):
            traces[k-1] = trace_Wk(trWh, k)
            gcv_approx_k[k-1] = np.sum((y - yk)**2) / ((1 - traces[k-1] / n)**2)
            yk_list.append(yk.copy())
            yk = W @ yk  # Apply one more smoothing iteration
        
        # Choose k (number of iterations) with lowest approximate GCV
        k_opt_idx = np.argmin(gcv_approx_k)
        k_opt = k_opt_idx + 1  # Convert to 1-based indexing
        
        if k_opt == 1:
            h_start = 0.5 * h_start
            i0 = i0 + 1
            print("new smaller h_start:", h_start)
        elif k_opt == k_max:
            h_start = 0.5 * np.sqrt(k_max) * h_start
            i0 = i0 + 1
            print("new bigger h_start:", h_start)
        else:
            i0 = i0max + 1
    
    elapsed_k = time.time() - start_time
    elapsed = elapsed_h + elapsed_k
    
    # Print summary
    print("\n--- Adaptive Smoothing Summary ---")
    print(f"time_elapsed_h: {elapsed_h}, time_elapsed_k: {elapsed_k}")
    print("h_start (final):", h_start)
    print("k_opt (final):", k_opt)
    print("k_max:", k_max)
    print("time_elapsed:", elapsed)
    print("-------------End (SNP)-------------")
    
    gc.collect()  # Trigger garbage collection
    
    # Return results
    return {
        'y_k_opt': yk_list[k_opt_idx].copy(),  # Final smoothed output
        'h_start': h_start,                    # Final chosen h
        'k_opt': k_opt,                        # Optimal iteration count
        'gcv_approx_k': gcv_approx_k,          # GCV values per iteration
        'time_elapsed': elapsed                # Elapsed time in seconds
    }