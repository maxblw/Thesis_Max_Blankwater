from turtle import pd


def save(df, suffix, savepath: str, date: str, date_ref: str, type: str, section: str = None, side: str = None):
    import yaml
    import pandas as pd

    path = f"{savepath}\\{type}_{suffix}_{date.replace(':', '-').replace(' ', '_')}"

    if type == 'BP':
        assert section is not None, "Section must be provided for BP type when saving the DataFrame."
        path = f"{savepath}\\{type}_{section}_{suffix}_{date.replace(':', '-').replace(' ', '_')}"
    if type == 'VP':
        assert side is not None, "Side must be provided for VP type when saving the DataFrame."
        path = f"{savepath}\\{type}_{side}_{suffix}_{date.replace(':', '-').replace(' ', '_')}"

    metadata = {
        'Filename': f"{type}_{suffix}_{date.replace(':', '-').replace(' ', '_')}.csv",
        'Type': type,
        'Date': date,
        'Reference date': date_ref}

    with open(f"{path}.yaml", 'w') as f:
        yaml.dump(metadata, f)

    df.to_csv(f"{path}.csv", index=False)



def import_raw_strain_measurements(filename: str, plot: bool = False, type: str = 'BP', 
                                   savepath: str = None, date: str = None, date_ref: str = None, section: str = None, side: str = None):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    """""
    Imports the strain measurements from the Excel file and processes them for further analysis. The function reads the data, interpolates it to a common length scale, and optionally plots the strain profiles.

    Parameters:
    - filename: str, the path to the Excel file containing the strain measurements.
    - plot: bool, whether to plot the strain profiles (default is False).
    - type: str, the type of data being imported (default is 'BP').
    Returns:
    - df: pandas DataFrame, containing the processed strain measurements with columns for length and strain at different angles.
    - df_T1, df_B, df_T: pandas DataFrames, containing the processed strain measurements for GA type (if applicable).
    - date: str, the date of the strain measurements (if provided).
    - date_ref: str, the reference date for the strain measurements (if provided).
    - savepath: str, the path to save the processed DataFrame and metadata (if provided).
    """""

    if type == 'BP':
        dfs = pd.read_excel(filename, sheet_name=None)
        keys = list(dfs.keys())
        df_a1 = dfs[keys[0]] #15 degrees
        df_a2 = dfs[keys[1]] #165 degrees
        df_a3 = dfs[keys[2]] #195 degrees
        df_a4 = dfs[keys[3]] #345 degrees

    if type == 'VP':
        dfs = pd.read_excel(filename, sheet_name=None)
        keys = list(dfs.keys())
        df_a1 = dfs[keys[1]]
        df_a2 = dfs[keys[0]]
        df_a3 = dfs[keys[3]]
        df_a4 = dfs[keys[2]]
    
    if type in ['BP', 'VP']:
        L_max = 0
        for df in [df_a1, df_a2, df_a3, df_a4]:
            df.index = df['Length']
            df.drop(columns=['Length'], inplace=True)
            L_max = max(L_max, df.index.max())

        df = pd.DataFrame(columns=['Length', 'Strain_a1', 'Strain_a2', 'Strain_a3', 'Strain_a4'])
        length = np.arange(0, L_max, 0.05)
        df['Length'] = length

        df['Strain_a1'] = np.interp(length, df_a1.index, df_a1['RelativeStrain'])
        df['Strain_a2'] = np.interp(length, df_a2.index, df_a2['RelativeStrain'])
        df['Strain_a3'] = np.interp(length, df_a3.index, df_a3['RelativeStrain'])
        df['Strain_a4'] = np.interp(length, df_a4.index, df_a4['RelativeStrain'])

        df.loc[df['Length'] > df_a1.index.max(), 'Strain_a1'] = np.nan
        df.loc[df['Length'] > df_a2.index.max(), 'Strain_a2'] = np.nan
        df.loc[df['Length'] > df_a3.index.max(), 'Strain_a3'] = np.nan
        df.loc[df['Length'] > df_a4.index.max(), 'Strain_a4'] = np.nan

        if plot:
            plt.figure(figsize=(12, 6))
            plt.plot(df['Length'], df['Strain_a1'], label='Strain $\\alpha_1$', color='blue')
            plt.plot(df['Length'], df['Strain_a2'], label='Strain $\\alpha_2$', color='green')
            plt.plot(df['Length'], df['Strain_a3'], label='Strain $\\alpha_3$', color='orange')
            plt.plot(df['Length'], df['Strain_a4'], label='Strain $\\alpha_4$', color='red')
            plt.xlabel('Length [m]')
            plt.ylabel('Relative Strain [$10^{-6}$]')
            plt.title(f'Strain Measurements {date}')
            plt.legend()
            plt.grid()
            plt.show()

            print(f"$\\alpha_1$ max: {df['Strain_a1'].max()}, $\\alpha_1$ min: {df['Strain_a1'].min()}")
            print(f"$\\alpha_2$ max: {df['Strain_a2'].max()}, $\\alpha_2$ min: {df['Strain_a2'].min()}")
            print(f"$\\alpha_3$ max: {df['Strain_a3'].max()}, $\\alpha_3$ min: {df['Strain_a3'].min()}")
            print(f"$\\alpha_4$ max: {df['Strain_a4'].max()}, $\\alpha_4$ min: {df['Strain_a4'].min()}")

    elif type == 'GA':
        dfs = pd.read_excel(filename, sheet_name=None)
        keys = list(dfs.keys())

        df_T1 = dfs[keys[0]] #T1
        df_B = dfs[keys[1]] #T2
        df_T = dfs[keys[2]] #T3
        
        L_max = 0
        for df in [df_T1, df_B, df_T]:
            df.index = df['Length']
            df.drop(columns=['Length'], inplace=True)
            L_max = max(L_max, df.index.max())
        
        df = pd.DataFrame(columns=['Length', 'Strain_T1', 'Strain_B', 'Strain_T'])
        length = np.arange(0, L_max, 0.05)
        df['Length'] = length
        idx_T1 = df['Length'] <= df_T1.index.max()
        idx_B = df['Length'] <= df_B.index.max()
        idx_T = df['Length'] <= df_T.index.max()

        df.loc[idx_T1, 'Strain_T1'] = np.interp(length[idx_T1], df_T1.index, df_T1['RelativeStrain'])
        df.loc[idx_B, 'Strain_B'] = np.interp(length[idx_B], df_B.index, df_B['RelativeStrain'])
        df.loc[idx_T, 'Strain_T'] = np.interp(length[idx_T], df_T.index, df_T['RelativeStrain'])

        if plot:
            plt.figure(figsize=(12, 6))
            plt.plot(df['Length'], df['Strain_T1'], label='T1', color='blue')
            plt.plot(df['Length'], df['Strain_B'], label='B', color='green')
            plt.plot(df['Length'], df['Strain_T'], label='T', color='red')
            plt.xlabel('Depth [m]')
            plt.ylabel('Relative Strain [$10^{-6}$]')
            plt.title('Strain Measurements for GA')
            plt.legend()
            plt.grid()
            plt.show()

    if savepath is not None:
        assert date and date_ref is not None, "Date and reference date must be provided when saving the DataFrame."
        save(df, suffix='raw_strain', savepath=savepath, date=date, date_ref=date_ref, type=type, section=section, side=side)
        

    return df



