import os
import io
import requests
import logging
import warnings
from pathlib import Path
from importlib import resources

import pandas as pnd
import gempipe
import cobra


__OPTTHR__ = 0.001   # optimization threshold


def get_expcon(logger):
    
    
    logger.info("Downloading the experimental constraints file...")
    sheet_id = "1qGbIIipHJgYQjk3M0xDWKvnTkeInPoTeH9unDQkZPwg"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    response = requests.get(url)  # download the requested file
    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)   # load into memory
        exceldb = pnd.ExcelFile(excel_data)
    else:
        logger.error(f"Error during download. Please contact the developer.")
        return 1
    
    
    # check table presence
    sheet_names = exceldb.sheet_names
    for i in ['media', 'PM1', 'PM2A', 'PM3B', 'PM4A', 'authors']: 
        if i not in sheet_names:
            logger.error(f"Sheet '{i}' is missing!")
            return 1
        
        
    # load the tables
    expcon = {}
    expcon['media'] = exceldb.parse('media')
    expcon['PM1'] = exceldb.parse('PM1')
    expcon['PM2A'] = exceldb.parse('PM2A')
    expcon['PM3B'] = exceldb.parse('PM3B')
    expcon['PM4A'] = exceldb.parse('PM4A')
    expcon['authors'] = exceldb.parse('authors')
    
    
    # assign substrates as index
    expcon['media'].index = expcon['media'].iloc[:, 1]
    # remove first 2 useless column (empty & substrates)
    expcon['media'] = expcon['media'].iloc[:, 2:]
    
    
    for sheet in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        # assign wells as index
        expcon[sheet].index = expcon[sheet].iloc[:, 2]
        # remove first 3 useless columns
        expcon[sheet] = expcon[sheet].iloc[:, 3:]
    

    return expcon



def get_biomass_dict():
    
    
    # Note: universal and conditional precursors have been defined in Xavier2017 .
    # Here presented in the same order of Xavier2017 .
    # Xavier2017: 10.1016/j.ymben.2016.12.002.
    biomass_dict = {
        ##### UNIVERSAL #####
        'ribo_nucleotides': [
            'atp_c', 'ctp_c', 'gtp_c', 'utp_c'
        ],
        'deoxyribo_nucleotides': [
            'datp_c', 'dctp_c', 'dgtp_c', 'dttp_c'
        ],
        'amino_acids': [
            'ala__L_c', 'arg__L_c', 'asn__L_c', 'asp__L_c', 'cys__L_c', 
            'gln__L_c', 'glu__L_c', 'gly_c',    'his__L_c', 'ile__L_c', 
            'leu__L_c', 'lys__L_c', 'met__L_c', 'ser__L_c', 'pro__L_c', 
            'thr__L_c', 'trp__L_c', 'tyr__L_c', 'val__L_c', 'phe__L_c'
        ],
        'cofactors_uni': [
            'nad_c',    # B3: Nicotinamide -adenine dinucleotide phosphate
            'nadp_c',   # B3: Nicotinamide -adenine dinucleotide phosphate
            'coa_c',    # B5: Coenzyme A  (dependant on 'pnto__R_c')
            'fad_c',    # B2: Flavin adenine dinucleotide
            'fmn_c',    # B2: Flavin mononucleotide
            'ribflv_c', # B2: ribovlavin. Non-active form acording to Xavier2017 but anyway included.
            #'f4200_c', # B2: included by Xavier2017 in 'universal' but the description seems conditional.
            'thf_c',    # B9: tetrahydrofolate 
            '10fthf_c', # B9: 10-Formyltetrahydrofolate
            '5mthf_c',  # B9: 5-Methyltetrahydrofolate
            'thmpp_c',  # B1: Thiamine diphosphate
            'pydx5p_c', # B6: pyridoxal 5-phosphate
            'amet_c',   # SAM: S-adenosyl-methionine
        ],
        ##### CONDITIONAL #####
        'cofactors_con': [
            #'f4200_c', # coenzyme f420 (electron transfer in methanogens, actinobacteria , and others)
            'ptrc_c',   # Putrescine
            'spmd_c',   # Sperimidine
            'pheme_c',  # protoheme
            'mql8_c',   # menaquinol / manaquinone (mqn8_c)
            'q8h2_c',   # ubiquinol / ubiquinone (q8_c)
            # Methionaquinone
            'btn_c',    # B7: biotin
            'ACP_c',    # Acyl-carrier protein
            'adocbl_c', # B12: Adenosylcobalamin
            # Lipoate
            'uacgam_c'  # uridine diphosphate N-Acetylglucosamine (UDP-GlcNAc)
        ],
        ##### ADDED ##### (conditionals not included or lumped in Xavier2017)
        'cofactors_add': [
            'hemeO_c',  # heme-O
            'sheme_c',  # siroheme
            'moco_c',   # molybdenum cofactor
            'phllqol_c',# phylloquinol / phylloquinone (phllqne_c)
            'gthrd_c',  # glutathione (reduced)
        ],
        'lipids': [
            'pe120_c', # phosphatidyl-ethanolamine (12:0;12:0)
            'pg120_c', # phosphatidyl-glycerol (12:0;12:0)
            'clpn120_c', # cardiolipin (12:0;12:0;12:0;12:0)
            # 1-lysyl phosphatidylglycerol (plantarum)
        ],
        'membrane_wall': [
            'peptidoSTA_c', # peptidoglycan (dependant on 'udcpdp_c')
            'WTAgg40r_20n_20a_P_c', # teichoic acids
            'WTArg40r_20g_20a_P_c', # teichoic acids
            'WTAg40g_20g_20a_P_c', # teichoic acids
            'LTAgg40g_20n_20a_c', # lipoteichoic acids
            'LTAga40g_20t_20a_c', # lipoteichoic acids            
            # capsular polysaccharides
            # kdo_lipid_A
        ],
        'energy_stock': [
            # glycogen
            # starch
            # PHA / PHB
        ]
    }
    return biomass_dict


    
def log_metrics(logger, model, universal=False):
    
    
    G = len([g.id for g in model.genes])
    R = len([r.id for r in model.reactions if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites]))==1])
    T = len([r.id for r in model.reactions if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites]))!=1])
    M = len([m.id for m in model.metabolites])
    uM = len(set([m.id.rsplit('_', 1)[0] for m in model.metabolites]))
    gr = len([gr.id for gr in model.groups])
    bP = len([m.id for m in model.reactions.get_by_id('Biomass').reactants])
    
    if universal:
        logger.info(f"Starting universe: [oG: {G}, R: {R}, T: {T}, uM: {uM}, bP: {bP}]")
    else:
        logger.info(f"Resulting model: [G: {G}, R: {R}, T: {T}, uM: {uM}, bP: {bP}]")
    
    
    
