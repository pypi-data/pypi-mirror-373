import os
import glob
import io
import requests
import logging
import warnings
import statistics
import math
from pathlib import Path
from importlib import resources
import concurrent.futures as confu 

import numpy as np
import pandas as pnd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator




def task_rawdata_collect(args):
    logger, file, pms, replicates, discarding = args
    
    strain = Path(file).stem

    res_df = []
    excel_file = pnd.ExcelFile(file, engine='openpyxl')
    for sheet in excel_file.sheet_names:
        
        # get the table: 
        df = excel_file.parse(sheet)
        
        # get time as number
        if sheet.startswith('T'): time = float(sheet[1:])
        else: time = float(sheet)
        
        # search for expected PMs, ODs and Replicates:
        for pm in pms.split(','):
            for od in ['590', '750']:
                for replicate in replicates.split(','):
                    readout = f'{pm} {od} {replicate}'
                    
                    
                    # check is this readout has to be discarded: 
                    possible_discardings = [
                        f'{strain} {pm} {od} {replicate} {time}',
                        f'{strain} {pm} {od} None {time}',
                        f'{strain} {pm} {od} {replicate} None',
                        f'{strain} {pm} {od} None None',
                    ]
                    if any([i in discarding for i in possible_discardings]):
                        logger.debug(f"Discarding readout as requested: '{strain}', PM '{pm}', OD '{od}', replicate '{replicate}', time '{time}'.")
                        continue 


                    # find boolean mask where value matches
                    mask = df == readout
                    # get the integer positions (row and column indices)
                    indices = list(zip(*mask.to_numpy().nonzero()))
                    # get the only result
                    try: result = indices[0]
                    except: 
                        #logger.debug(f"Expected readout not found: strain '{strain}', PM '{pm}', OD '{od}', replicate '{replicate}', time '{time}'.")
                        continue


                    # adjust indices
                    row_i = result[0] + 2
                    col_i = result[1] + 1
                    for pm_row_i, pm_row in enumerate([r for r in 'ABCDEFGH']):
                        for pm_col_i, pm_col in enumerate([c +1 for c in range(12)]):
                            # get proper well name
                            pm_col = str(pm_col)
                            if len(pm_col) == 1: pm_col = '0' + pm_col
                            well = f'{pm_row}{pm_col}'
                            # get proper plate name
                            plate = pm
                            if plate == 'PM1': pass
                            if plate == 'PM2': plate = 'PM2A'
                            if plate == 'PM3': plate = 'PM3B'
                            if plate == 'PM4': plate = 'PM4A'
                            # read value
                            value = df.iloc[row_i + pm_row_i, col_i + pm_col_i]
                            res_df.append({
                                'index_col': f"{plate}_{time}_{od}_{replicate}_{well}",
                                'pm': plate, 'time': time, 'od': od, 'replicate': replicate, 'well': well, 'value': value})                     
    res_df = pnd.DataFrame.from_records(res_df)
    res_df = res_df.set_index('index_col', drop=True, verify_integrity=True)


    # verbose logging
    logger.debug(f"Strain '{strain}' has {len(res_df['pm'].unique())} plates, {len(res_df['replicate'].unique())} replicates, and {len(res_df['time'].unique())} time points.")  
    
    
    return (strain, res_df)



def task_wavelength_subtraction(args):
    logger, strain, df, signal = args
    logger.debug(f"Processing strain '{strain}'...")
        
    df['value_norm'] = None   
    for index, row in df.iterrows(): 
        
        if signal in ['590', '750']:
            if row['od'] == signal:
                df.loc[index, 'value_norm'] = df.loc[index, 'value'] 
            
        else:  # '590-750'
            if row['od'] == '590':
                index_750 = f"{row['pm']}_{row['time']}_750_{row['replicate']}_{row['well']}"
                df.loc[index, 'value_norm'] = df.loc[index, 'value'] - df.loc[index_750, 'value']
        
    df = df[df['value_norm'].isna()==False]
    df = df.drop(columns=['od', 'value'])
    df.index = [f"{row['pm']}_{row['time']}_{row['replicate']}_{row['well']}" for index, row in df.iterrows()]
    
    return (strain, df)
        
    
    