def correct_temp(df: pd.DataFrame, temppath: str, type: str = 'BP', plot: bool = False, 
                 savepath: str = None, date: str = None, date_ref: str = None, 
                 section: str = None, side: str = None):
    import pandas as pd
    import numpy as np
    """""
    Corrects the strain measurements for temperature effects using the provided alpha values. Temparature file should have the sheets ordered as: 15, 165, 195, 345. The function reads the temperature data from the Excel file and applies the correction to the strain measurements.

    Parameters:
    - df: pandas DataFrame, containing the strain measurements with columns for length and strain at different angles.
    - alpha: list of float, the temperature correction coefficients for each strain measurement (default is None).

    Returns:
    - df_corrected: pandas DataFrame, containing the temperature-corrected strain measurements.
    """""

    alpha_T_fibre = 7.32
    alpha_T_steel = 12
    alpha_T_concrete = 10

    if type == 'BP':
        DT_all = pd.read_excel(temppath, sheet_name=None)
        keys = list(DT_all.keys())
        df_temp_a1 = DT_all[keys[0]]
        df_temp_a2 = DT_all[keys[1]]
        df_temp_a3 = DT_all[keys[2]]
        df_temp_a4 = DT_all[keys[3]]
        alpha_tot = alpha_T_fibre + alpha_T_steel

    if type == 'VP':
        DT_all = pd.read_excel(temppath, sheet_name=None)
        keys = list(DT_all.keys())
        df_temp_a1 = DT_all[keys[1]]
        df_temp_a2 = DT_all[keys[0]]
        df_temp_a3 = DT_all[keys[3]]
        df_temp_a4 = DT_all[keys[2]]
        alpha_tot = alpha_T_concrete + alpha_T_fibre

    if type in ['BP', 'VP']:
        # interpolate to fit strain measurements
        DT_a1 = np.interp(df['Length'], df_temp_a1['Length'], df_temp_a1['RelativeTemp'])
        DT_a2 = np.interp(df['Length'], df_temp_a2['Length'], df_temp_a2['RelativeTemp'])
        DT_a3 = np.interp(df['Length'], df_temp_a3['Length'], df_temp_a3['RelativeTemp'])
        DT_a4 = np.interp(df['Length'], df_temp_a4['Length'], df_temp_a4['RelativeTemp'])

        # correction values Delta_epsilon = alpha_tot * DT
        D_eps_a1 = alpha_tot * DT_a1
        D_eps_a2 = alpha_tot * DT_a2
        D_eps_a3 = alpha_tot * DT_a3
        D_eps_a4 = alpha_tot * DT_a4

        # subtract correction values from strain measurements
        df_corrected = df.copy()
        df_corrected['Strain_a1'] = df_corrected['Strain_a1'] + D_eps_a1
        df_corrected['Strain_a2'] = df_corrected['Strain_a2'] + D_eps_a2
        df_corrected['Strain_a3'] = df_corrected['Strain_a3'] + D_eps_a3
        df_corrected['Strain_a4'] = df_corrected['Strain_a4'] + D_eps_a4

        if plot:
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(2, 1, figsize=(12, 11), sharex=True, layout='tight')

            axes[0].plot(df_temp_a1['Length'], df_temp_a1['RelativeTemp'], label=f'$\Delta$ T $\\alpha_1$ ', color='blue')
            axes[0].plot(df_temp_a2['Length'], df_temp_a2['RelativeTemp'], label=f'$\Delta$ T $\\alpha_2$ ', color='green')
            axes[0].plot(df_temp_a3['Length'], df_temp_a3['RelativeTemp'], label=f'$\Delta$ T $\\alpha_3$ ', color='orange')
            axes[0].plot(df_temp_a4['Length'], df_temp_a4['RelativeTemp'], label=f'$\Delta$ T $\\alpha_4$ ', color='red')
            axes[0].set_xlabel('Length [m]')
            axes[0].set_ylabel('Relative Temperature [°C]')
            axes[0].set_title('Relative Temperature Measurements')
            axes[0].legend()
            axes[0].grid()

            axes[1].plot(df_corrected['Length'], df_corrected['Strain_a1'], label='Corrected Strain $\\alpha_1$', color='blue')
            axes[1].plot(df_corrected['Length'], df_corrected['Strain_a2'], label='Corrected Strain $\\alpha_2$', color='green')
            axes[1].plot(df_corrected['Length'], df_corrected['Strain_a3'], label='Corrected Strain $\\alpha_3$', color='orange')
            axes[1].plot(df_corrected['Length'], df_corrected['Strain_a4'], label='Corrected Strain $\\alpha_4$', color='red')
            axes[1].set_xlabel('Length [m]')
            axes[1].set_ylabel('Temperature-Corrected Relative Strain [$10^{-6}$]')
            axes[1].set_title('Temperature-Corrected Strain Measurements')
            axes[1].legend()
            axes[1].grid()
            plt.show()

            print(f"alpha_1 max: {df_corrected['Strain_a1'].max()}, alpha_1 min: {df_corrected['Strain_a1'].min()}")
            print(f"alpha_2 max: {df_corrected['Strain_a2'].max()}, alpha_2 min: {df_corrected['Strain_a2'].min()}")
            print(f"alpha_3 max: {df_corrected['Strain_a3'].max()}, alpha_3 min: {df_corrected['Strain_a3'].min()}")
            print(f"alpha_4 max: {df_corrected['Strain_a4'].max()}, alpha_4 min: {df_corrected['Strain_a4'].min()}")

    if type == 'GA':
        DT_all = pd.read_excel(temppath, sheet_name=None)
        keys = list(DT_all.keys())
        df_temp_T1 = DT_all[keys[0]]
        df_temp_B = DT_all[keys[1]]
        df_temp_T = DT_all[keys[2]]
        alpha_tot = alpha_T_fibre + alpha_T_steel

        # interpolate to fit strain measurements
        DT_T1 = np.interp(df['Length'], df_temp_T1['Length'], df_temp_T1['RelativeTemp'])
        DT_B = np.interp(df['Length'], df_temp_B['Length'], df_temp_B['RelativeTemp'])
        DT_T = np.interp(df['Length'], df_temp_T['Length'], df_temp_T['RelativeTemp'])

        # correction values Delta_epsilon = alpha_tot * DT
        D_eps_T1 = alpha_tot * DT_T1
        D_eps_B = alpha_tot * DT_B
        D_eps_T = alpha_tot * DT_T

        # subtract correction values from strain measurements
        df_corrected = df.copy()
        df_corrected['Strain_T1'] = df_corrected['Strain_T1'] + D_eps_T1
        df_corrected['Strain_B'] = df_corrected['Strain_B'] + D_eps_B
        df_corrected['Strain_T'] = df_corrected['Strain_T'] + D_eps_T

        if plot:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(12, 6))
            plt.plot(df_corrected['Length'], df_corrected['Strain_T1'], label='Corrected Strain T1', color='blue')
            plt.plot(df_corrected['Length'], df_corrected['Strain_B'], label='Corrected Strain B', color='green')
            plt.plot(df_corrected['Length'], df_corrected['Strain_T'], label='Corrected Strain T', color='red')
            plt.xlabel('Length [m]')
            plt.ylabel('Temperature-Corrected Relative Strain [$10^{-6}$]')
            plt.title('Temperature-Corrected Strain Measurements for GA')
            plt.legend()
            plt.grid()
            plt.show()

            print(f"alpha_1 max: {df_corrected['Strain_a1'].max()}, alpha_1 min: {df_corrected['Strain_a1'].min()}")
            print(f"alpha_2 max: {df_corrected['Strain_a2'].max()}, alpha_2 min: {df_corrected['Strain_a2'].min()}")
            print(f"alpha_3 max: {df_corrected['Strain_a3'].max()}, alpha_3 min: {df_corrected['Strain_a3'].min()}")
            print(f"alpha_4 max: {df_corrected['Strain_a4'].max()}, alpha_4 min: {df_corrected['Strain_a4'].min()}")

    if savepath is not None:
            assert date and date_ref is not None, "Date and reference date must be provided when saving the DataFrame."
            if type == 'BP':
                save(df_corrected, suffix='temp_corrected_strain', savepath=savepath, date=date, date_ref=date_ref, type=type, section=section)
            elif type == 'VP':
                save(df_corrected, suffix='temp_corrected_strain', savepath=savepath, date=date, date_ref=date_ref, type=type, side=side)
            else:
                save(df_corrected, suffix='temp_corrected_strain', savepath=savepath, date=date, date_ref=date_ref, type=type)

    return df_corrected



