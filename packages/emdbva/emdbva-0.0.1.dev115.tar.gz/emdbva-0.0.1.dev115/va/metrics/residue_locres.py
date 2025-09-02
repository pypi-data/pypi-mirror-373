from va.utils.misc import floattohex, scale_values, scale_value, float_to_hex
from va.utils.MapProcessor import MapProcessor
from va.utils.ChimeraxViews import ChimeraxViews
import numpy as np


def local_resolution_json(map, inmodels, radius, value_range):
    """
        Interpolate density value of one atom, if indices are on the same plane use nearest method
        otherwise use linear

    :param map: a string of full map path or a mrcfile object
    :param inmodels: Structure instance from biopython package mmcif parser
    :param radius: a number to define the radius that take into account around per atom
    :param value_range: tuple of local resolution value range used to colour the map
    :return: a dictionary with all residue local resolution values
    """

    map = MapProcessor(map)
    models = []
    if isinstance(inmodels, list):
        models = inmodels
    else:
        models.append(inmodels)
    result = {}
    modelcount = 0
    for model in models:
        modelcount += 1
        modelname = model.filename.split('/')[-1]
        atomcount = 0
        chainaiscore = {}
        data_result = {}
        allkeys = []
        allvalues = []
        colors = []
        chainai_atomsno = {}
        # use for generate mask for the whole model or the voxels involved
        # tmp_allindices = set()
        # tmp_allcoords = []
        for chain in model.get_chains():
            chain_name = chain.id
            chain_residue_count = 0
            chain_resolution = 0.
            for residue in chain.get_residues():
                residue_atom_count = 0
                chain_residue_count += 1
                residue_name = residue.resname
                residue_no = residue.id[1]
                nearresidue_voxels = set()
                for atom in residue.get_atoms():
                    if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                        continue
                    atomcount += 1
                    residue_atom_count += 1
                    onecoor = atom.coord
                    around_indices = map.get_close_voxels_indices(onecoor, radius)
                    nearresidue_voxels.update(around_indices)
                    # use for generate mask for the whole model or the voxels involved
                    # tmp_allcoords.append(onecoor)
                    # tmp_allindices.update(around_indices)
                if residue_atom_count == 0:
                    continue
                # residue inclusion section
                keystr = f'{chain_name}:{residue_no} {residue_name}'
                allkeys.append(keystr)
                cur_residue_resolution = map.residue_average_resolution(list(nearresidue_voxels))
                value = float('%.4f' % cur_residue_resolution)
                residue_color = floattohex([value])[0]
                chain_resolution += value
                allvalues.append(value)
                colors.append(residue_color)
            # chain inclusion section
            if chain_name in chainai_atomsno.keys():
                chain_resolution += chainai_atomsno[chain_name]['value']
                chain_residue_count += chainai_atomsno[chain_name]['residuesinchain']
            # For cases where one water molecule has a single but different chain id
            if chain_residue_count == 0:
                continue
            chainai_atomsno[chain_name] = {'value': chain_resolution, 'residuesinchain': chain_residue_count}

        # produce a mask for entire model
        # map.generate_mask(tmp_allcoords, radius)

        for chainname, chain_scores in chainai_atomsno.items():
            chain_ai = float('%.3f' % round((float(chain_scores['value']) / chain_scores['residuesinchain']), 4))
            aicolor = floattohex([chain_ai])[0]
            chainaiscore[chainname] = {'value': chain_ai, 'color': aicolor, 'numberOfResidues': chain_scores['residuesinchain']}
        # For using new_min and new_max which match to 0 and 1 for model-local-resolution colouring
        # map_min = map.map.data.min()
        # map_max = map.map.data.max()
        map_min, map_max = value_range
        residues_min = min(allvalues)
        residues_max = max(allvalues)
        real_min = map_min if map_min < residues_min else residues_min
        real_max = map_max if map_max > residues_max else residues_max
        new_min = scale_value(residues_min, real_min, real_max, 0, 1)
        new_max = scale_value(residues_max, real_min, real_max, 0, 1)

        data_result['residue'] = allkeys
        data_result['localResolution'] = allvalues
        data_result['color'] = [float_to_hex(i) for i in scale_values(allvalues, new_min, new_max)]
        # data_result['color'] = [float_to_hex(i) for i in scale_values(allvalues, 0, 1)]
        data_result['chainResolution'] = chainaiscore
        result[str(modelcount-1)] = {'name': modelname, 'data': data_result}

    return result

def model_local_resolution_views(input_json, map_name, data_type, chimerax_bin_dir):
    """
        Generate local resolution views based on the input json file

    :param input_json: a string of full path to input json file
    :param map_name: a string of map name
    :param data_type: a string of type
    """

    viewer = ChimeraxViews(chimerax_bin_dir, input_json)
    root_data = viewer.get_root_data(data_type)
    viewer.get_model_views(map_name, root_data, data_type)

def map_local_resolution_views(map_name, data_type, chimerax_bin_dir, work_dir, input_json=None):
    """
        Generate local resolution view based on local resolution map
    """
    if input_json:
        viewer = ChimeraxViews(chimerax_bin_dir, input_json)
        root_data = viewer.get_root_data('residue_local_resolution')
        viewer.get_map_views(map_name, root_data, data_type)
    else:
        viewer = ChimeraxViews(chimerax_bin_dir, None, work_dir)
        # viewer.get_views(map_name,None, data_type)
        viewer.get_map_views(map_name,None, data_type)

