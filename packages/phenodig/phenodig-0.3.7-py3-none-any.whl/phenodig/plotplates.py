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
from matplotlib.lines import Line2D



from .growthmodels import *



def task_plot_plate(args):
    strain, pm, df_pm, official_pm_tables, y_min, y_max, noynorm, output_folder, fitdf = args
    zoom = 1.2
    
    
    # prepare subplots:
    fig, axs = plt.subplots(
        nrows=8, ncols=12,
        figsize=(12*zoom, 8*zoom), 
        gridspec_kw={'width_ratios': [1 for i in range(12)]}
    ) 
    plt.subplots_adjust(wspace=0, hspace=0)


    # get min and max:
    if noynorm:
        y_min = min(df_pm['value_mean'] - df_pm['value_sem'])  
        y_max = max(df_pm['value_mean'] + df_pm['value_sem'])

    
    for i, row in enumerate('ABCDEFGH'):
        for j, col in enumerate([i+1 for i in range(12)]):
            col = str(col)
            if len(col)==1: col = f'0{col}'
            well = f'{row}{col}'


            # extract well datapoints: 
            x_vector = df_pm[df_pm['well']==well]['time'].to_list()
            y_vector = df_pm[df_pm['well']==well]['value_mean'].to_list()
            sem_vector = df_pm[df_pm['well']==well]['value_sem'].to_list()
            y_vector_eneg = [y-e if (y-e)>=0 else 0 for y,e in zip(y_vector, sem_vector) ]
            y_vector_epos = [y+e if (y+e)>=0 else 0 for y,e in zip(y_vector, sem_vector) ]
            
            # plot experimental points:
            axs[i, j].scatter(x_vector, y_vector, s=10, color='C4', edgecolor=None, alpha=0.8)
            # plot experimental error:
            axs[i, j].fill_between(x_vector, y_vector_eneg, y_vector_epos, color='grey', edgecolor=None, alpha=0.3)
            
            

            # normalize axis limit: 
            axs[i, j].set_ylim(y_min, y_max)
            axs[i, j].set_xlim(left=0)  
            


            with warnings.catch_warnings():
                # avoid "UserWarning: set_ticklabels() should only be used with a fixed number of ticks, i.e. after set_ticks() or using a FixedLocator."
                warnings.simplefilter("ignore")

                # set ticks:
                axs[i, j].xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))  
                axs[i, j].yaxis.set_major_locator(MaxNLocator(nbins=5)) 

                # set tick labels (exclude 0)
                axs[i, j].set_xticklabels([str(int(i)) if i!=0 else '' for i in axs[i, j].get_xticks()])
                axs[i, j].set_yticklabels([str(round(i,2)) if i!=0 else '' for i in axs[i, j].get_yticks()])

                # remove ticks for central plots
                if j!=0: axs[i, j].set_yticks([])
                if i!=7: axs[i, j].set_xticks([])
                


            # set background color
            call = fitdf.loc[f'{strain}_{pm}_{well}', 'call']
            bg_color = 'white'
            if call: 
                bg_color = '#f0ffdb'  # paler green
            else: 
                bg_color = 'mistyrose'
            axs[i, j].set_facecolor(bg_color)
            
            
            
            # extract fit parameters
            best_model = fitdf.loc[f'{strain}_{pm}_{well}', 'best_model']
            r2 = fitdf.loc[f'{strain}_{pm}_{well}', 'R2']
            aic = fitdf.loc[f'{strain}_{pm}_{well}', 'AIC']
            auc_raw = fitdf.loc[f'{strain}_{pm}_{well}', 'auc_raw']
            auc = fitdf.loc[f'{strain}_{pm}_{well}', 'auc'] 
            tlag = fitdf.loc[f'{strain}_{pm}_{well}', 'tlag']
            mu = fitdf.loc[f'{strain}_{pm}_{well}', 'mu']
            ymax = fitdf.loc[f'{strain}_{pm}_{well}', 'ymax']
            tdeath = fitdf.loc[f'{strain}_{pm}_{well}', 'tdeath']
            mudeath = fitdf.loc[f'{strain}_{pm}_{well}', 'mudeath']
            
            
            
            # plot fit:
            all_phenodig_models = [baranyi, baranyi_nolag, baranyi_nostat, baranyi_wexpd]
            for model_f in all_phenodig_models:
                if best_model == model_f.__name__:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        t_fit = get_more_t_point(x_vector, mult=100)
                        y_fit = model_f(t_fit, 0, tlag, mu, ymax, None, tdeath, mudeath)
                        axs[i, j].plot(t_fit, y_fit, color='C0', alpha=0.8, linewidth=0.5) 
                        axs[i, j].fill_between(t_fit, y_fit, color='C0', edgecolor=None, alpha=0.4)            
            


            # annotations:
            color = 'grey'
            padx, pady = max(x_vector)/40, y_max/10

            # title
            axs[i, j].text(padx, y_max - pady*0 -pady/2, well, fontsize=7, fontweight='bold', ha='left', va='top', color=color)

            # substrate name
            annot_substrate = official_pm_tables[pm].loc[well, 'substrate']
            if len(annot_substrate) > 15: annot_substrate = annot_substrate[0:15] + '...'
            annot_substrate = f'{annot_substrate}'
            axs[i, j].text(padx, y_max - pady*1 -pady/2, annot_substrate, fontsize=7, ha='left', va='top', color=color)

            # substrate kc
            annot_kc = official_pm_tables[pm].loc[well, 'kc']
            if type(annot_kc)==float : annot_kc = 'na'
            annot_kc = f'kc: {annot_kc}'
            axs[i, j].text(padx, y_max - pady*2 -pady/2, annot_kc, fontsize=6, ha='left', va='top', color=color)

            # best_model:
            annot_best_model = f'fit: {best_model}'
            axs[i, j].text(padx, y_max - pady*3 -pady/2, annot_best_model, fontsize=6, ha='left', va='top', color=color)
            
            # R2 
            annot_r2 = f'R2: {r2}'
            axs[i, j].text(padx, y_max - pady*4 -pady/2, annot_r2, fontsize=4, ha='left', va='top', color=color)
            
            # AIC
            annot_aic = f'AIC: {aic}'
            axs[i, j].text(padx, y_max - pady*4 -pady/2 -pady*0.7*1, annot_aic, fontsize=4, ha='left', va='top', color=color)
            
            # auc:
            annot_auc_raw = f'AUC e / f: {auc_raw} / {auc}'
            axs[i, j].text(padx, y_max - pady*4 -pady/2 -pady*0.7*2, annot_auc_raw, fontsize=4, ha='left', va='top', color=color)
            
            # tlag:
            if tlag != None: tlag = round(tlag, 2) 
            annot_tlag = f'tlag: {tlag}'
            axs[i, j].text(padx, y_max - pady*4 -pady/2 -pady*0.7*3, annot_tlag, fontsize=4, ha='left', va='top', color=color)
            
            # mu
            if mu != None: mu = round(mu, 2) 
            annot_mu = f'μ: {mu}'
            axs[i, j].text(padx, y_max - pady*4 -pady/2 -pady*0.7*4, annot_mu, fontsize=4, ha='left', va='top', color=color)
            
            # ymax
            if ymax != None: ymax = round(ymax, 2) 
            annot_ymax = f'ymax: {ymax}'
            axs[i, j].text(padx, y_max - pady*4 -pady/2 -pady*0.7*5, annot_ymax, fontsize=4, ha='left', va='top', color=color)
            
            # tdeath / mudeath:
            if tdeath != None: tdeath = round(tdeath, 2) 
            if mudeath != None: mudeath = round(mudeath, 2) 
            annot_tlag_mu_ymax = f'td / μd: {tdeath} / {mudeath}'
            axs[i, j].text(padx, y_max - pady*4 -pady/2 -pady*0.7*6, annot_tlag_mu_ymax, fontsize=4, ha='left', va='top', color=color)
            
            
            


    # set main title:
    fig.suptitle(f'{strain} - Biolog® {pm}', y=0.9)
    plt.savefig(f'{output_folder}/plates/{pm}_{strain}.png', dpi=200, bbox_inches='tight') 
    plt.close(fig)
    
    
    return 0