def correct_angle(df, 
                  alpha: list[float] = [15, 165, 195, 345], 
                  R: float = None, 
                  r: float = None, 
                  type: str = 'BP',
                  plot: bool = False,
                  savepath: str = None, date: str = None, date_ref: str = None, 
                  section: str = None, side: str = None):
    import numpy as np
    import pandas as pd

    """""
    Corrects the strain measurements for angle effects using the provided alpha values. The function applies the correction to the strain measurements based on the specified angles.

    Parameters:
    - df: pandas DataFrame, containing the strain measurements with columns for length and strain at different angles.
    - alpha: list of float, the angle correction coefficients for each strain measurement (default is None).
    - r: float, radius to the sensor in mm.
    - R: float, radius to the outer surface of the cilinder in mm.

    Returns:
    - df_corrected: pandas DataFrame, containing the angle-corrected strain measurements.
    """""

    if type == 'BP':
        assert np.all([a is not None for a in [R, r]]), "Both R and r must be provided for angle correction for type = BP."
        # Isolate moment and axial strain components based on the provided angles
        eps_N_gl = (df['Strain_a1'] + df['Strain_a3']) / 2
        eps_N_gr = (df['Strain_a2'] + df['Strain_a4']) / 2

        ## Moment components for glued fibers
        eps_M_a1 = (df['Strain_a1'] - eps_N_gl)
        eps_M_a3 = (df['Strain_a3'] - eps_N_gl)

        ## Moment components for grouted fibers
        eps_M_a2 = (df['Strain_a2'] - eps_N_gr)
        eps_M_a4 = (df['Strain_a4'] - eps_N_gr)

    if type == 'VP':
        assert alpha is not None, "Alpha values must be provided for VP type."
        assert np.all([a is not None for a in [R, r]]), "Both R and r must be provided for angle correction for type = VP."
        eps_N = (df['Strain_a1'] + df['Strain_a2'] + df['Strain_a3'] + df['Strain_a4']) / 4

        eps_M_a1 = df['Strain_a1'] - eps_N
        eps_M_a2 = df['Strain_a2'] - eps_N
        eps_M_a3 = df['Strain_a3'] - eps_N
        eps_M_a4 = df['Strain_a4'] - eps_N

    if type in ['BP', 'VP']:
        # Calculate the angle corrections based on the provided angles
        D_eps_a_a1 = eps_M_a1 * ((R / (r * np.abs(np.cos(np.radians(alpha[0]))))) - 1)
        D_eps_a_a2 = eps_M_a2 * ((R / (r * np.abs(np.cos(np.radians(alpha[1]))))) - 1)
        D_eps_a_a3 = eps_M_a3 * ((R / (r * np.abs(np.cos(np.radians(alpha[2]))))) - 1)
        D_eps_a_a4 = eps_M_a4 * ((R / (r * np.abs(np.cos(np.radians(alpha[3]))))) - 1)

        # Apply the angle correction to each strain measurement
        df_corrected = df.copy()
        df_corrected['Strain_a1'] = df_corrected['Strain_a1'] + D_eps_a_a1
        df_corrected['Strain_a2'] = df_corrected['Strain_a2'] + D_eps_a_a2
        df_corrected['Strain_a3'] = df_corrected['Strain_a3'] + D_eps_a_a3
        df_corrected['Strain_a4'] = df_corrected['Strain_a4'] + D_eps_a_a4

    if plot:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 6))
        plt.plot(df_corrected['Length'], df_corrected['Strain_a1'], label='Angle-Corrected Strain $\\alpha_1$', color='blue')
        plt.plot(df_corrected['Length'], df_corrected['Strain_a2'], label='Angle-Corrected Strain $\\alpha_2$', color='green')
        plt.plot(df_corrected['Length'], df_corrected['Strain_a3'], label='Angle-Corrected Strain $\\alpha_3$', color='orange')
        plt.plot(df_corrected['Length'], df_corrected['Strain_a4'], label='Angle-Corrected Strain $\\alpha_4$', color='red')
        plt.xlabel('Length [m]')
        plt.ylabel('Angle-Corrected Relative Strain [$10^{-6}$]')
        plt.title('Angle-Corrected Strain Measurements')
        plt.legend()
        plt.grid()
        plt.show()

        print(f"alpha_1 max: {df_corrected['Strain_a1'].max()}, alpha_1 min: {df_corrected['Strain_a1'].min()}")
        print(f"alpha_2 max: {df_corrected['Strain_a2'].max()}, alpha_2 min: {df_corrected['Strain_a2'].min()}")
        print(f"alpha_3 max: {df_corrected['Strain_a3'].max()}, alpha_3 min: {df_corrected['Strain_a3'].min()}")
        print(f"alpha_4 max: {df_corrected['Strain_a4'].max()}, alpha_4 min: {df_corrected['Strain_a4'].min()}")

    if savepath is not None:
        assert date and date_ref is not None, "Date and reference date must be provided when saving the DataFrame."
        if type == 'BP':
            save(df_corrected, suffix='angle_corrected_strain', savepath=savepath, date=date, date_ref=date_ref, type=type, section=section)
        else:
            save(df_corrected, suffix='angle_corrected_strain', savepath=savepath, date=date, date_ref=date_ref, type=type, side=side)

    return df_corrected



