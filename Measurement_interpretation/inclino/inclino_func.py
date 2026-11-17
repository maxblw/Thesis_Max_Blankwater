def setup_inclino_file(filename, originpath):
    """
    Sets up the inclino file by extracting the relevant columns and saving them to a new CSV file.

    Parameters:
    -------
    filename: str, 
        path to save the processed inclino measurements CSV file
    originpath: str, 
        path to the original inclino measurements Excel file
    """
    import pandas as pd
    import numpy as np

    df_temp = pd.read_excel(originpath)
    df = pd.DataFrame()
    date = df_temp['DateTime'].unique()[0]
    df['Z'] = df_temp[df_temp['DateTime'] == date]['Real Shape XZ Y']
    # df['Z'] = df['Z'] - df['Z'].iloc[-1]

    for date in df_temp['DateTime'].unique():
        X = df_temp[df_temp['DateTime'] == date]['Real Shape XZ X'].values
        Y = df_temp[df_temp['DateTime'] == date]['Real Shape YZ X'].values
        df[f'{date}_X'] = X
        df[f'{date}_Y'] = Y
    df.to_csv(filename, index=False)
    return df



def add_raw_inclino_measurements(measpath, rawpath):
    import pandas as pd
    import numpy as np

    """
    Adds raw inclino measurements from measpath to the raw inclino measurements in rawpath.

    Parameters:
    -------
    measpath: str, 
        path to the raw inclino measurements Excel file to add
    rawpath: str, 
        path to the existing raw inclino measurements CSV file

    Returns:
    -------
    df: pandas DataFrame
        the updated raw inclino measurements including the added measurements from measpath
    """

    df = pd.read_csv(rawpath)
    df_temp = pd.read_excel(measpath)
    for date in df_temp['DateTime'].unique():
        if not str(date) in df.columns:
            X = df_temp[df_temp['DateTime'] == date]['Real Shape XZ X'].values
            Y = df_temp[df_temp['DateTime'] == date]['Real Shape YZ X'].values
            df[f'{date}_X'] = np.interp(df['Z'], df_temp[df_temp['DateTime'] == date]['Real Shape XZ Y'], X)
            df[f'{date}_Y'] = np.interp(df['Z'], df_temp[df_temp['DateTime'] == date]['Real Shape XZ Y'], Y)
    df.to_csv(rawpath, index=False)
    return df     



def reference_inclino_measurements(rawpath, outpath, ref_date, type='X'):
    import pandas as pd
    """
    References the inclino measurements in rawpath to the measurements at ref_date and saves the referenced measurements in outpath.
    Parameters:
    -------
    type: str, 
        either 'X' or 'vector', if 'X' the X measurements are referenced, 
        if 'vector' the vector magnitude of the X and Y measurements is referenced. 
        Please use X only for the tubular pile Saaf measurements.
    rawpath: str, 
        path to the raw inclino measurements csv file
    outpath: str, 
        path to save the referenced inclino measurements csv file
    ref_date: str, 
        the date to reference the measurements to, in the format 'dd-mm-yyyy hh:mm:ss'

    Returns:
    -------
    df_out: pandas DataFrame
        the referenced inclino measurements
    """ 
    assert type in ['X', 'vector'], "type must be either 'X' or 'vector'"
    X = None
    Y = None

    # import raw inclino measurements
    df = pd.read_csv(rawpath)
    assert f'{ref_date}_X' in df.columns, f"ref_date {ref_date} not found in rawpath {rawpath}"
    df_out = pd.DataFrame()
    df_out['Z'] = df['Z']

    # initialize output DataFrame with Z values
    if type == 'X':
        for column in df.drop(['Z'], axis=1).columns:
            if column.endswith('_X'):
                df_out[column[:-2]] = df[column] - df[ref_date + '_X']
    # calculate vector magnitude of X and Y combined
    elif type == 'vector':
        for column in df.drop(['Z'], axis=1).columns:
            if column.endswith('_X'):
                X = df[column] - df[ref_date + '_X']
            elif column.endswith('_Y'):
                Y = df[column] - df[ref_date + '_Y']
            if (X is not None) and (Y is not None):
                df_out[column[:-2]] = (X**2 + Y**2)**0.5
                X = None
                Y = None
    df_out.to_csv(outpath, index=False)
    return df_out

def add_to_former(formerpath, latterpath, outpath, ref_date):
    """
    Adds the inclino measurements from the latter file to the former file, referencing the latter measurements to the ref_date.
    Parameters:
    -------
    formerpath: str,
        path to the former inclino measurements csv file
    latterpath: str,
        path to the latter inclino measurements csv file
    outpath: str,
        path to save the combined inclino measurements csv file
    ref_date: str,
        the date to reference the latter measurements to, in the format 'dd-mm-yyyy hh:mm:ss'
    """
    import pandas as pd
    import numpy as np
    
    df_former = pd.read_csv(formerpath)
    df_latter = pd.read_csv(latterpath)
    df = pd.DataFrame()
    df['Z'] = df_latter['Z']
    for column in df_latter.drop(['Z'], axis=1).columns:
        df[column] = df_latter[column] + np.interp(df['Z'], df_former['Z'], df_former[ref_date])
    df.to_csv(outpath, index=False)

def combine_inclino_measurements(formerpath, latterpath, outpath):
    """
    Combines the inclino measurements from the former and latter files, interpolating the latter measurements to match the Z values of the former measurements.
    Parameters:
    -------
    formerpath: str,
        path to the former inclino measurements csv file
    latterpath: str,
        path to the latter inclino measurements csv file
    outpath: str,
        path to save the combined inclino measurements csv file
    """
    import pandas as pd
    import numpy as np
    
    df_former = pd.read_csv(formerpath)
    df_latter = pd.read_csv(latterpath)
    df = pd.DataFrame()
    df['Z'] = df_former['Z']
    for column in df_former.drop(['Z'], axis=1).columns:
        df[column] = df_former[column]
    for column in df_latter.drop(['Z'], axis=1).columns:
        df.loc[df['Z'] <= df_latter['Z'].max(), column] = np.interp(df.loc[df['Z'] <= df_latter['Z'].max(), 'Z'], df_latter['Z'], df_latter[column])
    df.to_csv(outpath, index=False)