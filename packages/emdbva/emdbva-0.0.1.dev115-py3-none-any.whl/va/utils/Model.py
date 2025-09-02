import os
import sys
from Bio.PDB import MMCIFParser
from Bio.PDB.mmcifio import MMCIFIO
from Bio.PDB.PDBIO import Select
# from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.PDB.Structure import Structure
import timeit


class NotDisordered(Select):
    """
        Class used to select non-disordered atom from biopython structure instance
    """

    def accept_atom(self, atom):
        """
            Accept only atoms that at "A"
        :param atom: atom instance from biopython library
        :return: True or False
        """
        if (not atom.is_disordered()) or atom.get_altloc() == "A":
            atom.set_altloc(" ")
            return True
        else:
            return False


class Model:
    """
        MapProcessor class contains methods deal with map processing method and model associated map processing methods
        Instance can be initialized with either full map file path or a mrcfile map object
    """

    def __init__(self, input_model, input_dir=None):
        """
            Initialization method with input_model as full path or as a biopython mmcif object and the directory of it
        """
        self.model, self.model_dir = self._set_model_and_dir(input_model) if not input_model else self._set_model_and_dir(input_model, input_dir)

    @staticmethod
    def _set_model_and_dir(input_model, input_dir=None):
        if isinstance(input_model, str) and os.path.isfile(input_model):
            return input_model, os.path.dirname(input_model)
        elif isinstance(input_model, Structure) and input_dir:
            return input_model, input_dir
        else:
            return None, None
    def get_auth_comp_id_map(self, input_cif):
        '''
            Extract the auth_comp_id mapping from an mmCIF dictionary.
        Parameters:
        mmcif_dict (dict): Parsed mmCIF dictionary

        Returns:
        dict: A dictionary mapping (chain_id, resseq) to auth_comp_id
        '''

        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif)
        mmcif_dict = parser._mmcif_dict
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']
        auth_comp_ids = mmcif_dict['_atom_site.auth_comp_id']

        auth_comp_id_map = {}
        for chain, resseq, auth_comp_id in zip(chains, resseqs, auth_comp_ids):
            key = (chain, int(resseq))
            auth_comp_id_map[key] = auth_comp_id

        return auth_comp_id_map

    def get_formal_charge_map(self, input_cif):
        '''
            Extract the pdbx_formal_charge mapping from an mmCIF dictionary.
        Parameters:
        mmcif_dict (dict): Parsed mmCIF dictionary

        Returns:
        dict: A dictionary mapping (chain_id, resseq) to pdbx_formal_charge
        '''

        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif)
        mmcif_dict = parser._mmcif_dict
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']
        formal_charges = mmcif_dict['_atom_site.pdbx_formal_charge']

        formal_charge_map = {}
        for chain, resseq, formal_charge in zip(chains, resseqs, formal_charges):
            key = (chain, int(resseq))
            formal_charge_map[key] = formal_charge

        return formal_charge_map

    def save_updated_model(self, input_cif_file_one, input_cif_file):
        '''
            Save the first model from the mmCIF file to a new mmCIF file with auth_comp_id.
        Parameters:
        input_cif_file (str): Input mmCIF file path
        output_cif_file (str): Output mmCIF file path
        '''

        # Create the auth_comp_id_map
        auth_comp_id_map = self.get_auth_comp_id_map(input_cif_file_one)
        formal_charge_map = self.get_formal_charge_map(input_cif_file_one)

        # Extract the first model
        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif_file)
        mmcif_dict = parser._mmcif_dict
        first_model = structure[0]

        # Prepare to add auth_comp_id
        if '_atom_site.auth_comp_id' not in mmcif_dict:
            mmcif_dict['_atom_site.auth_comp_id'] = []
        if '_atom_site.pdbx_formal_charge' not in mmcif_dict:
            mmcif_dict['_atom_site.pdbx_formal_charge'] = []

        # Get the existing residue information
        residues = mmcif_dict['_atom_site.label_comp_id']
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']

        # Add auth_comp_id based on the map
        for res, chain, resseq in zip(residues, chains, resseqs):
            auth_comp_id = auth_comp_id_map.get((chain, int(resseq)), res)
            formal_charge = formal_charge_map.get((chain, int(resseq)), '?')
            mmcif_dict['_atom_site.auth_comp_id'].append(auth_comp_id)
            mmcif_dict['_atom_site.pdbx_formal_charge'].append(formal_charge)

        # Write the modified dictionary to a new mmCIF file
        io = MMCIFIO()
        io.set_dict(mmcif_dict)
        io.save(input_cif_file)

    def _structure_to_model(self, pid, cur_model_name):
        """
            Take structure object and output the used model object

        :param pid: String of anything or pdbid
        :param cur_model_name: String of the model name
        :return: TEMPy model instance which will be used for the whole calculation
        """

        p = MMCIFParser()
        io = MMCIFIO()
        org_file_name = cur_model_name
        match_text = 'data_'
        out_moderate_cif = cur_model_name + '_moderated.cif'
        match = self.remove_lines_after_match(cur_model_name, out_moderate_cif, match_text)
        if match:
            structure = p.get_structure(pid, out_moderate_cif)
            cur_model_name = out_moderate_cif
        else:
            structure = p.get_structure(pid, cur_model_name)

        if len(structure.get_list()) > 1:
            org_model = cur_model_name + '_org.cif'
            os.rename(cur_model_name, org_model)
            fstructure = structure[0]
            io.set_structure(fstructure)
            io.save(cur_model_name)
            self.save_updated_model(org_file_name, cur_model_name)
            used_frame = p.get_structure('first', cur_model_name)
            print('!!!There are multiple models in the cif file. Here we only use the first for calculation.')
        else:
            used_frame = structure

        # io.set_structure(used_frame)
        if self.has_disorder_atom(used_frame):
            cur_model_name = cur_model_name + '_Alt_A.cif'
            io.set_structure(used_frame)
            print('There are alternative atom in the model here we only use A for calculations and saved as {}'
                  .format(cur_model_name))
            io.save(cur_model_name, select=NotDisordered())
            new_structure = p.get_structure(pid, cur_model_name)
        else:
            new_structure = used_frame

        setattr(new_structure, "filename", org_file_name)
        tmodel = new_structure

        return tmodel

    @staticmethod
    def remove_lines_after_match(input_file, output_file, match_text):
        """
            Remove lines after the match text
        """

        try:
            with open(input_file, 'r') as infile:
                found_second_match = False
                match_count = 0
                content_before_second_match = []

                for line in infile:
                    if line.startswith(match_text):
                        match_count += 1
                        if match_count >= 2:
                            found_second_match = True
                            break
                    content_before_second_match.append(line)

            if found_second_match:
                with open(output_file, 'w') as outfile:
                    outfile.writelines(content_before_second_match)
                return True
            else:
                print('Second match not found in the file.')
                return False

        except FileNotFoundError:
            print(f'Error: Input file "{input_file}" not found.')
            return False
        except Exception as e:
            print(f'An error occurred: {str(e)}')

            return False

    @staticmethod
    def has_disorder_atom(structure):
        """
            Check if the model contains disorder atoms
        """

        ress = structure.get_residues()
        disorder_flag = False
        for res in ress:
            if res.is_disordered() == 1:
                disorder_flag = True
                return disorder_flag
        return disorder_flag

    def read_model_test(self):
        """
            Read models if '-f' argument is used
        """

        start = timeit.default_timer()
        if self.model is not None:
            model_name = self.model
            full_model_name = model_name
            try:
                model_size = os.stat(full_model_name).st_size
                pid = 'id'
                input_model = []
                tmodel = self._structure_to_model(pid, full_model_name)
                input_model.append(tmodel)

                end = timeit.default_timer()
                print('Read model time: %s' % (end - start))
                print('------------------------------------')

                return input_model, pid, model_size
            except:
                print('!!! File: %s does not exist or corrupted: %s!!!' % (full_model_name, sys.exc_info()[1]))
                print('------------------------------------')
                input_model = None

                return input_model
        else:
            print('No model is given.')
            input_model = None

            return input_model


    def final_model(self):
        """
            Get the final biopython model object
        """
        if isinstance(self.model, Structure):
            return self.model
        else:
            return self.read_model_test()

    @staticmethod
    def atom_numbers(model_filename):
        """
            Get the number of atoms in the model
        :param model_filename: string of full model name with path
        :return: integer of number of atoms
        """

        parser = MMCIFParser()
        structure = parser.get_structure('t', model_filename)
        atoms = structure.get_atoms()

        return sum(1 for _ in atoms)

