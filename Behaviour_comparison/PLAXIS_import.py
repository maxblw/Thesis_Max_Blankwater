from datetime import datetime


def get_BP_results(phase_num: int, server_id: int = 10001, password: str = 'W#D=Mygg5NxK#xw^', model_name: str = 'model_3', verbose: bool = False, embbeam=False):
    import pandas as pd
    import numpy as np
    from plxscripting.easy import new_server
    import datetime

    """
    Imports the results for tubular piles with the name "Tubular_Pile" from PLAXIS and saves them in a csv file. The results are averaged over all tubular piles in the model.
    phase_num: int, the phase number to import results from
    server_id: int, the server id of the PLAXIS model
    password: str, the password for the PLAXIS server
    """

    s_o, g_o = new_server('localhost', server_id, password=password)
    phase = g_o.Phases[phase_num]

    if verbose:
        print(f"processing BP results for {phase}...")

    allplates = g_o.plates
    allBP = []
    allBPbeams = []

    for plate in allplates:
        mat = []
        for segment in plate:
            mat.append(str(segment.Material.Name)) 
        if all(segmat == "Tubular_Pile" for segmat in mat):
            allBP.append(plate)
            # print(f"Plate {plate.Name} has uniform material: {mat[0]}")
    
    assert len(allBP) > 0, "No Tubular_Pile found in the model."

    Z = g_o.getresults(allBP[0], phase, g_o.ResultTypes.Plate.Z, "node")

    if embbeam:
        allbeams = g_o.embeddedbeams
        for beam in allbeams:
            mat = []
            for segment in beam:
                mat.append(str(segment.Material.Name)) 
            if all(segmat == "CombiwallPile" for segmat in mat):
                allBPbeams.append(beam)
                # print(f"Beam {beam.Name} has uniform material: {mat[0]}")
        assert len(allBPbeams) > 0, "No Combiwall pile as embedded beam found in the model."
        Z_emb = g_o.getresults(allBPbeams[0], phase, g_o.ResultTypes.EmbeddedBeam.Z, "node")

        df_Uy_emb = pd.DataFrame({'Z': Z_emb}).groupby('Z').mean().reset_index()
        df_M22_emb = pd.DataFrame({'Z': Z_emb}).groupby('Z').mean().reset_index()
        df_N22_emb = pd.DataFrame({'Z': Z_emb}).groupby('Z').mean().reset_index()

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

    BP_names = [BP.Name for BP in allBP]
    if embbeam:
        for i, BP in enumerate(allBPbeams):
            BP_name = BP_names[i]
            # print(f"Processing {BP.Name}...")
            Z_temp = g_o.getresults(BP, phase, g_o.ResultTypes.EmbeddedBeam.Z, "node")

            Uy = g_o.getresults(BP, phase, g_o.ResultTypes.EmbeddedBeam.Uy, "node")
            df_temp = pd.DataFrame({'Z': Z_temp, f'Uy_{BP_name}': Uy}).groupby('Z').mean().reset_index()
            df_Uy_emb[f'Uy_{BP_name}'] = np.interp(df_Uy_emb['Z'], df_temp['Z'], df_temp[f'Uy_{BP_name}'])
            df_Uy_emb[f'Uy_{BP_name}'] = -df_Uy_emb[f'Uy_{BP_name}']*1000

            M22 = g_o.getresults(BP, phase, g_o.ResultTypes.EmbeddedBeam.M2, "node")
            df_temp = pd.DataFrame({'Z': Z_temp, f'M22_{BP_name}': M22}).groupby('Z').mean().reset_index()
            df_M22_emb[f'M22_{BP_name}'] = -np.interp(df_M22_emb['Z'], df_temp['Z'], df_temp[f'M22_{BP_name}'])  ## times width of pile
            N22 = g_o.getresults(BP, phase, g_o.ResultTypes.EmbeddedBeam.N, "node")
            df_temp = pd.DataFrame({'Z': Z_temp, f'N22_{BP_name}': N22}).groupby('Z').mean().reset_index()
            df_N22_emb[f'N22_{BP_name}'] = np.interp(df_N22_emb['Z'], df_temp['Z'], df_temp[f'N22_{BP_name}']) ## times width of pile

        df_Uy_emb['U_avg'] = df_Uy_emb.iloc[:, 1:].mean(axis=1)
        df_M22_emb['M_avg'] = df_M22_emb.iloc[:, 1:].mean(axis=1)
        df_N22_emb['N_avg'] = df_N22_emb.iloc[:, 1:].mean(axis=1)

        df_Uy = pd.concat([df_Uy, df_Uy_emb], axis=0)
        df_M22 = pd.concat([df_M22, df_M22_emb], axis=0)
        df_N22 = pd.concat([df_N22, df_N22_emb], axis=0)

        df_Uy.drop_duplicates(subset='Z', keep='first', inplace=True)
        df_M22.drop_duplicates(subset='Z', keep='first', inplace=True)
        df_N22.drop_duplicates(subset='Z', keep='first', inplace=True)
    
    # for column in df.columns[1:]:
    #     if column.startswith('Uy_'):
    #         plt.plot(df[column], df['Z'], label=column, alpha=0.5)
    df_Uy.sort_values('Z', inplace=True, ascending=False)
    df_Uy.to_csv(f'out/{model_name}/BP_deform_{model_name}_{phase.Name}.csv', index=False)
    df_M22.sort_values('Z', inplace=True, ascending=False)
    df_N22.sort_values('Z', inplace=True, ascending=False)
    df_M22.to_csv(f'out/{model_name}/BP_moment_{model_name}_{phase.Name}.csv', index=False)
    df_N22.to_csv(f'out/{model_name}/BP_axial_{model_name}_{phase.Name}.csv', index=False)

    metadata = {
        'files': f'out/{model_name}/BP_{model_name}_{phase.Name}.csv',
        'phase': f'phase {str(phase.Name)}',
        'retrieved date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'model_name': model_name
    }

    with open(f'out/{model_name}/BP_{model_name}_{phase.Name}_metadata.yaml', 'w') as f:
        import yaml
        yaml.dump(metadata, f)