def task_plot_compareplate(args):
    logger, pm, df_pm, fitdf_pm, official_pm_tables, output_folder, noynorm, y_min, y_max = args
    zoom = 1.2
    
    
    # prepare subplots:
    fig, axs = plt.subplots(
        nrows=8, ncols=12,
        figsize=(12*zoom, 8*zoom), 
        gridspec_kw={'width_ratios': [1 for i in range(12)]}
    ) 
    plt.subplots_adjust(wspace=0, hspace=0)
    
    
    
    # get min and max:
    if noynorm:
        y_min = min(df_pm['value_mean'] - df_pm['value_sem'])  
        y_max = max(df_pm['value_mean'] + df_pm['value_sem'])
    
    
    
    for i, row in enumerate('ABCDEFGH'):
        for j, col in enumerate([i+1 for i in range(12)]):
            col = str(col)
            if len(col)==1: col = f'0{col}'
            well = f'{row}{col}'
            
            
            # get partecipating strains:
            cnt_color = -1
            for strain in df_pm['strain'].unique(): 
                cnt_color +=1
                
            

                # extract well datapoints: 
                x_vector = df_pm[(df_pm['well']==well) & (df_pm['strain']==strain)]['time'].to_list()
                y_vector = df_pm[(df_pm['well']==well) & (df_pm['strain']==strain)]['value_mean'].to_list()
                
                
                # extract fit parameters
                best_model = fitdf_pm.loc[f'{strain}_{pm}_{well}', 'best_model']
                tlag = fitdf_pm.loc[f'{strain}_{pm}_{well}', 'tlag']
                mu = fitdf_pm.loc[f'{strain}_{pm}_{well}', 'mu']
                ymax = fitdf_pm.loc[f'{strain}_{pm}_{well}', 'ymax']
                tdeath = fitdf_pm.loc[f'{strain}_{pm}_{well}', 'tdeath']
                mudeath = fitdf_pm.loc[f'{strain}_{pm}_{well}', 'mudeath']
                
                
                # if no fit, draw some mock points to align annotations
                if best_model == None:   
                    axs[i, j].plot(x_vector, y_vector, color=None, alpha=0.0, linewidth=0.0) 


                # plot fit:
                all_phenodig_models = [baranyi, baranyi_nolag, baranyi_nostat, baranyi_wexpd]
                for model_f in all_phenodig_models:
                    if best_model == model_f.__name__:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            t_fit = get_more_t_point(x_vector, mult=100)
                            y_fit = model_f(t_fit, 0, tlag, mu, ymax, None, tdeath, mudeath)
                            axs[i, j].plot(t_fit, y_fit, color=f'C{cnt_color}', alpha=0.8, linewidth=0.5) 
                

                
            # normalize axis limit:     
            axs[i, j].set_ylim(y_min, y_max)
            axs[i, j].set_xlim(left=0)  
            

            with warnings.catch_warnings():
                # avoid "UserWarning: set_ticklabels() should only be used with a fixed number of ticks, i.e. after set_ticks() or using a FixedLocator."
                warnings.simplefilter("ignore")

                # set ticks:
                axs[i, j].xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))  
                axs[i, j].yaxis.set_major_locator(MaxNLocator(nbins=5)) 

                # set tick labels (exclude 0)
                axs[i, j].set_xticklabels([str(int(i)) if i!=0 else '' for i in axs[i, j].get_xticks()])
                axs[i, j].set_yticklabels([str(round(i,2)) if i!=0 else '' for i in axs[i, j].get_yticks()])

                # remove ticks for central plots
                if j!=0: axs[i, j].set_yticks([])
                if i!=7: axs[i, j].set_xticks([])
                


            # set background color
            bg_color = 'whitesmoke'
            axs[i, j].set_facecolor(bg_color)
            
            
            
            # annotations:
            color = 'grey'
            padx, pady = max(x_vector)/40, y_max/10

            # title
            axs[i, j].text(padx, y_max - pady*0 -pady/2, well, fontsize=7, fontweight='bold', ha='left', va='top', color=color)

            # substrate name
            annot_substrate = official_pm_tables[pm].loc[well, 'substrate']
            if len(annot_substrate) > 15: annot_substrate = annot_substrate[0:15] + '...'
            annot_substrate = f'{annot_substrate}'
            axs[i, j].text(padx, y_max - pady*1 -pady/2, annot_substrate, fontsize=7, ha='left', va='top', color=color)

            # substrate kc
            annot_kc = official_pm_tables[pm].loc[well, 'kc']
            if type(annot_kc)==float : annot_kc = 'na'
            annot_kc = f'kc: {annot_kc}'
            axs[i, j].text(padx, y_max - pady*2 -pady/2, annot_kc, fontsize=6, ha='left', va='top', color=color)
            
            
            
    # set legend:
    legend_labels = []
    legend_colors = []
    cnt_color = -1
    for strain in df_pm['strain'].unique(): 
        cnt_color +=1
        legend_labels.append(strain)
        legend_colors.append(f'C{cnt_color}')
    fig.legend(
        handles=[Line2D([0], [0], color=color, lw=2) for color in legend_colors],
        labels=legend_labels,
        loc='center left',               
        bbox_to_anchor=(1, 0.5),       
        frameon=False                
    )
            
    
    # set main title:
    fig.suptitle(f'comparative - Biolog® {pm}', y=0.9)
    plt.savefig(f'{output_folder}/comp_plates/{pm}.png', dpi=200, bbox_inches='tight') 
    plt.close(fig)
    
    
    logger.info(f"'{output_folder}/comp_plates/{pm}.png' created!")
    return 0



