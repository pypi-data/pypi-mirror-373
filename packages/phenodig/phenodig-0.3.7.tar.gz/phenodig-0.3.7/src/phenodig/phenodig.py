import os


from .preproc import collect_raw_data
from .preproc import data_preprocessing

from .wellfits import curve_fitting

from .plotplates import plot_plates_strain
from .plotplates import plot_plates_compare

        
        
def phenodig(args, logger): 
    
    
    # adjust out folder path
    while args.output.endswith('/'):
        args.output = args.output[:-1]
        
    # adjust cores:
    if args.cores == 0:
        args.cores = os.cpu_count()
        if args.cores == None: args.cores = 1
        
    # check signal:
    admitted_signals = ['590', '750', '590-750']
    if args.signal not in admitted_signals:
        logger.warning(f"Provided --signal '{args.signal}' is not valid. Admitted values are {admitted_signals}. Proceeding with '590-750'.")
        args.signal = '590-750'
        
        
    strain_to_df = collect_raw_data(logger, args.cores, args.input, args.plates, args.replicates, args.discarding)
    if type(strain_to_df) == int: return 1


    strain_to_df = data_preprocessing(logger, args.cores, strain_to_df, args.output, args.signal, args.applylog)
    if type(strain_to_df) == int: return 1


    strain_to_bestfit = curve_fitting(logger, args.cores, args.output, strain_to_df, args.thr_auc, args.thr_ymax, args.thr_r2, args.keepfits, args.plotfits)
    if type(strain_to_bestfit) == int: return 1


    response = plot_plates_strain(logger, args.cores, args.output, strain_to_df, strain_to_bestfit, args.noynorm)
    if response==1: return 1
    
    
    response = plot_plates_compare(logger, args.cores, args.output, strain_to_df, strain_to_bestfit, args.noynorm)
    if response==1: return 1
     
    
    return 0