def get_GA_results(phase: int, row: str, server_id: int = 10001, password: str = 'W#D=Mygg5NxK#xw^', model_name: str = 'model_3', verbose: bool = False):
    import pandas as pd
    import numpy as np
    from plxscripting.easy import new_server
    import datetime

    """
    Imports the results for tubular piles with the name "Tubular_Pile" from PLAXIS and saves them in a csv file. The results are averaged over all tubular piles in the model.
    phase: int, the phase number to import results from
    server_id: int, the server id of the PLAXIS model
    password: str, the password for the PLAXIS server
    row: str, the row identifier for the GA results either 'B' or 'T'
    """

    assert row in ['B', 'T'], "Row must be either 'B' or 'T'"

    s_o, g_o = new_server('localhost', server_id, password=password)
    phase = g_o.Phases[phase]

    if verbose:
        print(f"processing GA results for {phase.Name}...")

    allbeams = g_o.embeddedbeams
    allGA = []
    for beam in allbeams:
        mat = []
        for segment in beam:
            mat.append(str(segment.Material.Name)) 
        if all(f"Grouted_{row}" in segmat for segmat in mat):
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

    df_BN.to_csv(f'out/{model_name}/GA_{row}_axial_{model_name}_{phase.Name}.csv', index=False)

    metadata = {
            'files': f'out/{model_name}/GA_{row}_axial_{model_name}_{phase.Name}.csv',
            'phase': f'phase {str(phase.Name)}',
            'row': row,
            'retrieved date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'model_name': model_name
        }

    with open(f'out/{model_name}/GA_{row}_{model_name}_{phase.Name}_metadata.yaml', 'w') as f:
        import yaml
        yaml.dump(metadata, f)
    return df_BN

def get_VP_results(phase_num: int, row: str, server_id: int = 10001, password: str = 'W#D=Mygg5NxK#xw^', model_name: str = 'model_3', verbose: bool = False):
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

    s_o, g_o = new_server('localhost', server_id, password=password)
    phase = g_o.Phases[phase_num]
    if verbose:
        print(f"processing VP results for {phase.Name}...")

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
        if verbose:
            print(f"Processing {VP.Name}...")
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
    for df in [df_BN, df_M2, df_Utot]:
        # df['Z'] = df['Z'] - 0.5
        # df = df.loc[df['Z'] >= 0].copy()
        if df is df_BN:
            df_BN = df
        elif df is df_M2:
            df_M2 = df
        elif df is df_Utot:
            df_Utot = df
    
    df_BN.to_csv(f'out/{model_name}/VP_{row}_axial_{model_name}_{phase.Name}.csv', index=False)
    df_M2.to_csv(f'out/{model_name}/VP_{row}_moment_{model_name}_{phase.Name}.csv', index=False)
    df_Utot.to_csv(f'out/{model_name}/VP_{row}_deform_{model_name}_{phase.Name}.csv', index=False)

    metadata = {
        'files': f'out/{model_name}/VP_{row}_{model_name}_{phase.Name}.csv',
        'phase': f'phase {str(phase.Name)}',
        'row': row,
        'retrieved date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'model_name': model_name
    }

    with open(f'out/{model_name}/VP_{row}_{model_name}_{phase.Name}_metadata.yaml', 'w') as f:
        import yaml
        yaml.dump(metadata, f)

def read_plaxis(phases, server_id: int = 10001, password: str = 'W#D=Mygg5NxK#xw^', model_name: str = 'model_3', grout_bodies: bool = True, verbose: bool = False, embbeam=False):
    for p in phases:
        if p>=2:
            get_BP_results(p, server_id=10001, password='W#D=Mygg5NxK#xw^', model_name=model_name, embbeam=embbeam)

            get_VP_results(p, row='L', server_id=10001, password='W#D=Mygg5NxK#xw^', model_name=model_name)
            get_VP_results(p, row='W', server_id=10001, password='W#D=Mygg5NxK#xw^', model_name=model_name)

        if p>=4 and grout_bodies:
            get_GA_results(p, row='B', server_id=10001, password='W#D=Mygg5NxK#xw^', model_name=model_name)
            get_GA_results(p, row='T', server_id=10001, password='W#D=Mygg5NxK#xw^', model_name=model_name)