def check_inputs(logger, universe, eggnog):
    
    
    # check if files exist
    if os.path.isfile(universe) == False: 
        logger.error(f"Provided --universe doesn't exist: {universe}.")
        return 1
    if os.path.isfile(eggnog) == False: 
        logger.error(f"Provided --eggnog doesn't exist: {eggnog}.")
        return 1
    
    
    # check the universe model format
    if universe.endswith('.xml'):
        universe = cobra.io.read_sbml_model(universe)
    else: 
        logger.error(f"Provided --universe must be in cobrapy-compatible SBML format (.xml extension).")
        return 1
    
    
    # log main universe metrics:
    log_metrics(logger, universe, universal=True)
        
        
    # load eggnog annotations
    eggnog = pnd.read_csv(eggnog, sep='\t', comment='#', header=None)
    eggnog.columns = 'query	seed_ortholog	evalue	score	eggNOG_OGs	max_annot_lvl	COG_category	Description	Preferred_name	GOs	EC	KEGG_ko	KEGG_Pathway	KEGG_Module	KEGG_Reaction	KEGG_rclass	BRITE	KEGG_TC	CAZy	BiGG_Reaction	PFAMs'.split('\t')
    eggnog = eggnog.set_index('query', drop=True, verify_integrity=True)
    
    return [universe, eggnog]



def parse_eggnog(eggnog):
    
    
    # PART 1. get KO codes available
    gid_to_kos = {}
    ko_to_gids = {}
    for gid, kos in eggnog['KEGG_ko'].items():
        if kos == '-': 
            continue
            
        if gid not in gid_to_kos.keys(): 
            gid_to_kos[gid] = set()
            
        kos = kos.split(',')
        kos = [i.replace('ko:', '') for i in kos]
        for ko in kos: 
            if ko not in ko_to_gids.keys(): 
                ko_to_gids[ko] = set()
                
            # populate dictionaries
            ko_to_gids[ko].add(gid)
            gid_to_kos[gid].add(ko)

    
    return ko_to_gids, gid_to_kos



def get_modeled_kos(model):
    
    
    # get modeled KO ids:
    modeled_gid_to_ko = {}
    modeled_ko_to_gid = {}
    
    for g in model.genes:
        if g.id in ['orphan', 'spontaneous']: 
            continue
        corresponding_ko = g.annotation['ko']
        
        modeled_gid_to_ko[g.id] = corresponding_ko
        modeled_ko_to_gid[corresponding_ko] = g.id
        
    modeled_kos = list(modeled_gid_to_ko.values())
        
    return modeled_kos, modeled_gid_to_ko, modeled_ko_to_gid



def subtract_kos(logger, model, eggonog_ko_to_gids):
    
    
    modeled_kos, _, modeled_ko_to_gid = get_modeled_kos(model)
        
        
    to_remove = []  # genes to delete
    for ko in modeled_kos: 
        if ko not in eggonog_ko_to_gids.keys():
            gid_to_remove = modeled_ko_to_gid[ko]
            to_remove.append(model.genes.get_by_id(gid_to_remove))
            
    
    # remove also orphan reactions!
    to_remove.append(model.genes.get_by_id('orphan'))
    
    
    # delete marked genes!
    # trick to avoid the WARNING "cobra/core/group.py:147: UserWarning: need to pass in a list" 
    # triggered when trying to remove reactions that are included in groups. 
    with warnings.catch_warnings():  # temporarily suppress warnings for this block
        warnings.simplefilter("ignore")  # ignore all warnings
        cobra_logger = logging.getLogger("cobra.util.solver")
        old_level = cobra_logger.level
        cobra_logger.setLevel(logging.ERROR)   

        cobra.manipulation.delete.remove_genes(model, to_remove, remove_reactions=True)

        # restore original behaviour: 
        cobra_logger.setLevel(old_level)   
        
   
    logger.info(f"Found {len(model.genes)} modeled orthologs.")
    return 0



def translate_remaining_kos(logger, model, eggonog_ko_to_gids):
    
    
    _, modeled_gid_to_ko, _ = get_modeled_kos(model) 
    
    
    # iterate reactions:
    for r in model.reactions:

        gpr = r.gene_reaction_rule

        # force each gid to be surrounded by spaces: 
        gpr = ' ' + gpr.replace('(', ' ( ').replace(')', ' ) ') + ' '
        
        for gid in modeled_gid_to_ko.keys():
            if f' {gid} ' in gpr:
                
                new_gids = eggonog_ko_to_gids[modeled_gid_to_ko[gid]]
                gpr = gpr.replace(f' {gid} ', f' ({" or ".join(new_gids)}) ')       
            

        # remove spaces between parenthesis
        gpr = gpr.replace(' ( ', '(').replace(' ) ', ')')
        # remove spaces at the extremes: 
        gpr = gpr[1: -1]


        # New genes are introduced. Parethesis at the extremes are removed if not necessary. 
        r.gene_reaction_rule = gpr
        r.update_genes_from_gpr()
            
            
    # remaining old 'Cluster_'s need to removed.
    # remove if (1) hte ID starts with clusters AND (2) they are no more associated with any reaction
    to_remove = []
    for g in model.genes:
        
        if g.id in ['orphan', 'spontaneous']:
            continue
            
        if g.id in modeled_gid_to_ko.keys() and len(g.reactions)==0:
            to_remove.append(g)
            
    # warning suppression not needed here, as no reaction is actually removed.
    cobra.manipulation.delete.remove_genes(model, to_remove, remove_reactions=True)
    
        
    logger.info(f"Translated orthologs to {len(model.genes)} genes.")
    return 0
        
    

def restore_gene_annotations(logger, model, universe, eggonog_gid_to_kos):
    
    
    for g in model.genes:
        if g.id == 'spontaneous': 
            continue
            
        names = []    
        for ko in eggonog_gid_to_kos[g.id]:
            
            # get the corresponding universal gene:
            uni_g = None
            for ug in universe.genes:
                if 'ko' not in ug.annotation.keys():
                    continue
                if ug.annotation['ko']==ko:  # take the first (and only)
                    uni_g = ug
                    break
            if uni_g == None:  
                # The ko provided by eggnog-mapper is still not modeled in the universe.
                # Multiple ko are possible for each gene. Of these, only 1 could b modeled.
                continue
            
            
            # transfer annotations of this ko/universal gene:
            for key in uni_g.annotation.keys():
                if key == 'ko':
                    continue   # resulting models will loose links to kos.
                if key not in g.annotation:
                    g.annotation[key] = []
                items = uni_g.annotation[key]
                if type(items)==str:  items = [items]
                for i in items:
                    g.annotation[key].append(i)
                    
            # collect names
            names.append(uni_g.name)
        g.name = '; '.join(names)


    
