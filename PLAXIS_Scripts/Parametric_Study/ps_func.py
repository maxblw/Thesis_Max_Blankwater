def initialize():
    from plxscripting.easy import new_server
    s_i, g_i = new_server('localhost', 10000, password='password')
    s_o, g_o = new_server('localhost', 10001, password='password')

    return s_i, g_i, s_o, g_o



def initialize_logs(run_name):
    import pandas as pd
    import numpy as np
    import os

    prompt = input(f"Initializing logs for run '{run_name}'. input y to continue, n to cancel: ")
    if prompt.lower() != 'y':
        print("Initialization cancelled.")
        return

    Z = pd.read_csv(f'..//..//Data//Input_coords//BP_Z.csv', index_col='Z').index
    L_T = pd.read_csv(f'..//..//Data//Input_coords//GAT_L.csv', index_col='L').index
    L_B = pd.read_csv(f'..//..//Data//Input_coords//GAB_L.csv', index_col='L').index
    Z_L = pd.read_csv(f'..//..//Data//Input_coords//VPL_Z.csv', index_col='Z').index
    Z_W = pd.read_csv(f'..//..//Data//Input_coords//VPW_Z.csv', index_col='Z').index

    os.makedirs(f'Logs//{run_name}', exist_ok=True)

    log_df = pd.DataFrame(columns=['run','time' ,'wl', 'd_level'])
    log_df.to_csv(f'Logs//{run_name}//_{run_name}_mainlog.csv', index=False)

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

