def plot_results(phase_1: int, type: str,
                path_plaxis: str,
                path_strains: str,
                path_inclino: str,
                date_strains: list[str],
                date_inclino: str,
                model_name: str = 'model_3',
                phase_0: int = None,
                row = None,
                section = None,
                section_inclino = None,
                presentation_plot: bool = False):
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    """
    Plots the results of the two phases in a single figure. If a phase_0 is given, the difference between phases is plotted.
    phase_1: int The phase number of the phase of interest.
    phase_0: int The phase number of the reference phase. If None, only phase_1 is plotted.
    path_plaxis: str The path to the plaxis output file.
    path_strains: str The path to the strains output files.
    path_inclino: str The path to the inclino output file.
    """

    # load PLAXIS data
    M_PLAXIS, N_PLAXIS, U_PLAXIS = read_PLAXIS_strains(type=type, path_plaxis=path_plaxis, model_name=model_name, phase_1=phase_1, phase_0=phase_0, row=row, section=section)

    # load strain data
    strain_list = []
    if date_strains:
        for i, date in enumerate(date_strains):
            if type == 'BP':
                assert section is not None, "section must be provided for type 'BP'"
                strains_path = f'{path_strains}\\{type}_{section[i]}_strain_forces_{date.replace(" ", "_").replace(":", "-")}.csv'

            elif type == 'VP':
                assert row is not None, "row must be provided for type 'VP'"
                strains_path = f'{path_strains}\\{type}_{row}_strain_forces_{date.replace(" ", "_").replace(":", "-")}.csv'

            elif type == 'GA':
                assert row is not None, "row must be provided for type 'GA'"
                strains_path = f'{path_strains}\\{type}_strain_forces_{date.replace(" ", "_").replace(":", "-")}.csv'

            if type in ['BP', 'VP']:
                df_strains = pd.read_csv(strains_path, header=0, index_col=0)
                df_strains.index = M_PLAXIS.index.max() - df_strains.index 
                M_strains = df_strains['M']
                N_strains = df_strains['N']
                U_strains = df_strains['U']

                strain_list.append((M_strains, N_strains, U_strains))

            elif type == 'GA':
                df_strains = pd.read_csv(strains_path, header=0, index_col=0)
                # df_strains.index = N_PLAXIS.index.max() - df_strains.index 
                N_strains = pd.DataFrame(df_strains[f'N_{row}'])
                if row == 'T':
                    N_strains = pd.concat([N_strains, df_strains[f'N_T1']], axis=1)
                strain_list.append((pd.Series(), N_strains, pd.Series()))

            if type == 'GA':
                N_PLAXIS.index = N_PLAXIS.index + (N_strains[f"N_{row}"].dropna().index.max() - N_PLAXIS.index.max())
                idx_0 = N_strains.index.min()
                print(f"idx_0: {idx_0}")
                N_PLAXIS.loc[idx_0, :] = N_PLAXIS.iloc[0, :]
                N_PLAXIS = N_PLAXIS.sort_index()

    # load inclino data
    if type in ['BP', 'VP']:
        if type == 'BP':
            assert section_inclino is not None, "section_inclino must be provided for type 'BP'"
            U_inclino_list = []
            for sec_i in section_inclino:
                U_inclino = pd.read_csv(f'{path_inclino}\\inclino_{type}_mt{sec_i}.csv', header=0, index_col=0)
                U_inclino = U_inclino.loc[:, date_inclino]
                U_inclino.index = U_inclino.index + M_PLAXIS.index.min()
                U_inclino = U_inclino[U_inclino.index < M_PLAXIS.index.max()]
                U_inclino_list.append(U_inclino)
        if type == 'VP':
            assert row is not None, "row must be provided for type 'VP'"
            U_inclino = pd.read_csv(f'{path_inclino}\\inclino_{type}_{row[0]}_mt76.csv', header=0, index_col=0)
            U_inclino = U_inclino.loc[:, date_inclino]
            U_inclino.index = U_inclino.index + M_PLAXIS.index.min()
            U_inclino = U_inclino[U_inclino.index < M_PLAXIS.index.max()]
            U_inclino_list = [U_inclino]

    ## Plotting
    if type in ['BP', 'VP']:
        fig, axes = plt.subplots(1, 3, figsize=(9, 5), sharey=True, layout='tight')

        for column in M_PLAXIS.columns:
            axes[0].plot(M_PLAXIS[column], M_PLAXIS.index, color = 'blue', alpha = 0.3)
        # axes[0].plot(M_PLAXIS['M_avg'], M_PLAXIS.index, label='PLAXIS', color = 'blue')
        axes[0].plot(M_PLAXIS['M_avg'], M_PLAXIS.index, label='Predicted', color = 'blue')
        axes[0].set_title('Moment')
        axes[0].set_ylabel('Z [m + NAP]')
        axes[0].set_xlabel('Moment [kNm]')

        for column in N_PLAXIS.columns:
            axes[1].plot(N_PLAXIS[column], N_PLAXIS.index, color = 'red', alpha = 0.3)
        axes[1].plot(N_PLAXIS['N_avg'], N_PLAXIS.index, label='Predicted', color = 'red')
        axes[1].set_title('Axial Force')
        # axes[1].set_ylabel('Z [m + NAP]')
        axes[1].set_xlabel('Axial Force [kN]')

        for column in U_PLAXIS.columns:
            axes[2].plot(U_PLAXIS[column], U_PLAXIS.index, color = 'green', alpha = 0.3)
        axes[2].plot(U_PLAXIS['U_avg'], U_PLAXIS.index, label='Predicted', color = 'green')
        axes[2].set_title('Deformation')
        # axes[2].set_ylabel('Z [m + NAP]')
        axes[2].set_xlabel('Deformation [mm]')

        for ax in axes:
            ax.minorticks_on()
            ax.grid(which='minor', axis='x', alpha=0.3)

            # plot strains
        linestyles = ['-', '--', '-.', ':']
        if date_strains:
            if len(date_strains) > 1:
                for i, (M_strains, N_strains, U_strains) in enumerate(strain_list):
                    assert section is not None, "section must be provided for type 'BP'"
                    assert len(strain_list) == len(section), "The number of strain files must match the number of sections provided."
                    axes[0].plot(M_strains, M_strains.index, label=f'M from strains sc{section[i]}', color = 'black', linestyle=linestyles[i])
                    axes[1].plot(N_strains, N_strains.index, label=f'N from strains sc{section[i]}', color = 'black', linestyle=linestyles[i])
                    # axes[2].plot(U_strains, U_strains.index, label=f'U from strains sc{section[i]}', color = 'black', linestyle=linestyles[i])
            else:
                M_strains, N_strains, U_strains = strain_list[0]
                # axes[0].plot(M_strains, M_strains.index, label='M from strains', color = 'black', linestyle='-')
                # axes[1].plot(N_strains, N_strains.index, label='N from strains', color = 'black', linestyle='-')
                axes[0].plot(M_strains, M_strains.index, label='Measured', color = 'black', linestyle='-')
                axes[1].plot(N_strains, N_strains.index, label='Measured', color = 'black', linestyle='-')
                # axes[2].plot(U_strains, U_strains.index, label='U from strains', color = 'black', linestyle='-')

            # plot inclino
        markers = ['o', 'x', '^', 'D']
        if len(U_inclino_list) > 1:
            for i, U_inclino in enumerate(U_inclino_list):
                axes[2].plot(U_inclino, U_inclino.index, label=f'U from inclino sc{section_inclino[i]}', color = 'black', linestyle='-', marker=markers[i], markersize=3, markerfacecolor='white')
        else:
            U_inclino = U_inclino_list[0]
            axes[2].plot(U_inclino, U_inclino.index, label='Measured', color = 'black', linestyle='-', marker='o', markersize=3, markerfacecolor='white')

            # general settings
        for ax in axes:
            ax.grid()
            ax.legend(
                loc='upper center',
                bbox_to_anchor=(0.4, -0.15)
            )
            if presentation_plot:
                ax.set_xlabel('')
                ax.set_ylabel('')
                ax.set_xticks([])
                ax.set_yticks([])
                ax.legend(loc='upper center',
                          bbox_to_anchor=(0.4, -0.05))
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)

    elif type == 'GA':
        fig, ax = plt.subplots(figsize=(10, 3), layout='tight')

        for column in N_PLAXIS.columns:
            ax.plot(N_PLAXIS.index, N_PLAXIS[column], color = 'red', alpha = 0.3)
        ax.plot(N_PLAXIS.index, N_PLAXIS['N_avg'], label='PLAXIS', color = 'red')
        ax.set_title(f'Axial Force {row}')
        ax.set_xlabel('Length [m]')
        ax.set_ylabel('Axial Force [kN]')
        ax.plot(N_strains.index, N_strains[f'N_{row}'], label='N from strains T', color = 'black', linestyle='-')
        ax.grid()
        if row == 'T':
            ax.plot(N_strains.index, N_strains[f'N_T1'], label='N from strains T1', color = 'black', linestyle='--')
        ax.legend()

        
    ## Transform for export
    if type in ['BP', 'VP']:
        df_PLAXIS = pd.DataFrame({'M_avg': M_PLAXIS['M_avg'], 'N_avg': N_PLAXIS['N_avg'], 'U_avg': U_PLAXIS['U_avg']}, index=M_PLAXIS.index)
        df_strain = pd.DataFrame()
        for i, (M_strains, N_strains, U_strains) in enumerate(strain_list):
            df_strain[f'M_strain_sc{section[i]}'] = M_strains
            df_strain[f'N_strain_sc{section[i]}'] = N_strains
            df_strain[f'U_strain_sc{section[i]}'] = U_strains
        df_inclino = pd.DataFrame()
        if len(U_inclino_list) > 0:
            for i, U_inclino in enumerate(U_inclino_list):
                df_inclino[f'U_inclino_sc{section_inclino[i]}'] = U_inclino
        else:
            df_inclino = U_inclino_list[0]

    elif type == 'GA':
        df_PLAXIS = pd.DataFrame({'N_avg': N_PLAXIS['N_avg']}, index=N_PLAXIS.index)
        df_strain = N_strains
        df_inclino = pd.DataFrame()  # No inclino data for GA type
    
    return  df_PLAXIS, df_strain, df_inclino

