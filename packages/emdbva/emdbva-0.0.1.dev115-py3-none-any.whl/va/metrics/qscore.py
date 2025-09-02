import re
import subprocess
import math
import traceback
from collections import OrderedDict
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
import matplotlib.pyplot as plt
from six import iteritems
from va.utils.misc import *
from va.utils.Model import *
import va


class Qscore:
    """
        Qscore module
    """

    def __init__(self, workdir, map, models, resolution):
        self.workdir = workdir
        self.map = map
        self.models = models
        self.resolution = resolution
        self.chimera_path = chimera_envcheck()

    def class_qscore(self):
        """
        Calculate Q-score
        """

        errors = []
        num_of_cores = max(1, int(os.cpu_count() / 2))  # Ensure at least 1 core is used

        if self.resolution is None or float(self.resolution) < 1.25:
            print("Skipping Q-score calculation due to resolution constraints.")
            return None

        try:
            chimera_app = self.chimera_path
            qscore_app = self.check_mapq(chimera_app)
            map_name = self.map

            if not self.models:
                print("No fitted model available. Q-score will not be calculated.")
                return None

            models = ' '.join([f'cif={model.filename}' for model in self.models])
            atom_numbers = [self.get_atom_number(model) for model in self.models]
            num_of_cores = min(num_of_cores, min(atom_numbers))

            qscore_cmd = self.construct_qscore_cmd(chimera_app, qscore_app, map_name, models, num_of_cores)
            print(qscore_cmd)
            self.run_qscore(qscore_cmd, errors)

        except Exception as e:
            err_msg = f"Q-score preparation error: {str(e)}"
            errors.append(err_msg)
            sys.stderr.write(err_msg + '\n')
            print(traceback.format_exc())

        return None

    @staticmethod
    def check_mapq(chimera_app):
        """
            Check if MapQ is properly installed.
        :param chimera_app: Path to the Chimera application.
        :return: Full path to Q-score script if found, else None.
        """

        if not chimera_app:
            sys.stderr.write('Error: Chimera was not found.\n')
            return None

        # Resolve symlink if applicable
        realchimeraapp = os.path.realpath(chimera_app) if os.path.islink(chimera_app) else chimera_app

        # Determine the base directory and construct the Q-score path
        if 'Contents' in realchimeraapp:
            base_dir = realchimeraapp.split('Contents')[0]
            qscore_path = os.path.join(base_dir, 'Contents/Resources/share/mapq/mapq_cmd.py')
        elif 'bin' in realchimeraapp:
            base_dir = realchimeraapp.split('bin')[0]
            qscore_path = os.path.join(base_dir, 'share/mapq/mapq_cmd.py')
        else:
            sys.stderr.write('Error: Invalid Chimera executable format.\n')
            return None

        # Check if the Q-score script exists
        if os.path.isfile(qscore_path):
            return qscore_path

        sys.stderr.write('Error: Q-score script not found.\n')
        return None

    def get_atom_number(self, model):
        """
            Get atom numbers, checking for moderated CIF files.
        """

        moderated_cif = f'{os.path.basename(model.filename)}_moderated.cif'
        file_path = os.path.join(self.workdir, moderated_cif)
        return Model.atom_numbers(file_path if os.path.isfile(file_path) else model.filename)

    def construct_qscore_cmd(self, chimera_app, qscore_app, map_name, models, num_of_cores):
        """Helper function to construct the Q-score command."""
        vor_contents = chimera_app.split('Contents')[0] if 'Contents' in chimera_app else chimera_app.split('bin')[0]
        return f"{sys.executable} {qscore_app} {vor_contents} map={map_name} {models} np={num_of_cores} res={self.resolution} sigma=0.4"

    def run_qscore(self, qscore_cmd, errlist):
        """
            Execute the Q-score calculation.
        """
        try:
            process = subprocess.Popen(qscore_cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       cwd=self.workdir)
            output = process.communicate('n\n')[0]
            self.check_qscore_errors(output, errlist)
            self.process_qscore()
        except Exception as e:
            err_msg = f"Q-score calculation error: {str(e)}"
            errlist.append(err_msg)
            sys.stderr.write(err_msg + '\n')
            print(traceback.format_exc())

    @staticmethod
    def check_qscore_errors(output, errors):
        """
            Check Qscore output
        """
        err_qscore = 'error'
        output_lines = output.decode('utf-8').split('\n') if sys.version_info[0] >= 3 else output.split('\n')

        for item in output_lines:
            print(item)
            if err_qscore in item.lower():
                err_line = item.strip()
                errors.append(err_line)
                assert err_qscore not in output.decode('utf-8'), err_line

    def process_qscore(self):

        try:
            self.read_qscore()
            chimerax_app = chimerax_envcheck()
            self.qscoreview(chimerax_app)
        except:
            err = 'Q-score results processing failed: {}'.format(sys.exc_info()[1])
            print(traceback.format_exc())
            sys.stderr.write(err + '\n')

    def _read_qscore(self):
        """
            Load the Q-score CIF file to match Q-score 1.8.2.
            Outputs a JSON file with
             Q-score information derived from the CIF file.
        """

        qscore_data = OrderedDict()
        final_data = OrderedDict()
        total_atoms = 0
        total_qscores = 0.0
        qfiles = []
        mapname = self.map

        for model_idx, model in enumerate(self.models):
            original_model = os.path.basename(model.filename)
            qfile = f"{self.workdir}{original_model}__Q__{mapname}.cif"

            if not os.path.isfile(qfile):
                raise ValueError(f"Q-score CIF file not found: {qfile}")

            try:
                parser = MMCIFParser()
                parser._mmcif_dict = MMCIF2Dict(qfile)

                coords = zip(
                    parser._mmcif_dict['_atom_site.Cartn_x'],
                    parser._mmcif_dict['_atom_site.Cartn_y'],
                    parser._mmcif_dict['_atom_site.Cartn_z']
                )
                qscores = parser._mmcif_dict['_atom_site.Q-score']

                # Map rounded coordinates to Q-scores
                coord_qscore_map = {
                    tuple(map(math.floor, map(float, coord))): float(qscore) if qscore != '?' else 0.0
                    for coord, qscore in zip(coords, qscores)
                }

                structure = parser.get_structure(qfile, qfile)
                for atom in structure.get_atoms():
                    atom_key = tuple(map(math.floor, atom.coord))
                    setattr(atom, 'qscore', coord_qscore_map.get(atom_key, 0.0))

                qfiles.append(structure)

                # Convert CIF data to Q-score dictionary
                try:
                    cif_data = self.newcif_toqdict(structure, original_model)
                    # cif_data = self.qcif_to_qdict(structure, original_model)
                    total_atoms += cif_data['data']['numberofatoms']
                    total_qscores += cif_data['data']['numberofatoms'] * cif_data['data']['averageqscore']
                    qscore_data[str(model_idx)] = cif_data
                except Exception as e:
                    err_msg = f"Q-score calculation error (Model: {model.filename}): {e}"
                    sys.stderr.write(err_msg + '\n')

            except Exception as e:
                sys.stderr.write(f"Error processing Q-score CIF file {qfile}: {e}\n")
                continue

        if total_atoms:
            qscore_data['allmodels_average_qscore'] = round(total_qscores / total_atoms, 3)

        if qscore_data:
            final_data['qscore'] = qscore_data
            try:
                json_path = f"{self.workdir}{mapname}_qscore.json"
                with codecs.open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(final_data, f, indent=4)
            except Exception as e:
                sys.stderr.write(f"Error saving Q-score JSON file: {e}\n")
        else:
            print("Q-score data not collected. Please check the input files.")
