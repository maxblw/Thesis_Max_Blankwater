from turtle import pd


def initialize():
    """
    Initialize connections to Plaxis input and output servers. (startup the servers in PLAXIS3D first)

    Returns
    -------
    s_i : object
        Plaxis input state object.
    g_i : object
        Plaxis input geometry object.
    s_o : object
        Plaxis output state object.
    g_o : object
        Plaxis output geometry object.
    """
    from plxscripting.easy import new_server
    # initialize connections to Plaxis servers
    s_i, g_i = new_server('localhost', 10000, password='password')
    s_o, g_o = new_server('localhost', 10001, password='password')

    return s_i, g_i, s_o, g_o

def initialize_logs(run_name):
    import pandas as pd
    import numpy as np
    import os

    """
    Initialize log files for a new run. This will overwrite existing logs for the given run name.
    """

    check = input(f'Are you sure you want to initialize logs for {run_name}? This will OVERWRITE existing logs with the same name. (y/n): ')
    if check.lower() != 'y':
        print('Initialization aborted.')
        return

    # read input coordinates for different measurement sets
    Z = pd.read_csv(f'Logs//Input_coords//BP_Z.csv', index_col='Z').index
    L_T = pd.read_csv(f'Logs//Input_coords//GAT_L.csv', index_col='L').index
    L_B = pd.read_csv(f'Logs//Input_coords//GAB_L.csv', index_col='L').index
    Z_L = pd.read_csv(f'Logs//Input_coords//VPL_Z.csv', index_col='Z').index
    Z_W = pd.read_csv(f'Logs//Input_coords//VPW_Z.csv', index_col='Z').index

    # initialize log files for the run
    os.makedirs(f'Logs/{run_name}', exist_ok=True)

    log_df = pd.DataFrame(columns=['run', 'Time', 'E_A', 'E_B', 'E_C', 'phi_A', 'phi_B', 'phi_C', 'psi_A', 'psi_C', 'NMSE', 'SSE'])
    log_df.to_csv(f'Logs/{run_name}//_{run_name}_mainlog.csv', index=False)

    BP_M = pd.DataFrame({'Z': Z})
    BP_M.to_csv(f'Logs//{run_name}//{run_name}_BP_M.csv', index=False)

    BP_N = pd.DataFrame({'Z': Z})
    BP_N.to_csv(f'Logs//{run_name}//{run_name}_BP_N.csv', index=False)

    BP_U = pd.DataFrame({'Z': Z})
    BP_U.to_csv(f'Logs//{run_name}//{run_name}_BP_U.csv', index=False)

    VPL_M = pd.DataFrame({'Z': Z_L})
    VPL_M.to_csv(f'Logs//{run_name}//{run_name}_VPL_M.csv', index=False)

    VPL_N = pd.DataFrame({'Z': Z_L})
    VPL_N.to_csv(f'Logs//{run_name}//{run_name}_VPL_N.csv', index=False)

    VPL_U = pd.DataFrame({'Z': Z_L})
    VPL_U.to_csv(f'Logs//{run_name}//{run_name}_VPL_U.csv', index=False)

    VPW_M = pd.DataFrame({'Z': Z_W})
    VPW_M.to_csv(f'Logs//{run_name}//{run_name}_VPW_M.csv', index=False)

    VPW_N = pd.DataFrame({'Z': Z_W})
    VPW_N.to_csv(f'Logs//{run_name}//{run_name}_VPW_N.csv', index=False)

    VPW_U = pd.DataFrame({'Z': Z_W})
    VPW_U.to_csv(f'Logs//{run_name}//{run_name}_VPW_U.csv', index=False)

    GAT_results = pd.DataFrame({'L': L_T})
    GAT_results.to_csv(f'Logs//{run_name}//{run_name}_GAT_results.csv', index=False)

    GAB_results = pd.DataFrame({'L': L_B})
    GAB_results.to_csv(f'Logs//{run_name}//{run_name}_GAB_results.csv', index=False)

    # Initialize comparison logs
    L_comp = np.linspace(0, 32.5, 100)
    Z_comp = L_comp - 35.5
    comparison = pd.DataFrame({'Z': Z_comp})
    comparison.to_csv(f'Logs//{run_name}//{run_name}_comparison.csv', index=False)