def task_blank_subtraction(args):
    logger, strain, df = args
    logger.debug(f"Processing strain '{strain}'...")

    for index, row in df.iterrows():
        # get the well of the blank
        if row['pm'] in ['PM1', 'PM2A', 'PM3B']:
            well_black = 'A01'
        else:  # PM4A is both for P and S
            if row['well'][0] in ['A','B','C','D','E']:
                well_black = 'A01'  # P
            else: well_black = 'F01'  # S
        # get the index of the blank
        index_blank = f"{row['pm']}_{row['time']}_{row['replicate']}_{well_black}"
        df.loc[index, 'value_norm'] = df.loc[index, 'value_norm'] - df.loc[index_blank, 'value_norm']
        if df.loc[index_blank, 'value_norm'] < 0: 
            df.loc[index_blank, 'value_norm'] = 0
            
    return (strain, df)



def task_T0_subtraction(args):
    logger, strain, df = args
    logger.debug(f"Processing strain '{strain}'...")
        
    for index, row in df.iterrows():
        index_T0 = f"{row['pm']}_0.0_{row['replicate']}_{row['well']}"
        df.loc[index, 'value_norm'] = df.loc[index, 'value_norm'] - df.loc[index_T0, 'value_norm']
        if df.loc[index, 'value_norm'] < 0: 
            df.loc[index, 'value_norm'] = 0
            
    return (strain, df)



def task_logtransform(args):
    logger, strain, df = args
    logger.debug(f"Processing strain '{strain}'...")
        
    for index, row in df.iterrows():
        # math.log --> base e
        # math.log10 --> base 10
        # math.log1p --> base e; do not raise error if 0 or negative input
        df.loc[index, 'value_norm'] = math.log1p(df.loc[index, 'value_norm'])
            
    return (strain, df)



def task_mean_sem(args):
    logger, strain, df, output_folder = args
    logger.debug(f"Processing strain '{strain}'...")
        
    found_reps = list(df['replicate'].unique())
    df['value_mean'] = None   # dedicated column
    df['value_sem'] = None   # dedicated column
    for index, row in df.iterrows():
        values = []
        for rep in found_reps:
            index_rep = f"{row['pm']}_{row['time']}_{rep}_{row['well']}"
            try: value = df.loc[index_rep, 'value_norm']
            except: continue  # replicate missing for some reason
            values.append(value)
        if len(values) > 1:
            # get the # standard error of the mean (standard deviation)
            std_dev = statistics.stdev(values)
            sem = std_dev / math.sqrt(len(values))
            df.loc[index, 'value_mean'] = statistics.mean(values)
            df.loc[index, 'value_sem'] = sem
        else:  # no replicates
            df.loc[index, 'value_mean'] = df.loc[index, 'value_norm']
            df.loc[index, 'value_sem'] = 0
    df = df.drop(columns=['replicate', 'value_norm'])
    df = df.drop_duplicates()
    df.index = [f"{row['pm']}_{row['time']}_{row['well']}" for index, row in df.iterrows()]
    
    # save long tables
    df.to_excel(f'{output_folder}/preproc/preproc_{strain}.xlsx')
    logger.info(f"'{output_folder}/preproc/preproc_{strain}.xlsx' created!")
    
    return (strain, df)



