
def optimize_differential_evolution(bounds, optimize_function, optimize_args, init_guess=None, maxiter=100, popsize=5, seed=42):
    """
    Use differential evolution for global optimization to find good initial parameters.
    
    Parameters:
    -----------
    bounds : list of tuples
        List of (min, max) bounds for each parameter
    optimize_function : callable
        Function to minimize, should return RMSE/objective value
    optimize_args : tuple
        Additional arguments to pass to optimize_function
    init_guess : list, optional
        Initial guess (will be included in population if provided)
    maxiter : int, default=1000
        Maximum number of iterations
    popsize : int, default=15
        Population size multiplier (total population = popsize * len(bounds))
    seed : int, default=42
        Random seed for reproducibility
        
    Returns:
    --------
    best_params : list
        Best parameters found
    best_rmse : float
        Best RMSE/objective value found
    """
    from scipy.optimize import differential_evolution
    
    # Convert bounds to format expected by differential_evolution
    # Handle fixed parameters (where low == high)
    bounds_array = []
    fixed_params = {}
    variable_indices = []
    
    for i, (low, high) in enumerate(bounds):
        if low == high:
            fixed_params[i] = low
        else:
            bounds_array.append((low, high))
            variable_indices.append(i)
    
    if not bounds_array:
        # All parameters are fixed
        if init_guess is not None:
            rmse = optimize_function(init_guess, *optimize_args)
            return list(init_guess), rmse
        else:
            params = [bounds[i][0] for i in range(len(bounds))]
            rmse = optimize_function(params, *optimize_args)
            return params, rmse
    
    def objective_wrapper(x_variable):
        """Wrapper to handle fixed parameters"""
        # Reconstruct full parameter vector
        x_full = [0.0] * len(bounds)
        
        # Set fixed parameters
        for idx, val in fixed_params.items():
            x_full[idx] = val
            
        # Set variable parameters
        for i, idx in enumerate(variable_indices):
            x_full[idx] = x_variable[i]

        return optimize_function(x_full, *optimize_args)
    print(bounds_array)
    # Prepare initial guess for variable parameters only
    # init_variable = None
    # if init_guess is not None:
    #     init_variable = [init_guess[i] for i in variable_indices]
    
    result = differential_evolution(
        objective_wrapper,
        bounds_array,
        maxiter=maxiter,
        popsize=popsize,
        seed=seed,
        atol=1e-6,
        tol=1e-6,
        polish=False,
        init='latinhypercube',  # Good initialization strategy
        updating='immediate',    # Often more robust
        workers=1              # Set to -1 for parallel processing if needed
    )
    
    # Reconstruct full parameter vector
    best_params_full = [0.0] * len(bounds)
    for idx, val in fixed_params.items():
        best_params_full[idx] = val
    for i, idx in enumerate(variable_indices):
        best_params_full[idx] = result.x[i]
            
    if not result.success:
        print(f"Optimization failed: {result.message}")
    return best_params_full, result.fun
            

def optimize_coordinate_descent(bounds, optimize_function, optimize_args, init_guess=None, 
                                points=20, max_iterations=3):
    """
    Coordinate descent optimization: optimize one parameter at a time in specified order.
    
    Parameters:
    -----------
    bounds : list of tuples
        List of (min, max) bounds for each parameter
    optimize_function : callable
        Function to minimize, should return RMSE/objective value
    optimize_args : tuple
        Additional arguments to pass to optimize_function
    init_guess : list, optional
        Initial guess for all parameters
    parameter_map : dict
        Dictionary mapping parameter names to indices
    points : int, default=20
        Number of points to evaluate for each parameter
    max_iterations : int, default=3
        Number of complete cycles through all parameters
        
    Returns:
    --------
    best_params : list
        Best parameters found
    best_rmse : float
        Best RMSE/objective value found
    """
    
    # Parameter optimization order
    param_order = ['gamma_offset', 'omega_offset', 'alpha', 'delta', 'beta', 'epsilon']
    
    # Initialize with provided guess or bounds midpoint
    if init_guess is not None:
        current_params = list(init_guess)
    else:
        current_params = []
        for low, high in bounds:
            if low == high:
                current_params.append(low)
            else:
                current_params.append((low + high) / 2.0)
    
    # Get current best RMSE
    best_rmse = optimize_function(current_params, *optimize_args)
    best_params = current_params.copy()
    
    total_function_calls = 1  # Count the initial evaluation
    
    print(f"Initial RMSE: {best_rmse:.6f}")
    
    # Iterate through multiple cycles
    for iteration in range(max_iterations):
        print(f"\nIteration {iteration + 1}/{max_iterations}")
        improved_this_iteration = False
        
        # Go through each parameter in specified order
        for param_name in param_order:
            if param_name not in SCANNER_PARAMETER_MAP:
                continue  # Skip if parameter not in map
                
            param_idx = SCANNER_PARAMETER_MAP[param_name]
            
            # Skip if parameter is fixed
            low, high = bounds[param_idx]
            if low == high:
                continue
            
            print(f"  Optimizing {param_name} (index {param_idx})")
            
            # Create test values for this parameter
            test_values = np.linspace(low, high, points)
            
            best_value_for_param = current_params[param_idx]
            best_rmse_for_param = best_rmse
            
            # Test each value for this parameter
            for test_value in test_values:
                # Create test parameter vector
                test_params = current_params.copy()
                test_params[param_idx] = test_value
                
                # Evaluate
                rmse = optimize_function(test_params, *optimize_args)
                total_function_calls += 1
                
                # Update if better
                if rmse < best_rmse_for_param:
                    best_rmse_for_param = rmse
                    best_value_for_param = test_value
            
            # Update current parameters if improvement found
            if best_rmse_for_param < best_rmse:
                old_value = current_params[param_idx]
                current_params[param_idx] = best_value_for_param
                improvement = best_rmse - best_rmse_for_param
                best_rmse = best_rmse_for_param
                best_params = current_params.copy()
                improved_this_iteration = True
                
                print(f"    {param_name}: {old_value:.6f} -> {best_value_for_param:.6f} "
                      f"(RMSE: {best_rmse:.6f}, improvement: {improvement:.6f})")
            else:
                print(f"    {param_name}: no improvement (current: {current_params[param_idx]:.6f})")
        
        # Early stopping if no improvement in this iteration
        if not improved_this_iteration:
            print(f"  No improvement in iteration {iteration + 1}, stopping early")
            break
    
    print(f"\nCoordinate descent completed:")
    print(f"  Total function calls: {total_function_calls}")
    print(f"  Final RMSE: {best_rmse:.6f}")
    
    return best_params, best_rmse