def plot_plates_strain(logger, cores, output_folder, strain_to_df, strain_to_fitdf, noynorm):
        
    logger.info(f"Plotting PM plates...")


    # load official mappings
    official_pm_tables = {}
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        with resources.path("phenodig.assets", f"{pm}.csv") as asset_path: 
            official_pm_tables[pm] = pnd.read_csv(asset_path, index_col=1, names=['plate','substrate','source','u1','u2','u3','u4','kc','cas'])
    

    # get global y min/max
    y_min, y_max = None, None
    if noynorm == False:
        mins, maxs = [], []
        for strain, df in strain_to_df.items():
            mins.append(min(df['value_mean'] - df['value_sem']))
            maxs.append(max(df['value_mean'] + df['value_sem']))
        y_min, y_max = min(mins), max(maxs)


    # iterate strains:
    os.makedirs(f'{output_folder}/plates/', exist_ok=True)
    for strain, df in strain_to_df.items():
        fitdf = strain_to_fitdf[strain]   # get fits
        
        # iterate plates:
        with confu.ProcessPoolExecutor(max_workers=cores) as executor:  
            futures = []
            
            for pm in df['pm'].unique():
                df_pm = df[df['pm']==pm]
                


                future = executor.submit(task_plot_plate, (strain, pm, df_pm, official_pm_tables, y_min, y_max, noynorm, output_folder, fitdf))
                futures.append(future)
                
            confu.wait(futures)  # block until all futures are done
            for future in futures:
                response = future.result()
                if response == 1: 
                    return 1
            
        logger.info(f"'{output_folder}/plates/*_{strain}.png' created!")
        
        
    return 0