def include_forced(logger, model, universe, force_inclusion):
    
    if force_inclusion != '-':
        forced_rids = force_inclusion.split(',')
        
        modeled_rids = [r.id for r in model.reactions]
        universal_rids = [r.id for r in universe.reactions]
        
        introduced_rids = []
        for rid in forced_rids: 
            
            if rid not in universal_rids:
                logger.info(f"Ignoring reaction ID {rid} since it's not included in the universe.")
                continue
            
            if rid not in modeled_rids:
                gempipe.import_from_universe(model, universe, rid, gpr='')
                introduced_rids.append(rid)
            else:
                logger.debug(f"Requested reaction ID {rid} was already included.")
        logger.info(f"Reactions forcibly included and orphans: {introduced_rids}.")
        
    return 0



def adjust_biomass_equation(logger, model, universe):
    
    
    # Note: universal and conditional precursors have been defined in 10.1016/j.ymben.2016.12.002 .
    precursor_to_pathway = {  # listing alternative biosynthetic pathways
        
        ##### cofactors_con #####
        #'f4200_c', # coenzyme f420 (electron transfer in methanogens, actinobacteria , and others)
        #'ptrc_c',   # Putrescine
        #'spmd_c',   # Sperimidine
        'pheme_c': ['M00868', 'M00121', 'M00926'],   # protoheme (heme)
        'mql8_c': ['M00116', 'M00930', 'M00931'],  # menaquinol
        'q8h2_c': ['M00117', 'M00989', 'M00128'],  # ubiquinol
        # Methionaquinone
        #'btn_c',    # B7: biotin
        #'ACP_c',    # Acyl-carrier protein
        'adocbl_c': ['M00122'],   # vitamin B12 (cobolamin)
        # Lipoate
        #'uacgam_c'  # uridine diphosphate N-Acetylglucosamine (UDP-GlcNAc)
        
        ##### cofactors_add #####
        'hemeO_c': ['gr_HemeO'],  # heme-O
        'sheme_c': ['M00846'],   # siroheme
        'moco_c': ['M00880'],  # molybdenum cofactor
        'phllqol_c': ['M00932'],  # phylloquinol
        'gthrd_c': ['M00118'],  # Reduced glutathione
        
        ##### lipids #####
        #'pe120_c', # phosphatidyl-ethanolamine (12:0;12:0)
        #'pg120_c', # phosphatidyl-glycerol (12:0;12:0)
        #'clpn120_c', # cardiolipin (12:0;12:0;12:0;12:0)
        
        ##### membrane_wall #####
        # 1-lysyl phosphatidylglycerol (plantarum)
        'peptidoSTA_c': ['gr_ptdSTA'], # peptidoglycan (dependant on 'udcpdp_c')
        'WTAgg40r_20n_20a_P_c': ['gr_WTA3'], # teichoic acids
        'WTArg40r_20g_20a_P_c': ['gr_WTA2'], # teichoic acids
        'WTAg40g_20g_20a_P_c':  ['gr_WTA1'], # teichoic acids
        'LTAgg40g_20n_20a_c':  ['gr_LTA1'], # lipoteichoic acids
        'LTAga40g_20t_20a_c':  ['gr_LTA2'], # lipoteichoic acids            
        # capsular polysaccharides
        # kdo_lipid_A
        
    }
    modeled_rids = [r.id for r in model.reactions]
    
    
    cnt_removed = 0
    varprec = {}  # dictionary of variable biomass precursors
    for precursor, pathways in precursor_to_pathway.items(): 
        
        pathway_to_absence = {}
        pathway_to_compstring = {}   # completeness string
        for pathway in pathways:   # 2+ pathways might lead to the same precursor
            # initialize counters:
            cnt_members_tot = 0
            cnt_members_present = 0

            
            if pathway not in [gr.id for gr in universe.groups]:
                continue   # still missing from the universe
                
            for member in universe.groups.get_by_id(pathway).members:
                cnt_members_tot += 1    
                if member.id in modeled_rids:
                    cnt_members_present += 1
            # populate dicts:
            pathway_to_absence[pathway] = (cnt_members_present / cnt_members_tot) < 0.50
            pathway_to_compstring[pathway] = f'{pathway}: {cnt_members_present}/{cnt_members_tot}'
            

        varprec[precursor] = '; '.join(list(pathway_to_compstring.values()))
        if all(list(pathway_to_absence.values())):
            cnt_removed += 1
            logger.debug(f"Biomass precursor '{precursor}' seems not required ({varprec[precursor]}).")
            # add metabolites to the right side (they will disappear if the balance if 0)
            model.reactions.Biomass.add_metabolites({precursor: 0.01})

       
    logger.info(f"Removed {cnt_removed} biomass precursors.")
    return varprec



def verify_growth(model, boolean=True):
        
    global __OPTTHR__
    res = model.optimize()
    obj_value = res.objective_value
    status = res.status
    if boolean:
        if obj_value < __OPTTHR__ or status=='infeasible':
            return False
        else: return True
    else:
        if status =='infeasible':
            return 'infeasible'
        elif obj_value < __OPTTHR__:
            return 0
        else:
            return round(obj_value, 3)



