from tabnanny import verbose

import openturns as ot
import numpy as np



def pca_reconstruction_error(Y: np.array, n_components: int):
    from sklearn.decomposition import PCA
    import numpy as np

    """
    Computes PCA reconstruction error for a given number of principal components.

    Parameters
    ----------
    Y : array (K x N)
        Output samples of K runs with N datapoints.
    n_components : int
        Number of principal components to retain.

    Returns
    -------
    error_mean : float
        Mean relative reconstruction error across all samples.
    error_all : array (K,)
        Reconstruction error for each sample.
    """

    # Fit PCA
    pca = PCA(n_components=n_components)
    Z = pca.fit_transform(Y)          # Reduced coordinates
    Y_rec = pca.inverse_transform(Z)  # Reconstructed outputs

    # Compute relative reconstruction error for each sample
    error_all = np.linalg.norm(Y - Y_rec, axis=1) / np.linalg.norm(Y, axis=1)
    error_avg = np.mean(error_all)

    return error_avg, error_all



def train_PCE(X_train: ot.Sample, U_train: ot.Sample, total_degree: int, n_components: int = 3):
    from sklearn.decomposition import PCA
    import openturns as ot

    """
    Trains a Polynomial Chaos Expansion (PCE) surrogate model using PCA for dimensionality reduction
    Parameters
    ---------- 
    X_train : ot.Sample
        Training input samples.
    U_train : ot.Sample
        Training output samples.
    total_degree : int
        Total degree of the polynomial chaos expansion.
    n_components : int, optional
        Number of principal components to retain (default is 3).

    Returns
    -------
    pce_models : list
        List of trained PCE models for each PCA mode.
    pca : PCA
        Trained PCA model.
    results : list
        List of results from the FunctionalChaosAlgorithm for each PCA mode.
    """

    # Fit PCA to the training output samples and transform to sample type
    pca = PCA(n_components=n_components)
    U_modes = ot.Sample(pca.fit_transform(U_train))
    U_modes = ot.Sample(pca.fit_transform(U_train))
    distribution = ot.JointDistribution([ot.Normal(12E3, 3E3), 
                                         ot.Normal(58E3, 14.5E3), 
                                         ot.Normal(38.7, 2.0), 
                                         ot.Normal(35.4, 1.8)])

    # Define the polynomial basis, adaptive strategy and selection algorithm for PCE
    input_dim = distribution.getDimension()
    basis = ot.OrthogonalProductPolynomialFactory(
        [distribution.getMarginal(i) for i in range(input_dim)]
    )
    enumerate_function = basis.getEnumerateFunction()

    basis_size = enumerate_function.getBasisSizeFromTotalDegree(total_degree)
    adaptive_strategy = ot.FixedStrategy(basis, basis_size)

    selection_algo = ot.LeastSquaresMetaModelSelectionFactory()
    projection_strategy = ot.LeastSquaresStrategy(selection_algo)

    pce_models = []
    results = []
    for k in range(U_modes.getDimension()):
        y = U_modes[:, k]
        algo = ot.FunctionalChaosAlgorithm(
            X_train, y,
            distribution,
            adaptive_strategy,
            projection_strategy
        )
        algo.run()
        result = algo.getResult()
        results.append(algo.getResult())
        pce_models.append(result.getMetaModel())
    
    return pce_models, pca, results