def plot_plates_compare(logger, cores, output_folder, strain_to_df, strain_to_fitdf, noynorm):
        
    logger.info(f"Comparing PM plates...")


    # load official mappings
    official_pm_tables = {}
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        with resources.path("phenodig.assets", f"{pm}.csv") as asset_path: 
            official_pm_tables[pm] = pnd.read_csv(asset_path, index_col=1, names=['plate','substrate','source','u1','u2','u3','u4','kc','cas'])


    # create a global df:
    global_df = []
    for strain, df in strain_to_df.items():
        df['strain'] = strain
        global_df.append(df)
    global_df = pnd.concat(global_df)
    
    
    # create a global fit df:
    global_fitdf = []
    for strain, df in strain_to_fitdf.items():
        df['strain'] = strain
        global_fitdf.append(df)
    global_fitdf = pnd.concat(global_fitdf)
    
    
    
    # get global y min/max
    y_min, y_max = None, None
    if noynorm == False:
        y_min = min(global_df['value_mean'] - global_df['value_sem'])
        y_max = max(global_df['value_mean'] + global_df['value_sem'])

    
    
    # iterate over plates:
    os.makedirs(f'{output_folder}/comp_plates/', exist_ok=True)
    with confu.ProcessPoolExecutor(max_workers=cores) as executor:  
        futures = []

        for pm in global_df['pm'].unique():
            df_pm = global_df[global_df['pm']==pm]
            fitdf_pm = global_fitdf[global_fitdf['pm']==pm]


            future = executor.submit(task_plot_compareplate, (logger, pm, df_pm, fitdf_pm, official_pm_tables, output_folder, noynorm, y_min, y_max))
            futures.append(future)

        confu.wait(futures)  # block until all futures are done
        for future in futures:
            response = future.result()
            if response == 1: 
                return 1

    
    
        
    return 0