def strain_to_NM(df, R_o, R_i=None, type = 'BP', E=210, plot=False, simplified=False,
                 savepath: str = None, date: str = None, date_ref: str = None, 
                 section: str = None, side: str = None):
    import numpy as np
    import pandas as pd
    """
    Convert strain measurements to normal force (N) and bending moment (M) for a given cross-section.

    Parameters:
    - df: pandas DataFrame, containing the strain measurements with columns for length and strain at different angles.
    - R_o: float, outer radius of the cross-section in mm.
    - R_i: float, inner radius of the cross-section in mm, only applicable for type = 'BP'.
    - type: str, type of cross-section ('BP' for tubular pile).

    Returns:
    - df_NM: pandas DataFrame, containing the calculated normal force and bending moment.
    """

    # Cross-sectional properties for tubular piles
    if type == 'BP': 
        assert R_i is not None, "Inner radius (R_i) must be provided for tubular pile (BP) type."

        A = np.pi * (R_o**2 - R_i**2)  # Cross-sectional area of the beam in mm^2
        I = (np.pi / 4) * (R_o**4 - R_i**4)  # Second moment of area for tubular pile in mm^4
        W = I / R_o  # Section modulus for tubular pile in mm^3

    # Crossesctional properties for vibropiles
    elif type == 'VP':
        assert E != 210, "For vibropiles, please provide the correct Young's modulus (E) in GPa."
        assert R_i is None, "Inner radius (R_i) should not be provided for vibropile (VP) type."

        A = np.pi * R_o**2  # Cross-sectional area of the beam in mm^2
        I = (np.pi / 4) * R_o**4  # Second moment of area for solid circular section in mm^4
        W = I / R_o  # Section modulus for solid circular section in mm^3

    # Calculate normal force (N) and bending moment (M) from strain measurements
    if type in ['BP', 'VP']:
        eps_w = (df['Strain_a1'] + df['Strain_a4']) / 2
        eps_l = (df['Strain_a2'] + df['Strain_a3']) / 2

        if simplified:
            eps_w = df['Strain_a1']
            eps_l = df['Strain_a3']

        sigma_w = eps_w * E * 10**-3  # Stress on waterside (MPa)
        sigma_l = eps_l * E * 10**-3 # Stress on landside (MPa)

        M = W * (sigma_w - sigma_l) / 2 * 10**-6 # Bending moment (kNm)
        N = A * (sigma_w + sigma_l) / 2 * 10**-3 # Normal force (kN)

        kappa = (eps_w - eps_l).iloc[::-1] / (R_o)
        dx = df['Length'].diff().fillna(0).iloc[::-1]*1000  # length increments
        U = -np.cumsum(np.cumsum(kappa * dx)*dx).iloc[::-1] *10**-6  # displacement in mm

        if plot == True:
            import matplotlib.pyplot as plt
    
            if type == 'BP':
                print(f"R_o: {R_o:.2f} mm, R_i: {R_i:.2f} mm, E: {E:.2f} GPa")
            elif type == 'VP':
                print(f"R: {R_o:.2f} mm, E: {E:.2f} GPa")
            print(f"I: {I:.2e} mm^4, A: {A:.2e} mm^2, W: {W:.2e} mm^3")
            print(f"Max M: {M.max():.2f} kNm, Min M: {M.min():.2f} kNm, Max N: {N.max():.2f} kN, Min N: {N.min():.2f} kN")
    
            fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    
            axes[0].plot(df['Length'], sigma_w, label='Stress Waterside', color='blue')
            axes[0].plot(df['Length'], sigma_l, label='Stress Landside', color='red')
            axes[0].set_xlabel('Length [m]')
            axes[0].set_ylabel('Stress [MPa]')
            axes[0].legend()
            axes[0].grid()
            
            axes[1].plot(df['Length'], M, label='Bending Moment (M)', color='black')
            axes[1].set_xlabel('Length [m]')
            axes[1].set_ylabel('Bending Moment [kNm]')
            axes[1].legend()
            axes[1].grid()
    
            axes[2].plot(df['Length'], N, label='Normal Force (N)', color='black')
            axes[2].set_xlabel('Length [m]')
            axes[2].set_ylabel('Axial Force [kN]')
            axes[2].legend()
            axes[2].grid()
    
            plt.show()

        df['N'] = N
        df['M'] = M
        df['U'] = U

    if type == 'GA':
        assert R_i and R_o is not None, "Both R_o and R_i must be provided for GA type."
        assert E != 210, "For GA type, please provide the correct Young's modulus (E) in GPa."

        A = np.pi * (R_o**2 - R_i**2)  # Cross-sectional area of the beam in mm^2
        I = (np.pi / 4) * (R_o**4 - R_i**4)  # Second moment of area for tube in mm^4
        W = I / R_o  # Section modulus for tube in mm^3

        eps_T1 = df['Strain_T1']
        eps_B = df['Strain_B']
        eps_T = df['Strain_T']

        sigma_T1 = eps_T1 * E * 10**-3  # Stress on T1 (MPa)
        sigma_B = eps_B * E * 10**-3 # Stress on B (MPa)
        sigma_T = eps_T * E * 10**-3 # Stress on T (MPa)

        N_T1 = A * sigma_T1 * 10**-3 # Normal force on T1 (kN)
        N_B = A * sigma_B * 10**-3 # Normal force on B (kN)
        N_T = A * sigma_T * 10**-3 # Normal force on T (kN)

        if plot:
            import matplotlib.pyplot as plt
            print(f"R_o: {R_o:.2f} mm, E: {E:.2f} GPa")
            print(f"I: {I:.2e} mm^4, A: {A:.2e} mm^2, W: {W:.2e} mm^3")
            print(f"Max N_T1: {N_T1.max():.2f} kN, Min N_T1: {N_T1.min():.2f} kN")
            print(f"Max N_B: {N_B.max():.2f} kN, Min N_B: {N_B.min():.2f} kN")
            print(f"Max N_T: {N_T.max():.2f} kN, Min N_T: {N_T.min():.2f} kN")

            fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
            axes[0].plot(df['Length'], sigma_T1, label='Stress T1', color='blue')
            axes[0].plot(df['Length'], sigma_B, label='Stress B', color='green')
            axes[0].plot(df['Length'], sigma_T, label='Stress T', color='red')
            axes[0].set_xlabel('Length [m]')
            axes[0].set_ylabel('Stress [MPa]')
            axes[0].legend()
            axes[0].grid()

            axes[1].plot(df['Length'], N_T1, label='Normal Force T1', color='blue')
            axes[1].plot(df['Length'], N_B, label='Normal Force B', color='green')
            axes[1].plot(df['Length'], N_T, label='Normal Force T', color='red')
            axes[1].set_xlabel('Length [m]')
            axes[1].set_ylabel('Axial Force [kN]')
            axes[1].legend()
            axes[1].grid()

            

        df['N_T1'] = N_T1
        df['N_B'] = N_B
        df['N_T'] = N_T

    if savepath is not None:
        assert date and date_ref is not None, "Date and reference date must be provided when saving the DataFrame."
        if type == 'BP':
            save(df, suffix='strain_forces', savepath=savepath, date=date, date_ref=date_ref, type=type, section=section)
        else:
            save(df, suffix='strain_forces', savepath=savepath, date=date, date_ref=date_ref, type=type, side=side)

    return df
