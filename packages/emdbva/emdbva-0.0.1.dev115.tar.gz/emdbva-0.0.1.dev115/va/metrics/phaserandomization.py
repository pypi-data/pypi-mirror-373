from va.utils.ChimeraxViews import *
from va.utils.misc import find_rawmap_file
import numpy as np
import mrcfile
import argparse
from math import sqrt, cos, pi
from scipy.ndimage import distance_transform_edt
from tqdm import tqdm

def create_relion_folders(root, mapname, result_type=None):
    """
        Create <mapname>_relion folder in the va directory and subfolders containing mask, fsc and local_resolution
    """
    relion_dir = f'{root}{mapname}_relion'
    mask_dir = f'{relion_dir}/mask'
    fsc_dir = f'{relion_dir}/fsc'
    local_resolution_dir = f'{relion_dir}/local_resolution'

    if create_directory(relion_dir) and create_directory(mask_dir):
        print('Relion folder and mask folder created.')
        if result_type == 'fsc':
            if create_directory(fsc_dir):
                print('FSC folder created.')
                return fsc_dir, mask_dir
            else:
                print('FSC folder was not created. Please check.')
                return None, None

        if result_type == 'locres':
            if create_directory(local_resolution_dir):
                print('Local resolution folder created.')
                return local_resolution_dir, mask_dir
            else:
                print('Local resolution folder was not created. Please check.')
                return None, None
        print('Check the input folder type either fsc or locres.')
        return None, None
    else:
        print('Relion folder and mask folder was not created. Please check')
        return None, None


def check_mrc(input_map):
    """
    Check if the input map is in MRC format. If not, create a symbolic link in the same folder ends with mrc
    """

    suffix = '.mrc'
    if not input_map.endswith('.mrc'):
        last_dot_index = input_map.rfind('.')
        mrc_input_map = input_map[:last_dot_index] + suffix
        if create_symbolic_link(input_map, mrc_input_map):
            return mrc_input_map
    else:
        print('MRC file format.')
        return input_map

def relion_mask(raw_map, out_dir, mapname=None):
    relion_mask_executable_name = 'relion_mask_create'
    relion_mask_executable = find_executable(relion_mask_executable_name)
    if relion_mask_executable:
        original_input_mrc = check_mrc(raw_map)
        angpix = get_voxel_size(raw_map)
        input_mrc = mrcfile.open(original_input_mrc)
        d = input_mrc.data
        max_val_thirty = f'{calc_level_dev(d)[0]}'

        dilatepx, softpx = calculate_pixels(angpix)
        mask_loose = os.path.join(out_dir, f'{mapname}_mask.mrc')

        threading_numbers = int(os.cpu_count() * 0.8)
        relion_mask_cmd = (f'{relion_mask_executable} --i {original_input_mrc} --o {mask_loose} --ini_threshold '
                           f'{max_val_thirty} --extend_inimask {dilatepx} --width_soft_edge '
                           f'{softpx} --j {threading_numbers}')
        print(f'Relion mask command: {relion_mask_cmd}')
        # Produce my own mask to compare with relion mask and time
        try:
            ownmask_loose = os.path.join(out_dir, f'{mapname}_ownmask.mrc')
            relion_auto_mask(original_input_mrc, ownmask_loose, float(max_val_thirty), dilatepx, softpx)
            print(f'Relion auto mask command: {relion_auto_mask.__name__}')
        except Exception as e:
            print(f'Own mask failed: {e}')
            ownmask_loose = None

        if angpix and max_val_thirty and dilatepx and softpx and input_mrc:
            subprocess.run(relion_mask_cmd, shell=True)
            if not MapProcessor.check_map_starts(mask_loose, original_input_mrc):
                print('Relion mask does not have the same nstarts as the original map.')
                MapProcessor.update_map_starts(original_input_mrc, mask_loose)

            return mask_loose
        else:
            print(f'!!! Check the cmd: {relion_mask_cmd}')
            return None
    else:
        print('Relion mask executable is not found.')


