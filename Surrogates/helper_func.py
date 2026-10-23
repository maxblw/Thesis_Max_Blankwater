def plot_pca_reconerror(errors):
    import matplotlib.pyplot as plt
    import numpy as np
    """
    Plots the PCA reconstruction error against the number of principal components.
    """
    errors = np.array(errors)
    plt.plot([1, 2, 3, 4, 5, 6, 7, 8, 9 ,10], errors*100, marker='o', markerfacecolor='r', color = 'k')
    plt.xlabel('Number of Principal Components')
    plt.ylabel('Mean Reconstruction Error [%]')
    plt.title('PCA Reconstruction Error vs Number of Principal Components')
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    plt.axhline(y=0.1, color='r', linestyle='--', label='Chosen number of PCs')
    plt.grid(True)
    plt.show()



def plot_sobol_indices_cal(sobol_first=None, sobol_total=None):
    import matplotlib.pyplot as plt
    import numpy as np
    """
    Plots the Sobol indices for each input parameter.
    """
    n_modes = 3
    n_X = 4
    degrees_list = [1, 2, 3, 4, 5, 6, 7, 8, 9 ,10]
    # Import Sobol indices from CSV files if not provided
    if sobol_first is None or sobol_total is None:
        sobol_total_1 = np.load('Logs/Calibration_Surrogate/sobol_total_1.npy')
        sobol_total_2 = np.load('Logs/Calibration_Surrogate/sobol_total_2.npy')
        sobol_total_3 = np.load('Logs/Calibration_Surrogate/sobol_total_3.npy')
        sobol_total_4 = np.load('Logs/Calibration_Surrogate/sobol_total_4.npy')

    else:
        sobol_total_1, sobol_total_2, sobol_total_3, sobol_total_4 = sobol_total
    
    factor = 1.5
    fig, axes = plt.subplots(n_modes, n_X, figsize=(11.69*factor, 8.27*factor), constrained_layout = True)

    colors_X = ['r', 'g', 'b', 'c']
    labels = [ '$E_B$', '$E_C$', '$\\phi_A$', '$\\phi_B$']

    for mode in range(n_modes):
        sobol = [sobol_total_1[:, :, mode], sobol_total_2[:, :, mode], sobol_total_3[:, :, mode], sobol_total_4[:, :, mode]]
        for idx, X_i in enumerate(sobol):
                axes[mode, idx].plot(degrees_list, X_i.mean(axis=0), color = colors_X[idx], label=f'mean index {labels[idx]}')
                axes[mode, idx].fill_between(degrees_list, X_i.mean(axis=0) - X_i.std(axis=0), X_i.mean(axis=0) + X_i.std(axis=0), color = colors_X[idx], alpha=0.3, label=f'index ± 1 std')
    for ax in axes.flat:
        ax.grid()
        ax.set_xticks(degrees_list)
        ax.grid(which='minor', axis='x', linestyle='--', linewidth=0.5)

    for i, ax in enumerate(axes.flat[0:4]):
        ax.set_title(labels[i])
    for i, ax in enumerate(axes.flat[8:12]):
        ax.set_xlabel('Trial run')
        ax.legend(loc='lower right')

    axes[0, 0].set_ylabel('Sobol index mode 1')
    axes[1, 0].set_ylabel('Sobol index mode 2')
    axes[2, 0].set_ylabel('Sobol index mode 3')



