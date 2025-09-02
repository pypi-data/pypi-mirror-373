import sys
import timeit
import numpy as np
import bisect
import codecs
import json
import matplotlib.pyplot as plt
from collections import OrderedDict
from va.utils.misc import *
from scipy.interpolate import RegularGridInterpolator
import math


class Inclusion:
    def __init__(self, map, cl, model, workdir):
        self.map = map
        self.cl = cl
        self.model = model
        self.workdir = workdir
        self.mapname = os.path.basename(map.fullname)

    # @execution_time('inclusion')
    # def atom_inclusion(self):
    #     """
    #     Generate atom inclusion and residue atom inclusion information verses different contour level
    #     Both full atoms and backbone information are included.
    #     Results wrote to JSON file
    #
    #     :return: None
    #     """
    #     if self.model is None:
    #         self._log_error('REMINDER: atom inclusion and residue inclusion will not be calculated without model structure.')
    #         return
    #
    #     if self.cl is None:
    #         self._log_error('REMINDER: atom inclusion and residue inclusion will not be calculated without contour level given.')
    #         return
    #
    #     combinresult = self.density_interpolation()
    #     atomindict, resindict = self._process_combinresult(combinresult)
    #     self._save_results(atomindict, resindict)
    #
    # def _log_error(self, message):
    #     sys.stderr.write(message + '\n')
    #     print('------------------------------------')
    # def _save_results(self, atomindict, resindict):
    #     try:
    #         with codecs.open(self.workdir + self.mapname + '_atom_inclusion.json', 'w', encoding='utf-8') as f:
    #             json.dump(atomindict, f)
    #     except:
    #         sys.stderr.write(f'Saving to atom inclusion json error: {sys.exc_info()[1]}.\n')
    #
    #     try:
    #         with codecs.open(self.workdir + self.mapname + '_residue_inclusion.json', 'w', encoding='utf-8') as f1:
    #             json.dump(resindict, f1)
    #     except:
    #         sys.stderr.write(f'Saving to residue inclusion json error: {sys.exc_info()[1]}.\n')
    #
    # def _process_combinresult(self, combinresult):
    #     atomindict, resindict = OrderedDict(), OrderedDict()
    #     datadict, resdict = OrderedDict(), OrderedDict()
    #     counter, allmodels_numberatoms, allmodels_atom_inclusion = 0, 0, 0.0
    #
    #     for key, value in combinresult.items():
    #         try:
    #             print(key, value)
    #             exit()
    #             interpolations, allcontoursdict, chainaiscore, atomoutsidebox = value
    #             models = [curmodel for curmodel in self.model if key in curmodel.filename] if isinstance(self.model, list) else [self.model]
    #             model = self._get_single_model(models)
    #             allatoms = list(model.get_atoms())
    #             result = self.__getfractions(interpolations, allatoms)
    #             print('test 4----------')
    #             levels = self._get_levels()
    #             datadict[str(counter)] = self._create_datadict_entry(key, levels, result, atomoutsidebox, chainaiscore)
    #             allmodels_numberatoms += int(result[3])
    #             allmodels_atom_inclusion += result[3] * result[2]
    #             self._plot_inclusion(levels, result)
    #         except:
    #             self._handle_error('Atom inclusion calculation error', key, datadict, counter)
    #
    #         try:
    #             resdict[str(counter)] = self._create_resdict_entry(key, allcontoursdict)
    #         except:
    #             self._handle_error('Residue inclusion calculation error', key, resdict, counter)
    #
    #         counter += 1
    #
    #     if allmodels_numberatoms != 0:
    #         datadict['average_ai_allmodels'] = round(allmodels_atom_inclusion / allmodels_numberatoms, 3)
    #     atomindict['atom_inclusion_by_level'] = datadict
    #     resindict['residue_inclusion'] = resdict
    #
    #     return atomindict, resindict
    #
    # def _get_single_model(self, models):
    #     if len(models) == 1:
    #         return models[0]
    #     elif len(models) == 0:
    #         print('There is no model!')
    #         exit()
    #     else:
    #         print('There are more than one model which should be only one.')
    #         exit()
    #
    # def __getfractions(self, interpolation, model):
    #     """
    #     Produce atom inclusion fraction information for full atoms and backbone trace
    #
    #     :param interpolation: List of interpolation values
    #     :param model: Protein model in mmcif format
    #     :return: Tuple contains full atom inclusion fractions and backbone inclusion fractions
    #     """
    #     bins = self._get_bins()
    #     print('inside 1 ----------')
    #     print(interpolation)
    #     newinterpolation = [interpolation[i] for i in range(len(interpolation)) if 'H' not in model[i].fullname]
    #     print('inside 2 ----------')
    #     entire_average = sum(np.asarray(newinterpolation) > self.cl) / float(len(newinterpolation))
    #     print('inside 3 ----------')
    #     full_atom_inclusion = self._calculate_inclusion(bins, newinterpolation)
    #     print('inside 4 ----------')
    #     backbone_inclusion = self._calculate_inclusion(bins, [interpolation[i] for i in range(len(interpolation)) if model[i].fullname in self._backbone_atoms()])
    #
    #     return full_atom_inclusion, backbone_inclusion, entire_average, float(len(newinterpolation))
    #
    # def _get_bins(self):
    #     bins = np.linspace(self.map.data.min(), self.map.data.max(), 129)
    #     binlist = bins.tolist()
    #     bisect.insort(binlist, self.cl)
    #     binlist.pop(binlist.index(self.cl) - 1)
    #     return np.asarray(binlist)
    #
    # def _calculate_inclusion(self, bins, interpolations):
    #     return [sum(np.asarray(interpolations) > i) / float(len(interpolations)) for i in bins]
    #
    # def _backbone_atoms(self):
    #     return ['N', 'C', 'O', 'CA', "C3'", "C4'", "C5'", "O3'", "O5'", 'P', 'OXT']
    #
    # def _get_levels(self):
    #     levels = np.linspace(self.map.data.min(), self.map.data.max(), 129)
    #     binlist = levels.tolist()
    #     bisect.insort(binlist, self.cl)
    #     binlist.pop(binlist.index(self.cl) - 1)
    #     return np.asarray(binlist)
    #
    # def _create_datadict_entry(self, key, levels, result, atomoutsidebox, chainaiscore):
    #     return {
    #         'name': key,
    #         'level': [round(elem, 6) for elem in levels.tolist()],
    #         'all_atom': [round(elem, 3) for elem in result[0]],
    #         'backbone': [round(elem, 3) for elem in result[1]],
    #         'atomoutside': atomoutsidebox,
    #         'chainaiscore': chainaiscore,
    #         'totalNumberOfAtoms': int(result[3]),
    #         'average_ai_model': round(result[2], 3),
    #         'average_ai_color': floattohex([round(result[2], 6)])[0]
    #     }
    #
    # def _plot_inclusion(self, levels, result):
    #     data_len = len(levels.tolist())
    #     plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[0]], '-g', label='Full atom')
    #     plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[1]], '-b', label='Backbone')
    #     plt.plot(data_len * [self.cl], np.linspace(0, 1, data_len), '-r', label='Recommended contour level')
    #     plt.legend(loc='lower left')
    #     plt.savefig(self.workdir + self.mapname + '_inclusion.png')
    #     plt.close()
    #
    #
    # def _handle_error(self, error_message, key, dict_to_update, counter):
    #     err = f'{error_message}(Model: {key}): {sys.exc_info()[1]}.'
    #     sys.stderr.write(err + '\n')
    #     dict_to_update[str(counter)] = {'err': {f'{error_message.lower().replace(" ", "_")}_err': [err]}}
    #
    # def _create_resdict_entry(self, key, allcontoursdict):
    #     contourdict = OrderedDict()
    #     for contour, keysvalues in allcontoursdict.items():
    #         allvalues, allkeys = keysvalues[1], keysvalues[0]
    #         colours = floattohex(allvalues)
    #         contourkey = str(round(float(contour), 6))
    #         contourdict[contourkey] = OrderedDict([('color', colours), ('inclusion', allvalues), ('residue', allkeys)])
    #     contourdict['name'] = key
    #     return contourdict
    #
    #
    # def density_interpolation(self):
    #     """
    #     Interpolate density value of one atom, if indices are on the same plane use nearest method
    #     otherwise use linear
    #
    #     :return: List contains all density interpolations of atoms from model
    #     """
    #     myinter = self.interpolation()
    #     models = self.model if isinstance(self.model, list) else [self.model]
    #     contourrange = np.asarray([self.cl])
    #     result = {}
    #
    #     for model in models:
    #         allcontoursdict, atomoutsidenum, chainaiscore = self._process_model(model, contourrange, myinter)
    #         result[model.filename.split('/')[-1]] = ([], allcontoursdict, chainaiscore, atomoutsidenum)
    #
    #     return result
    #
    # def _process_model(self, model, contourrange, myinter):
    #     allcontoursdict, atomoutsidenum, chainaiscore = OrderedDict(), 0, {}
    #     chainai_atomsno = {}
    #
    #     for contour in contourrange:
    #         interpolations, allkeys, allvalues = [], [], []
    #         for chain in model.get_chains():
    #             chainatominterbin, chain_atom_count = 0, 0
    #             for residue in chain.get_residues():
    #                 resatominterbin, residue_atom_count = 0, 0
    #                 for atom in residue.get_atoms():
    #                     if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
    #                         continue
    #                     onecoor = atom.coord
    #                     oneindex = self.__getindices(onecoor)[1]
    #                     curinterpolation = self._get_interpolation_value(oneindex, myinter)
    #                     interpolations.append(curinterpolation)
    #                     atominterbin = 1 if curinterpolation > contour else 0
    #                     resatominterbin += atominterbin
    #                     if 'H' not in atom.name:
    #                         chainatominterbin += atominterbin
    #                         chain_atom_count += 1
    #                 if residue_atom_count == 0:
    #                     continue
    #                 keystr = f"{chain.id}:{residue.id[1]} {residue.resname}"
    #                 allkeys.append(keystr)
    #                 allvalues.append(round(float(resatominterbin) / residue_atom_count, 4))
    #
    #             if chain.id in chainai_atomsno:
    #                 chainatominterbin += chainai_atomsno[chain.id]['value']
    #                 chain_atom_count += chainai_atomsno[chain.id]['atomsinchain']
    #             if chain_atom_count == 0:
    #                 continue
    #             chainai_atomsno[chain.id] = {'value': chainatominterbin, 'atomsinchain': chain_atom_count}
    #
    #         for chainname, chain_scores in chainai_atomsno.items():
    #             chain_ai = round(float(chain_scores['value']) / chain_scores['atomsinchain'], 4)
    #             chainaiscore[chainname] = {'value': chain_ai, 'color': floattohex([chain_ai])[0], 'numberOfAtoms': chain_scores['atomsinchain']}
    #         allcontoursdict[str(contour)] = (allkeys, allvalues)
    #
    #     return allcontoursdict, atomoutsidenum, chainaiscore
    #
    # def __getindices(self, onecoor):
    #     """
    #     Find one atom's indices corresponding to its cubic or plane
    #     the 8 (cubic) or 4 (plane) indices are saved in indices variable
    #
    #     :param onecoor: List contains the atom coordinates in (x, y, z) order
    #     :return: Tuple contains two list of index: first has the 8 or 4 indices in the cubic;
    #              second has the float index of the input atom
    #     """
    #     zindex, yindex, xindex = self._calculate_indices(onecoor)
    #     indices = np.array(np.meshgrid(np.arange(int(math.floor(xindex)), int(math.ceil(xindex)) + 1),
    #                                    np.arange(int(math.floor(yindex)), int(math.ceil(yindex)) + 1),
    #                                    np.arange(int(math.floor(zindex)), int(math.ceil(zindex)) + 1))).T.reshape(-1, 3)
    #     return indices, [xindex, yindex, zindex]
    #
    # def _calculate_indices(self, onecoor):
    #     zdim, ydim, xdim = self.map.header.cella.z, self.map.header.cella.y, self.map.header.cella.x
    #     znintervals, ynintervals, xnintervals = self.map.header.mz, self.map.header.my, self.map.header.mx
    #     z_apix, y_apix, x_apix = zdim / znintervals, ydim / ynintervals, xdim / xnintervals
    #     map_zsize, map_ysize, map_xsize = self.map.header.nz, self.map.header.ny, self.map.header.nx
    #
    #     if self.map.header.cellb.alpha == self.map.header.cellb.beta == self.map.header.cellb.gamma == 90.:
    #         crs = [self.map.header.mapc, self.map.header.mapr, self.map.header.maps]
    #         ordinds = [crs.index(1), crs.index(2), crs.index(3)]
    #         zindex = float(onecoor[2] - self.map.header.origin.z) / z_apix - self.map.header.nzstart
    #         yindex = float(onecoor[1] - self.map.header.origin.y) / y_apix - self.map.header.nystart
    #         xindex = float(onecoor[0] - self.map.header.origin.x) / x_apix - self.map.header.nxstart
    #     else:
    #         apixs = [x_apix, y_apix, z_apix]
    #         xindex, yindex, zindex = self.matrix_indices(apixs, onecoor)
    #
    #     return zindex, yindex, xindex
    #
    # def map_matrix(self, apixs, angs):
    #     """
    #     Calculate the matrix to transform Cartesian coordinates to fractional coordinates
    #
    #     :param apixs: array of apix length
    #     :param angs: array of angles in alpha, beta, gamma order
    #     :return: Transformation matrix
    #     """
    #     ang = (angs[0] * math.pi / 180, angs[1] * math.pi / 180, angs[2] * math.pi / 180)
    #     insidesqrt = 1 + 2 * math.cos(ang[0]) * math.cos(ang[1]) * math.cos(ang[2]) - \
    #                  math.cos(ang[0]) ** 2 - \
    #                  math.cos(ang[1]) ** 2 - \
    #                  math.cos(ang[2]) ** 2
    #
    #     cellvolume = apixs[0] * apixs[1] * apixs[2] * math.sqrt(insidesqrt)
    #     prematrix = [
    #         [1 / apixs[0], -math.cos(ang[2]) / (apixs[0] * math.sin(ang[2])), apixs[1] * apixs[2] * (math.cos(ang[0]) * math.cos(ang[2]) - math.cos(ang[1])) / (cellvolume * math.sin(ang[2]))],
    #         [0, 1 / (apixs[1] * math.sin(ang[2])), apixs[0] * apixs[2] * (math.cos(ang[1]) * math.cos(ang[2]) - math.cos(ang[0])) / (cellvolume * math.sin(ang[2]))],
    #         [0, 0, apixs[0] * apixs[1] * math.sin(ang[2]) / cellvolume]
    #     ]
    #     return np.asarray(prematrix)
    #
    # def matrix_indices(self, apixs, onecoor):
    #     """
    #     Method 2: using the fractional coordinate matrix to calculate the indices when the maps are non-orthogonal
    #
    #     :return: Indices in x, y, z order
    #     """
    #     crs = [self.map.header.mapc, self.map.header.mapr, self.map.header.maps]
    #     ordinds = [crs.index(1), crs.index(2), crs.index(3)]
    #     angs = [self.map.header.cellb.alpha, self.map.header.cellb.beta, self.map.header.cellb.gamma]
    #     matrix = self.map_matrix(apixs, angs)
    #     result = matrix.dot(np.asarray(onecoor))
    #     return result[0] - self.map.header.nxstart, result[1] - self.map.header.nystart, result[2] - self.map.header.nzstart
    #
    # def _get_interpolation_value(self, oneindex, myinter):
    #     if any(idx < 0 or idx >= dim for idx, dim in zip(oneindex, [self.map.header.nx, self.map.header.ny, self.map.header.nz])):
    #         return self.map.data.min()
    #     return myinter(oneindex).tolist()[0]
    #
    # def interpolation(self):
    #     """
    #     Use scipy regulargrid interpolation method feed with all maps info
    #
    #     :return: A interpolation function
    #     """
    #     mapdata = np.swapaxes(self.map.data, 0, 2)
    #     x, y, z = range(mapdata.shape[2]), range(mapdata.shape[1]), range(mapdata.shape[0])
    #     return RegularGridInterpolator((x, y, z), mapdata)
    #

    # This section is the whole new atom_inclusion section
    def atom_inclusion(self):
        """
        Generate atom inclusion and residue atom inclusion information across different contour levels.
        Saves results as JSON and generates a plot.
        """
        if not self.model:
            sys.stderr.write('REMINDER: Atom inclusion and residue inclusion require a model structure.\n')
            return

        if self.cl is None:
            sys.stderr.write('REMINDER: Atom inclusion and residue inclusion require a contour level.\n')
            return

        start_time = timeit.default_timer()
        combinresult = self.__nnewinterthird()
        atom_inclusion_data, residue_inclusion_data = OrderedDict(), OrderedDict()
        all_atoms_count, total_atom_inclusion = 0, 0.0

        for idx, (key, value) in enumerate(combinresult.items()):
            try:
                model = self._get_model_by_key(key)
                if not model:
                    sys.stderr.write(f'No valid model found for key: {key}\n')
                    continue

                interpolations, all_contours, chainaiscore, atomoutsidebox = value
                allatoms = list(model.get_atoms())
                result = self.__getfractions(interpolations, allatoms)
                levels = self._adjust_levels(self.map.data, self.cl)

                avg_ai_model = round(result[2], 3)  # Extract average_ai_model from result
                avg_ai_color = floattohex([round(result[2], 6)])[0]  # Convert to color representation

                atom_inclusion_entry = self._build_atom_inclusion_entry(
                    key, levels, result, atomoutsidebox, chainaiscore, avg_ai_model, avg_ai_color
                )

                atom_inclusion_data[str(idx)] = atom_inclusion_entry

                # Update cumulative atom inclusion values
                all_atoms_count += int(result[3])
                total_atom_inclusion += result[3] * result[2]

                self._plot_inclusion(levels, result)

            except Exception as e:
                sys.stderr.write(f'Atom inclusion calculation error (Model: {key}): {e}\n')

            try:
                residue_inclusion_data[str(idx)] = self._build_residue_inclusion_entry(key, all_contours)
            except Exception as e:
                sys.stderr.write(f'Residue inclusion calculation error (Model: {key}): {e}\n')

        # Compute the overall average_ai_allmodels value
        if all_atoms_count:
            avg_ai_allmodels = round(total_atom_inclusion / all_atoms_count, 3)
            atom_inclusion_data['average_ai_allmodels'] = avg_ai_allmodels

        # Save JSON outputs
        self._safe_json_dump(f"{self.workdir}{self.mapname}_atom_inclusion.json",
                             {'atom_inclusion_by_level': atom_inclusion_data})
        self._safe_json_dump(f"{self.workdir}{self.mapname}_residue_inclusion.json",
                             {'residue_inclusion': residue_inclusion_data})

        print(f'Inclusion calculation time: {timeit.default_timer() - start_time} seconds')

    def _get_model_by_key(self, key):
        """Retrieve the correct model from self.model based on key."""
        if isinstance(self.model, list):
            models = [m for m in self.model if key in m.filename]
            if len(models) == 1:
                return models[0]
            sys.stderr.write(f'Error: Expected 1 model for {key}, found {len(models)}.\n')
            return None
        return self.model if key in self.model.filename else None

    def _adjust_levels(self, map_data, contour_level):
        """Adjust contour levels to ensure proper sorting and inclusion of the given contour level."""
        levels = np.linspace(map_data.min(), map_data.max(), 129).tolist()
        bisect.insort(levels, contour_level)
        levels.pop(levels.index(contour_level) - 1)
        return np.array(levels)

    def _build_atom_inclusion_entry(self, key, levels, result, atomoutsidebox, chainaiscore, avg_ai_model,
                                    avg_ai_color):
        """Format atom inclusion data into an ordered dictionary."""
        return {
            'name': key,
            'level': [round(x, 6) for x in levels.tolist()],
            'all_atom': [round(x, 3) for x in result[0]],
            'backbone': [round(x, 3) for x in result[1]],
            'atomoutside': atomoutsidebox,
            'chainaiscore': chainaiscore,
            'totalNumberOfAtoms': int(result[3]),
            'average_ai_model': avg_ai_model,
            'average_ai_color': avg_ai_color  # Now included properly in the output
        }

    def _build_residue_inclusion_entry(self, key, all_contours):
        """Format residue inclusion data into an ordered dictionary."""
        contour_dict = OrderedDict({'name': key})
        for contour, values in all_contours.items():
            all_values, all_keys = values[1], values[0]
            contour_dict[str(round(float(contour), 6))] = OrderedDict(
                {'color': floattohex(all_values), 'inclusion': all_values, 'residue': all_keys})
        return contour_dict

    def _plot_inclusion(self, levels, result):
        """Generate and save the atom inclusion plot."""
        plt.plot(levels, result[0], '-g', label='Full atom')
        plt.plot(levels, result[1], '-b', label='Backbone')
        plt.axvline(self.cl, color='r', linestyle='--', label='Recommended contour level')
        plt.legend(loc='lower left')
        plt.savefig(f"{self.workdir}{self.mapname}_inclusion.png")
        plt.close()

    def _safe_json_dump(self, filepath, data):
        """Safely dump data to a JSON file with error handling."""
        try:
            with codecs.open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            sys.stderr.write(f'Error saving JSON file {filepath}: {e}\n')
    # End section of the whole new atom_inclusion section

    ################ below is the traditional one ################
    # def atom_inclusion(self):
    #     """
    #     Generate atom inclusion and residue atom inclusion information verses different contour level
    #     Both full atoms and backbone information are included.
    #     Results wrote to JSON file
    #
    #     :return: None
    #     """
    #     if self.model is None:
    #         sys.stderr.write('REMINDER: atom inclusion and residue inclusion will not be calculated without '
    #                          'model structure.\n')
    #         print('------------------------------------')
    #     elif self.cl is None:
    #         sys.stderr.write('REMINDER: atom inclusion and residue inclusion will not be calculated '
    #                          'without contour level given.\n')
    #         print('------------------------------------')
    #     else:
    #         start = timeit.default_timer()
    #         map = self.map
    #
    #         # modelnames = [ model.filename for model in self.model ]
    #         # version 1 use tempy
    #         # combinresult = self.__interthird()
    #         # version 2 use biopython but not optmised for biopython
    #         # combinresult = self.__newinterthird()
    #         # version 3 use biopython need more tests and then delete the other two above
    #         combinresult = self.__nnewinterthird()
    #         atomindict = OrderedDict()
    #         resindict = OrderedDict()
    #         datadict = OrderedDict()
    #         resdict = OrderedDict()
    #         counter = 0
    #         errlist = []
    #         reserrlist = []
    #         allmodels_numberatoms = 0
    #         allmodels_atom_inclusion = 0.0
    #         for key, value in combinresult.items():
    #             try:
    #                 interpolations, allcontoursdict, chainaiscore, atomoutsidebox = value
    #                 if isinstance(self.model, list):
    #                     models = [curmodel for curmodel in self.model if key in curmodel.filename]
    #                 else:
    #                     models = list()
    #                     models.append(self.model)
    #
    #                 if len(models) == 1:
    #                     model = models[0]
    #                 elif len(models) == 0:
    #                     print('There is no model!')
    #                     exit()
    #                 else:
    #                     print('There are more than one model which should be only one.')
    #                     exit()
    #
    #                 allatoms = list(model.get_atoms())
    #                 result = self.__getfractions(interpolations, allatoms)
    #                 levels = np.linspace(map.data.min(), map.data.max(), 129)
    #
    #                 binlist = levels.tolist()
    #                 bisect.insort(binlist, self.cl)
    #                 clindex = binlist.index(self.cl)
    #                 binlist.pop(clindex - 1)
    #                 levels = np.asarray(binlist)
    #
    #                 datadict[str(counter)] = {'name': key, 'level': [round(elem, 6) for elem in levels.tolist()],
    #                                           'all_atom': [round(elem, 3) for elem in result[0]],
    #                                           'backbone': [round(elem, 3) for elem in result[1]],
    #                                           'atomoutside': atomoutsidebox,
    #                                           'chainaiscore': chainaiscore,
    #                                           'totalNumberOfAtoms': int(result[3]),
    #                                           'average_ai_model': round(result[2], 3),
    #                                           'average_ai_color': floattohex([round(result[2], 6)])[0]}
    #                 allmodels_numberatoms += int(result[3])
    #                 allmodels_atom_inclusion += result[3]*result[2]
    #
    #                 data_len = len(levels.tolist())
    #                 plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[0]], '-g', label='Full atom')
    #                 plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[1]], '-b', label='Backbone')
    #                 plt.plot(data_len * [self.cl], np.linspace(0, 1, data_len), '-r', label='Recommended contour level')
    #                 plt.legend(loc='lower left')
    #                 plt.savefig(self.workdir + self.mapname + '_inclusion.png')
    #                 plt.close()
    #             except:
    #                 err = 'Atom inclusion calculation error(Model: {}): {}.'.format(key, sys.exc_info()[1])
    #                 errlist.append(err)
    #                 sys.stderr.write(err + '\n')
    #             if errlist:
    #                 datadict[str(counter)] = {'err': {'atom_inclusion_err': errlist}}
    #
    #             contourdict = OrderedDict()
    #             try:
    #                 for contour, keysvalues in allcontoursdict.items():
    #                     allvalues = keysvalues[1]
    #                     allkeys = keysvalues[0]
    #                     colours = floattohex(allvalues)
    #                     contourkey = str(round(float(contour), 6))
    #                     contourdict[contourkey] = OrderedDict([('color', colours), ('inclusion', allvalues),
    #                                                            ('residue', allkeys)])
    #
    #                 contourdict['name'] = key
    #                 resdict[str(counter)] = contourdict
    #             except:
    #                 err = 'Residue inclusion calculation error(Model: {}): {}.'.format(key, sys.exc_info()[1])
    #                 reserrlist.append(err)
    #                 sys.stderr.write(err + '\n')
    #             if reserrlist:
    #                 resdict[str(counter)] = {'err': {'residue_inclusion_err': reserrlist}}
    #             counter += 1
    #
    #         if allmodels_numberatoms != 0:
    #             average_ai_allmodels = allmodels_atom_inclusion / allmodels_numberatoms
    #             datadict['average_ai_allmodels'] = round(average_ai_allmodels, 3)
    #         atomindict['atom_inclusion_by_level'] = datadict
    #         resindict['residue_inclusion'] = resdict
    #
    #         try:
    #             with codecs.open(self.workdir + self.mapname + '_atom_inclusion.json', 'w',
    #                              encoding='utf-8') as f:
    #                 json.dump(atomindict, f)
    #         except:
    #             sys.stderr.write('Saving to atom inclusion json error: {}.\n'.format(sys.exc_info()[1]))
    #
    #         try:
    #             with codecs.open(self.workdir + self.mapname + '_residue_inclusion.json', 'w',
    #                              encoding='utf-8') as f1:
    #                 json.dump(resindict, f1)
    #         except:
    #             sys.stderr.write('Saving to residue inclusion json error: {}.\n'.format(sys.exc_info()[1]))
    #
    #         end = timeit.default_timer()
    #         print('Inclusion time: %s' % (end - start))
    #         print('------------------------------------')
    #
    #     return None

    def __nnewinterthird(self):
        """

            Interpolate density value of one atom, if indices are on the same plane use nearest method
            otherwise use linear

        :param map: TEMPy map instance
        :param model: Structure instance from TEMPy package mmcif parser
        :return: List contains all density interpolations of atoms from model

        """

        myinter = self.__interPolation()
        # Might having multple models
        models = []
        if isinstance(self.model, list):
            models = self.model
        else:
            models.append(self.model)
        map = self.map
        contour = self.cl
        # Range of contour level values for scaler bar
        # Todo: Right now with fixed number of points on both sides of the recommended contour level, could improve to
        # Todo: generate a reasonable range surround the recommended contour level
        # Setting a smarter range between (contour-sig,contour, countour + sig)
        # mapsig = map.std()
        # mapsig = map.data.std()
        # contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # contourrange = np.concatenate((np.linspace(map.min(), contour, 3, endpoint=False), np.linspace(contour, map.max(), 3)), axis=None)
        # When running for EMDB keep it as a flexible range for onedep or other users only run it once for recommended
        # contour level:

        # if self.emdid:
        #     contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                    np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # else:
        #     contourrange = np.asarray([contour])

        contourrange = np.asarray([contour])
        result = {}
        for model in models:
            allcontoursdict = OrderedDict()
            atomoutsidenum = 0
            modelname = model.filename.split('/')[-1]

            atomcount = 0
            chaincount = 1
            chainatoms = 0
            chainaiscore = {}
            chainai = 0.

            for contour in contourrange:
                interpolations = []
                allkeys = []
                allvalues = []
                preresid = 0
                prechain = ''
                aiprechain = ''
                preres = ''
                rescount = 0
                sumatominterbin = 0
                chainai_atomsno = {}
                for chain in model.get_chains():
                    chainatominterbin = 0
                    chain_atom_count = 0
                    chain_name = chain.id
                    for residue in chain.get_residues():
                        resatominterbin = 0
                        residue_atom_count = 0
                        residue_name = residue.resname
                        residue_no = residue.id[1]
                        for atom in residue.get_atoms():
                            if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                                continue
                            # if 'H' not in atom.name:
                            atomcount += 1
                            residue_atom_count += 1
                            # chain_atom_count += 1
                            onecoor = atom.coord
                            oneindex = self.__getindices(onecoor)[1]
                            # if oneindex[0] > map.x_size() - 1 or oneindex[0] < 0 or \
                            #         oneindex[1] > map.y_size() - 1 or oneindex[1] < 0 or \
                            #         oneindex[2] > map.z_size() - 1 or oneindex[2] < 0:
                            if oneindex[0] > map.header.nx - 1 or oneindex[0] < 0 or \
                                    oneindex[1] > map.header.ny - 1 or oneindex[1] < 0 or \
                                    oneindex[2] > map.header.nz - 1 or oneindex[2] < 0:
                                # curinterpolation = map.min()
                                curinterpolation = map.data.min()
                                atomoutsidenum += 1
                            else:
                                curinterpolation = myinter(oneindex).tolist()[0]
                            interpolations.append(curinterpolation)
                            atominterbin = 1 if curinterpolation > contour else 0
                            resatominterbin += atominterbin
                            if 'H' not in atom.name:
                                chainatominterbin += atominterbin
                                chain_atom_count += 1
                            sumatominterbin += atominterbin
                        if residue_atom_count == 0:
                            continue
                        # residue inclusion section
                        keystr = chain_name + ':' + str(residue_no) + ' ' + residue_name
                        allkeys.append(keystr)
                        value = float('%.4f' % round((float(resatominterbin) / residue_atom_count), 4))
                        allvalues.append(value)

                    # chain inclusion section
                    if chain_name in chainai_atomsno.keys():
                        chainatominterbin += chainai_atomsno[chain_name]['value']
                        chain_atom_count += chainai_atomsno[chain_name]['atomsinchain']
                    # For cases where one water molecule has a sigle but different chain id
                    if chain_atom_count == 0:
                        continue
                    chainai_atomsno[chain_name] = {'value': chainatominterbin, 'atomsinchain': chain_atom_count}

                for chainname, chain_scores in chainai_atomsno.items():
                    chain_ai = float('%.3f' % round((float(chain_scores['value']) / chain_scores['atomsinchain']), 4))
                    aicolor = floattohex([chain_ai])[0]
                    chainaiscore[chainname] = {'value': chain_ai, 'color': aicolor,
                                               'numberOfAtoms': chain_scores['atomsinchain']}
                allcontoursdict[str(contour)] = (allkeys, allvalues)
                print('Model: %s at contour level %s has %s atoms stick out of the density.' % (modelname, contour,
                                                                                                atomoutsidenum))

            # result[modelname] = (interpolations, allkeys, allvalues)
            # result: {modelname #1: (interpolations #1, {contour1: (allkeys, allvalues), contour2: (allkeys, allvalues)
            # ...}), modelname #2: (interpolations #2, {contour1: (allkeys, allvalues),...}),...}
            result[modelname] = (interpolations, allcontoursdict, chainaiscore, atomoutsidenum)

        return result

    def __getfractions(self, interpolation, model):
        """

            Produce atom inclusion fraction information for full atoms and backbone trace

        :param interpolation: List of interpolation values
        :param map: Electron density map in mrc/map format
        :param model: Protein model in mmcif format
        :return: Tuple contains full atom inclusion fractions and backbone inclusion fractions

        """

        map = self.map
        bins = np.linspace(map.data.min(), map.data.max(), 129)
        binlist = bins.tolist()
        bisect.insort(binlist, self.cl)
        clindex = binlist.index(self.cl)
        binlist.pop(clindex - 1)
        bins = np.asarray(binlist)

        newinterpolation = []
        for i in range(len(interpolation)):
            # if 'H' not in model[i].atom_name:
            if 'H' not in model[i].fullname:
                newinterpolation.append(interpolation[i])

        # Whole model average atom inlcusion
        entire_average = sum(np.asarray(newinterpolation) > self.cl) / float(len(newinterpolation))

        # Full atom inclusion
        a = []
        templist = np.asarray(newinterpolation)
        for i in bins:
            x = sum(templist > i) / float(len(templist))
            a.append(x)

        traceinter = []
        for i in range(len(interpolation)):
            if (model[i].fullname == 'N' or model[i].fullname == 'C' or model[i].fullname == 'O' or
                    model[i].fullname == 'CA' or model[i].fullname == "C3'" or model[i].fullname == "C4'" or
                    model[i].fullname == "C5'" or model[i].fullname == "O3'" or model[i].fullname == "O5'" or
                    model[i].fullname == 'P' or model[i].fullname == 'OXT'):
                traceinter.append(interpolation[i])

        # Backbone inclusion
        b = []
        temptraceinter = np.asarray(traceinter)
        for j in bins:
            y = sum(temptraceinter > j) / float(len(temptraceinter))
            b.append(y)

        return a, b, entire_average, float(len(newinterpolation))

    def __interPolation(self):
        """

            Usc scipy regulargrid interpolation method feed with all maps info

        :param map: Electron density map in mrc/map format
        :param model: Protein model in mmcif format
        :return: A interpolation function

        """

        # mapdata = self.map.getMap()
        mapdata = self.map.data
        tmpmapdata = np.swapaxes(mapdata, 0, 2)
        clim, blim, alim = mapdata.shape
        x = range(alim)
        y = range(blim)
        z = range(clim)
        myinter = RegularGridInterpolator((x, y, z), tmpmapdata)

        return myinter

    def __getindices(self, onecoor):
        """

            Find one atom's indices correspoding to its cubic or plane
            the 8 (cubic) or 4 (plane) indices are saved in indices variable

        :param map: Density map instance from TEMPy.MapParser
        :param onecoor: List contains the atom coordinates in (x, y, z) order
        :return: Tuple contains two list of index: first has the 8 or 4 indices in the cubic;
                 second has the float index of the input atom

        """

        # For non-cubic or skewed density maps, they might have different apix on different axises
        map = self.map
        zdim = map.header.cella.z
        znintervals = map.header.mz
        z_apix = zdim / znintervals

        ydim = map.header.cella.y
        ynintervals = map.header.my
        y_apix = ydim / ynintervals

        xdim = map.header.cella.x
        xnintervals = map.header.mx
        x_apix = xdim / xnintervals

        map_zsize = map.header.nz
        map_ysize = map.header.ny
        map_xsize = map.header.nx

        # if map.header[13] == map.header[14] == map.header[15] == 90.:
        if map.header.cellb.alpha == map.header.cellb.beta == map.header.cellb.gamma == 90.:
            # Figure out the order of the x, y, z based on crs info in the header
            # crs = list(map.header[16:19])
            crs = [map.header.mapc, map.header.mapr, map.header.maps]
            # ordinds save the indices correspoding to x, y ,z
            ordinds = [crs.index(1), crs.index(2), crs.index(3)]

            zindex = float(onecoor[2] - map.header.origin.z) / z_apix - map.header.nzstart
            yindex = float(onecoor[1] - map.header.origin.y) / y_apix - map.header.nystart
            xindex = float(onecoor[0] - map.header.origin.x) / x_apix - map.header.nxstart

            zfloor = int(math.floor(zindex))
            if zfloor >= map_zsize - 1:
                zceil = zfloor
            else:
                zceil = zfloor + 1

            yfloor = int(math.floor(yindex))
            if yfloor >= map_ysize - 1:
                yceil = yfloor
            else:
                yceil = yfloor + 1

            xfloor = int(math.floor(xindex))
            if xfloor >= map_xsize - 1:
                xceil = xfloor
            else:
                xceil = xfloor + 1
        else:
            # Method 2: by using the fractional coordinate matrix
            # Chosen as the primary for the current implementation
            apixs = [x_apix, y_apix, z_apix]
            # Method 1: by using the atom projection on planes
            # xindex, yindex, zindex = self.projection_indices(onecoor))
            xindex, yindex, zindex = self.matrix_indices(apixs, onecoor)

            zfloor = int(math.floor(zindex))
            if zfloor >= map_zsize - 1:
                zceil = zfloor
            else:
                zceil = zfloor + 1

            yfloor = int(math.floor(yindex))
            if yfloor >= map_ysize - 1:
                yceil = yfloor
            else:
                yceil = yfloor + 1

            xfloor = int(math.floor(xindex))
            if xfloor >= map_xsize - 1:
                xceil = xfloor
            else:
                xceil = xfloor + 1

        indices = np.array(np.meshgrid(np.arange(xfloor, xceil + 1), np.arange(yfloor, yceil + 1),
                                       np.arange(zfloor, zceil + 1))).T.reshape(-1, 3)
        oneindex = [xindex, yindex, zindex]

        return (indices, oneindex)

    def map_matrix(self, apixs, angs):
        """

            calculate the matrix to transform Cartesian coordinates to fractional coordinates
            (check the definination to see the matrix formular)

        :param apixs: array of apix lenght
        :param angs: array of anglex in alpha, beta, gamma order
        :return:
        """

        ang = (angs[0] * math.pi / 180, angs[1] * math.pi / 180, angs[2] * math.pi / 180)
        insidesqrt = 1 + 2 * math.cos(ang[0]) * math.cos(ang[1]) * math.cos(ang[2]) - \
                     math.cos(ang[0]) ** 2 - \
                     math.cos(ang[1]) ** 2 - \
                     math.cos(ang[2]) ** 2

        cellvolume = apixs[0] * apixs[1] * apixs[2] * math.sqrt(insidesqrt)

        m11 = 1 / apixs[0]
        m12 = -math.cos(ang[2]) / (apixs[0] * math.sin(ang[2]))

        m13 = apixs[1] * apixs[2] * (math.cos(ang[0]) * math.cos(ang[2]) - math.cos(ang[1])) / (
                    cellvolume * math.sin(ang[2]))
        m21 = 0
        m22 = 1 / (apixs[1] * math.sin(ang[2]))
        m23 = apixs[0] * apixs[2] * (math.cos(ang[1]) * math.cos(ang[2]) - math.cos(ang[0])) / (
                    cellvolume * math.sin(ang[2]))
        m31 = 0
        m32 = 0
        m33 = apixs[0] * apixs[1] * math.sin(ang[2]) / cellvolume
        prematrix = [[m11, m12, m13], [m21, m22, m23], [m31, m32, m33]]
        matrix = np.asarray(prematrix)

        return matrix

    def matrix_indices(self, apixs, onecoor):
        """

            Method 2: using the fractional coordinate matrix to calculate the indices when the maps are non-orthogonal

        :return:
        """

        # Method 2: by using the fractional coordinate matrix
        # Chosen as the main function for the current implementation

        # Figure out the order of the x, y, z based on crs info in the header
        # crs = list(self.map.header[16:19])
        crs = [self.map.header.mapc, self.map.header.mapr, self.map.header.maps]
        # ordinds save the indices correspoding to x, y ,z
        ordinds = [crs.index(1), crs.index(2), crs.index(3)]
        # angs = self.map.header[13:16]
        angs = [self.map.header.cellb.alpha, self.map.header.cellb.beta, self.map.header.cellb.gamma]
        matrix = self.map_matrix(apixs, angs)
        result = matrix.dot(np.asarray(onecoor))
        # xindex = result[0] - self.map.header[4 + ordinds[0]]
        # yindex = result[1] - self.map.header[4 + ordinds[1]]
        # zindex = result[2] - self.map.header[4 + ordinds[2]]
        xindex = result[0] - self.map.header.nxstart
        yindex = result[1] - self.map.header.nystart
        zindex = result[2] - self.map.header.nzstart

        return (xindex, yindex, zindex)