def run_iteration(run_name, phase_list, s_i, g_i, s_o, g_o, parameters, test = False):
    import pandas as pd
    import numpy as np
    from results_func import get_results

    """
    use this function to run a single iteration of the calibration process.
    Parameters:
    run_name : str
        The name of the current calibration run.
    phase_list : list
        List of phases to run in this iteration.
    s_i : object
        Plaxis input state object.
    g_i : object
        Plaxis input geometry object.
    s_o : object
        Plaxis output state object.
    g_o : object
        Plaxis output geometry object.
    parameters : list
        List of parameters to set for this iteration. of the shape:
        ['E_A', 'E_B', 'E_C', 'phi_A', 'phi_B', 'phi_C', 'psi_A', 'psi_B', 'psi_C']
    test : bool, optional
        If True, run in test mode (default is False).
    """

    set_parameters(s_i, g_i, *parameters)

    if test:
        delta_t = 0
        delta_t = run_calculation(s_i, g_i, [0, 1])
    elif not test:
        delta_t = run_calculation(s_i, g_i, phase_list)

    log_df = pd.read_csv(f'Logs/{run_name}/_{run_name}_mainlog.csv', index_col='run')
    run = log_df.index.max() + 1
    if np.isnan(run):
        run = 0

    # read plaxis output results for each phase an write to logs
    for phase in phase_list:
        if phase >= 4:
            df_BP, df_GA_B, df_GA_T, df_VP_L, df_VP_W = get_results(g_i, g_o, phase)

            BP_M = pd.read_csv(f'Logs/{run_name}/{run_name}_BP_M.csv', index_col='Z')
            BP_N = pd.read_csv(f'Logs/{run_name}/{run_name}_BP_N.csv', index_col='Z')
            BP_U = pd.read_csv(f'Logs/{run_name}/{run_name}_BP_U.csv', index_col='Z')
            BP_M[f'M_{run_name}_P{phase}_R{run}'] = df_BP['M_avg'].reindex(BP_M.index, method='ffill')
            BP_N[f'N_{run_name}_P{phase}_R{run}'] = df_BP['N_avg'].reindex(BP_N.index, method='ffill')
            BP_U[f'U_{run_name}_P{phase}_R{run}'] = df_BP['U_avg'].reindex(BP_U.index, method='ffill')
            BP_M.to_csv(f'Logs/{run_name}/{run_name}_BP_M.csv', index=True)
            BP_N.to_csv(f'Logs/{run_name}/{run_name}_BP_N.csv', index=True)
            BP_U.to_csv(f'Logs/{run_name}/{run_name}_BP_U.csv', index=True)
        
            GAB_N = pd.read_csv(f'Logs/{run_name}/{run_name}_GAB_results.csv', index_col='L')
            GAB_N[f'NB_{run_name}_P{phase}_R{run}'] = df_GA_B['NB'].reindex(GAB_N.index, method='ffill')
            GAB_N.to_csv(f'Logs/{run_name}/{run_name}_GAB_results.csv', index=True)

            GAT_N = pd.read_csv(f'Logs/{run_name}/{run_name}_GAT_results.csv', index_col='L')
            GAT_N[f'NT_{run_name}_P{phase}_R{run}'] = df_GA_T['NT'].reindex(GAT_N.index, method='ffill')
            GAT_N.to_csv(f'Logs/{run_name}/{run_name}_GAT_results.csv', index=True)

            VPL_M = pd.read_csv(f'Logs/{run_name}/{run_name}_VPL_M.csv', index_col='Z')
            VPL_N = pd.read_csv(f'Logs/{run_name}/{run_name}_VPL_N.csv', index_col='Z')
            VPL_U = pd.read_csv(f'Logs/{run_name}/{run_name}_VPL_U.csv', index_col='Z')
            VPL_M[f'M_{run_name}_P{phase}_R{run}'] = df_VP_L['M_avg'].reindex(VPL_M.index, method='ffill')
            VPL_N[f'N_{run_name}_P{phase}_R{run}'] = df_VP_L['N_avg'].reindex(VPL_N.index, method='ffill')
            VPL_U[f'U_{run_name}_P{phase}_R{run}'] = df_VP_L['U_avg'].reindex(VPL_U.index, method='ffill')
            VPL_M.to_csv(f'Logs/{run_name}/{run_name}_VPL_M.csv', index=True)
            VPL_N.to_csv(f'Logs/{run_name}/{run_name}_VPL_N.csv', index=True)
            VPL_U.to_csv(f'Logs/{run_name}/{run_name}_VPL_U.csv', index=True)  

            VPW_M = pd.read_csv(f'Logs/{run_name}/{run_name}_VPW_M.csv', index_col='Z')
            VPW_N = pd.read_csv(f'Logs/{run_name}/{run_name}_VPW_N.csv', index_col='Z')
            VPW_U = pd.read_csv(f'Logs/{run_name}/{run_name}_VPW_U.csv', index_col='Z')
            VPW_M[f'M_{run_name}_P{phase}_R{run}'] = df_VP_W['M_avg'].reindex(VPW_M.index, method='ffill')
            VPW_N[f'N_{run_name}_P{phase}_R{run}'] = df_VP_W['N_avg'].reindex(VPW_N.index, method='ffill')
            VPW_U[f'U_{run_name}_P{phase}_R{run}'] = df_VP_W['U_avg'].reindex(VPW_U.index, method='ffill')
            VPW_M.to_csv(f'Logs/{run_name}/{run_name}_VPW_M.csv', index=True)
            VPW_N.to_csv(f'Logs/{run_name}/{run_name}_VPW_N.csv', index=True)
            VPW_U.to_csv(f'Logs/{run_name}/{run_name}_VPW_U.csv', index=True)
        
            # results_GA_B = pd.read_csv(f'logs/{run_name}_GAB_results.csv', index_col='L')
            # results_GA_B[f'NB_{phase}_{run}'] = df_GA_B['NB'].reindex(results_GA_B.index, method='ffill')
            # results_GA_B.to_csv(f'logs/{run_name}_GAB_results.csv', index=True)

    SSE, RMSE = comparison(run, run_name)

    log_df.loc[run] = [delta_t, 
                       parameters[0], 
                       parameters[1], 
                       parameters[2], 
                       parameters[3], 
                       parameters[4], 
                       parameters[5], 
                       parameters[6],                       
                       parameters[8], SSE, RMSE]
    log_df.to_csv(f'Logs/{run_name}/{run_name}_log.csv', index=True)