def collect_raw_data(logger, cores, input_folder, pms, replicates, discarding):
    logger.info(f"Collecting raw data...")
    
    
    # check file presence
    files = glob.glob(f'{input_folder}/*.xlsx')
    if len(files) == 0:
        logger.error(f"No .xlsx file found in the provided directory ('--input {input_folder}').")
        return 1
    
    
    # obtain a comprehensible representation of datapoints to discard: 
    formatted_discarding = []
    for d in discarding.split(','):
        dfields = d.split(':')
        if len(dfields) == 2:
            strain, pm, replicate, time = dfields + [None, None]
        elif len(dfields) == 3:
            if dfields[-1][-1].isdigit():  # last field is a time
                strain, pm, replicate, time = dfields[:2] + [None] + [dfields[2]]
                if time.startswith('T'): time = float(time[1:])
            else:  # last field is a replicate
                strain, pm, replicate, time = dfields + [None]
        elif len(dfields) == 4: 
            strain, pm, replicate, time = dfields
            if time.startswith('T'): time = float(time[1:])
        else:
            logger.error(f"Invalid syntax found ('--discarding {discarding}').")
            return 1
        formatted_discarding.append(f"{strain} {pm} 590 {replicate} {time}")
        formatted_discarding.append(f"{strain} {pm} 750 {replicate} {time}")

            
    discarding = formatted_discarding
            
    
    # each strain has its own xlsx file: 
    strain_to_df = {}
    with confu.ProcessPoolExecutor(max_workers=cores) as executor:  
        futures = []
        for file in files:
            future = executor.submit(task_rawdata_collect, (logger, file, pms, replicates, discarding))
            futures.append(future)
        confu.wait(futures)  # block until all futures are done
        for future in futures:
            (strain, df) = future.result()
            strain_to_df[strain] = df
        
        
    logger.info(f"Found {len(strain_to_df)} strains in input.")
    return strain_to_df


                    
def data_preprocessing(logger, cores, strain_to_df, output_folder, signal, applylog):
    os.makedirs(f'{output_folder}/preproc/', exist_ok=True)
    
    
    
    # step 1: OD590 - OD750:
    logger.info(f"Substracting wavelengths...")
    with confu.ProcessPoolExecutor(max_workers=cores) as executor:  
        futures = []
        for i, strain in enumerate(strain_to_df.keys()):
            future = executor.submit(task_wavelength_subtraction, (logger, strain, strain_to_df[strain], signal))
            futures.append(future)
        confu.wait(futures)  # block until all futures are done
        for future in futures:
            (strain, df) = future.result()
            strain_to_df[strain] = df

        
        
    # step 2: subtraction of the blank
    logger.info(f"Substracting negative controls...")
    with confu.ProcessPoolExecutor(max_workers=cores) as executor:        
        futures = []
        for i, strain in enumerate(strain_to_df.keys()):
            future = executor.submit(task_blank_subtraction, (logger, strain, strain_to_df[strain]))
            futures.append(future)
        confu.wait(futures)  # block until all futures are done
        for future in futures:
            (strain, df) = future.result()
            strain_to_df[strain] = df


        
    # step 3: substraction of T0
    logger.info(f"Substracting T0...")
    with confu.ProcessPoolExecutor(max_workers=cores) as executor:        
        futures = []
        for i, strain in enumerate(strain_to_df.keys()):
            future = executor.submit(task_T0_subtraction, (logger, strain, strain_to_df[strain]))
            futures.append(future)
        confu.wait(futures)  # block until all futures are done
        for future in futures:
            (strain, df) = future.result()
            strain_to_df[strain] = df
            
            
    
    # step 4: logarithm transformate (only if explicitly requested)
    if applylog:
        logger.info(f"Applying logarithm transformation...")
        with confu.ProcessPoolExecutor(max_workers=cores) as executor:        
            futures = []
            for i, strain in enumerate(strain_to_df.keys()):
                future = executor.submit(task_logtransform, (logger, strain, strain_to_df[strain]))
                futures.append(future)
            confu.wait(futures)  # block until all futures are done
            for future in futures:
                (strain, df) = future.result()
                strain_to_df[strain] = df


    
    # step 5: get mean +- sem given replicates
    logger.info(f"Computing mean and SEM...")
    with confu.ProcessPoolExecutor(max_workers=cores) as executor:        
        futures = []
        for i, strain in enumerate(strain_to_df.keys()):
            future = executor.submit(task_mean_sem, (logger, strain, strain_to_df[strain], output_folder))
            futures.append(future)
        confu.wait(futures)  # block until all futures are done
        for future in futures:
            (strain, df) = future.result()
            strain_to_df[strain] = df
        
        
        
    return strain_to_df