def train_PCE_ps(X_train: ot.Sample, U_train: ot.Sample, total_degree: int, n_components: int = 3):
    import openturns as ot
    from sklearn.decomposition import PCA
    """
    Trains PCE models for each PCA mode using the provided training samples. for the parametric study

    Parameters
    ----------
    X_train : ot.Sample
        Training input samples.
    U_train : ot.Sample
        Training output samples.
    total_degree : int
        Total degree of the polynomial chaos expansion.
    n_components : int, optional
        Number of principal components to retain (default is 3).

    Returns
    -------
    pce_models : list
        List of trained PCE models for each PCA mode.
    pca : PCA
        Trained PCA model.
    results : list
        List of results from the FunctionalChaosAlgorithm for each PCA mode.
    """

    pca = PCA(n_components=n_components)
    U_modes = ot.Sample(pca.fit_transform(U_train))
    # print("Number of PCA modes:", U_modes.getDimension())
    U_modes = ot.Sample(pca.fit_transform(U_train))
    # distribution = ot.JointDistribution([ot.Normal(12E3, 3E3), ot.Normal(58E3, 14.5E3), ot.Normal(38.7, 2.0), ot.Normal(35.4, 1.8)])
    distribution = ot.JointDistribution([ot.Normal() for _ in range(X_train.getDimension())])

    input_dim = distribution.getDimension()
    basis = ot.OrthogonalProductPolynomialFactory(
        [distribution.getMarginal(i) for i in range(input_dim)]
    )
    enumerate_function = basis.getEnumerateFunction()

    basis_size = enumerate_function.getBasisSizeFromTotalDegree(total_degree)
    adaptive_strategy = ot.FixedStrategy(basis, basis_size)

    selection_algo = ot.LeastSquaresMetaModelSelectionFactory()
    projection_strategy = ot.LeastSquaresStrategy(selection_algo)

    pce_models = []
    results = []
    for k in range(U_modes.getDimension()):
        y = U_modes[:, k]
        algo = ot.FunctionalChaosAlgorithm(
            X_train, y,
            distribution,
            adaptive_strategy,
            projection_strategy
        )
        algo.run()
        result = algo.getResult()
        results.append(algo.getResult())
        pce_models.append(result.getMetaModel())
    return pce_models, pca, results



def predict_modes(x_new: np.ndarray, pce_models: list):
    import openturns as ot
    import numpy as np

    """
    Predicts the PCA mode coefficients for a new input sample using the trained PCE models.

    Parameters
    ----------
    x_new : array-like
        New input sample.
    pce_models : list
        List of trained PCE models for each PCA mode.

    Returns
    -------
    a_pred : array
        Predicted PCA mode coefficients.
    """

    x_new = ot.Sample([x_new])
    a_pred = [model(x_new)[0] for model in pce_models]

    return np.array(a_pred).T[0]



def predict_deformation(x_new, pca, pce_models):
    """
    Predicts the deformation for a new input sample using the trained PCE models and PCA.

    Parameters
    ----------
    x_new : array-like
        New input sample.
    pca : PCA
        Trained PCA model.
    pce_models : list
        List of trained PCE models for each PCA mode.

    Returns
    -------
    y_pred : array
        Predicted deformation.
    """

    a_pred = predict_modes(x_new, pce_models)
    # print("Predicted PCA coefficients for x_new:", a_pred.shape)

    return pca.inverse_transform([a_pred])[0]