def set_parameters(s_i, g_i, E_A, E_B, E_C, phi_A, phi_B, phi_C, psi_A, psi_B,psi_C):
    """
    Sets the material parameters for the given Plaxis input geometry object.

    Parameters:
    s_i : object
        Plaxis input state object.
    g_i : object
        Plaxis input geometry object.
    E_A, E_B, E_C : float
        Young's modulus for materials A, B, and C.
    phi_A, phi_B, phi_C : float
        Friction angle for materials A, B, and C.
    psi_A, psi_B, psi_C : float
        Dilation angle for materials A, B, and C.
    """
    E = [E_A, E_B, E_C]
    phi = [phi_A, phi_B, phi_C]
    psi = [psi_A, psi_B, psi_C]

    idx_soilmat = [15, 1, 3]
    name_soilmat = ['A2', 'B', 'C']

    for i in range(3):
        E_50 = E[i]
        E_oed = E[i]
        if idx_soilmat[i] == 1:
            E_oed = 0.5 * E[i]
        E_ur = 4 * E_50

        g_i.Materials[idx_soilmat[i]].E50Ref = E_50
        g_i.Materials[idx_soilmat[i]].EOedRef = E_oed
        g_i.Materials[idx_soilmat[i]].EURRef = E_ur

        phi_i = phi[i]
        psi_i = psi[i]

        g_i.Materials[idx_soilmat[i]].phi = phi_i
        g_i.Materials[idx_soilmat[i]].psi = psi_i