########################################################
    def qcif_to_qdict(self, qscorecif, orgmodel):
        """
            Take Qscore form mmcif file into a dictionary
        :return: DICT contains Q-score data
        """
        residues, colors, model_colors, qscores, chain_qscore = [], [], [], [], {}
        protein_qscores = self._get_protein_qscores(qscorecif)
        average_qscore = round(sum(protein_qscores) / len(protein_qscores), 3) if protein_qscores else 0.0
        min_qscore, max_qscore = self._get_min_max_qscores(qscorecif)

        for chain in qscorecif.get_chains():
            self._process_chain(chain, chain_qscore, residues, colors, qscores, min_qscore, max_qscore)

        self._process_model_colors(qscores, min_qscore, max_qscore, model_colors)
        qfractions = self._calculate_qfractions(qscores, protein_qscores)
        self._plot_qscore_distribution(qscores, protein_qscores)

        tdict = OrderedDict([
            ('averageqscore', average_qscore),
            ('averageqscore_color', floattohex([average_qscore])[0]),
            ('numberofatoms', len(protein_qscores)),
            ('color', colors),
            ('model_color', model_colors),
            ('inclusion', qscores),
            ('qscore', qscores),
            ('residue', residues),
            ('chainqscore', chain_qscore),
            ('qFractionDistribution', qfractions)
        ])

        return OrderedDict([('name', orgmodel), ('data', tdict)])

    def _get_protein_qscores(self, qscorecif):
        return [atom.qscore for atom in qscorecif.get_atoms() if
                not atom.name.startswith('H') and atom.get_parent().resname != 'HOH']

    def _get_min_max_qscores(self, qscorecif):
        qscore_list = [atom.qscore for atom in qscorecif.get_atoms()]
        return (min(qscore_list), max(qscore_list)) if qscore_list else (None, None)

    def _process_chain(self, chain, chain_qscore, residues, colors, qscores, min_qscore, max_qscore):
        curchain_name = chain.id
        curchain_qscore = [atom.qscore for atom in chain.get_atoms() if
                           not atom.name.startswith('H') and atom.get_parent().resname != 'HOH']
        if not curchain_qscore:
            return

        averagecurchain_qscore = round(sum(curchain_qscore) / len(curchain_qscore), 3)
        chain_qscore[curchain_name] = {'value': averagecurchain_qscore,
                                       'color': floattohex([averagecurchain_qscore])[0]}

        for residue in chain:
            if residue.resname == 'HOH':
                continue
            curres_qscore, curres_color = self._process_residue(residue, min_qscore, max_qscore)
            residues.append(self._format_residue_string(curchain_name, residue))
            colors.append(curres_color)
            qscores.append(curres_qscore)

    def _process_residue(self, residue, min_qscore, max_qscore):
        atoms_inresidue = [atom.qscore for atom in residue if
                           not atom.name.startswith('H') and atom.get_parent().resname != 'HOH']
        curres_qscore = round(sum(atoms_inresidue) / len(atoms_inresidue), 3) if atoms_inresidue else 0.0
        curres_color = self._get_residue_color(curres_qscore, min_qscore, max_qscore)
        return curres_qscore, curres_color

    def _get_residue_color(self, curres_qscore, min_qscore, max_qscore):
        if curres_qscore > 1.0:
            if min_qscore == max_qscore:
                return '#000000'
            scaled_qscore = (curres_qscore - min_qscore) / (max_qscore - min_qscore)
            return floattohex([scaled_qscore], True)[0]
        return floattohex([curres_qscore])[0]

    def _format_residue_string(self, curchain_name, residue):
        curres_id = residue.id[1]
        icode = residue.id[2].strip() if residue.id[2] != ' ' else ''
        return f'{curchain_name}:{curres_id}{icode} {residue.resname}'

    def _process_model_colors(self, qscores, min_qscore, max_qscore, model_colors):
        for res_qscore in qscores:
            if min_qscore == max_qscore:
                model_colors.append('#000000')
            else:
                scaled_qscore = (res_qscore - min_qscore) / (max_qscore - min_qscore)
                model_colors.append(float_to_hex(scaled_qscore, [(255, 0, 0), (255, 255, 255), (0, 0, 255)]))

    def _calculate_qfractions(self, qscores, protein_qscores):
        levels = np.linspace(-1, 1, 100)
        qarray = np.array(qscores)
        hist, _ = np.histogram(qarray, bins=levels)
        protein_qarray = np.array(protein_qscores)
        phist, _ = np.histogram(protein_qarray, bins=levels)
        return {
            'qLevels': list(np.around(levels[1:], 3)),
            'qResidueFractions': list(np.around(hist / qarray.size, 3)),
            'qAtomFractions': list(np.around(phist / protein_qarray.size, 3))
        }

    def _plot_qscore_distribution(self, qscores, protein_qscores):
        levels = np.linspace(-1, 1, 100)
        qarray = np.array(qscores)
        hist, bin_edges = np.histogram(qarray, bins=levels)
        plt.plot(bin_edges[1:], hist / qarray.size)

        protein_qarray = np.array(protein_qscores)
        phist, p_bin_edges = np.histogram(protein_qarray, bins=levels)
        plt.plot(p_bin_edges[1:], phist / protein_qarray.size)
        plt.xlabel('Q-score')
        plt.ylabel('Fraction')
        plt.legend(('Residue: ' + '(' + str(qarray.size) + ')', 'Atom: ' + '(' + str(protein_qarray.size) + ')'),
                   loc='upper left', shadow=True)
        plt.title(f'Map: {self.map} at: {self.resolution}Å' if self.map and self.resolution else 'Map Q-score')
        plt.savefig(f'{self.workdir}{self.map}_qscore.png')
        plt.close()

