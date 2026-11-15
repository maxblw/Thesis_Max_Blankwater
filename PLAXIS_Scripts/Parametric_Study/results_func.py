
def get_results(g_i, g_o, phase):
    import pandas as pd
    g_i.view(g_i.Phases[phase])
    df_BP = get_BP_results(g_o, phase)
    df_GA_B = get_GA_results(g_o, phase, 'B')
    df_GA_T = get_GA_results(g_o, phase, 'T')

    df_GA_B.rename(columns={'N_avg': 'NB'}, inplace=True)
    df_GA_T.rename(columns={'N_avg': 'NT'}, inplace=True)

    df_VP_L = get_VP_results(g_o, phase, 'L')
    df_VP_W = get_VP_results(g_o, phase, 'W')

    g_o.close()
    return df_BP, df_GA_B, df_GA_T, df_VP_L, df_VP_W

def get_BP_results(g_o, phase_num):
    import pandas as pd
    import numpy as np
    from plxscripting.easy import new_server
    import datetime

    """
    Imports the results for tubular piles with the name "Tubular_Pile" from PLAXIS and saves them in a csv file. The results are averaged over all tubular piles in the model.
    """
    assert phase_num in [4, 5, 6, 7, 8, 9, 10], "phase must contain a sheet pile"
    phase = g_o.Phases[phase_num]

    allplates = g_o.plates
    allBP = []
    for plate in allplates:
        mat = []
        for segment in plate:
            mat.append(str(segment.Material.Name)) 
        if all(segmat == "Tubular_Pile" for segmat in mat):
            allBP.append(plate)
            # print(f"Plate {plate.Name} has uniform material: {mat[0]}")
    
    assert len(allBP) > 0, "No Tubular_Pile found in the model."

    Z = g_o.getresults(allBP[0], phase, g_o.ResultTypes.Plate.Z, "node")

    df_Uy = pd.DataFrame({'Z': Z}).groupby('Z').mean().reset_index()
    df_M22 = pd.DataFrame({'Z': Z}).groupby('Z').mean().reset_index()
    df_N22 = pd.DataFrame({'Z': Z}).groupby('Z').mean().reset_index()

    for BP in allBP:
        # print(f"Processing {BP.Name}...")
        Z_temp = g_o.getresults(BP, phase, g_o.ResultTypes.Plate.Z, "node")

        Uy = g_o.getresults(BP, phase, g_o.ResultTypes.Plate.Uy, "node")
        df_temp = pd.DataFrame({'Z': Z_temp, f'Uy_{BP.Name}': Uy}).groupby('Z').mean().reset_index()
        df_Uy[f'Uy_{BP.Name}'] = np.interp(df_Uy['Z'], df_temp['Z'], df_temp[f'Uy_{BP.Name}'])
        df_Uy[f'Uy_{BP.Name}'] = -df_Uy[f'Uy_{BP.Name}'] *1000

        M22 = g_o.getresults(BP, phase, g_o.ResultTypes.Plate.M22, "node")
        df_temp = pd.DataFrame({'Z': Z_temp, f'M22_{BP.Name}': M22}).groupby('Z').mean().reset_index()
        df_M22[f'M22_{BP.Name}'] = -np.interp(df_M22['Z'], df_temp['Z'], df_temp[f'M22_{BP.Name}']) * 1.42 ## times width of pile

        N22 = g_o.getresults(BP, phase, g_o.ResultTypes.Plate.N22, "node")
        df_temp = pd.DataFrame({'Z': Z_temp, f'N22_{BP.Name}': N22}).groupby('Z').mean().reset_index()
        df_N22[f'N22_{BP.Name}'] = np.interp(df_N22['Z'], df_temp['Z'], df_temp[f'N22_{BP.Name}']) * 1.42 ## times width of pile

    df_Uy['U_avg'] = df_Uy.iloc[:, 1:].mean(axis=1)
    df_M22['M_avg'] = df_M22.iloc[:, 1:].mean(axis=1)
    df_N22['N_avg'] = df_N22.iloc[:, 1:].mean(axis=1)

    df_BP = pd.DataFrame({
        'Z': df_Uy['Z'],
        'U_avg': df_Uy['U_avg'],
        'M_avg': df_M22['M_avg'],
        'N_avg': df_N22['N_avg']
    })
    df_BP.set_index('Z', inplace=True)
    return df_BP