def apply_medium_given_column(logger, model, medium, column, is_reference=False):
        
        
    # retrieve metadata
    description = column.iloc[0]
    doi = column.iloc[1]
    author = column.iloc[2]
    units = column.iloc[3]

    
    # convert substrates to dict
    column = column.iloc[4:]
    column = column.to_dict()

    
    # add trace elements:
    column['fe2'] = 'NL'
    column['mobd'] = 'NL'
    column['cobalt2'] = 'NL'


    # reset exchanges
    gempipe.reset_growth_env(model)    
    modeled_rids = [r.id for r in model.reactions]


    for substrate, value in column.items():

        if type(value)==float:
            continue   # empty cell, exchange will remain close

            
        # check if exchange is modeled
        if is_reference == False: 
            if f'EX_{substrate}_e' not in modeled_rids:
                logger.error(f"No exchange reaction found for substrate '{substrate}' in medium '{medium}'.")
                return 1
        else:  # external reference models might follow different standards.
            # The exr might not be present. 
            if f'EX_{substrate}_e' not in modeled_rids:
                logger.info(f"Reference has no exchange reaction for '{substrate}' in medium '{medium}': this substrate will be ignored.")
                continue


        # case "not limiting"
        value = value.strip().rstrip()
        if value == 'NL':   # non-limiting case
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = -1000


        # case "single value"
        elif '+-' not in value and '±' not in value:  # single number case
            value = value.replace(' ', '')  # eg "- 0.03" --> "-0.03"
            try: value = float(value)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value}.")
                return 1
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = value


        # case "with experimental error"
        else:  # value +- error
            if '±' in value: 
                value, error = value.split('±', 1)
            else: value, error = value.split('+-', 1)
            value = value.rstrip()
            error = error.strip()
            value = value.replace(' ', '')  # eg "- 0.03" --> "-0.03"
            try: value = float(value)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value} +- {error}.")
                return 1
            try: error = float(error)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value} +- {error}.")
                return 1
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = value -error
            model.reactions.get_by_id(f'EX_{substrate}_e').upper_bound = value +error

    return 0



def get_gapfilling_repository(logger, universe, reference, exclude_orphans):
    
    
    # if provided, use the reference model as repository of reactions
    if reference != '-':   
        if reference.endswith('.xml'):
            refmodel = cobra.io.read_sbml_model(reference)
        elif reference.endswith('.json'):
            refmodel = cobra.io.load_json_model(reference)
        else:
            logger.error(f"Likely unsupported format found in --reference. Please use '.xml' or '.json'.")
            return 1
        repository = refmodel
    else:
        repository = universe


    # make an editable copy:
    repository_nogenes = repository.copy()


    if exclude_orphans:
        logger.info(f"Gapfilling is performed after removing orphan reactions.")
        to_remove = []

        cnt = 0
        for r in repository_nogenes.reactions: 
            if len(r.genes) !=0:
                continue 
            if len(r.metabolites) ==1:
                continue   # exclude exchanges/sinks/demands
            if any([m.id.endswith('_e') for m in r.metabolites]):
                continue   # exclude transporters

            cnt +=1
            to_remove.append(r)
            logger.debug(f"Removing orphan #{cnt}: {r.id} ({r.reaction}).")
        repository_nogenes.remove_reactions(to_remove)


    # remove genes to avoid the "ValueError: id purP is already present in list"
    cobra.manipulation.delete.remove_genes(repository_nogenes, [g.id for g in repository_nogenes.genes], remove_reactions=False)

    
    return repository_nogenes



