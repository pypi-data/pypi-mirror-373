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


from .growthmodels import *



def task_fit_and_plotfit(args):
    logger, strain, df_pm, plotfits, pm, well, substrate, output_folder = args
    zoom = 1.2
    
    
    # initiate the new row for the 'fitdf' dataframe:
    new_row = {'index_col': f'{strain}_{pm}_{well}',
        'strain': strain, 'pm': pm, 'well': well,
        'substrate': substrate
    }


    # skip blank wells: 
    if (well=='A01' and pm in ['PM1', 'PM2A', 'PM3B']) \
        or (well in ['A01', 'F01'] and pm=='PM4A'):   
        return new_row
        
    
    # extract experimental data: 
    time = df_pm[df_pm['well']==well]['time'].to_numpy()
    y = df_pm[df_pm['well']==well]['value_mean'].to_numpy()
    
    
    # skip flat-signal wells (all 0):
    if np.all(y == 0):
        return new_row
    
    
    # plot experimental data
    if plotfits:
        fig, ax = plt.subplots(
            nrows=1, ncols=1,
            figsize=(12*zoom, 8*zoom), 
            gridspec_kw={'width_ratios': [1]}
        ) 
        plt.subplots_adjust(wspace=0, hspace=0)
        ax.plot(time, y, 'o', label='experimental')


    # compute the area under the curve: 
    auc_raw = round(np.trapz(y, time),2)
    new_row['auc_raw'] = auc_raw
    
    # compute max recorded signal
    ymax_raw = max(y)
    new_row['ymax_raw'] = ymax_raw


    # provide initial guess for model's parameters:
    pnames, p0, key_lag, key_plateau  = guess_params(time, y, n_bins=7)
    if plotfits:  # plot the 2 heights defining lag and plateau phases.  
        ax.axhline(y=key_lag[1], color='grey', linestyle='-.')
        ax.axhline(y=key_plateau[0], color='grey', linestyle='-.')


    # iterate growth models: 
    all_phenodig_models = [baranyi, baranyi_nolag, baranyi_nostat, baranyi_wexpd]
    colors = [f'C{i}' for i in range(len(all_phenodig_models))]
    for model_f, color in zip(all_phenodig_models, colors):
        model_id = model_f.__name__


        # do the real fitting: 
        try:
            with warnings.catch_warnings():
                # eg: "RuntimeWarning: overflow encountered in exp"
                warnings.simplefilter("ignore")
                # predict model's parameters: 
                params, _ = curve_fit(model_f, time, y, p0=p0, maxfev=5000)
                # predict values using the parametrized model:
                y_pred = model_f(time, *params)
        except: 
            # eg "RuntimeError: Optimal parameters not found: Number of calls to function has reached maxfev = 5000."
            continue  # try next model


        # extract and save parameters: 
        for pname, pvalue in zip(pnames, params):
            new_row[f'{pname}_{model_id}'] = pvalue
            
            
        # impose 'mudeath' positive as in 'growthmodels.py':
        if new_row[f'mudeath_{model_id}'] < 0:   
            new_row[f'mudeath_{model_id}'] = -1 * new_row[f'mudeath_{model_id}']
            
            
        # compute the !fitted! area under the curve (increase datapoints beforehand):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t_fit = get_more_t_point(time, mult=100)
            y_fit = model_f(t_fit, *params)
            auc = round(np.trapz(y_fit, t_fit),2)
            new_row[f'auc_{model_id}'] = auc


        # compute and save metrics:
        r2 = R2(y, y_pred)
        n_params = len(inspect.signature(model_f).parameters) -2  # '-2' because of 't', 't0'
        n_params = n_params - get_unused_params(model_id)
        aic = AIC(y, y_pred, n_params)
        new_row[f'R2_{model_id}'] = r2
        new_row[f'AIC_{model_id}'] = aic
        

        # draw the fit (more time points: smoother)
        if plotfits:
            ax.plot(t_fit, y_fit, '--', color=color, label=f'{model_id} (R2={r2}; AIC={aic})')


    # draw decorations for the plot: 
    if plotfits:
        ax.set_xlabel('time')
        ax.set_ylabel('processed signal')
        ax.set_facecolor('whitesmoke')
        ax.set_title(f'bacterial growth models\nstrain: {strain} PM: {pm} well: {well}')
        ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5))
        ax.grid(True)
        plt.savefig(f'{output_folder}/plotfits/{pm}_{well}_{strain}.png', dpi=200, bbox_inches='tight') 
        plt.close(fig)  

    
    return new_row