def plot_sobol_indices_ps(sobol_first=None, sobol_total=None):
    import matplotlib.pyplot as plt
    import numpy as np
    """
    Plots the Sobol indices for each input parameter.
    """
    n_modes = 5
    degrees_list = [1, 2, 3, 4, 5, 6, 7, 8, 9 ,10]
    factor = 1.5
    n_X = 2
    fig, axes = plt.subplots(n_modes, n_X, figsize=(10*factor, 5*factor), tight_layout = True)

    colors_X = ['r', 'b']
    labels = ['Sobol index for dredging Level', 'Sobol index for water level']

    if sobol_first is None or sobol_total is None:
            sobol_total_1 = np.load('Logs/Parametric_Study_Surrogate/sobol_total_1.npy')
            sobol_total_2 = np.load('Logs/Parametric_Study_Surrogate/sobol_total_2.npy')
    else:
            sobol_total_1, sobol_total_2 = sobol_total

    for mode in range(n_modes):
        sobol = [sobol_total_2[:, :, mode], sobol_total_1[:, :, mode]]
        for idx, X_i in enumerate(sobol):
                axes[mode, idx].plot(degrees_list, X_i.mean(axis=0), color = colors_X[idx], label=f'mean index {labels[idx]}')
                axes[mode, idx].fill_between(degrees_list, X_i.mean(axis=0) - X_i.std(axis=0), X_i.mean(axis=0) + X_i.std(axis=0), color = colors_X[idx], alpha=0.3, label=f'index ± 1 std')
    for ax in axes.flat:
        ax.grid()
        ax.set_xticks(degrees_list)
        ax.grid(which='minor', axis='x', linestyle='--', linewidth=0.5)

    for i, ax in enumerate(axes.flat[0:2]):
        ax.set_title(labels[i])
    for i, ax in enumerate(axes.flat[4:6]):
        ax.set_xlabel('Trial run')
        ax.legend(loc='lower right')

    for i in range(n_modes):
        axes[i, 0].set_ylabel(f'Index mode {i+1}')



def plot_errors(folder_name: str, n_degrees: int = 10):
    import numpy as np
    import matplotlib.pyplot as plt
    """
    Plots the R2, RMSE, and GNAE errors against the polynomial degree.
    """
    degrees_list = list(range(1, n_degrees + 1))

    R2 = np.loadtxt(f'Logs/{folder_name}/R2.csv', delimiter=',')
    RMSE = np.loadtxt(f'Logs/{folder_name}/RMSE.csv', delimiter=',')
    GNAE = np.loadtxt(f'Logs/{folder_name}/GNAE.csv', delimiter=',')

    R2_95_lo = np.percentile(R2, 5, axis=0)
    R2_95_hi = np.percentile(R2, 95, axis=0)

    GNAE_95_lo = np.percentile(GNAE, 5, axis=0)
    GNAE_95_hi = np.percentile(GNAE, 95, axis=0)

    RMSE_95_lo = np.percentile(RMSE, 5, axis=0)
    RMSE_95_hi = np.percentile(RMSE, 95, axis=0)


    fig, axes = plt.subplots(1, 2, figsize=(15, 3))
    axes[0].plot(degrees_list, np.mean(R2, axis=0), color='r', label='Mean $R^2$')
    axes[0].fill_between(degrees_list, R2_95_lo, R2_95_hi, color='r', alpha=0.3, label='95% CI')
    axes[0].fill_between(degrees_list, np.min(R2, axis=0), np.max(R2, axis=0), color='r', alpha=0.1, label='Min-Max range')
    axes[0].set_ylabel('R2 [-]')
    axes[0].grid(True)
    axes[0].legend()
    axes[0].set_title('$R^2$ vs Polynomial degree')

    # axes[1].plot(range(n_degrees), np.mean(RMSE, axis=0), color='b', label='Mean RMSE')
    # axes[1].fill_between(range(n_degrees), RMSE_95_lo, RMSE_95_hi, color='b', alpha=0.3, label='95% CI')
    # axes[1].fill_between(range(n_degrees), np.min(RMSE, axis=0), np.max(RMSE, axis=0), color='b', alpha=0.2, label='Min-Max range')
    # axes[1].set_xlabel('Polynomial degree')
    # axes[1].set_ylabel('RMSE [mm]')
    # axes[1].grid(True)
    # axes[1].legend()
    # axes[1].set_title('RMSE vs Polynomial degree')

    axes[1].plot(degrees_list, np.mean(GNAE, axis=0), color='b', label='Mean GNAE')
    axes[1].fill_between(degrees_list, GNAE_95_lo, GNAE_95_hi, color='b', alpha=0.3, label='95% CI')
    axes[1].fill_between(degrees_list, np.min(GNAE, axis=0), np.max(GNAE, axis=0), color='b', alpha=0.1, label='Min-Max range')
    axes[1].set_xlabel('Polynomial degree')
    axes[1].set_ylabel('GNAE [%]')
    axes[1].grid(True)
    axes[1].legend()
    axes[1].set_title('GNAE vs Polynomial degree')