def relion_fsc(mapone, maptwo, mask_file=None, out_dir=None):
    """
    Relion FSC calculation running
    """
    if out_dir is None:
        out_dir = os.getcwd()
    relion_executable_name = 'relion_postprocess'
    relion_postprocess_executable = find_executable(relion_executable_name)
    mapone_mrc = check_mrc(mapone)
    maptwo_mrc = check_mrc(maptwo)
    halfmap_exists = mapone_mrc and maptwo_mrc
    if halfmap_exists and relion_postprocess_executable:
        if os.path.isfile(mask_file or ''):

            subprocess.run(f"{relion_postprocess_executable} --i {mapone_mrc} --i2 {maptwo_mrc} --o {out_dir}/fsc"
                               f" --mask {mask_file} --auto_bfac", shell=True, check=True)
            print(
                f'FSC cmd: {relion_postprocess_executable} --i {mapone_mrc} --i2 {maptwo_mrc} --o {out_dir}/fsc '
                f'--mask {mask_file} --auto_bfac", shell=True)')

            return True
        else:
            print('No mask applied for FSC calculation.')
            print(
                f'!!! Check the cmd: {relion_postprocess_executable} --i {mapone_mrc} --i2 {maptwo_mrc} --o {out_dir}/fsc --auto_bfac')
            subprocess.run(f"{relion_postprocess_executable} --i {mapone_mrc} --i2 {maptwo_mrc} --o {out_dir}/fsc --auto_bfac",
                           shell=True, check=True)


            return True
    else:
        print('Relion postprocess executable is not found or half maps missing/error.')
        print(f'!!! Check the cmd: f"{relion_postprocess_executable} --i {mapone_mrc} --i2 {maptwo_mrc} --o {out_dir}/fsc '
              f'--mask {mask_file} --auto_bfac", shell=True)"')
        return None


def relion_fsc_calculation(mapone, maptwo, root, mapname=None):
    """
        Calculates FSc using Relion
    return: data dictionary of fsc
    """

    result_type = 'fsc'
    if not mapname:
        mapname = f'{os.path.basename(mapone)}_{os.path.basename(maptwo)}'
    fsc_dir, mask_dir = create_relion_folders(root, mapname, result_type)

    try:
        if fsc_dir and mask_dir:
            raw_map_name = find_rawmap_file(root)
            filtered_raw_map = f'{root}{raw_map_name}_lowpassed.mrc'
            relion_mask_name = os.path.join(mask_dir, f'{mapname}_mask.mrc')
            if not os.path.isfile(filtered_raw_map):
                relion_mask_name = relion_mask(filtered_raw_map, mask_dir, mapname)
            relion_fsc_result = relion_fsc(mapone, maptwo, relion_mask_name, fsc_dir)
            if relion_fsc_result:
                return f'{fsc_dir}/fsc.star'
            else:
                return None

    except Exception as e:
        print('No relion or fsc calculation was wrong.')
        return None

def get_voxel_size(input_map):

    try:
        with mrcfile.open(input_map, permissive=True) as mrc:
            voxel_size = mrc.voxel_size

            return float(voxel_size['x'])
    except Exception as e:
        print('No voxel size of the map.')
        return None


def calculate_pixels(angpix):
    """
    Calculate hard and soft pixel for mask map
    """

    if angpix != 0:
        dilatepx = 10 / angpix
        softpx = 5 / angpix
        return dilatepx, softpx
    else:
        print('No hard and soft radius for mask as voxel value is 0.')
        return None, None


# following is the Python version of Relion auto masking
def relion_auto_mask_fast(data, threshold, extend_pixels, edge_width, verbose=True):
    steps = []
    if verbose:
        steps = tqdm(total=3, desc="Masking Steps", unit="step")

    # Step 1: Initial binary mask
    mask = (data >= threshold).astype(np.float32)
    if verbose:
        tqdm.write("== Initial binary mask created ==")
        steps.update(1)

    # Step 2: Extend or shrink mask
    if extend_pixels != 0:
        if verbose:
            tqdm.write(f"== {'Extending' if extend_pixels > 0 else 'Shrinking'} mask by {extend_pixels} pixels ==")
        distance = distance_transform_edt(mask < 0.5 if extend_pixels > 0 else mask > 0.5)
        if extend_pixels > 0:
            mask[(mask < 0.5) & (distance <= extend_pixels)] = 1.0
        else:
            mask[(mask > 0.5) & (distance <= abs(extend_pixels))] = 0.0
        if verbose:
            steps.update(1)

    else:
        if verbose:
            steps.update(1)  # Skip if no extend

    # Step 3: Apply soft edge
    if edge_width > 0:
        if verbose:
            tqdm.write(f"== Applying soft edge with width {edge_width} pixels ==")
        edge_distance = distance_transform_edt(mask < 0.5)
        edge_zone = (mask < 0.5) & (edge_distance < edge_width)
        mask[edge_zone] = 0.5 + 0.5 * np.cos(pi * edge_distance[edge_zone] / edge_width)
        if verbose:
            steps.update(1)
    else:
        if verbose:
            steps.update(1)  # Skip if no soft edge

    if verbose:
        steps.close()

    return mask.astype(np.float32)

def relion_auto_mask(input_file, output_file, threshold, extend_pixels, edge_width, verbose=True):
    with mrcfile.open(input_file) as mrc:
        data = mrc.data.copy()
        voxel_size = mrc.voxel_size.copy()

    mask = relion_auto_mask_fast(data, threshold, extend_pixels, edge_width, verbose)

    with mrcfile.new(output_file, overwrite=True) as mrc:
        mrc.set_data(mask)
        mrc.voxel_size = voxel_size  # retain voxel size from input

    if verbose:
        print(f"== Mask saved to {output_file} ==")