def sobol_error_trials(n_trials: int, n_modes: int, n_degrees: int, X_raw, U, n_vars: int = 4):
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score
    import openturns as ot
    import numpy as np

    """
    Performs multiple trials of training and evaluating PCE models with PCA for different polynomial degrees.
    
    Parameters
    ----------
    n_trials : int
        Number of trials to perform.
    n_modes : int
        Number of PCA modes.
    n_degrees : int
        Maximum polynomial degree to consider.
    X_raw : array-like
        Input samples.
    U : array-like
        Output samples.

    Returns
    -------
    R2 : array
        R2 scores for each trial and polynomial degree.
    RMSE : array
        Root Mean Square Error for each trial and polynomial degree.
    GNAE : array
        Generalized Normalized Absolute Error for each trial and polynomial degree.
    sobol_first : list
        List of first-order Sobol index arrays for each mode and polynomial degree.
    sobol_total : list
        List of total-order Sobol index arrays for each mode and polynomial degree.
    """
    assert n_vars in [2, 4], "only implemented for 2 or 4 variables"
    # Define the list of polynomial degrees to evaluate
    degrees_list = np.arange(1, n_degrees + 1, 1).tolist()

    # Generate empty error arrays for RMSE, R2, and GNAE metrics
    RMSE = np.zeros((n_trials, n_degrees))
    R2 = np.zeros((n_trials, n_degrees))
    GNAE = np.zeros((n_trials, n_degrees))

    # Generate empty arrays for Sobol indices (first-order and total-order) for each mode and degree
    sobol_first_1 = np.zeros((n_trials, n_degrees, n_modes))
    sobol_first_2 = np.zeros((n_trials, n_degrees, n_modes))
    if n_vars > 2:
        sobol_first_3 = np.zeros((n_trials, n_degrees, n_modes))
        sobol_first_4 = np.zeros((n_trials, n_degrees, n_modes))

    sobol_total_1 = np.zeros((n_trials, n_degrees, n_modes))
    sobol_total_2 = np.zeros((n_trials, n_degrees, n_modes))
    if n_vars > 2:
        sobol_total_3 = np.zeros((n_trials, n_degrees, n_modes))
        sobol_total_4 = np.zeros((n_trials, n_degrees, n_modes))

    # Loop over the number of trials
    for trial in range(n_trials):
        # Generate training and testing sets and convert them to OpenTURNS Sample objects
        X_train_val, X_test_val, U_train_val, U_test_val = train_test_split(X_raw, U, test_size=0.2)
        X_train = ot.Sample(X_train_val)
        X_test = ot.Sample(X_test_val)
        U_train = ot.Sample(U_train_val)
        
        print(f"Trial {trial + 1}", end="\r")
        # Loop over the polynomial degrees to evaluate
        for n in degrees_list:
            # Train PCE models for the current degree
            if n_vars == 2:
                pce_models, pca, results = train_PCE_ps(X_train, U_train, total_degree=n)
            elif n_vars == 4:
                pce_models, pca, results = train_PCE(X_train, U_train, total_degree=n)
            R2_i = []
            RMSE_i = []
            GNAE_i = []

            # Loop over the test samples to evaluate the trained models
            for i in range(len(X_test)):
                # Predict the deformation for the current test sample
                Y_test_i = predict_deformation(X_test[i], pca, pce_models)
                
                R2_i.append(r2_score(U_test_val[i], Y_test_i))
                RMSE_i.append(np.sqrt(np.mean((U_test_val[i] - Y_test_i)**2)))

                num = np.abs(U_test_val[i] - Y_test_i)
                denom = U_test_val[i].max() - U_test_val[i].min()
                GNAE_i.append(num / denom * 100)

                for idx, result in enumerate(results):
                    sobol = ot.FunctionalChaosSobolIndices(result)
                
                    first_pce = [sobol.getSobolIndex(i) for i in range(X_train.getDimension())]
                    total_pce = [sobol.getSobolTotalIndex(i) for i in range(X_train.getDimension())]

                    sobol_first_1[trial, degrees_list.index(n), idx] = first_pce[0]  ## phi_A sobol
                    sobol_first_2[trial, degrees_list.index(n), idx] = first_pce[1]  ## phi_B sobol
                    if n_vars > 2:
                        sobol_first_3[trial, degrees_list.index(n), idx] = first_pce[2]  ## E_B sobol
                        sobol_first_4[trial, degrees_list.index(n), idx] = first_pce[3]  ## E_C sobol
                    sobol_total_1[trial, degrees_list.index(n), idx] = total_pce[0]  
                    sobol_total_2[trial, degrees_list.index(n), idx] = total_pce[1]
                    if n_vars > 2:
                        sobol_total_3[trial, degrees_list.index(n), idx] = total_pce[2]  
                        sobol_total_4[trial, degrees_list.index(n), idx] = total_pce[3]  

                R2[trial, degrees_list.index(n)] = np.mean(R2_i)
                RMSE[trial, degrees_list.index(n)] = np.mean(RMSE_i)
                GNAE[trial, degrees_list.index(n)] = np.mean(GNAE_i)

        if n_vars == 2:
            path = "logs/Parametric_Study_Surrogate/"
        elif n_vars == 4:
            path = "logs/Calibration_Surrogate/"
        np.savetxt(path + "R2.csv", R2, delimiter=",")
        np.savetxt(path + "RMSE.csv", RMSE, delimiter=",")
        np.savetxt(path + "GNAE.csv", GNAE, delimiter=",")

        np.save(path + "sobol_first_1.npy", sobol_first_1)
        np.save(path + "sobol_first_2.npy", sobol_first_2)
        if n_vars > 2:
            np.save(path + "sobol_first_3.npy", sobol_first_3)
            np.save(path + "sobol_first_4.npy", sobol_first_4)

        np.save(path + "sobol_total_1.npy", sobol_total_1)
        np.save(path + "sobol_total_2.npy", sobol_total_2)
        if n_vars > 2:
            np.save(path + "sobol_total_3.npy", sobol_total_3)
            np.save(path + "sobol_total_4.npy", sobol_total_4)

        sobol_first = [sobol_first_1, sobol_first_2]
        sobol_total = [sobol_total_1, sobol_total_2]
        if n_vars > 2:
            sobol_first.append(sobol_first_3)
            sobol_first.append(sobol_first_4)
            sobol_total.append(sobol_total_3)
            sobol_total.append(sobol_total_4)

    return R2, RMSE, GNAE, sobol_first, sobol_total