def gapfill_on_media(logger, model, universe, expcon, media, varprec, reference, exclude_orphans):
    
    
    
    # get biomass precursors to gap-fill: 
    biomass_mids = []
    for value in get_biomass_dict().values(): biomass_mids = biomass_mids + value
    
    
    # prepare biomass sheet for excel output
    df_B = pnd.DataFrame()
    df_B['name'] = None
    df_B['cond'] = None
    df_B['coeff'] = None
    for mid in biomass_mids:
        
        df_B.loc[mid, 'name'] = universe.metabolites.get_by_id(mid).name
        df_B.loc[mid, 'coeff'] = 0.01
        if mid in varprec.keys():
            df_B.loc[mid, 'cond'] = varprec[mid]
            if mid not in [m.id for m in  model.reactions.Biomass.reactants]:  
                df_B.loc[mid, 'coeff'] = None
        else:  # biomass precursor is NOT variable (it's mandatory)
            df_B.loc[mid, 'cond'] = None
            
    
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: gap-filling will be skipped.")
        return df_B
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
        
        
    # get the repository of reactions:
    reference = '-'   # force universe: only universe will be used in this gap-filing step.
    repository_nogenes = get_gapfilling_repository(logger, universe, reference, exclude_orphans)
    
    
    logger.info(f"Gap-filling for biomass on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_B[f'{medium}'] = None
        logger.debug(f"Gap-filling on medium '{medium}'...")
                    
            
        
        # apply medium both on universe and model:
        response = apply_medium_given_column(logger, repository_nogenes, medium, expcon['media'][medium])
        if response == 1: return 1
        if not verify_growth(repository_nogenes):
            logger.error(f"Medium '{medium}' does not support growth of universe.")
            return 1
        
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
        if verify_growth(model):
            logger.info(f"No need to gapfill model on medium '{medium}'.")
            continue


        # launch gap-filling separately for each biomass precursor:
        for mid in biomass_mids:
            if mid in [m.id for m in model.reactions.Biomass.reactants]:
            
                # save time if it can already be synthesized
                if gempipe.can_synth(model, mid)[0]:
                    df_B.loc[mid, f'{medium}'] = ''
                    logger.debug(f"Gap-filled 0 reactions on medium '{medium}' for '{mid}': [].")
                    continue   # save time!


                # otherwise perform the actual gap-fill:    
                suggested_rids = gempipe.perform_gapfilling(model, repository_nogenes, mid, nsol=1, verbose=False)
                df_B.loc[mid, f'{medium}'] = '; '.join(suggested_rids)
                logger.debug(f"Gap-filled {len(suggested_rids)} reactions on medium '{medium}' for '{mid}': {suggested_rids}.")
                for rid in suggested_rids:
                    gempipe.import_from_universe(model, repository_nogenes, rid, gpr='')
                
                
    return df_B

    
    
def focused_suggestions_on_media(logger, model, universe, expcon, media, suggest, reference, exclude_orphans):
    
    
    # get metabolites mids on which to focus: 
    if suggest == '-':
        return 0    
    focus_mids = suggest.split(',')
    modeld_mids = [m.id for m in model.metabolites]


    # get involved media:
    if media == '-':
        logger.info(f"No media provided: synthesis suggestions will be skipped.")
        return 0
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1


    # get the repository of reactions:
    repository_nogenes = get_gapfilling_repository(logger, universe, reference, exclude_orphans)


    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue

        
        # apply medium both on universe and model:
        if_reference = True if reference != '-' else False
        response = apply_medium_given_column(logger, repository_nogenes, medium, expcon['media'][medium], if_reference)
        if response == 1: return 1

        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1

            
        for mid in focus_mids:
            logger.info(f"Suggesting missing reactions for '{mid}' on  medium '{medium}'...")

            
            # focus on a particular metabolite:
            if not (mid in modeld_mids and mid.endswith('_c')):
                logger.info(f"Cytosolic metabolite defined with --suggest is not included: '{mid}'.")
                continue
            
            
            # repository model must be able to produce it:
            if not gempipe.can_synth(repository_nogenes, mid)[0]:
                logger.info(f"Medium '{medium}' does not support synthesis of '{mid}' in repository model.")
                continue

            
            nsol = 5   # number of solutions
            logger.info(f"Computing {nsol} solutions for cytosolic metabolite {mid}...")
            # model and universe are already set up with the same growth medium:
            print()
            # perform gap-filling, solutions are shown using print()
            _ = gempipe.perform_gapfilling(model, repository_nogenes, mid, nsol=nsol)
            print()

    
    return 0

    
    
def grow_on_media(logger, model, expcon, media, fva):
    obj_id = 'max(obj)'
    
    
    # prepare biomass sheet for excel output
    df_G = pnd.DataFrame()
    
    
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: growth simulations will be skipped.")
        return df_G
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # initialize dataframe
    df_G.loc[obj_id, 'name'] = f'Objective reaction {gempipe.get_objectives(model)}'
    for r in model.reactions:
        df_G.loc[r.id, 'name'] = r.name
        
        
    logger.info(f"Growing on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column con the excel output
        df_G[f'{medium}'] = None
        logger.debug(f"Growing on medium '{medium}'...")
                    
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1

    
        # perform FBA
        res_fba = verify_growth(model, boolean=False)
        df_G.loc[obj_id, f'{medium}'] = res_fba
        
        
        # perform FVA if requested:
        if fva and (res_fba not in [0, 'infeasible']):
            logger.debug(f"FVA on medium '{medium}'...")
            df_fva = cobra.flux_analysis.flux_variability_analysis(model, model.reactions, fraction_of_optimum=0.9)
            for rid, row in df_fva.iterrows():
                df_G.loc[rid, f'{medium}'] = f"({round(row['minimum'], 3)}, {round(row['maximum'], 3)})"

    
    return df_G

    

def synthesize_on_media(logger, model, expcon, media, synth):
    
    global __OPTTHR__
    
    # prepare biomass sheet for excel output
    df_S = pnd.DataFrame()
    
    
    # get involved media:
    if synth == False:
        return df_S
    if media == '-':
        logger.info(f"No media provided: biosynthesis test will be skipped.")
        return df_S
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # initialize dataframe
    logger.info(f"Testing synthesis on {len(media)} media...")
    for m in model.metabolites:
        df_S.loc[m.id, 'name'] = m.name
        
        
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column con the excel output
        df_S[f'{medium}'] = None
        logger.debug(f"Testing synthesis on medium '{medium}'...")
                    
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1

    
        for m in model.metabolites:
            if m.id.endswith('_c'):
                binary, obj_value, status = gempipe.can_synth(model, m.id)
                if status =='infeasible':
                    df_S.loc[m.id, f'{medium}'] = 'infeasible'
                elif obj_value == 0:
                    df_S.loc[m.id, f'{medium}'] = 0
                elif obj_value < __OPTTHR__:
                    df_S.loc[m.id, f'{medium}'] = f'<{__OPTTHR__}'
                else:
                    df_S.loc[m.id, f'{medium}'] = round(obj_value, 3)

    
    return df_S



def omission_on_media(logger, model, expcon, media, omission):
        
    
    # define metabolites for single omission experiments  
    # Note: they are all universal
    pure_mids = set([
        # 20 aminoacids
        'ala__L', 'arg__L', 'asn__L', 'asp__L', 'cys__L', 
        'gln__L', 'glu__L', 'gly', 'his__L', 'ile__L', 
        'leu__L', 'lys__L', 'met__L', 'phe__L', 'pro__L', 
        'ser__L', 'thr__L', 'trp__L', 'tyr__L', 'val__L', 
        # 5 nucleotides
        'ade', 'gua', 'csn', 'thym', 'ura'])
    modeled_rids = [r.id for r in model.reactions]
    
    
    # prepare biomass sheet for excel output
    df_O = pnd.DataFrame()
    
    
    # get involved media:
    if omission == False:
        return df_O
    if media == '-':
        logger.info(f"No media provided: single omissions will be skipped.")
        return df_O
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
        
    # check if the target exchange reaction exists:
    for pure_mid in list(pure_mids):
        if f'EX_{pure_mid}_e' not in modeled_rids:
            logger.debug(f"Exchange reaction 'EX_{pure_mid}_e' not found during single omissions: it will be ignored.")
            df_O.loc[pure_mid, 'name'] = 'NA'
            pure_mids = pure_mids - set([pure_mid]) 
        else:  # initialize dataframe
            m = model.metabolites.get_by_id(f'{pure_mid}_e')
            df_O.loc[pure_mid, 'name'] = m.name
    
    
    logger.info(f"Performing single omissions on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_O[f'{medium}'] = None
        logger.debug(f"Performing single omissions on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1


        # set up exchange reactions:
        for pure_mid1 in pure_mids:
            for pure_mid2 in pure_mids:
                exr_id = f'EX_{pure_mid2}_e'
                
                if pure_mid2 != pure_mid1:
                    model.reactions.get_by_id(exr_id).lower_bound = -1000
                else:
                    model.reactions.get_by_id(exr_id).lower_bound = -0
                    
                    
            # perform FBA
            res_fba = verify_growth(model, boolean=False)
            df_O.loc[pure_mid1, f'{medium}'] = res_fba
               
            
    return df_O



def clean_formula(formula):
    
    # avoid confusion with 'C':
    formula = formula.replace('Ca', '').replace('Co', '').replace('Cu', '').replace('Cd', '').replace('Cr', '').replace('Cs', '').replace('Cl', '')   
    # avoid confusion with 'N':
    formula = formula.replace('Na', '').replace('Nb', '').replace('Ni', '').replace('Ne', '')
    # avoid confusion with 'P':
    formula = formula.replace('Pd', '').replace('Pt', '').replace('Pb', '').replace('Po', '')
    # avoid confusion with 'S':
    formula = formula.replace('Sc', '').replace('Si', '').replace('Sn', '').replace('Sb', '').replace('Se', '')
    
    return formula



def get_CNPS_sources(model):
    
    CNPS_sources = {'C': set(), 'N': set(), 'P': set(), 'S': set()}
    for r in model.reactions: 
        if len(r.metabolites)==1 and list(r.metabolites)[0].id.endswith('_e'):
            m = list(r.metabolites)[0]
            
            formula = m.formula
            formula = clean_formula(formula)
            
            if 'C' in formula: CNPS_sources['C'].add(r.id)
            if 'N' in formula: CNPS_sources['N'].add(r.id)
            if 'P' in formula: CNPS_sources['P'].add(r.id)
            if 'S' in formula: CNPS_sources['S'].add(r.id)
    
    return CNPS_sources


    
def get_source_name(atom):
    
    if atom=='C': return 'carbon'
    elif atom=='N': return 'nitrogen'
    elif atom=='P': return 'phosphorus'
    elif atom=='S': return 'sulfur'
    
    
    
def cnps_on_media(logger, model, expcon, media, cnps):
    
    
    # prepare biomass sheet for excel output
    df_C = pnd.DataFrame()
    
    
    # get involved media:
    if cnps == '-':
        return df_C
    if media == '-':
        logger.info(f"No media provided: alternative substrate analysis will be skipped.")
        return df_C
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # get main/starting C/N/P/S sources:
    if cnps == 'std': cnps = 'glc__D,nh4,pi,so4'
    startings = cnps.split(',')
    if len(startings) != 4: 
        logger.error(f"Starting sources must be 4: C, N, P, and S, in this order ({len(startings)} provided: {startings}).")
        return 1
    modeled_rids = [r.id for r in model.reactions]
    source_to_exr = {}
    for mid, source in zip(startings, ['C','N','P','S']):
        if mid.endswith('_e'): 
            mid_e = mid
        else: mid_e = mid + '_e'
        exr_id = f'EX_{mid_e}'
        if exr_id not in modeled_rids:
            logger.error(f"Expected exchange for {source} source not found (provided metabolite: '{mid}'; expected exchange: '{exr_id}').")
            return 1
        else:
            m = model.metabolites.get_by_id(mid_e)
            if source not in clean_formula(m.formula):
                logger.error(f"{source} source provided ('{mid}') does not contain {source} atoms.")
                return 1
            else:
                source_to_exr[source] = exr_id
            

    # define rows
    CNPS_sources = get_CNPS_sources(model)
    for source in ['C','N','P','S']:
        for exr_id in CNPS_sources[source]:
            m = list(model.reactions.get_by_id(exr_id).metabolites)[0]
            df_C.loc[f"[{source}] {exr_id}", 'source'] = get_source_name(source)
            df_C.loc[f"[{source}] {exr_id}", 'exchange'] = exr_id 
            df_C.loc[f"[{source}] {exr_id}", 'name'] = m.name    
    
    
    logger.info(f"Performing alternative substrate analysis on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_C[f'{medium}'] = None
        logger.debug(f"Performing alternative substrate analysis on medium '{medium}'...")
        
        
        not_part = set()
        for source in ['C','N','P','S']:
            for exr_id in CNPS_sources[source]:
                
                # apply medium
                response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
                if response == 1: return 1
            
                
                # maybe the starting substrate is not part of the medium
                if source_to_exr[source] not in list(model.medium.keys()):
                    not_part.add(f"[{source}] {source_to_exr[source]}")
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"NA"
                    continue
                
            
                model.reactions.get_by_id(source_to_exr[source]).lower_bound = -0
                obj0 = verify_growth(model, boolean=False)
                model.reactions.get_by_id(exr_id).lower_bound = -1000
                obj1 = verify_growth(model, boolean=False)
                
                
                if obj1 == 'infeasible':
                    df_C.loc[f"[{source}] {exr_id}", medium] = 'infeasible'
                elif obj0 == 'infeasible':
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"{obj1} (Δ=/)"
                else:
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"{obj1} (Δ={obj1-obj0})"
        
    
        # log if some starting source was not contained in this medium
        if not_part != set(): 
            logger.debug(f"Specified starting sources {not_part} were not contained in medium '{medium}'.")
    
    return df_C
    


def biolog_on_media(logger, model, universe, expcon, media, biolog, reference, exclude_orphans):
    
    
    # prepare biomass sheet for excel output
    df_P = pnd.DataFrame()
    
    
    # load assets:
    official_pm_tables = {}
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        with resources.path("unipruner.assets", f"{pm}.csv") as asset_path: 
            official_pm_tables[pm] = pnd.read_csv(asset_path, index_col=1, names=['plate','substrate','source','u1','u2','u3','u4','kc','cas'])
    
    
    # get involved media:
    if biolog == '-':
        return df_P
    if media == '-':
        logger.info(f"No media provided: Biolog(R)-based model curation will be skipped.")
        return df_P
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # get plates for this strain
    avail_plates = []
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        if biolog in expcon[pm].columns: 
            avail_plates.append(pm)
    if avail_plates == set():
        logger.info(f"No Biolog(R) plates found for strain '{biolog}': Biolog(R)-based model curation will be skipped.")
        return df_P
    else:
        logger.info(f"Found {len(avail_plates)} Biolog(R) plates for strain '{biolog}': {sorted(avail_plates)}.")
        
        
    # get kc annotations:
    kc_to_exr = {}
    for m in model.metabolites: 
        if m.id.endswith('_e') == False:
            continue
        if 'kegg.compound' not in m.annotation.keys():
            continue
        kc_ids = m.annotation['kegg.compound']
        if type(kc_ids) == str: kc_ids = [kc_ids]
        kc_ids = [i for i in kc_ids if i!='CXXXXX']  
        for kc_id in kc_ids:
            kc_to_exr[kc_id] = f'EX_{m.id}'
        
        
    # prepare rows:
    for pm in avail_plates:
        for well, row in official_pm_tables[pm].iterrows():
            # write substrate name:
            df_P.loc[f"{pm}:{well}", 'substrate'] = row['substrate']
            
            
            # write source type:
            if pm in ['PM1', 'PM2A']: 
                df_P.loc[f"{pm}:{well}", 'source'] = 'carbon'
            elif pm == 'PM3B': 
                df_P.loc[f"{pm}:{well}", 'source'] = 'nitrogen'
            else:
                if well[0] in ['F','G','H']: df_P.loc[f"{pm}:{well}", 'source'] = 'sulfur'
                else: df_P.loc[f"{pm}:{well}", 'source'] = 'phosphorus'
            
            
            # get kc and write the correspondent exchange
            kc = row['kc']
            if type(kc)==float: 
                df_P.loc[f"{pm}:{well}", 'exchange'] = 'NA'
            elif kc.startswith('C'):
                if kc not in kc_to_exr.keys():
                    df_P.loc[f"{pm}:{well}", 'exchange'] = 'NA'
                else:
                    df_P.loc[f"{pm}:{well}", 'exchange'] = kc_to_exr[kc]
            elif kc.startswith('D'):
                df_P.loc[f"{pm}:{well}", 'exchange'] =  'NA'  # TODO manage exchanges in this case
            else:
                df_P.loc[f"{pm}:{well}", 'exchange'] =  '???'
                
                
    
    # get the repository of reactions:
    reference = '-'   # force universe: only universe will be used in this gap-filing step.
    repository_nogenes = get_gapfilling_repository(logger, universe, reference, exclude_orphans)
    
    
    logger.info(f"Performing Biolog(R)-based model curation on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_P[f'{medium}'] = None
        logger.debug(f"Performing Biolog(R)-based model curation on medium '{medium}'...")
        

    
    return df_P



def essential_genes_on_media(logger, model, expcon, media, essential):
    
    global __OPTTHR__
    
    
    # prepare biomass sheet for excel output
    df_E = pnd.DataFrame()
    
    
    # get involved media:
    if essential == False:
        return df_E
    if media == '-':
        logger.info(f"No media provided: essential genes prediction will be skipped.")
        return df_E
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    

    # define rows
    for g in model.genes:
        if g.id in ['spontaneous', 'orphan']:
            continue
        df_E.loc[f"{g.id}", 'name'] = g.name    
        df_E.loc[f"{g.id}", 'involving'] = '; '.join([r.id for r in g.reactions])
    
    
    logger.info(f"Predicting essential genes on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_E[f'{medium}'] = None
        logger.debug(f"Predicting essential genes on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
    
    
        # verify growth:
        obj = verify_growth(model, boolean=False)
        if obj in ['infeasible', 0]:
            df_E[f'{medium}'] = 'NA'
            continue
    
        
        single = cobra.flux_analysis.single_gene_deletion(model)
        for index, row in single.iterrows(): 
            gid = list(row['ids'])[0]  # they are single deletions
            if gid in ['spontaneous', 'orphan']:
                continue
                

            if row['status'] == 'infeasible': 
                df_E.loc[f"{gid}", medium] = 'True'
            elif row['growth'] < __OPTTHR__:
                df_E.loc[f"{gid}", medium] = 'True'
            else: 
                df_E.loc[f"{gid}", medium] = round(row['growth'], 3)
    
    return df_E



def growth_factors_on_media(logger, model, expcon, media, factors):
        
    
    # prepare biomass sheet for excel output
    df_F = pnd.DataFrame()
    
    
    # get involved media:
    if factors == False:
        return df_F
    if media == '-':
        logger.info(f"No media provided: essential genes prediction will be skipped.")
        return df_F
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # define rows
    df_F['mid'] = ''
    df_F['name'] = ''

    
    logger.info(f"Predicting growth factors on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_F[f'{medium}'] = None
        logger.debug(f"Predicting growth factors on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
    
    
        # verify growth:
        obj = verify_growth(model, boolean=False)
        if obj not in ['infeasible', 0]:
            df_F[f'{medium}'] = ''
        else:
            while obj in ['infeasible', 0]:
                res_dict = gempipe.sensitivity_analysis(model, scaled=False, top=1)
                for exr_id, value in res_dict.items():
                    if value < 0:
                        model.reactions.get_by_id(exr_id).lower_bound = -1000
                        obj = verify_growth(model, boolean=False)
                        df_F.loc[exr_id, f'{medium}'] = 'ADD'

         
    # populate 'mid'/'name' columns:
    for exr_id, row in df_F.iterrows():
        r = model.reactions.get_by_id(exr_id)
        m = list(r.metabolites)[0]
        df_F.loc[exr_id, 'mid'] = m.id.rsplit('_', 1)[0]
        df_F.loc[exr_id, 'name'] = m.name
    # replace index with 'mid':
    df_F = df_F.set_index('mid', drop=True)
        
        
    return df_F


    
def remove_disconnected(logger, model):
    
    to_remove = []
    for m in model.metabolites:
        if len(m.reactions) == 0:
            to_remove.append(m)
    model.remove_metabolites(to_remove)
    logger.info(f"Removed {len(to_remove)} disconnected metabolites.")
    
    

def write_excel_model(model, filepath, df_B, df_G, df_S, df_O, df_C, df_P, df_E, df_F):
    
    df_R = []
    df_M = []
    df_T = []
    df_A = []
    
    # format df_B:  # biomass assembly
    df_B.insert(0, 'mid', '')  # new columns as first
    df_B['mid'] = df_B.index
    df_B = df_B.reset_index(drop=True)
    
    # format df_G:  # growth tests
    df_G.insert(0, 'rid', '')  # new columns as first
    df_G['rid'] = df_G.index
    df_G = df_G.reset_index(drop=True)
    
    # format df_S:  # biosynthetic capabilities
    df_S.insert(0, 'mid', '')  # new columns as first
    df_S['mid'] = df_S.index
    df_S = df_S.reset_index(drop=True)
    
    # format df_O:  # single omission
    df_O.insert(0, 'mid', '')  # new columns as first
    df_O['mid'] = df_O.index
    df_O = df_O.reset_index(drop=True)
    
    # format df_C:  phenotype screening (CNPS)
    df_C.insert(0, 'substrate', '')  # new columns as first
    df_C['substrate'] = df_C.index
    df_C = df_C.reset_index(drop=True)
    
    # format df_P:  phenotype screening (Biolog(R))
    df_P.insert(0, 'plate:well', '')  # new columns as first
    df_P['plate:well'] = df_P.index
    df_P = df_P.reset_index(drop=True)
    
    # format df_E:  essential genes
    df_E.insert(0, 'gid', '')  # new columns as first
    df_E['gid'] = df_E.index
    df_E = df_E.reset_index(drop=True)
    
    # format df_F:  growth factors
    df_F.insert(0, 'mid', '')  # new columns as first
    df_F['mid'] = df_F.index
    df_F = df_F.reset_index(drop=True)
    
    
    for r in model.reactions:
        
        
        # handle artificial reactions
        if r.id == 'Biomass':
            df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'biomass', 'name': r.name})
            
            
        elif len(r.metabolites) == 1:
            if len(r.metabolites)==1 and list(r.metabolites)[0].id.rsplit('_',1)[-1] == 'e': 
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'exchange', 'name': r.name})
            elif r.lower_bound < 0 and r.upper_bound > 0:
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'sink', 'name': r.name})
            elif r.lower_bound == 0 and r.upper_bound > 0:
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'demand', 'name': r.name})
          
        
        else: # more than 1 metabolite involved
            
            # get kr codes: 
            if 'kegg.reaction' not in r.annotation.keys():  kr_ids = ''
            else:  
                kr_ids = r.annotation['kegg.reaction']
                if type(kr_ids) == str: kr_ids = [kr_ids]
                kr_ids = '; '.join([i for i in kr_ids if i!='RXXXXX'])

            # introduce reaction in the correct table: 
            r_dict = {'rid': r.id, 'rstring': r.reaction, 'kr': kr_ids, 'gpr': r.gene_reaction_rule, 'name': r.name}
            if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites])) == 1:
                df_R.append(r_dict)
            else: df_T.append(r_dict)
        
        
    for m in model.metabolites: 
        
        # get kc codes: 
        if 'kegg.compound' not in m.annotation.keys():  kc_ids = ''
        else:  
            kc_ids = m.annotation['kegg.compound']
            if type(kc_ids) == str: kc_ids = [kc_ids]
            kc_ids = '; '.join([i for i in kc_ids if i!='CXXXXX'])
        
        df_M.append({'mid': m.id, 'formula': m.formula, 'charge': m.charge, 'kc': kc_ids, 'name': m.name})

    
    
    df_R = pnd.DataFrame.from_records(df_R)
    df_M = pnd.DataFrame.from_records(df_M)
    df_T = pnd.DataFrame.from_records(df_T)
    df_A = pnd.DataFrame.from_records(df_A)
    with pnd.ExcelWriter(filepath) as writer:
        df_R.to_excel(writer, sheet_name='Reactions', index=False)
        df_M.to_excel(writer, sheet_name='Metabolites', index=False)
        df_T.to_excel(writer, sheet_name='Transporters', index=False)
        df_A.to_excel(writer, sheet_name='Artificials', index=False)
        df_B.to_excel(writer, sheet_name='Biomass', index=False)
        if len(df_P)!=0: df_P.to_excel(writer, sheet_name='Biolog®', index=False)
        if len(df_G)!=0: df_G.to_excel(writer, sheet_name='Growth', index=False)
        if len(df_S)!=0: df_S.to_excel(writer, sheet_name='Synthesis', index=False)
        if len(df_O)!=0: df_O.to_excel(writer, sheet_name='Omission', index=False)
        if len(df_C)!=0: df_C.to_excel(writer, sheet_name='Substrates', index=False)
        if len(df_E)!=0: df_E.to_excel(writer, sheet_name='Essential', index=False)
        if len(df_F)!=0: df_F.to_excel(writer, sheet_name='Factors', index=False)

    
        
