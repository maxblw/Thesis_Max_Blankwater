def plot_calibration_errors(RMSE_deform, RMSE_theta, NRSME_deform, NRSME_theta):
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    xmin = -2
    xmax = len(RMSE_deform.index)

    fig, axes = plt.subplots(3, figsize=(15, 9), layout='tight')
    axes[0].plot(RMSE_deform.index, RMSE_deform['RMSE_deform'], color='k', marker='o', markerfacecolor='red')
    # axes[0].set_xlabel('Run')
    axes[0].set_ylabel('RMSE [mm]')
    axes[0].set_xlim([xmin, xmax])
    axes[0].set_title('Deformation RMSE over calibration Runs')
    axes[0].set_xticks(np.arange(0, len(RMSE_deform.index), 5))
    axes[0].minorticks_on()
    axes[0].grid(True)
    axes[0].grid(which='minor', linestyle='--', linewidth=0.5)


    axes[1].plot(RMSE_theta.index, RMSE_theta['RMSE_theta'], color='k', marker='o', markerfacecolor='blue')
    # axes[1].set_xlabel('Run')
    axes[1].set_ylabel('RMSE [mm/m]')
    axes[1].set_title('Slope RMSE over Calibration Runs')
    axes[1].set_xlim([xmin, xmax])
    axes[1].set_xticks(np.arange(0, len(RMSE_theta.index), 5))
    axes[1].minorticks_on()
    axes[1].grid(True)
    axes[1].grid(which='minor', linestyle='--', linewidth=0.5)


    axes[2].plot(NRSME_deform.index, NRSME_deform['NRSME_deform'], color='r', 
                label='Normalized Deformation RMSE', alpha=0.5)
    axes[2].plot(NRSME_theta.index, NRSME_theta['NRSME_theta'], color='b',
                label='Normalized Slope RMSE', alpha=0.5)

    # axes[2].fill_between(NRSME_deform.index, NRSME_deform['NRSME_deform'], NRSME_theta['NRSME_theta'], color='gray', alpha=0.3)

    average_NRSME = pd.DataFrame((NRSME_deform['NRSME_deform']+NRSME_theta['NRSME_theta'])/2, columns=['Average_NRSME'])
    axes[2].plot(average_NRSME.index, average_NRSME, color='k', marker='o', markerfacecolor='purple', label='Average Normalized RMSE')

    ymin = average_NRSME['Average_NRSME'].min() -0.01
    ymax = average_NRSME['Average_NRSME'].max() +0.01

    axes[2].legend(loc='upper right')
    # axes[2].set_yscale('log')
    axes[2].set_xlabel('Run')
    axes[2].set_ylabel('NRMSE [-]')
    axes[2].set_ylim([ymin, ymax])
    axes[2].set_title('NRMSE over Calibration Runs')
    axes[2].set_xlim([xmin, xmax])
    axes[2].set_xticks(np.arange(0, len(NRSME_deform.index), 5))
    axes[2].minorticks_on()
    axes[2].grid(which='minor', linestyle='--', linewidth=0.5)
    axes[2].grid(True)


    plt.show()

    average_NRSME.sort_values(ascending=True, inplace=True, by='Average_NRSME')
    idx_min = average_NRSME.index.values[:10]
    idx_min = [int(i) for i in idx_min]
    display(average_NRSME.head())
    return idx_min


def plot_best_runs(idx_min, log, U_cor, theta):
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    colors = plt.cm.plasma(np.linspace(0, 1, len(idx_min)))
    i_0 = 0
    colors2 = plt.cm.plasma(np.linspace(0, 1, len(idx_min)))
    fig, ax = plt.subplots(2, figsize=(15, 12), layout='tight')
    U_inclino = pd.read_csv('..\\..\\Data\\Measurements\\comparison_inclino.csv', index_col = 'Z')
        
    for run in idx_min:
        column = f'R_{run}'
        runparams = log.loc[run, ['phi_A', 'phi_B', 'E_B', 'E_C']]
        columnlabel = column
        if len(columnlabel) < 5:
            columnlabel = columnlabel[:2] + '_' + columnlabel[2:]
        ax[0].plot(U_cor[column], U_cor.index, label=f'{columnlabel}: $\\varphi_A$={runparams["phi_A"]:.2f}, $\\varphi_B$={runparams["phi_B"]:.2f}, $E_B$={runparams["E_B"]/1000:.2f}E3, $E_C$={runparams["E_C"]/1000:.2f}E3', color=colors[i_0])
        ax[1].plot(theta[column], theta.index, label=f'{columnlabel}: $\\varphi_A$={runparams["phi_A"]:.2f}, $\\varphi_B$={runparams["phi_B"]:.2f}, $E_B$={runparams["E_B"]/1000:.2f}E3, $E_C$={runparams["E_C"]/1000:.2f}E3', color=colors2[i_0])
        i_0 += 1
        # else:
            # ax[0].plot(U_cor[column], U_cor.index, 'k', alpha=0.3)
            # ax[1].plot(theta[column], theta.index, 'k', alpha=0.3)
    ax[0].fill_betweenx(U_cor.index, U_cor.min(axis=1), U_cor.max(axis=1), color='gray', edgecolor='black', label='Envelope', alpha=0.3)
    ax[0].plot(U_inclino, U_inclino.index, label='Inclino', color='red', marker='o', markerfacecolor='white')

    ax[0].axhline(y = -16, color='black', linestyle='--')
    ax[0].axhline(y = -28.5, color='black', linestyle='--')
    ax[0].axhline(y = -8, color='black', linestyle='--')
    ax[0].minorticks_on()
    ax[0].tick_params(axis='x', which='both')
    ax[0].grid()
    ax[0].grid(which='minor', linewidth=0.5, axis='x', ls = '--')
    ax[0].legend(loc = 'lower right', bbox_to_anchor=(1.2, 0))
    ax[0].text(10, (-16 + -28.5)/2, 'Layer B', ha='center', va='bottom', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax[0].text(10, (-16 + -8)/2, 'Layer A', ha='center', va='bottom', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax[0].text(10, (-28.5 + -35.5)/2, 'Layer C', ha='center', va='bottom', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax[0].set_xlabel('Deformation [mm]')
    ax[0].set_ylabel('Level [m+NAP]')
    ax[0].set_title('Deformation over Calibration Runs')

    ax[1].fill_betweenx(theta.index, theta.iloc[:, 1:].min(axis=1), theta.iloc[:, 1:].max(axis=1), color='gray', edgecolor='black', label='Envelope', alpha=0.3)
    ax[1].plot(theta['U_inclino'], theta.index, label='Inclino', color='red', marker='o', markerfacecolor='white')
    ax[1].axhline(y = -16, color='black', linestyle='--')
    ax[1].axhline(y = -28.5, color='black', linestyle='--')
    ax[1].axhline(y = -8, color='black', linestyle='--')
    ax[1].text(-4, (-16 + -28.5)/2, 'Layer B', ha='center', va='bottom', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax[1].text(-4, (-16 + -8)/2, 'Layer A', ha='center', va='bottom', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax[1].text(-4, (-28.5 + -35.5)/2, 'Layer C', ha='center', va='bottom', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax[1].minorticks_on()
    ax[1].tick_params(axis='x', which='both')
    ax[1].grid()
    ax[1].grid(which='minor', linewidth=0.5, axis='x', ls = '--')
    ax[1].legend(loc = 'lower right', bbox_to_anchor=(1.2, 0))
    ax[1].set_xlabel('Slope [mm/m]')
    ax[1].set_ylabel('Level [m+NAP]')
    ax[1].set_title('Slope over Calibration Runs')

    plt.show()