def test_model(pca, pce_models, X_test_val, U_test_val, Z, U_meas):
    import matplotlib.pyplot as plt
    from sklearn.metrics import r2_score
    import numpy as np

    """
    Tests the trained PCE models with PCA on a test set and plots the predicted vs. actual deformations.
    Parameters
    ----------
    pca : PCA object
        The trained PCA model.
    pce_models : list of Function
        The trained PCE models for each mode.
    X_test : array-like
        The test input samples.
    U_test : array-like
        The test output samples.
    Z : array-like
        The depth values corresponding to the output samples.
    U_meas : array-like
        The measured deformation values.
    """

    X_test = ot.Sample(X_test_val)
    U_test = ot.Sample(U_test_val)
    U_meas['U_inclino'] = U_meas['U_inclino'].values + U_test_val[0][0]  # Adjust measured values to match the first test sample

    errors = []
    R_sq = []
    GNEA = []
    n = 8
    maxdif = []

    colors = plt.cm.plasma(np.linspace(0, 1, n))
    fig, axes = plt.subplots(figsize=(12, 6))
    for i, U_i in enumerate(U_test[:n]):
        if i == 0:
            axes.plot(U_i, Z, color=colors[i], label='FEM')
        else:
            axes.plot(U_i, Z, color=colors[i])
    for i, X_i in enumerate(X_test[:n]):
        u_pred_i = predict_deformation(X_i, pca, pce_models)
        if i == 0:
            axes.plot(u_pred_i, Z, color=colors[i], ls='', label=f"PCE", marker='x', markersize=3, markerfacecolor='None')
        else:
            axes.plot(u_pred_i, Z, color=colors[i], ls='', marker='x', markersize=3, markerfacecolor='None')

        error = np.mean(np.abs(u_pred_i - U_test[:n][i]))
        errors.append(error)
        R_sq.append(r2_score(U_test[:n][i], u_pred_i))
        num = np.abs(U_test_val[:n][i] - u_pred_i)
        denom = U_test_val[:n][i].max() - U_test_val[:n][i].min()
        GNEA.append((num / denom) * 100)

        maxdif.append(np.max(np.abs(u_pred_i - U_test[:n][i])))

    axes.plot(U_meas['U_inclino'], Z, color='r', label='Measured')
    axes.set_xlabel('Predicted deformation [mm]')
    axes.set_ylabel('depth [m + NAP]')
    axes.minorticks_on()
    axes.grid(True)
    axes.set_title('FEM Testing Set vs. PCE Predicted Deformation')
    axes.grid(which='minor', axis= 'x', linestyle='--', linewidth=0.5)
    axes.legend()

    return errors, R_sq, GNEA, maxdif


