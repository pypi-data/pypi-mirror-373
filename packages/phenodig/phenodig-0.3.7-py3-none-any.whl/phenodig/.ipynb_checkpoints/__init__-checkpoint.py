import argparse
import sys
import logging 
import traceback
import importlib.metadata
from datetime import datetime


from .phenodig import phenodig

from .logutils import set_header_trailer_formatter
from .logutils import set_usual_formatter
from .logutils import get_logger



def main(): 
    
    
    # define the header of main- and sub-commands. 
    header = f'phenodig v{importlib.metadata.metadata("phenodig")["Version"]},\ndeveloped by Gioele Lazzari (gioele.lazzari@univr.it).'
    
    
    # create the command line arguments:
    parser = argparse.ArgumentParser(description=header, add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    parser.add_argument("-v", "--version", action="version", version=f"v{importlib.metadata.metadata('phenodig')['Version']}", help="Show version number and exit.")
    
    
    parser.add_argument("-c", "--cores", metavar='', type=int, default=0, help="How many cores to use (0: all the available cores).")
    parser.add_argument("--verbose", action='store_true', help="Make stdout messages more verbose, including debug messages.")
    parser.add_argument("-i", "--input", metavar='', type=str, default='./', help="Folder containing input excel files.")
    parser.add_argument("-o", "--output", metavar='', type=str, default='./', help="Output folder (will be created if not existing).")
    parser.add_argument("-r", "--replicates", metavar='', type=str, default='A,B', help="Replicate IDs (comma-separated). For example: 'A,B'. The same IDs are expected to appear in the input excel files.")
    parser.add_argument("-p", "--plates", metavar='', type=str, default='PM1,PM2,PM3,PM4', help="Biolog(R) plate IDs (comma-separated). For example: 'PM1,PM2,PM3,PM4'. The same IDs are expected to appear in the input excel files.")
    parser.add_argument("-d", "--discarding", metavar='', type=str, default='5220:PM3:A', help="Datapoints to discard from the analysis. From single timepoints in single replicates, up to all replicates of a plate: datapoints to discard can be specified by using the flexible syntax '{strain}:{plate}:{replicate}:{time}'. At least the first two fields must be given. For example: '5220:PM3:A,6332:PM2:B'.")
    parser.add_argument("--signal", metavar='', type=str, default='590-750', help="Signal to process (choose between '590', '750', or '590-750').")
    parser.add_argument("--applylog", action='store_true', help="Apply logarithm transformation during preprocessing (as final step, just before mediating the replicates).")
    parser.add_argument("--thr_auc", metavar='', type=float, default=0.1, help="Threshold for fitted AUC, to be used during growth calling.")
    parser.add_argument("--thr_ymax", metavar='', type=float, default=0.05, help="Threshold for max recorded signal, to be used during growth calling.")
    parser.add_argument("--thr_r2", metavar='', type=float, default=0.8, help="Threshold for R2, to be used during growth calling.")
    parser.add_argument("--noynorm", action='store_true', help="Do not normalize the Y axis of PM plots.")
    parser.add_argument("--keepfits", action='store_true', help="Keep fitting tables (all tested models): 'all_models/fitting_*.xlsx'.")
    parser.add_argument("--plotfits", action='store_true', help="Produce plots for the fittings (all tested models): 'all_models/plotfits/*.png'.")
    

    # check the inputted subcommand, automatic sys.exit(1) if a bad subprogram was specied. 
    args = parser.parse_args()
    
    
    # set up the logger:
    logger = get_logger('phenodig', args.verbose)
    
    
    
    # show a welcome message:
    set_header_trailer_formatter(logger.handlers[0])
    logger.info(header + '\n')
    command_line = 'phenodig ' # print the full command line:
    for arg, value in vars(args).items():
        command_line = command_line + f"--{arg} {value} "
    logger.info('Inputted command line: "' + command_line.rstrip() + '".\n')
    

    
    # run the program:
    set_usual_formatter(logger.handlers[0])
    current_date_time = datetime.now()
    formatted_date = current_date_time.strftime("%Y-%m-%d")
    logger.info(f"Welcome to phenodig! Launching the tool on {formatted_date}...")
    try: 
        response = phenodig(args, logger)
            
        if response == 0:
            logger.info("phenodig terminated without errors!")
    except: 
        # show the error stack trace for this un-handled error: 
        response = 1
        logger.error('Traceback is reported below.\n\n' + traceback.format_exc())


    
    # terminate the program:
    set_header_trailer_formatter(logger.handlers[0])
    if response == 1: 
        print(file=sys.stderr)  # separate last error from fresh prompt
        sys.exit(1)
    else: 
        # show a bye message
        logger.info('\n' + header)
        sys.exit(0) # exit without errors
        
        
        
        
if __name__ == "__main__":
    main()