def get_GA_results(g_o, phase_num, row):
    import pandas as pd
    import numpy as np

    """
    Imports the results for tubular piles with the name "Tubular_Pile" from PLAXIS and saves them in a csv file. The results are averaged over all tubular piles in the model.
    """

    assert row in ['B', 'T'], "Row must be either 'B' or 'T'"

    phase = g_o.Phases[phase_num]

    allbeams = g_o.embeddedbeams
    allGA = []
    for beam in allbeams:
        mat = []
        for segment in beam:
            mat.append(str(segment.Material.Name)) 
        if all(segmat == f"Grouted_{row}" for segmat in mat):
            allGA.append(beam)

    assert len(allGA) > 0, f"No Grouted_{row} found in the model."

    Y0 = g_o.getresults(allGA[0], phase, g_o.ResultTypes.EmbeddedBeam.Y, "node")
    Z0 = g_o.getresults(allGA[0], phase, g_o.ResultTypes.EmbeddedBeam.Z, "node")
    L = np.abs(np.sqrt((np.array(Z0) - Z0[0])**2 + (np.array(Y0) - Y0[0])**2))
    df_BN = pd.DataFrame({'L': L}).groupby('L').mean().reset_index()

    for GA in allGA:
        Z_temp = g_o.getresults(GA, phase, g_o.ResultTypes.EmbeddedBeam.Z, "node")
        Y_temp = g_o.getresults(GA, phase, g_o.ResultTypes.EmbeddedBeam.Y, "node")
        L_temp = np.abs(np.sqrt((np.array(Z_temp) - Z_temp[0])**2 + (np.array(Y_temp) - Y_temp[0])**2))
        N = g_o.getresults(GA, phase, g_o.ResultTypes.EmbeddedBeam.N, "node")
        df_BN[f'N_{GA.Name}'] = np.interp(df_BN['L'], L_temp, N)
    df_BN['N_avg'] = df_BN.iloc[:, 1:].mean(axis=1)
    df_BN.drop(columns=df_BN.columns[1:-1], inplace=True)
        
    return df_BN

def get_VP_results(g_o, phase_num, row):
    import pandas as pd
    import numpy as np
    from plxscripting.easy import new_server
    import datetime

    """
    Imports the results for tubular piles with the name "Tubular_Pile" from PLAXIS and saves them in a csv file. The results are averaged over all tubular piles in the model.
    phase_num: int, the phase number to import results from
    row: str, the row identifier for the VP results either 'L' or 'W'
    server_id: int, the server id of the PLAXIS model
    password: str, the password for the PLAXIS server
    model_name: str, the name of the model
    """

    assert row in ['L', 'W'], "Row must be either 'L' or 'W'"

    phase = g_o.Phases[phase_num]

    allbeams = g_o.embeddedbeams
    allVP = []
    for beam in allbeams:
        mat = []
        for segment in beam:
            mat.append(str(segment.Material.Name)) 
        if all(segmat == f"Vibropile_{row}" for segmat in mat):
            allVP.append(beam)
    # Y0 = g_o.getresults(allVP[0], phase, g_o.ResultTypes.EmbeddedBeam.Y, "node")
    Z0 = g_o.getresults(allVP[0], phase, g_o.ResultTypes.EmbeddedBeam.Z, "node")
    # L = np.abs(np.sqrt((np.array(Z0) - Z0[0])**2 + (np.array(Y0) - Y0[0])**2))
    df_BN = pd.DataFrame({'Z': Z0}).groupby('Z').mean().reset_index()
    df_M2 = pd.DataFrame({'Z': Z0}).groupby('Z').mean().reset_index()
    df_Utot = pd.DataFrame({'Z': Z0}).groupby('Z').mean().reset_index()

    assert len(allVP) > 0, f"No Vibropile_{row} found in the model."

    for VP in allVP:
        Z_temp = g_o.getresults(VP, phase, g_o.ResultTypes.EmbeddedBeam.Z, "node")
        # Y_temp = g_o.getresults(VP, phase, g_o.ResultTypes.EmbeddedBeam.Y, "node")
        # L_temp = np.abs(np.sqrt((np.array(Z_temp) - Z_temp[0])**2 + (np.array(Y_temp) - Y_temp[0])**2))
        N = g_o.getresults(VP, phase, g_o.ResultTypes.EmbeddedBeam.N, "node")
        M2 = g_o.getresults(VP, phase, g_o.ResultTypes.EmbeddedBeam.M2, "node")
        Utot = g_o.getresults(VP, phase, g_o.ResultTypes.EmbeddedBeam.Uy, "node")
        df_temp = pd.DataFrame({'Z': Z_temp, f'N_{VP.Name}': N, f'M2_{VP.Name}': M2, f'Utot_{VP.Name}': Utot}).groupby('Z').mean().reset_index()
        df_BN[f'N_{VP.Name}'] = np.interp(df_BN['Z'], df_temp['Z'], df_temp[f'N_{VP.Name}'])
        df_M2[f'M2_{VP.Name}'] = np.interp(df_M2['Z'], df_temp['Z'], df_temp[f'M2_{VP.Name}'])
        df_Utot[f'Utot_{VP.Name}'] = -np.interp(df_Utot['Z'], df_temp['Z'], df_temp[f'Utot_{VP.Name}']) * 1000
        # df_Utot[f'Utot_{VP.Name}'] = df_Utot[f'Utot_{VP.Name}'] - df_Utot[f'Utot_{VP.Name}'].iloc[-1]


    df_BN['N_avg'] = df_BN.iloc[:, 1:].mean(axis=1)
    df_M2['M_avg'] = df_M2.iloc[:, 1:].mean(axis=1)
    df_Utot['U_avg'] = df_Utot.iloc[:, 1:].mean(axis=1)

    df_VP = pd.DataFrame({
        'Z': df_BN['Z'],
        'N_avg': df_BN['N_avg'],
        'M_avg': df_M2['M_avg'],
        'U_avg': df_Utot['U_avg']
    })
    df_VP.set_index('Z', inplace=True)

    return df_VP