def test_model_ps(pca, pce_models, X_test_val, U_test_val, Z):
    import matplotlib.pyplot as plt
    from sklearn.metrics import r2_score
    import numpy as np

    """
    Tests the trained PCE models with PCA on a test set and plots the predicted vs. actual deformations.
    Parameters
    ----------
    pca : PCA object
        The trained PCA model.
    pce_models : list of Function
        The trained PCE models for each mode.
    X_test : array-like
        The test input samples.
    U_test : array-like
        The test output samples.
    Z : array-like
        The depth values corresponding to the output samples.
    U_meas : array-like
        The measured deformation values.
    """

    X_test = ot.Sample(X_test_val)
    U_test = ot.Sample(U_test_val)

    errors = []
    R_sq = []
    GNEA = []
    n = U_test_val.shape[0]
    maxdif = []

    colors = plt.cm.plasma(np.linspace(0, 1, n))
    fig, axes = plt.subplots(figsize=(12, 6))
    for i, U_i in enumerate(U_test[:n]):
        if i == 0:
            axes.plot(U_i, Z, color=colors[i], label='FEM')
        else:
            axes.plot(U_i, Z, color=colors[i])
    for i, X_i in enumerate(X_test[:n]):
        u_pred_i = predict_deformation(X_i, pca, pce_models)
        if i > 0:
            axes.plot(u_pred_i, Z, color=colors[i], ls='', label=f"PCE: wl={X_i[0]}, dl={X_i[1]}", marker='x', markersize=3, markerfacecolor='None')
        else:
            axes.plot(u_pred_i, Z, color=colors[i], ls='', marker='x', markersize=3, markerfacecolor='None')

        error = np.mean(np.abs(u_pred_i - U_test[:n][i]))
        errors.append(error)
        R_sq.append(r2_score(U_test[:n][i], u_pred_i))
        num = np.abs(U_test_val[:n][i] - u_pred_i)
        denom = U_test_val[:n][i].max() - U_test_val[:n][i].min()
        GNEA.append((num / denom) * 100)

        maxdif.append(np.max(np.abs(u_pred_i - U_test[:n][i])))

    axes.set_xlabel('Predicted deformation [mm]')
    axes.set_ylabel('depth [m + NAP]')
    axes.minorticks_on()
    axes.grid(True)
    axes.set_title('FEM Testing Set vs. PCE Predicted Deformation')
    axes.grid(which='minor', axis= 'x', linestyle='--', linewidth=0.5)
    axes.legend()

    return errors, R_sq, GNEA, maxdif


def define_param_list(X_raw, n_steps, U_meas, verbose=False):
    import numpy as np
    """
    Defines the parameter ranges for the input parameters based on the raw input data.
    Parameters
    ----------
    X_raw : array-like
        The raw input data samples.
    n_steps : int
        The number of steps within parameter range
    Returns
    -------
    E_B : array-like
        The range of E_B values.
    E_C : array-like
        The range of E_C values.
    phi_A : array-like
        The range of phi_A values.
    phi_B : array-like
        The range of phi_B values.
    """

    # Get the minimum and maximum values for each parameter from the raw input data
    E_B_lo = X_raw[:,0].min()
    E_B_hi = X_raw[:,0].max()

    E_C_lo = X_raw[:,1].min()
    E_C_hi = X_raw[:,1].max()

    phi_A_lo = X_raw[:,2].min()
    phi_A_hi = X_raw[:,2].max()

    phi_B_lo = X_raw[:,3].min()
    phi_B_hi = X_raw[:,3].max()

    n = n_steps
    if verbose:
        print("E_B_lo:", E_B_lo)
        print("E_B_hi:", E_B_hi)
        print("E_C_lo:", E_C_lo)
        print("E_C_hi:", E_C_hi)
        print("phi_A_lo:", phi_A_lo)
        print("phi_A_hi:", phi_A_hi)
        print("phi_B_lo:", phi_B_lo)
        print("phi_B_hi:", phi_B_hi)

    phi_A = np.linspace(phi_A_lo, phi_A_hi, n)
    phi_B = np.linspace(phi_B_lo, phi_B_hi, n)
    E_B = np.linspace(E_B_lo, E_B_hi, n)
    E_C = np.linspace(E_C_lo, E_C_hi, n)

    params = []
    for phi_A_i in phi_A:
        for phi_B_i in phi_B:
            for E_B_i in E_B:
                for E_C_i in E_C:
                    x_new = [E_B_i, E_C_i, phi_A_i, phi_B_i]
                    params.append(x_new)

    # NRSME_avg = (np.array(NRSME_deform) + np.array(NRSME_slope)) / 2
    params = np.array(params)

    # U_pred_min = np.min(np.array(U_predicted), axis=0)
    # U_pred_max = np.max(np.array(U_predicted), axis=0)

    # plt.fill_between(Z[Z < max_level], U_pred_min, U_pred_max, color='gray', alpha=0.5)
    return params