def run_iteration(run_name, phase_list, s_i, g_i, s_o, g_o, parameters, test = False):
    import pandas as pd
    import numpy as np
    from results_func import get_results

    set_parameters(s_i, g_i, parameters)
    if test:
        delta_t = 0
        delta_t = run_calculation(s_i, g_i, [0])
    elif not test:
        delta_t = run_calculation(s_i, g_i, phase_list)

    log_df = pd.read_csv(f'Logs//{run_name}//_{run_name}_mainlog.csv', index_col='run')
    run = log_df.index.max() + 1
    if np.isnan(run):
        run = 0

    for phase in phase_list:
        if phase >= 4:
            df_BP, df_GA_B, df_GA_T, df_VP_L, df_VP_W = get_results(g_i, g_o, phase)

            BP_M = pd.read_csv(f'logs/BP/{run_name}_BP_M.csv', index_col='Z')
            BP_N = pd.read_csv(f'logs/BP/{run_name}_BP_N.csv', index_col='Z')
            BP_U = pd.read_csv(f'logs/BP/{run_name}_BP_U.csv', index_col='Z')
            BP_M[f'M_{run_name}_P{phase}_R{run}'] = df_BP['M_avg'].reindex(BP_M.index, method='ffill')
            BP_N[f'N_{run_name}_P{phase}_R{run}'] = df_BP['N_avg'].reindex(BP_N.index, method='ffill')
            BP_U[f'U_{run_name}_P{phase}_R{run}'] = df_BP['U_avg'].reindex(BP_U.index, method='ffill')
            BP_M.to_csv(f'logs/BP/{run_name}_BP_M.csv', index=True)
            BP_N.to_csv(f'logs/BP/{run_name}_BP_N.csv', index=True)
            BP_U.to_csv(f'logs/BP/{run_name}_BP_U.csv', index=True)
        
            GAB_N = pd.read_csv(f'logs/GAB/{run_name}_GAB_results.csv', index_col='L')
            GAB_N[f'NB_{run_name}_P{phase}_R{run}'] = df_GA_B['NB'].reindex(GAB_N.index, method='ffill')
            GAB_N.to_csv(f'logs/GAB/{run_name}_GAB_results.csv', index=True)

            GAT_N = pd.read_csv(f'logs/GAT/{run_name}_GAT_results.csv', index_col='L')
            GAT_N[f'NT_{run_name}_P{phase}_R{run}'] = df_GA_T['NT'].reindex(GAT_N.index, method='ffill')
            GAT_N.to_csv(f'logs/GAT/{run_name}_GAT_results.csv', index=True)

            VPL_M = pd.read_csv(f'logs/VPL/{run_name}_VPL_M.csv', index_col='Z')
            VPL_N = pd.read_csv(f'logs/VPL/{run_name}_VPL_N.csv', index_col='Z')
            VPL_U = pd.read_csv(f'logs/VPL/{run_name}_VPL_U.csv', index_col='Z')
            VPL_M[f'M_{run_name}_P{phase}_R{run}'] = df_VP_L['M_avg'].reindex(VPL_M.index, method='ffill')
            VPL_N[f'N_{run_name}_P{phase}_R{run}'] = df_VP_L['N_avg'].reindex(VPL_N.index, method='ffill')
            VPL_U[f'U_{run_name}_P{phase}_R{run}'] = df_VP_L['U_avg'].reindex(VPL_U.index, method='ffill')
            VPL_M.to_csv(f'logs/VPL/{run_name}_VPL_M.csv', index=True)
            VPL_N.to_csv(f'logs/VPL/{run_name}_VPL_N.csv', index=True)
            VPL_U.to_csv(f'logs/VPL/{run_name}_VPL_U.csv', index=True)  

            VPW_M = pd.read_csv(f'logs/VPW/{run_name}_VPW_M.csv', index_col='Z')
            VPW_N = pd.read_csv(f'logs/VPW/{run_name}_VPW_N.csv', index_col='Z')
            VPW_U = pd.read_csv(f'logs/VPW/{run_name}_VPW_U.csv', index_col='Z')
            VPW_M[f'M_{run_name}_P{phase}_R{run}'] = df_VP_W['M_avg'].reindex(VPW_M.index, method='ffill')
            VPW_N[f'N_{run_name}_P{phase}_R{run}'] = df_VP_W['N_avg'].reindex(VPW_N.index, method='ffill')
            VPW_U[f'U_{run_name}_P{phase}_R{run}'] = df_VP_W['U_avg'].reindex(VPW_U.index, method='ffill')
            VPW_M.to_csv(f'logs/VPW/{run_name}_VPW_M.csv', index=True)
            VPW_N.to_csv(f'logs/VPW/{run_name}_VPW_N.csv', index=True)
            VPW_U.to_csv(f'logs/VPW/{run_name}_VPW_U.csv', index=True)
        
            # results_GA_B = pd.read_csv(f'logs/{run_name}_GAB_results.csv', index_col='L')
            # results_GA_B[f'NB_{phase}_{run}'] = df_GA_B['NB'].reindex(results_GA_B.index, method='ffill')
            # results_GA_B.to_csv(f'logs/{run_name}_GAB_results.csv', index=True)

    log_df.loc[run] = [delta_t, 
                       parameters[0], 
                       parameters[1]]
    log_df.to_csv(f'logs/{run_name}_log.csv', index=True)

def run_calculation(s_i, g_i, phase_num):
    from time import time
    import numpy as np
    g_i.gotostages()
    start = time()

    for n in phase_num:
        phase = g_i.Phases[n]
        g_i.calculate(phase)
    
    end = time()
    elapsed_time = np.round(end - start, 2)
    return elapsed_time


def set_parameters(s_i, g_i, parameters):
    wl = parameters[0]
    d_level = parameters[1]

    assert d_level <= -16.5 and d_level > -29, "d_level must be between -29 and -16"

    g_i.gotostructures() 

    holes = g_i.boreholes
    for borehole in holes:
        borehole.Head = wl

    surfaces = g_i.surfaces
    for surface in surfaces:
        if surface.Name == "dredged_surface":
            if surface.z != d_level:
                surface.z = d_level

                g_i.gotomesh()
                g_i.mesh()

                

def set_soil_parameters(s_i, g_i, E_A, E_B, E_C, phi_A, phi_B, phi_C, psi_A, psi_C):
    E = [E_A, E_B, E_C]
    phi = [phi_A, phi_B, phi_C]
    psi = [psi_A, 0, psi_C]

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