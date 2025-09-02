import os
import numpy as np
from math import floor
import math
import mrcfile
import subprocess
import shutil
from skimage import measure
from va.utils.misc import *
from va.utils.Model import *
from va.metrics.contour_level_predicator import *
from scipy.fft import fftn, ifftn, fftfreq


class MapProcessor:
    """
        MapProcessor class contains methods deal with map processing method and model associated map processing methods
        Instance can be initialized with either full map file path or a mrcfile map object
    """

    def __init__(self, input_map=None):
        if isinstance(input_map, str):
            if os.path.isfile(input_map):
                self.map = mrcfile.open(input_map)
            else:
                self.map = None
        elif isinstance(input_map, mrcfile.mrcfile.MrcFile):
            self.map = input_map
        else:
            self.map = None

    def get_indices(self, one_coord):
        """
            Find one atom's indices corresponding to its cubic or plane
            the 8 (cubic) or 4 (plane) indices are saved in indices variable

        :param one_coord: List contains the atom coordinates in (x, y, z) order
        :return: Tuple contains two list of index: first has the 8 or 4 indices in the cubic;
                 second has the float index of the input atom
        """
        # For non-cubic or skewed density maps, they might have different apix on different axes
        zdim = self.map.header.cella.z
        znintervals = self.map.header.mz
        z_apix = zdim / znintervals

        ydim = self.map.header.cella.y
        ynintervals = self.map.header.my
        y_apix = ydim / ynintervals

        xdim = self.map.header.cella.x
        xnintervals = self.map.header.mx
        x_apix = xdim / xnintervals

        map_zsize = self.map.header.nz
        map_ysize = self.map.header.ny
        map_xsize = self.map.header.nx

        if self.map.header.cellb.alpha == self.map.header.cellb.beta == self.map.header.cellb.gamma == 90.:
            zindex = float(one_coord[2] - self.map.header.origin.z) / z_apix - self.map.header.nzstart
            yindex = float(one_coord[1] - self.map.header.origin.y) / y_apix - self.map.header.nystart
            xindex = float(one_coord[0] - self.map.header.origin.x) / x_apix - self.map.header.nxstart

        else:
            # fractional coordinate matrix
            xindex, yindex, zindex = self.matrix_indices(one_coord)

        zfloor = int(floor(zindex))
        if zfloor >= map_zsize - 1:
            zceil = zfloor
        else:
            zceil = zfloor + 1

        yfloor = int(floor(yindex))
        if yfloor >= map_ysize - 1:
            yceil = yfloor
        else:
            yceil = yfloor + 1

        xfloor = int(floor(xindex))
        if xfloor >= map_xsize - 1:
            xceil = xfloor
        else:
            xceil = xfloor + 1

        indices = np.array(np.meshgrid(np.arange(xfloor, xceil + 1), np.arange(yfloor, yceil + 1),
                                       np.arange(zfloor, zceil + 1))).T.reshape(-1, 3)
        oneindex = [xindex, yindex, zindex]

        return (indices, oneindex)

    def matrix_indices(self, onecoor):
        """
            using the fractional coordinate matrix to calculate the indices when the maps are non-orthogonal

        :param onecoor: list contains the atom coordinates in (x, y, z) order
        :return: tuple of indices in x, y, z order
        """

        # Figure out the order of the x, y, z based on crs info in the header
        apixs = self.map.voxel_size.tolist()
        angs = [self.map.header.cellb.alpha, self.map.header.cellb.beta, self.map.header.cellb.gamma]
        matrix = self.map_matrix(apixs, angs)
        result = matrix.dot(np.asarray(onecoor))
        xindex = result[0] - self.map.header.nxstart
        yindex = result[1] - self.map.header.nystart
        zindex = result[2] - self.map.header.nzstart

        return xindex, yindex, zindex

    @staticmethod
    def map_matrix(apixs, angs):
        """
            calculate the matrix to transform Cartesian coordinates to fractional coordinates
            (check the definition to see the matrix formular)

        :param apixs: array of apix/voxel size
        :param angs: array of angles in alpha, beta, gamma order
        :return: a numpy array to be used for calculated fractional coordinates
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

    def get_close_voxels_indices(self, onecoor, n):
        """
            Given onecoor, return the nearby voxels indices; radius defined by n

        :param onecoor: list contains the atom coordinates in (x, y, z) order
        :param n: a number integer of float which define radius voxel check range radius = (n*average_voxel_size)
        :return: a list of tuples of indices in (z, y, x) format to adapt to mrcfile data format
        """

        xind, yind, zind = self.get_indices(onecoor)[1]
        voxel_sizes = self.map.voxel_size.tolist()
        atom_xind = int(xind)
        atom_yind = int(yind)
        atom_zind = int(zind)

        average_voxel_size = sum(voxel_sizes) / 3.
        radius = n * average_voxel_size
        rx = int(round(radius / voxel_sizes[0]))
        ry = int(round(radius / voxel_sizes[1]))
        rz = int(round(radius / voxel_sizes[2]))

        indices = []
        for x in range(atom_xind - rx, atom_xind + rx):
            for y in range(atom_yind - ry, atom_yind + ry):
                for z in range(atom_zind - rz, atom_zind + rz):
                    d = average_voxel_size * math.sqrt(
                        (x - atom_xind) ** 2 + (y - atom_yind) ** 2 + (z - atom_zind) ** 2)
                    if d <= radius:
                        indices.append([x, y, z])
        result = [tuple(x[::-1]) for x in indices]

        return result

    def generate_mask(self, coords, radius):
        """
            Based on the coordinates, generate a mask based on the radius
            The mask based on the map initialized in the MapProcessor class

        :param coords: a list of tuples in (x, y, z) format
        :param radius: an integer or float define the radius of mask range around the coordinate
        """

        dir_name = os.path.dirname(self.map._iostream.name)
        map_name = os.path.basename(self.map._iostream.name)
        mask = np.zeros_like(self.map.data)
        for coord in coords:
            near_indices = self.get_close_voxels_indices(coord, radius)
            for ind in near_indices:
                mask[ind] = 1
        out_map = mrcfile.new(f'{dir_name}/{map_name}_residue_mask.mrc', overwrite=True)
        out_map.set_data(mask)
        out_map.voxel_size = self.map.voxel_size
        out_map.close()

    @staticmethod
    def check_map_zeros(input_map_name):
        """
            Check if the map has all zeros in the data
        :param input_map_name: Path to the map file
        """
        with mrcfile.open(input_map_name, mode='r') as input_map:
            if np.all(input_map.data == 0):
                print(f'{input_map_name} has all zeros in the data.')
                return True
            else:
                print(f'{input_map_name} does not have all zeros in the data.')
                return False

    @staticmethod
    def check_map_starts(map_one_path, map_two_path):
        """
            Check if two maps have the same origin in their headers.
        :param map_one_path: Path to the first map file
        :param map_two_path: Path to the second map file
        :return: True if both maps have the same origin, False otherwise
        """
        with mrcfile.open(map_one_path, mode='r') as map_one, mrcfile.open(map_two_path, mode='r') as map_two:
            starts_one = (map_one.header.nxstart, map_one.header.nystart, map_one.header.nzstart)
            starts_two = (map_two.header.nxstart, map_two.header.nystart, map_two.header.nzstart)

            return starts_one == starts_two

    @staticmethod
    def update_map_starts(source_map_path, target_map_path):
        """
            Update the nxstart, nystart, and nzstart values of the target map to match those of the source map.
        :param source_map_path: Path to the source map file
        :param target_map_path: Path to the target map file
        """
        with mrcfile.open(source_map_path, mode='r') as source_map, mrcfile.open(target_map_path,
                                                                                 mode='r+') as target_map:
            target_map.header.nxstart = source_map.header.nxstart
            target_map.header.nystart = source_map.header.nystart
            target_map.header.nzstart = source_map.header.nzstart
            target_map.update_header_stats()
            target_map.flush()

    def residue_average_resolution(self, indices, mapdata=None):
        """
            given mapdata and indices, calculate the average value of these density values

        :param mapdata: numpy array of map data
        :param indices: list of tuples of (x, y, z) coordinates
        return: average value of these density values
        """

        sum_local_resolution = 0.
        if mapdata is None:
            mapdata = self.map.data
        for ind in indices:
            sum_local_resolution += mapdata[ind]

        return sum_local_resolution / len(indices)

    @staticmethod
    def save_map(map_data, output_mapname, voxel_size=1., nstarts=(0, 0, 0)):
        """
            save to a new map
        :param map_data: np array of map data
        :param output_mapname: full path to output map
        :param voxel: voxel size use default as 1 if not given
        """

        m = mrcfile.new(output_mapname, overwrite=True)
        m.set_data(map_data)
        m.voxel_size = voxel_size
        m.header.nxstart = nstarts[0]
        m.header.nystart = nstarts[1]
        m.header.nzstart = nstarts[2]

        m.header.mapc = 1  # Columns = X axis
        m.header.mapr = 2  # Rows = Y axis
        m.header.maps = 3
        m.close()

    @staticmethod
    def get_map_volume(full_input_map_name, contour=1.0):
        """
            Collect the map volume
        :param full_input_map_name: string of full path to input map
        :param contour: contour value if not provided use 1.0 as default
        """

        input_map = mrcfile.mmap(full_input_map_name, mode='r')
        # apix = input_map.voxel_size.tolist()
        voxel_volume = np.prod(input_map.voxel_size.tolist())
        voxel_count = np.sum(input_map.data >= contour)
        map_volume = voxel_volume * voxel_count

        return map_volume


    @staticmethod
    def mask_map(input_map, mask, output_mapname=None):
        """
            Mask the input map
        :param input_map: string of full path to input map
        :param mask: string of full path to mask
        :param output_mapname: full path to output map name
        """

        in_map = mrcfile.open(input_map)
        in_map_name = os.path.basename(input_map)
        in_map_data = in_map.data
        mask_map = mrcfile.open(mask)
        mask_data = mask_map.data
        mask_name = os.path.basename(mask)
        work_dir = os.path.dirname(input_map)
        if output_mapname is None:
            output_mapname = f'{work_dir}/{in_map_name}_{mask_name}_masked.map'
        if in_map_data.shape != mask_data.shape and input_map.voxel_size == mask.voxel_size:
            print(f'Map shape mismatch: {in_map_data.shape} and {mask_data.shape} or '
                  f'voxel size mismatch: {input_map.voxel_size} and {mask_data.voxel_size}')

            return None
        else:
            out_data = in_map_data * mask_data
            voxel = in_map.voxel_size
            input_nstarts = (in_map.header.nxstart, in_map.header.nystart, in_map.header.nzstart)
            MapProcessor.save_map(out_data, output_mapname, voxel, input_nstarts)

            return output_mapname

    @staticmethod
    def binarized_mask(mask, map_name):
        """
            Produce a mask with 0 and 1s (for Relion mask with value > 0.5)
        :param mask: a string of full path to a mask
        :param map_name: a string of full path of primary map related to this mask
        """

        mask_map = mrcfile.open(mask)
        mask_nstarts = (mask_map.header.nxstart, mask_map.header.nystart, mask_map.header.nzstart)
        mask_map_data = mask_map.data > 0.5
        new_data = mask_map_data.astype(np.uint8)
        voxel_size = mask_map.voxel_size
        work_dir = os.path.dirname(os.path.dirname(os.path.dirname(mask)))
        outmap_name = f'{work_dir}/{map_name}_binarized_mask.map'
        MapProcessor.save_map(new_data, outmap_name, voxel_size, mask_nstarts)

        return outmap_name

    @staticmethod
    def predict_contour(input_map):
        """
            Given input map, predict the contour leve
        :param input_map: a string of full input map path
        :return: a float of the contour
        """

        m = mrcfile.open(input_map)
        d = m.data
        # non-cubic map use padding 0 to make it cubic
        if not all(dim == d.shape[0] for dim in d.shape):
            dim_shape = max(d.shape)
            target_shape = (dim_shape, dim_shape, dim_shape)
            d = pad_array(m.data, target_shape)
        norm_pred = calc_level_dev(d)[0]
        pred_cl = keep_three_significant_digits(float(norm_pred))

        return pred_cl


    @staticmethod
    def map_indices(input_map, contour):
        """
            Given input map and contour return all indices that correspond to the contour value larger than contour
        :param input_map: a string of full input map path
        :param contour: a float value of the contour
        :return: a list of tuples in (x, y, z)
        """
        map = mrcfile.open(input_map)

        return np.where(map.data >= contour)

    @staticmethod
    def map_minmax(map_one, map_two):
        """
            Get input map min and max value
        :param map_one(masked_raw_map): a full path of input map one
        :param map_two: a full path of input map two
        """

        masked_raw_predicted_contour = MapProcessor.predict_contour(map_one)
        all_indices = MapProcessor.map_indices(map_one, masked_raw_predicted_contour)
        local_res_map = mrcfile.open(map_two)
        all_values = local_res_map.data[all_indices]

        return np.min(all_values), np.max(all_values)


    def model_area_indices(self, input_map, model, radius=3):
        """
            Get all indices of the 'mask' that used for the area around the model in the map
        """
        map = MapProcessor(input_map)
        # use for generate mask for the whole model or the voxels involved
        all_indices = set()
        # all_coordinates = []
        for chain in model.get_chains():
            for residue in chain.get_residues():
                residue_atom_count = 0
                for atom in residue.get_atoms():
                    if atom.name.startswith('H') or atom.get_parent().resname == 'HOH':
                        continue
                    one_coordinate = atom.coord
                    around_indices = map.get_close_voxels_indices(one_coordinate, radius)
                    # use for generate mask for the whole model or the voxels involved
                    # all_coordinates.append(one_coordinate)
                    all_indices.update(around_indices)
                if residue_atom_count == 0:
                    continue

        # Get model volume based on voxel size and indices numbers
        voxel_volume = np.prod(map.map.voxel_size.tolist())
        model_volume = len(all_indices) * voxel_volume

        return all_indices, len(all_indices), model_volume



    def model_ratio(self, input_map, model, radius=3):
        """
            Check the percentage of a model that covered the input map
        :param input_map: a string of full input map path
        :param model: a string of full model path
        :param radius: distance to the atom which defined the model area, default as 3
        """

        work_dir = None

        if isinstance(input_map, str):
            work_dir = os.path.dirname(input_map)
        elif isinstance(input_map, mrcfile.mrcfile.MrcFile):
            input_map = input_map._iostream.name
            work_dir = os.path.dirname(input_map)
        model_container = Model(model, work_dir)
        # model_container = Model('/Users/zhe/Downloads/tests/VA/nfs/msd/work2/emdb/development/staging/em/81/8117/va/5irx.cif')
        loaded_model = model_container.final_model()
        model_area_indices, model_area_indices_number, model_volume = self.model_area_indices(input_map, loaded_model, radius)
        # Save model volume into json
        out_file = f'{work_dir}/{os.path.basename(input_map)}_modelvolume.json'
        model_volume_dict = {'model_volume': {'volume': model_volume, 'radius': radius}}
        out_json(model_volume_dict, out_file)

        ## code for model area into a map
        # mask = np.zeros_like(self.map.data)
        # for i in model_area_indices:
        #     mask[i] = 1
        # out_map = mrcfile.new(f'{work_dir}/model_area.mrc', overwrite=True)
        # out_map.set_data(mask)
        # out_map.voxel_size = self.map.voxel_size
        # out_map.close()
        ##
        predicated_contour_level = self.predict_contour(input_map)
        map_area = self.map_indices(input_map, predicated_contour_level)
        map_area_indices = list(zip(map_area[0], map_area[1], map_area[2]))
        overlapped_area = set(map_area_indices) & set(model_area_indices)
        overlapped_area_size = len(list(overlapped_area))
        # ### code for put overlap region as a map
        # mask = np.zeros_like(self.map.data)
        # for i in overlapped_area:
        #     mask[i] = 1
        # out_map = mrcfile.new(f'{work_dir}/overlap.mrc', overwrite=True)
        # out_map.set_data(mask)
        # out_map.voxel_size = self.map.voxel_size
        # out_map.close()
        # ##
        overlap_to_model = keep_three_significant_digits(overlapped_area_size/model_area_indices_number)
        overlap_to_map = keep_three_significant_digits(overlapped_area_size/len(map_area_indices))
        model_to_map = keep_three_significant_digits(model_area_indices_number/len(map_area_indices))
        print(f'overlap/model: {overlap_to_model}')
        print(f'overlap/map: {overlap_to_map}')
        print(f'model/map: {model_to_map}')
        final_result = {'model_map_ratio': {'overlap_to_model': overlap_to_model, 'overlap_to_map': overlap_to_map,
                                            'model_to_map': model_to_map}}
        out_file = f'{work_dir}/{os.path.basename(input_map)}_modelmapratio.json'
        out_json(final_result, out_file)

        return out_file


    @staticmethod
    def compute_surface_area(mrc_file, contour_level):
        """
            Compute the surface area of a 3D cryo-EM density map at a given contour level.
        - mrc_file (str): Path to the .mrc file.
        - contour_level (float): The density threshold to define the surface.

        Returns:
        - float: Surface area in arbitrary units.
        """

        with mrcfile.open(mrc_file, permissive=True) as mrc:
            volume = mrc.data.astype(np.float32)
            voxel_size = mrc.voxel_size['x']

        # Apply Marching Cubes algorithm to extract surface mesh
        verts, faces, _, _ = measure.marching_cubes(volume, level=contour_level)

        # Compute surface area by summing the area of all mesh triangles
        def triangle_area(v1, v2, v3):
            return 0.5 * np.linalg.norm(np.cross(v2 - v1, v3 - v1))

        surface_area = sum(triangle_area(verts[f[0]], verts[f[1]], verts[f[2]]) for f in faces)

        # Convert area to real space (scaling by voxel size squared)
        surface_area *= (voxel_size ** 2)

        return surface_area

    @staticmethod
    def compute_surface_ratio(map_one, map_two):
        """
        Compute the surface ratios of the primary map and raw map before masking.

        :param map_one: Name of the primary map file
        :param map_two: Name of the raw map file
        :return: Surface ratio before masking
        """

        primary_map = mrcfile.open(map_one)
        primary_data = primary_map.data
        predicated_contour_primary_map = calc_level_dev(primary_data)[0]
        primary_map_surface = MapProcessor.compute_surface_area(map_one, predicated_contour_primary_map)

        raw_map = mrcfile.open(f'{map_two}')
        raw_data = raw_map.data
        predicated_contour_raw_map = calc_level_dev(raw_data)[0]
        raw_map_surface = MapProcessor.compute_surface_area(f'{map_two}', predicated_contour_raw_map)

        surface_ratio_before_masking = keep_three_significant_digits(raw_map_surface / primary_map_surface)
        return surface_ratio_before_masking


    @staticmethod
    def low_pass_filter(mrcdata, low_pass, voxel_size, filter_edge_width=0.2):
        """
            Apply low-pass filter to a 2D or 3D image (map) in Fourier space
        while maintaining original dimensions.

        Parameters:
        -----------
        img : ndarray
            Input image/map (2D or 3D numpy array)
        low_pass : float
            Low-pass filter resolution in Angstroms
        angpix : float
            Pixel size in Angstroms
        filter_edge_width : int, optional
            Width of the filter edge (default: 2)

        Returns:
        --------
        ndarray
            Low-pass filtered image/map with original dimensions
        """

        shape = mrcdata.shape
        ndim = mrcdata.ndim
        # Calculate frequency grid in physical units (1/Å)
        freq_arrays = []
        for i, size in enumerate(shape):
            # Create frequency array for this dimension
            freq = fftfreq(size) / voxel_size  # Convert to 1/Å
            # Reshape for broadcasting
            new_shape = [1] * ndim
            new_shape[i] = size
            freq_arrays.append(freq.reshape(new_shape))

        # Create n-dimensional frequency grid
        freq_grid = np.sqrt(sum(f ** 2 for f in freq_arrays))

        # Create low-pass filter
        cutoff = 1.0 / low_pass  # Convert resolution to frequency cutoff

        # Gaussian filter with smooth transition
        # filter_mask = np.exp(-(freq_grid / cutoff) ** 2)

        # Convert resolution to sigma in frequency space
        # The factor of 2 accounts for Gaussian -> resolution relationship
        sigma_freq = cutoff / (2 * np.sqrt(2 * np.log(2)))
        sigma_freq *= (1 + filter_edge_width)  # Adjust for requested edge width
        filter_mask = np.exp(-(freq_grid ** 2) / (2 * sigma_freq ** 2))
        ft = fftn(mrcdata)
        filtered_ft = ft * filter_mask
        filtered_mrcdata = np.real(ifftn(filtered_ft))
        if np.all(filtered_mrcdata <= 0):
            filtered_mrcdata = (filtered_mrcdata - filtered_mrcdata.min()) / (filtered_mrcdata.max() - filtered_mrcdata.min())

        return filtered_mrcdata

    @staticmethod
    def low_pass_filter_map(mrc_file, low_pass, output_filename, filter_edge_width=0.2):
        """
            Apply low-pass filter to the map in Fourier space while maintaining original dimensions.

        Parameters:
        -----------
        low_pass : float
            Low-pass filter resolution in Angstroms
        filter_edge_width : int, optional
            Width of the filter edge (default: 2)

        Returns:
        --------
        ndarray
            Low-pass filtered map with original dimensions
        """

        try:
            mrc_data = mrc_file.data
            voxel_size = mrc_file.voxel_size.x
            filtered_data = MapProcessor.low_pass_filter(mrc_data, low_pass, voxel_size, filter_edge_width)
            with mrcfile.new(output_filename, overwrite=True) as mrc:
                mrc.set_data(filtered_data.astype(np.float32))
                if isinstance(voxel_size, (float, int)):
                    mrc.voxel_size = voxel_size
                else:
                    mrc.voxel_size = tuple([voxel_size] * mrc_data.ndim)

            return output_filename
        except Exception as e:
            print(f'Error: {e}')
            return None

    @staticmethod
    def low_pass_filter_relion(mrc_file, low_pass, output_filename):
        """
            Apply low-pass filter to the map in Fourier space while maintaining original dimensions.
        Parameters:
        -----------
        low_pass : float
            Low-pass filter resolution in Angstroms
        """
        # Check if relion_image_handler executable exists
        if not shutil.which('relion_image_handler'):
            print('Error: relion_image_handler executable not found.')
            return None

        # Construct the command
        cmd = [
            'relion_image_handler',
            '--i', mrc_file,
            '--o', output_filename,
            '--lowpass', str(low_pass)
        ]
        print(f'Relion low pass filter command: {cmd}')

        try:
            # Run the command
            subprocess.run(cmd, check=True)
            return output_filename
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}')
            return None