def read_PLAXIS_strains(type: str, path_plaxis: str, model_name: str, phase_1: int, phase_0: int = None, row = None, section = None):
    import pandas as pd
    suffix_1 = f'{model_name}_Phase_{phase_1}.csv'
    
    if type in ['GA', 'VP']:
            row = row[0]
            if type == 'GA':
                assert row in ['T', 'B'], "row must be either 'T' or 'B' for type 'GA'"
            elif type == 'VP':
                assert row in ['L', 'W'], "row must be either 'L' or 'W' for type 'VP'"
            
            prefix = f'{type}_{row}'
            path_N_PLAXIS_1 = f'{path_plaxis}\\{prefix}_axial_{suffix_1}'
            N_PLAXIS_1 = pd.read_csv(path_N_PLAXIS_1, header=0, index_col=0)
            if type == 'VP':
                path_M_PLAXIS_1 = f'{path_plaxis}\\{prefix}_moment_{suffix_1}'
                M_PLAXIS_1 = pd.read_csv(path_M_PLAXIS_1, header=0, index_col=0)
                path_U_PLAXIS_1 = f'{path_plaxis}\\{prefix}_deform_{suffix_1}'
                U_PLAXIS_1 = pd.read_csv(path_U_PLAXIS_1, header=0, index_col=0)
    
            if phase_0 is not None:
                suffix_0 = f'{model_name}_Phase_{phase_0}.csv'
                path_N_PLAXIS_0 = f'{path_plaxis}\\{prefix}_axial_{suffix_0}'
                N_PLAXIS_0 = pd.read_csv(path_N_PLAXIS_0, header=0, index_col=0) 
                if type == 'VP':               
                    path_M_PLAXIS_0 = f'{path_plaxis}\\{prefix}_moment_{suffix_0}'
                    M_PLAXIS_0 = pd.read_csv(path_M_PLAXIS_0, header=0, index_col=0)
                    path_U_PLAXIS_0 = f'{path_plaxis}\\{prefix}_deform_{suffix_0}'
                    U_PLAXIS_0 = pd.read_csv(path_U_PLAXIS_0, header=0, index_col=0)

    elif type == 'BP':
        assert section is not None, "section must be provided for type 'BP'"

        prefix = f'{type}'

        path_M_PLAXIS_1 = f'{path_plaxis}\\{prefix}_moment_{suffix_1}'
        M_PLAXIS_1 = pd.read_csv(path_M_PLAXIS_1, header=0, index_col=0)
        path_N_PLAXIS_1 = f'{path_plaxis}\\{prefix}_axial_{suffix_1}'
        N_PLAXIS_1 = pd.read_csv(path_N_PLAXIS_1, header=0, index_col=0)
        path_U_PLAXIS_1 = f'{path_plaxis}\\{prefix}_deform_{suffix_1}'
        U_PLAXIS_1 = pd.read_csv(path_U_PLAXIS_1, header=0, index_col=0)

        if phase_0 is not None:
            suffix_0 = f'{model_name}_Phase_{phase_0}.csv'
            path_M_PLAXIS_0 = f'{path_plaxis}\\{prefix}_moment_{suffix_0}'
            M_PLAXIS_0 = pd.read_csv(path_M_PLAXIS_0, header=0, index_col=0)
            path_N_PLAXIS_0 = f'{path_plaxis}\\{prefix}_axial_{suffix_0}'
            N_PLAXIS_0 = pd.read_csv(path_N_PLAXIS_0, header=0, index_col=0)
            path_U_PLAXIS_0 = f'{path_plaxis}\\{prefix}_deform_{suffix_0}'
            U_PLAXIS_0 = pd.read_csv(path_U_PLAXIS_0, header=0, index_col=0)

    if type in ['BP', 'VP']:
        if phase_0 is not None:
            M_PLAXIS = M_PLAXIS_1 - M_PLAXIS_0
            N_PLAXIS = N_PLAXIS_1 - N_PLAXIS_0
            U_PLAXIS = U_PLAXIS_1 - U_PLAXIS_0
        else:
            N_PLAXIS = N_PLAXIS_1
            M_PLAXIS = M_PLAXIS_1
            U_PLAXIS = U_PLAXIS_1

        if type == 'VP':
            M_PLAXIS = M_PLAXIS[M_PLAXIS.index < -2]
            N_PLAXIS = N_PLAXIS[N_PLAXIS.index < -2]
            U_PLAXIS = U_PLAXIS[U_PLAXIS.index < -2]

        for column in U_PLAXIS.columns:
            U_PLAXIS[column] = U_PLAXIS[column] - U_PLAXIS.sort_index()[column].iloc[0]

    elif type == 'GA':
        N_PLAXIS = N_PLAXIS_1
        if phase_0 is not None:
            N_PLAXIS = N_PLAXIS_1 - N_PLAXIS_0
        M_PLAXIS = pd.DataFrame()
        U_PLAXIS = pd.DataFrame()
            
    return M_PLAXIS, N_PLAXIS, U_PLAXIS