def run_calculation(s_i, g_i, phase_num):
    from time import time
    import numpy as np
    """
    Runs the calculation for the specified phases in the Plaxis model.

    Parameters:
    s_i : object
        Plaxis input state object.
    g_i : object
        Plaxis input geometry object.
    phase_num : list of int
        List of phase numbers to calculate.

    Returns:
    elapsed_time : float
        Time taken to run the calculation in seconds.
    """

    start = time()

    for n in phase_num:
        phase = g_i.Phases[n]
        g_i.calculate(phase)
    
    end = time()
    elapsed_time = np.round(end - start, 2)
    return elapsed_time

def comparison(run: int, run_name: str):
    import numpy as np
    import pandas as pd

    """
    Creates dataframe used for comparison of calibrations.

    Parameters:
    run (int): The current run number.
    run_name (str): The name of the current run.

    Returns:
    SSE (float): Sum of squared errors.
    RMSE (float): Root mean squared error.
    """

    inclino = pd.read_csv("..\\..\\Data\\Measurements\\comparison_inclino.csv", index_col='Z')
    inclino['L'] = inclino.index + 35.5

    # import coordinates for comparison
    U_read = pd.read_csv(f'Logs\\{run_name}\\{run_name}_BP_U.csv', index_col='Z')
    U_read['L'] = U_read.index + 35.5

    phase_0 = 4
    phase_1 = 8

    #import main comparison file
    comp_total = pd.read_csv(f'Logs\\{run_name}\\{run_name}_comparison.csv', index_col='Z')
    Z = comp_total.index
    L = Z + 35.5

    U_read['U_cor'] = U_read[f'U_{run_name}_P{phase_1}_R{run}'] - U_read[f'U_{run_name}_P{phase_0}_R{run}']
    U_read['U_cor'] = U_read['U_cor'] - U_read['U_cor'].iloc[0]

    df_comp = pd.DataFrame({'Z': Z, 'L': L})
    df_comp['U_cor'] = np.interp(df_comp['L'], U_read['L'], U_read['U_cor'])

    inclino.sort_values('L', inplace=True)
    df_comp['U_inclino'] = np.interp(df_comp['L'], inclino['L'], inclino['U_inclino'])
    df_comp.drop(columns=['L'], inplace=True)

    df_comp['error'] = df_comp['U_cor'] - df_comp['U_inclino']
    df_comp['norm_squared_error'] = (df_comp['error'] / df_comp['U_inclino'])**2
    df_comp.set_index('Z', inplace=True)

    comp_total = pd.read_csv(f'Logs\\{run_name}\\{run_name}_comparison.csv', index_col='Z')
    comp_total[f"U_cor_R{run}"] = U_read['U_cor']
    comp_total[f"U_inclino_R{run}"] = df_comp['U_inclino']
    comp_total[f"error_R{run}"] = df_comp['error']
    comp_total[f"norm_squared_error_R{run}"] = df_comp['norm_squared_error']
    comp_total.to_csv(f'Logs\\{run_name}\\{run_name}_comparison.csv', index=True)

    SSE = np.sum(df_comp['norm_squared_error'])
    RMSE = np.sqrt(np.mean(df_comp['error']**2))
    return SSE, RMSE