def run_calibration(pce_models, pca, params, Z, U_meas):
    NRSME_deform = []
    NRSME_slope = []
    RSME_deform = []
    RSME_slope = []

    U_predicted = []
    theta_predicted = []

    i = 0
    for X_i in params:
        U_i = predict_deformation(X_i, pca, pce_models)
        U_predicted.append(U_i)
        theta_i = np.gradient(U_i, Z)
        theta_predicted.append(theta_i)
        NRSME_deform.append(np.mean(np.sqrt((U_i - U_meas['U_inclino'])**2)) / abs(U_meas['U_inclino'].max() - U_meas['U_inclino'].min()))
        NRSME_slope.append(np.mean(np.sqrt((theta_i - U_meas['slope'])**2)) / abs(U_meas['slope'].max() - U_meas['slope'].min()))
        RSME_deform.append(np.sqrt(np.mean((U_i - U_meas['U_inclino'])**2)))
        RSME_slope.append(np.sqrt(np.mean((theta_i - U_meas['slope'])**2)))
        i+= 1
        print(f"Iteration {i}: X_i = {X_i}", end="\r")

    return NRSME_deform, NRSME_slope, RSME_deform, RSME_slope, U_predicted, theta_predicted



def determine_sobol(results, X_train, verbose=False):
    sobol_E_B = []
    sobol_E_C = []
    sobol_phi_A = []
    sobol_phi_B = []

    for pce_result in results:
        sobol = ot.FunctionalChaosSobolIndices(pce_result)

        first_pce = [sobol.getSobolIndex(i) for i in range(X_train.getDimension())]
        total_pce = [sobol.getSobolTotalIndex(i) for i in range(X_train.getDimension())]

        sobol_E_B.append(total_pce[0])
        sobol_E_C.append(total_pce[1])
        sobol_phi_A.append(total_pce[2])
        sobol_phi_B.append(total_pce[3])

        parameter_labels = ['E_B', 'E_C', 'phi_A', 'phi_B']
        strings_first = [f"{parameter_labels[i]}: {first_pce[i]:.3f}" for i in range(len(first_pce))]
        strings_total = [f"{parameter_labels[i]}: {total_pce[i]:.3f}" for i in range(len(total_pce))]
        if verbose:
            print("First-order Sobol indices:", strings_first[0], strings_first[1], strings_first[2], strings_first[3])
            print("Total-order Sobol indices:", strings_total[0], strings_total[1], strings_total[2], strings_total[3])
            print()
    return sobol_E_B, sobol_E_C, sobol_phi_A, sobol_phi_B



def pca_displacement_field(Y, n_components):
    import numpy as np
    from sklearn.decomposition import PCA

    """
    Perform PCA on the displacement field and return the principal components, scaled components, and their importance.

    Parameters:
    Y : ndarray
        sample data
    n_components : int
        The number of principal components to retain.

    Returns:
    pc_fields : ndarray
        The principal component displacement fields.
    pc_fields_scaled : ndarray
        The scaled principal component displacement fields.
    importance : ndarray
        The explained variance ratio of each principal component.
    """

    # Perform PCA on the displacement field data
    pca = PCA(n_components=n_components)
    Y_pca = pca.fit_transform(Y)

    # Get the principal components from the PCA object
    components = pca.components_

    # Reshape the principal components into displacement fields
    pc_fields = components.reshape(n_components, 100)

    # Scale the principal components by the explained variance ratio
    importance = pca.explained_variance_ratio_
    pc_fields_scaled = pc_fields.copy()
    for i in range(n_components):
        pc_fields_scaled[i] *= importance[i]

    return pc_fields, pc_fields_scaled, importance