#####################################################

    def read_qscore(self):
        """
            (original and unused) Load the Q-score cif file match to Qscore 1.8.2 (temparary)
            Output json file with Q-score information derived from cif file
        :return: None
        """

        mapname = self.map
        qfiles = []
        qscoreerrlist = []
        modelnum = 0
        qscoredict = OrderedDict()
        finaldict = OrderedDict()
        allmodels_numberofatoms = 0
        allmodels_qscores = 0.
        for model in self.models:
            orgmodel = os.path.basename(model.filename)
            curmodel = orgmodel
            qfile = '{}{}__Q__{}.cif'.format(self.workdir, curmodel, mapname)
            if os.path.isfile(qfile):
                p = MMCIFParser()
                p._mmcif_dict = MMCIF2Dict(qfile)
                coords = zip(p._mmcif_dict['_atom_site.Cartn_x'], p._mmcif_dict['_atom_site.Cartn_y'], p._mmcif_dict['_atom_site.Cartn_z'])
                qscores = p._mmcif_dict['_atom_site.Q-score']
                coords_qscores_dict = OrderedDict()
                for coord, qscore in zip(coords, qscores):
                    float_coord = tuple(map(float, coord))
                    # org_coord_key = tuple(map(lambda x: math.floor(x * 10 ** 2) / 10 ** 2, float_coord))
                    org_coord_key = tuple(map(lambda x: math.floor(x), float_coord))
                    coords_qscores_dict[org_coord_key] = float(qscore) if qscore != '?' else 0.
                pqscorecif = p.get_structure(qfile, qfile)
                for atom in pqscorecif.get_atoms():
                    # coord_key = tuple(map(float, map(str, atom.coord)))
                    coord_key = tuple(map(float, tuple(map(str, atom.coord))))
                    # new_coord_key = tuple(map(lambda x: math.floor(x * 10 ** 2) / 10 ** 2, coord_key))
                    new_coord_key = tuple(map(lambda x: math.floor(x), coord_key))
                    setattr(atom, 'qscore', coords_qscores_dict[new_coord_key])
                qscorecif = pqscorecif if len(pqscorecif.get_list()) == 1 else pqscorecif[0]
                qfiles.append(qscorecif)
                try:
                    cifdict = self.newcif_toqdict(qscorecif, orgmodel)
                    allmodels_numberofatoms += cifdict['data']['numberofatoms']
                    allmodels_qscores += cifdict['data']['numberofatoms']*cifdict['data']['averageqscore']
                    qscoredict[str(modelnum)] = cifdict
                    modelnum += 1
                except:
                    err = 'Qscore calculation error (Model: {}): {}.'.format(model.filename, sys.exc_info()[1])
                    qscoreerrlist.append(err)
                    sys.stderr.write(err + '\n')
            else:
                raise ValueError
        if allmodels_numberofatoms != 0:
            allmodels_average_qscore = allmodels_qscores / allmodels_numberofatoms
            # qscoredict.update({'allmodels_average_qscore': round(allmodels_average_qscore, 3)})
            qscoredict['allmodels_average_qscore'] = round(allmodels_average_qscore, 3)
        if qscoredict:
            finaldict['qscore'] = qscoredict
            try:
                with codecs.open(self.workdir + self.map + '_qscore.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except:
                sys.stderr.write('Saving to Qscore json error: {}.\n'.format(sys.exc_info()[1]))
        else:
            print('Qscore was not collected, please check!')

    def newcif_toqdict(self, qscorecif, orgmodel):
        """

            Given cif biopython object and convert to a dictory which contains all data for JSON

        :return: DICT contains Q-score data from mmcif (biopython object)
        """

        residues = []
        colors = []
        qscores = []
        model_colors = []
        chain_qscore = {}
        qscore_list = [atom.qscore for atom in qscorecif.get_atoms() if atom.qscore > 1.0]
        protein_qscores = []
        for atom in qscorecif.get_atoms():
            if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                continue
            protein_qscores.append(atom.qscore)
        average_qscore = round(sum(protein_qscores) / len(protein_qscores), 3)
        if qscore_list:
            min_qscore = min(qscore_list)
            max_qscore = max(qscore_list)
        for chain in qscorecif.get_chains():
            curchain_name = chain.id
            curchain_qscore = []
            for atom in chain.get_atoms():
                if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                    continue
                curchain_qscore.append(atom.qscore)
            if not curchain_qscore:
                continue
            averagecurchain_qscore = round(sum(curchain_qscore) / len(curchain_qscore), 3)
            atoms_inchain = 0
            qscore_inchain = 0.
            for residue in chain:
                curres_name = residue.resname
                if curres_name == 'HOH':
                    continue
                curres_id = residue.id[1]
                atoms_inresidue = 0
                qscore_inresidue = 0.
                for atom in residue:
                    if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                        continue
                    atoms_inchain += 1
                    atoms_inresidue += 1
                    curatom_qscore = atom.qscore
                    qscore_inchain += curatom_qscore
                    qscore_inresidue += curatom_qscore
                if atoms_inresidue != 0.:
                    curres_qscore = round(qscore_inresidue / atoms_inresidue, 3)
                else:
                    curres_qscore = 0.
                if curres_qscore > 1.0:
                    if min_qscore == max_qscore:
                        curres_color = '#000000'
                    else:
                        scaled_qscore = (curres_qscore - min_qscore) / (max_qscore - min_qscore)
                        curres_color = floattohex([scaled_qscore], True)[0]
                else:
                    curres_color = floattohex([curres_qscore])[0]

                icode = residue.id[2]
                if icode != ' ':
                    curres_string = '{}:{}{} {}'.format(curchain_name, curres_id, icode, curres_name)
                else:
                    curres_string = '{}:{} {}'.format(curchain_name, curres_id, curres_name)
                residues.append(curres_string)
                colors.append(curres_color)
                qscores.append(curres_qscore)
            averageqscore_incolor = floattohex([averagecurchain_qscore])[0]
            chain_qscore[curchain_name] = {'value': averagecurchain_qscore, 'color': averageqscore_incolor}
        min_qscore = min(qscores)
        max_qscore = max(qscores)
        for res_qscore in qscores:
            if min_qscore == max_qscore:
                curres_model_color = '#000000'
            else:
                scaled_qscore = (res_qscore - min_qscore) / (max_qscore - min_qscore)
                platelet = [(255, 0, 0), (255, 255, 255), (0, 0, 255)]
                curres_model_color = float_to_hex(scaled_qscore, platelet)
            model_colors.append(curres_model_color)
        levels = np.linspace(-1, 1, 100)
        qarray = np.array(qscores)
        hist, bin_edges = np.histogram(qarray, bins=levels)
        plt.plot(bin_edges[1:], hist/qarray.size)

        protein_qarray = np.array(protein_qscores)
        phist, p_bin_edges = np.histogram(protein_qarray, bins=levels)
        plt.plot(p_bin_edges[1:], phist/protein_qarray.size)
        plt.xlabel('Q-score')
        plt.ylabel('Fraction')
        plt.legend(('Residue: ' + '(' + str(qarray.size) + ')', 'Atom: ' + '(' + str(protein_qarray.size) + ')'), loc='upper left', shadow=True)
        if self.map and self.resolution:
            plt.title('Map: ' + self.map + ' at: ' + str(self.resolution) + 'Å')
        else:
            plt.title('Map Q-score ')
        plt.savefig(self.workdir + self.map + '_qscore.png')
        plt.close()
        q_residue_fractions = list(np.around(hist/qarray.size, 3))
        q_protein_fractions = list(np.around(phist/protein_qarray.size, 3))
        qfractions = {'qLevels': list(np.around(levels[1:], 3)), 'qResidueFractions': q_residue_fractions,
                      'qAtomFractions': q_protein_fractions}

        tdict = OrderedDict([
            ('averageqscore', average_qscore),
            ('averageqscore_color', floattohex([average_qscore])[0]),
            ('numberofatoms', len(protein_qscores)),
            ('color', colors),
            ('model_color', model_colors),
            ('inclusion', qscores),
            ('qscore', qscores),
            ('residue', residues),
            ('chainqscore', chain_qscore),
            ('qFractionDistribution', qfractions)
        ])

        resultdict = OrderedDict([('name', orgmodel), ('data', tdict)])

        return resultdict

    # def newcif_toqdict(self, qscorecif, orgmodel):
    #     """
    #         (original and unused) Given cif biopython object and convert to a dictory which contains all data for JSON
    #     :return: DICT contains Q-score data from mmcif (biopython object)
    #     """
    #
    #     residues = []
    #     colors = []
    #     model_colors = []
    #     qscores = []
    #     chain_qscore = {}
    #     # qscore_list = [atom.qscore for atom in qscorecif.get_atoms() if atom.qscore > 1.0]
    #     qscore_list = [atom.qscore for atom in qscorecif.get_atoms()]
    #     min_qscore = None
    #     max_qscore = None
    #     protein_qscores = []
    #     for atom in qscorecif.get_atoms():
    #         if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
    #             continue
    #         protein_qscores.append(atom.qscore)
    #     average_qscore = round(sum(protein_qscores) / len(protein_qscores), 3)
    #     if qscore_list:
    #         min_qscore = min(qscore_list)
    #         max_qscore = max(qscore_list)
    #     for chain in qscorecif.get_chains():
    #         curchain_name = chain.id
    #         curchain_qscore = []
    #         for atom in chain.get_atoms():
    #             if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
    #                 continue
    #             curchain_qscore.append(atom.qscore)
    #         if not curchain_qscore:
    #             continue
    #         averagecurchain_qscore = round(sum(curchain_qscore) / len(curchain_qscore), 3)
    #         atoms_inchain = 0
    #         qscore_inchain = 0.
    #         for residue in chain:
    #             curres_name = residue.resname
    #             if curres_name == 'HOH':
    #                 continue
    #             curres_id = residue.id[1]
    #             atoms_inresidue = 0
    #             qscore_inresidue = 0.
    #             for atom in residue:
    #                 if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
    #                     continue
    #                 atoms_inchain += 1
    #                 atoms_inresidue += 1
    #                 curatom_qscore = atom.qscore
    #                 qscore_inchain += curatom_qscore
    #                 qscore_inresidue += curatom_qscore
    #             if atoms_inresidue != 0.:
    #                 curres_qscore = round(qscore_inresidue / atoms_inresidue, 3)
    #             else:
    #                 curres_qscore = 0.
    #             if curres_qscore > 1.0:
    #                 if min_qscore == max_qscore:
    #                     curres_color = '#000000'
    #                 else:
    #                     scaled_qscore = (curres_qscore - min_qscore) / (max_qscore - min_qscore)
    #                     curres_color = floattohex([scaled_qscore], True)[0]
    #             else:
    #                 curres_color = floattohex([curres_qscore])[0]
    #
    #             icode = residue.id[2]
    #             if icode != ' ':
    #                 curres_string = '{}:{}{} {}'.format(curchain_name, curres_id, icode, curres_name)
    #             else:
    #                 curres_string = '{}:{} {}'.format(curchain_name, curres_id, curres_name)
    #             residues.append(curres_string)
    #             colors.append(curres_color)
    #             qscores.append(curres_qscore)
    #
    #     min_qscore = min(qscores)
    #     max_qscore = max(qscores)
    #     for res_qscore in qscores:
    #         if min_qscore == max_qscore:
    #             curres_model_color = '#000000'
    #         else:
    #             scaled_qscore = (res_qscore - min_qscore) / (max_qscore - min_qscore)
    #             platelet = [(255, 0, 0), (255, 255, 255), (0, 0, 255)]
    #             curres_model_color = float_to_hex(scaled_qscore, platelet)
    #         model_colors.append(curres_model_color)
    #
    #         averageqscore_incolor = floattohex([averagecurchain_qscore])[0]
    #         chain_qscore[curchain_name] = {'value': averagecurchain_qscore, 'color': averageqscore_incolor}
    #     print(chain_qscore)
    #
    #     levels = np.linspace(-1, 1, 100)
    #     qarray = np.array(qscores)
    #     hist, bin_edges = np.histogram(qarray, bins=levels)
    #     plt.plot(bin_edges[1:], hist / qarray.size)
    #
    #     protein_qarray = np.array(protein_qscores)
    #     phist, p_bin_edges = np.histogram(protein_qarray, bins=levels)
    #     plt.plot(p_bin_edges[1:], phist / protein_qarray.size)
    #     plt.xlabel('Q-score')
    #     plt.ylabel('Fraction')
    #     plt.legend(('Residue: ' + '(' + str(qarray.size) + ')', 'Atom: ' + '(' + str(protein_qarray.size) + ')'),
    #                loc='upper left', shadow=True)
    #     if self.map and self.resolution:
    #         plt.title('Map: ' + self.map + ' at: ' + str(self.resolution) + 'Å')
    #     else:
    #         plt.title('Map Q-score ')
    #     plt.savefig(self.workdir + self.map + '_qscore.png')
    #     plt.close()
    #     q_residue_fractions = list(np.around(hist / qarray.size, 3))
    #     q_protein_fractions = list(np.around(phist / protein_qarray.size, 3))
    #     qfractions = {'qLevels': list(np.around(levels[1:], 3)), 'qResidueFractions': q_residue_fractions,
    #                   'qAtomFractions': q_protein_fractions}
    #
    #     # score_type = 'qscore'
    #     # new_dict = {'id': self.emdid, 'resolution': float(self.resolution), 'name': orgmodel, score_type: average_qscore}
    #     # plot_name = '{}_{}_{}_bar.png'.format(self.mapname, orgmodel, score_type)
    #     # score_dir = os.path.dirname(va.__file__)
    #     # relative_towhole, relative_totwo = bar(new_dict, score_type, self.workdir, score_dir, plot_name)
    #     # qbar = {'whole': relative_towhole, 'relative': relative_totwo}
    #
    #     tdict = OrderedDict([
    #         ('averageqscore', average_qscore),
    #         ('averageqscore_color', floattohex([average_qscore])[0]),
    #         # ('qscore_bar', qbar),
    #         ('numberofatoms', len(protein_qscores)),
    #         ('color', colors),
    #         ('model_color', model_colors),
    #         ('inclusion', qscores),
    #         ('qscore', qscores),
    #         ('residue', residues),
    #         ('chainqscore', chain_qscore),
    #         ('qFractionDistribution', qfractions)
    #     ])
    #
    #     resultdict = OrderedDict([('name', orgmodel), ('data', tdict)])
    #
    #     return resultdict

    def qscoreview(self, chimeraapp):
        """

            X, Y, Z images which model was colored by Q-score

        :return:
        """

        # read json
        start = timeit.default_timer()
        injson = glob.glob(self.workdir + '*_qscore.json')
        basedir = self.workdir
        mapname = self.map
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        score_dir = os.path.dirname(va.__file__)
        rescolor_file = f'{score_dir}/utils/rescolor.py'
        errlist = []

        fulinjson = injson[0] if injson else None
        try:
            if fulinjson:
                with open(fulinjson, 'r') as f:
                    args = json.load(f)
            else:
                args = None
                print('There is no Qscore json file.')
        except TypeError:
            err = 'Open Qscore JSON error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        else:
            if args is not None:
                models = args['qscore']
                try:
                    del models['err']
                except:
                    print('Qscore json result is correct')

                print('There is/are %s model(s).' % len(models))
                for (key, value) in iteritems(models):
                    # for (key2, value2) in iteritems(value):
                    if type(value) is float:
                        continue
                    keylist = list(value)
                    for key in keylist:
                        if key != 'name':
                            colors = value[key]['color']
                            model_colors = value[key]['model_color']
                            residues = value[key]['residue']
                            qscores = value[key]['inclusion']
                        else:
                            modelname = value[key]
                            model = self.workdir + modelname
                            chimerafname = '{}_{}_qscore_chimera.cxc'.format(modelname, mapname)
                            surfacefn = '{}{}_{}'.format(basedir, modelname, mapname)
                            chimeracmd = chimerafname
                            chimera_model_cmd = '{}_{}_qscore_model_chimera.cxc'.format(modelname, mapname)
                            # pdbmodelname = '{}{}__Q__{}.pdb'.format(basedir, modelname[:-4], mapname[:-4])
                            pdbmodelname = '{}{}__Q__{}.cif'.format(basedir, modelname, mapname)

                    with open(self.workdir + chimeracmd, 'w') as fp:
                        fp.write("open " + str(pdbmodelname) + " format mmcif" + '\n')
                        fp.write(f"open {rescolor_file}\n")
                        # fp.write("open " + str(pdbmodelname) + " format pdb" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        count = 0
                        number_of_item = len(colors)
                        for (color, residue, qscore) in zip(colors, residues, qscores):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # 1st way of getting res_id
                            # res_id = re.sub("\D", "", restmp)
                            # 2nd way of getting res
                            res_id = re.findall(r'-?\d+', restmp)[0]
                            if count == 0:
                                count += 1
                                fp.write(f'rescolors /{chain}:{res_id} {color} ')
                            elif count == number_of_item - 1:
                                fp.write(f'/{chain}:{res_id} {color}\n')
                            else:
                                count += 1
                                fp.write(f'/{chain}:{res_id} {color} ')

                            # fp.write(
                            #     'color /' + chain + ':' + res_id + ' ' + color + '\n'
                            # )
                            if qscore > 1.0:
                                fp.write(
                                    'show /' + chain + ':' + res_id + ' atoms' + '\n'
                                    'style /' + chain + ':' + res_id + ' stick' + '\n'
                                )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_zqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_xqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_yqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )

                    with open(self.workdir + chimera_model_cmd, 'w') as fp:
                        fp.write("open " + str(pdbmodelname) + " format mmcif" + '\n')
                        fp.write(f"open {rescolor_file}\n")
                        # fp.write("open " + str(pdbmodelname) + " format pdb" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        count = 0
                        number_of_item = len(colors)
                        for (color, residue, qscore) in zip(model_colors, residues, qscores):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # 1st way of getting res_id
                            # res_id = re.sub("\D", "", restmp)
                            # 2nd way of getting res
                            res_id = re.findall(r'-?\d+', restmp)[0]
                            if count == 0:
                                count += 1
                                fp.write(f'rescolors /{chain}:{res_id} {color} ')
                            elif count == number_of_item - 1:
                                fp.write(f'/{chain}:{res_id} {color}\n')
                            else:
                                count += 1
                                fp.write(f'/{chain}:{res_id} {color} ')

                            # fp.write(
                            #     'color /' + chain + ':' + res_id + ' ' + color + '\n'
                            # )
                            if qscore > 1.0:
                                fp.write(
                                    'show /' + chain + ':' + res_id + ' atoms' + '\n'
                                    'style /' + chain + ':' + res_id + ' stick' + '\n'
                                )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_model_zqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_model_xqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_model_yqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )
                    try:
                        if not bindisplay:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                                  cwd=self.workdir, shell=True)
                            print('Colored models based on Qscore were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models based on Qscore were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} Qscore view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        if not bindisplay:
                            subprocess.check_call(
                                locCHIMERA + " --offscreen --nogui " + self.workdir + chimera_model_cmd,
                                cwd=self.workdir, shell=True)
                            print('Colored models based on Qscore were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimera_model_cmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models based on Qscore were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} Qscore view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        for axis in ['x', 'y', 'z']:
                            qscore_surface = f'{surfacefn}_{axis}qscoresurface.jpeg'
                            qscore_mode_surface = f'{surfacefn}_model_{axis}qscoresurface.jpeg'
                            if os.path.isfile(qscore_surface):
                                scale_image(qscore_surface, (300, 300))
                            if os.path.isfile(qscore_mode_surface):
                                scale_image(qscore_mode_surface, (300, 300))
                    except:
                        err = 'Scaling model Qscore view error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    jpegs = glob.glob(self.workdir + '/*surface.jpeg')
                    modelsurf = dict()
                    finalmmdict = dict()
                    if self.models:
                        # print "self.models:%s" % self.models
                        for model in self.models:
                            modelname = os.path.basename(model.filename)
                            surfacefn = '{}_{}'.format(modelname, self.map)
                            modelmapsurface = dict()
                            for jpeg in jpegs:
                                if modelname in jpeg and 'xqscore' in jpeg:
                                    modelmapsurface['x'] = str(surfacefn) + '_scaled_xqscoresurface.jpeg'
                                if modelname in jpeg and 'yqscore' in jpeg:
                                    modelmapsurface['y'] = str(surfacefn) + '_scaled_yqscoresurface.jpeg'
                                if modelname in jpeg and 'zqscore' in jpeg:
                                    modelmapsurface['z'] = str(surfacefn) + '_scaled_zqscoresurface.jpeg'
                            if errlist:
                                modelmapsurface['err'] = {'model_fit_err': errlist}
                            modelsurf[modelname] = modelmapsurface
                        finalmmdict['qscore_surface'] = modelsurf

                        try:
                            with codecs.open(self.workdir + self.map + '_qscoreview.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finalmmdict, f)
                        except:
                            sys.stderr.write(
                                'Saving Qscore view to JSON error: {}.\n'.format(sys.exc_info()[1]))

                end = timeit.default_timer()
                print('Qscore surface time: %s' % (end - start))
                print('------------------------------------')