def unipruner(args, logger): 
    
        
    
    # check input files:
    response = check_inputs(logger, args.universe, args.eggnog)
    if type(response)==int:
        return 1
    universe = response[0]
    eggnog = response[1]
        
    
    # check file structure ('expcon'= experimental constraints)
    expcon = get_expcon(logger)
    if type(expcon)==int: return 1

    
    ##### PRUNING
    # get important dictionaries: 'eggnog_ko_to_gids' and 'eggonog_gid_to_kos'
    eggnog_ko_to_gids, eggonog_gid_to_kos = parse_eggnog(eggnog)
    #
    model = universe.copy()
    model.id = Path(args.eggnog).stem        
    #
    subtract_kos(logger, model, eggnog_ko_to_gids)
    #
    translate_remaining_kos(logger, model, eggnog_ko_to_gids)
    #
    restore_gene_annotations(logger, model, universe, eggonog_gid_to_kos)
    #####
    
    
    ###### GAPFILLING
    # force inclusion of reactions:  
    include_forced(logger, model, universe, args.force_inclusion)
    #
    # adjust biomass equation:
    # get the variable precursors dataframe ('variable_precs_df')
    varprec = adjust_biomass_equation(logger, model, universe)
    #
    # gap-fill based on media:
    df_B = gapfill_on_media(logger, model, universe, expcon, args.gap_fill, varprec, args.reference, args.exclude_orphans)
    if type(df_B)==int: return 1
    #
    # perform Biolog(R) simulations based on media. Gap-filling is included. 
    df_P = biolog_on_media(logger, model, universe, expcon, args.gap_fill, args.biolog, args.reference, args.exclude_orphans)
    if type(df_P)==int: return 1
    ######

    
    # remove disconnected metabolites
    remove_disconnected(logger, model)
    
    
    ##### ANALYSIS
    # growth simulations based on media
    df_G = grow_on_media(logger, model, expcon, args.fba, args.fva)
    if type(df_G)==int: return 1
    #
    # test synthesis based on media
    df_S = synthesize_on_media(logger, model, expcon, args.fba, args.synth)
    if type(df_S)==int: return 1
    #
    # perform single omission experiments based on media
    df_O = omission_on_media(logger, model, expcon, args.fba, args.omission)
    if type(df_O)==int: return 1
    #
    # perform alternative substrate anaysis based on media
    df_C = cnps_on_media(logger, model, expcon, args.fba, args.cnps)
    if type(df_C)==int: return 1
    #
    # predict essential genes
    df_E = essential_genes_on_media(logger, model, expcon, args.fba, args.essential)
    if type(df_E)==int: return 1
    #
    # predict growth factors
    df_F = growth_factors_on_media(logger, model, expcon, args.fba, args.factors)
    if type(df_F)==int: return 1
    #####
    
    
    # reset growth environment befor saving the model
    gempipe.reset_growth_env(model)
                     
    
    # output the model:
    cobra.io.save_json_model(model, f'{model.id}.json')        # JSON
    cobra.io.write_sbml_model(model, f'{model.id}.xml')        # SBML   # groups are saved only to SBML
    write_excel_model(model, f'{model.id}.xlsx', df_B, df_G, df_S, df_O, df_C, df_P, df_E, df_F)  
    logger.info(f"'{os.getcwd()}/{model.id}.json' created!")
    logger.info(f"'{os.getcwd()}/{model.id}.xml' created!")
    logger.info(f"'{os.getcwd()}/{model.id}.xlsx' created!")
    log_metrics(logger, model)
    
    
    # suggest missing reactions focusing of provided metabolites
    response = focused_suggestions_on_media(logger, model, universe, expcon, args.gap_fill, args.suggest, args.reference, args.exclude_orphans)
    if response==1: return 1
    

    
    return 0