def get_bestfit_and_call_table(fitdf, threshold_auc, threshold_ymax_raw, threshold_r2):
    
    
    # keep base columns:
    bestfit_df = fitdf[['strain', 'pm', 'well', 'substrate', 'auc_raw', 'ymax_raw']].copy()

    # create missing columns
    newcols = ['best_model', 'AIC', 'R2', 'auc', 'mu', 'mudeath', 'tdeath', 'tlag', 'ymax']
    for col in newcols: bestfit_df[col] = None
    
    
    # iterate wells:
    for index, row in fitdf.iterrows():
        
        
        # determine best model using R2 and AIC (in this order of priority!):
        best_model = None
        r2 = None
        aic = None
        
        all_phenodig_models = [baranyi, baranyi_nolag, baranyi_nostat, baranyi_wexpd]
        for model_f in all_phenodig_models:
            curr_model = model_f.__name__
            curr_r2 = fitdf.loc[index, f'R2_{curr_model}']
            curr_aic = fitdf.loc[index, f'AIC_{curr_model}']
            
            if pnd.isna(curr_r2):  
                # this model was not fitted
                continue   
            
            if r2 == None:  
                # this is the first fitted model (there could be better ones)
                r2 = curr_r2
                aic = curr_aic
                best_model = curr_model
                
            elif (curr_r2 > r2) or (curr_r2 == r2 and curr_aic < aic):   
                # here is another fitted model, better then the previous one:
                r2 = curr_r2
                aic = curr_aic
                best_model = curr_model
                
            else:
                # here is another fitted model, but performs worst than the previous one:
                pass
        
        
        # fill new columns
        if best_model==None:    # no fitted model (eg Negative Wells)
            bestfit_df.loc[index, 'best_model'] = None
            bestfit_df.loc[index, f'call'] = False
            
        else:
            bestfit_df.loc[index, 'best_model'] = best_model
            for col in ['AIC', 'R2', 'auc', 'mu', 'mudeath', 'tdeath', 'tlag', 'ymax']:
                bestfit_df.loc[index, col] = fitdf.loc[index, f'{col}_{best_model}']

            if best_model != 'baranyi_wexpd': 
                bestfit_df.loc[index, f'mudeath'] = None
                bestfit_df.loc[index, f'tdeath'] = None
            if best_model == 'baranyi_nolag': 
                bestfit_df.loc[index, f'tlag'] = None
            if best_model == 'baranyi_nostat': 
                bestfit_df.loc[index, f'ymax'] = None

            if row['substrate'] == 'Negative Control':
                bestfit_df.loc[index, f'best_model'] = None


            # actual growth calling:
            if \
                bestfit_df.loc[index, f'ymax_raw'] >= threshold_ymax_raw and \
                bestfit_df.loc[index, f'auc'] >= threshold_auc and \
                bestfit_df.loc[index, f'R2'] >= threshold_r2:
                
                bestfit_df.loc[index, f'call'] = True
            else:
                bestfit_df.loc[index, f'call'] = False
        
    
    return bestfit_df

                                                   
                                                   
