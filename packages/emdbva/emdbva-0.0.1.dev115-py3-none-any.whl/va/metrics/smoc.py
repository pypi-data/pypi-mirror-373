import sys
import os
from TEMPy.maps.map_parser import MapParser
from TEMPy.protein.structure_parser import mmCIFParser
from TEMPy.protein.scoring_functions import FastSMOC
from collections import OrderedDict
from va.utils.misc import create_directory
from va.utils.misc import check_same_keys
from va.utils.misc import floattohex


def restructure_dict(data):
    """
    Reformat dictionary
    data: a dictionary as "('A', 659, 'PHE'), ('A', 416, 'GLU'), ('C', 651, 'GLU'), ('A', 498, 'GLN')}"
    return: a dictionary {'A': {416: 'GLU', 498: 'GLN', 659: 'PHE'}, 'C': {651: 'GLU'}}
    """

    restructured_dict = {}
    for item in data:
        chain, number, residue = item
        if chain not in restructured_dict:
            restructured_dict[chain] = {}
        restructured_dict[chain][number] = residue
    # Sort residue numbers within each chain
    for chain in restructured_dict:
        restructured_dict[chain] = dict(sorted(restructured_dict[chain].items()))
    return restructured_dict



def run_smoc(full_modelpath, full_mappath, res, output_path):
    """
        smoc score
    :return:
    """

    errlist = []
    result_dict = {}
    try:
        create_directory(output_path)
        cmap = MapParser.readMRC(full_mappath)
        model = mmCIFParser.read_mmCIF_file(full_modelpath)
        window = 11
        scorer = FastSMOC(model, cmap, float(res))
        chain_scores = {}
        chains = set(a.chain for a in model.atomList)
        residues_set = set((a.chain, a.res_no, a.res) for a in model.atomList)
        residues = restructure_dict(residues_set)
        for chain in chains:
            # original way below but smoc results may see nan value (37889)
            # chain_scores[chain] = scorer.score_chain_contig(chain, window)
            tmp_chain_scores = scorer.score_chain_contig(chain, window)
            chain_scores[chain] = {k: (0.0 if v != v else v) for k, v in tmp_chain_scores.items()}
        smoc_result = [residues, chain_scores]

        model_name = os.path.basename(full_modelpath)
        result_dict = smoc_todict(model_name, smoc_result)
    except AssertionError:
        sys.stderr.write('SMOC does not work well. \n')

    return result_dict, errlist

def smoc_todict(model_name, smoc_result):
    """
        Save SMOC results into json file
    :param smoc_result:
    :return: json file name
    """

    colors = []
    smocs = []
    residues = []
    chain_smocs = OrderedDict()
    check = check_same_keys(smoc_result[0], smoc_result[1])
    if check:
        chain_all = smoc_result[0].keys()
        chain_length = len(chain_all)
        for chain in smoc_result[0].keys():
            chain_smoc = 0.
            residues_list = smoc_result[0][chain].keys()
            for residue_no in residues_list:
                residue_smoc = smoc_result[1][chain][residue_no]
                chain_smoc += residue_smoc
                residue_type = smoc_result[0][chain][residue_no]
                residue_color = floattohex([residue_smoc])[0]
                residue_string = '{}:{} {}'.format(chain, residue_no, residue_type)
                colors.append(residue_color)
                smocs.append(float('%.3f' % residue_smoc))
                residues.append(residue_string)

            chain_smocvalue = chain_smoc / chain_length if chain_length != 0. else 0.
            chain_smoccolor = floattohex([chain_smocvalue])[0]
            chain_smocs[chain] = {'value': float('%.3f' % chain_smocvalue), 'color': chain_smoccolor}

        average_smoc = float('%.3f' % (sum(smocs)/len(smocs)))
        average_smoc_color = floattohex([average_smoc])[0]

        data = {'averagesmoc': average_smoc, 'averagesmoc_color': average_smoc_color, 'color': colors,
                'smoc_scores': smocs, 'residue': residues, 'chainsmoc': chain_smocs}

        result_dict = {'name': model_name, 'data': data}

        return result_dict
    return None