def import_measurements(path, Z):
    import pandas as pd
    import numpy as np

    """
    Fixes the measured deformation values by interpolating them to match the Z values.
    Parameters:
        path (str): The path to the CSV file containing the measured deformation values.
        Z (array-like): The Z values to which the measured deformation values should be interpolated.
    Returns:
        U_meas (pd.DataFrame): The interpolated measured deformation values.
    """

    U_meas = pd.DataFrame(index=Z)
    U_m_temp = pd.read_csv(path, index_col=0)
    U_m_temp = U_m_temp.sort_index(ascending=True)
    U_meas['U_inclino'] = np.interp(Z, U_m_temp.index, U_m_temp.iloc[:,0])
    U_meas['slope'] = np.gradient(U_meas['U_inclino'], Z)
    return U_meas

def plot_sobol(pca, sobol_E_B, sobol_E_C, sobol_phi_A, sobol_phi_B):
    import matplotlib.pyplot as plt
    import numpy as np

    groups = {'$E_B$': sobol_E_B, '$E_C$': sobol_E_C, '$\\phi_A$': sobol_phi_A, '$\\phi_B$': sobol_phi_B}

    variance_ratio = np.round(pca.explained_variance_ratio_, 3)
    print(f"Variance ratio PCA: {variance_ratio}")

    fig, ax = plt.subplots(1, 2, figsize = (12, 4), gridspec_kw={'width_ratios': [2, 1]})

    labels = ['$E_B$', '$E_C$', '$\\phi_A$', '$\\phi_B$']
    colors = [(1, 0, 0, 0.5), (0, 0, 1, 0.5), (0.5, 0, 0.5, 0.5), (1, 0.5, 0, 0.5)]

    ax[0].grid(linewidth=1, linestyle='--', axis='y', alpha = 0.5)
    ax[0].grouped_bar(groups, tick_labels = [f'Mode 1: {variance_ratio[0]*100:.1f}%', f'Mode 2: {variance_ratio[1]*100:.1f}%', f'Mode 3: {variance_ratio[2]*100:.1f}%'], group_spacing=1, colors=colors, edgecolor=(0,0,0,1), linewidth=1)
    ax[0].legend()

    ax[0].set_ylabel('Maximum Deformation [mm]')
    ax[0].set_xlabel('Mode and relative importance')
    ax[0].set_title('PCE Predictions versus FEM predictions for maximum deformation per run')

    wedgeprops = {'edgecolor': 'black', 'linewidth': 1, 'alpha': 0.5} 


    total_importance = [float(np.round(np.sum(sobol_X * variance_ratio), 3)) for i, sobol_X in enumerate([np.array(sobol_E_B), np.array(sobol_E_C), np.array(sobol_phi_A), np.array(sobol_phi_B)])]
    print(f"Total importance per parameter: {total_importance}")

    ax[1].pie(total_importance, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops=wedgeprops)
    ax[1].set_title('Relative Importance')
    plt.show()



def plot_pca_fields(pc_fields, pc_fields_scaled, importance, Z):
    import matplotlib.pyplot as plt
    import numpy as np

    """
    Plot the principal component displacement fields and their scaled versions.

    Parameters:
    pc_fields : ndarray
        The principal component displacement fields.
    pc_fields_scaled : ndarray
        The scaled principal component displacement fields.
    importance : ndarray
        The explained variance ratio of each principal component.
    Z : ndarray
        Vertical coordinates
    """

    colors = plt.cm.plasma(np.linspace(0, 1, pc_fields_scaled.shape[0]))
    fig, axes = plt.subplots(1, 2)
    for i in range(pc_fields_scaled.shape[0]):
        axes[0].plot(pc_fields[i], Z, color=colors[i], label=f'PC {i+1}')
        axes[1].plot(pc_fields_scaled[i], Z, color=colors[i], label=f'PC {i+1}, scale: {importance[i]:.3f}')

    for ax in axes:
        ax.set_xlabel('Relative field value [-]')
        ax.grid(True)
    axes[0].set_ylabel('Z [m + NAP]')
    axes[0].set_title('Displacement fields')
    axes[1].set_title('Scaled displacement fields')
    # axes[1].legend(loc='lower right', bbox_to_anchor=(1.5, 0))
    axes[1].legend()

    plt.tight_layout()