def curve_fitting(logger, cores, output_folder, strain_to_df, threshold_auc, threshold_ymax_raw, threshold_r2, keepfits, plotfits):
    logger.info(f"Fitting signals...")
    
    
    # create folders if needed: 
    os.makedirs(f'{output_folder}/bestfit/', exist_ok=True)
    if keepfits: 
        os.makedirs(f'{output_folder}/allfits/', exist_ok=True)
    if plotfits: 
        os.makedirs(f'{output_folder}/plotfits/', exist_ok=True)
    
    
    # load official mappings
    official_pm_tables = {}
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        with resources.path("phenodig.assets", f"{pm}.csv") as asset_path: 
            official_pm_tables[pm] = pnd.read_csv(asset_path, index_col=1, names=['plate','substrate','source','u1','u2','u3','u4','kc','cas'])
    
    
    # iterate strains:
    strain_to_fitdf = {}
    for strain, df in strain_to_df.items():
        logger.debug(f"Processing strain '{strain}'...")
        strain_to_fitdf[strain] = None
        fitdf = []
        
        
        # iterate wells of the plate: 
        with confu.ProcessPoolExecutor(max_workers=cores) as executor:  
            futures = []
                
            # iterate Biolog(R) plates:  
            for pm in df['pm'].unique():
                df_pm = df[df['pm']==pm]   # get experimental data
                
                # iterate wells
                for i, row in enumerate('ABCDEFGH'):
                    for j, col in enumerate([i+1 for i in range(12)]):


                        # get basic info for the well: 
                        col = str(col)
                        if len(col)==1: col = f'0{col}'
                        well = f'{row}{col}'
                        substrate = official_pm_tables[pm].loc[well, 'substrate']


                        future = executor.submit(task_fit_and_plotfit, (logger, strain, df_pm, plotfits, pm, well, substrate, output_folder))
                        futures.append(future)
                
                
            confu.wait(futures)  # block until all futures are done
            for future in futures:
                new_row = future.result()
                fitdf.append(new_row)

                    
        # sort 'fitdf':
        fitdf = pnd.DataFrame.from_records(fitdf)
        fitdf = fitdf.set_index('index_col', drop=True, verify_integrity=True)
        sorted_cols = set(list(fitdf.columns)) - set(['strain', 'pm', 'well', 'substrate', 'auc_raw', 'ymax_raw'])
        sorted_cols = sorted(list(sorted_cols))
        sorted_cols = ['strain', 'pm', 'well', 'substrate', 'auc_raw', 'ymax_raw'] + sorted_cols
        fitdf = fitdf[sorted_cols]  # columns by alphabetical order
        
        
        # save 'fitdf' (first format the index):
        if keepfits:
            fitdf_xlsx = fitdf.reset_index(drop=True)
            fitdf_xlsx.index = fitdf_xlsx.index +1
            fitdf_xlsx.to_excel(f'{output_folder}/allfits/allfits_{strain}.xlsx')
            logger.debug(f"'{output_folder}/allfits/allfits_{strain}.xlsx' created!")
        
        
        # Get the best fit and perform growth calling (table 'bestfit_df') + populate dictionary.
        # Explanation: at this point 'fitdf' is a big table containing [AIC,R2,mu,mudeath,tdeath,tlag,tmax,y0,ymax] 
        # for each of the fitted models (eg [baranyi,baranyi_nolag,baranyi_nostat,wexpd]), in addition to the 
        # base columns ['strain', 'pm', 'well', 'substrate', 'auc_raw', 'ymax_raw']. From 'fitdf', 'bestfitdf' is derived.
        # 'bestfitdf' contains information for ony 1 fitting: the best one. This is done in 'get_bestfit_and_call_table()'.
        # In the same function, growth-calling is also performed, applying user-provided thresholds.
        bestfitdf = get_bestfit_and_call_table(fitdf, threshold_auc, threshold_ymax_raw, threshold_r2)
        strain_to_fitdf[strain] = bestfitdf
        
        
        # save 'bestfit_df' (first format the index):
        bestfitdf_xlsx = bestfitdf.reset_index(drop=True)
        bestfitdf_xlsx.index = bestfitdf_xlsx.index +1
        bestfitdf_xlsx.to_excel(f'{output_folder}/bestfit/bestfit_{strain}.xlsx')
        logger.info(f"'{output_folder}/bestfit/bestfit_{strain}.xlsx' created!")


    return strain_to_fitdf

