import subprocess
from va.utils.MapProcessor import MapProcessor
import sys
from distutils.spawn import find_executable
import numpy as np
import mrcfile
from PIL import Image, ImageSequence
import glob
import json
import codecs
from va.utils.misc import *

import matplotlib.pyplot as plt


def run_locres(mapone, maptwo, output_path, resmappy_path=None):
    errlist = []
    try:
        bindisplay = os.getenv('DISPLAY')
        mapone_name = os.path.basename(mapone)
        maptwo_name = os.path.basename(maptwo)
        locres_map = f'{output_path}/{mapone_name}_{maptwo_name}'
        one_linkname = mapone_name[:-2] + 'rc'
        two_linkname = maptwo_name[:-2] + 'rc'
        run_mapone_name = create_symbolic_link(mapone, one_linkname)
        run_maptwo_name = create_symbolic_link(maptwo, two_linkname)
        if bindisplay:
            assert find_executable('relion_postprocess') is not None
            respath = find_executable('relion_postprocess')
            resmap_cmd = '{} --i {} --i2 {} --o {} --locres --locres_sampling 30'.format( respath, run_mapone_name, run_maptwo_name, locres_map)
            print(resmap_cmd)
        else:
            if resmappy_path == None:
                raise Exception('No ResMap.py path provided.')
            else:
                resmap_cmd = '{} --i {} --i2 {} --o {} --locres --locres_sampling 30'.format( resmappy_path, run_mapone_name, run_maptwo_name, locres_map)
                print(resmap_cmd)
        create_directory(output_path)
        try:
            process = subprocess.Popen(resmap_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       cwd=output_path)
            output = process.communicate('n\n')[0]
            errqscore = 'error'
            for item in output.decode('utf-8').split('\n') if sys.version_info[0] >= 3 else output.split('\n'):
                print(item)
                if errqscore in item.lower():
                    errline = item.strip()
                    errlist.append(errline)
                    assert errqscore not in output.decode('utf-8'), errline

            # if sys.version_info[0] >= 3:
            #     for item in output.decode('utf-8').split('\n'):
            #         # item = cline.decode('utf-8').strip()
            #         print(item)
            #         if errqscore in item.lower():
            #             errline = item.strip()
            #             errlist.append(errline)
            #             assert errqscore not in output.decode('utf-8'), errline
            #
            # else:
            #     for item in output.split('\n'):
            #         print(item)
            #         if errqscore in item.lower():
            #             errline = item.strip()
            #             errlist.append(errline)
            #             assert errqscore not in output.decode('utf-8'), errline
            output_locres_file = f'{locres_map}_locres.mrc'
            if not MapProcessor.check_map_starts(output_locres_file, mapone):
                print('Relion mask does not have the same nstarts as the original map.')
                MapProcessor.update_map_starts(mapone, output_locres_file)
        except subprocess.CalledProcessError as suberr:
            err = 'Local resolution from Relion calculation error: {}.'.format(suberr)
            errlist.append(err)
            sys.stderr.write(err + '\n')
    except AssertionError as exerr:
        err = 'Relion executable is not there.'
        errlist.append(err)
        sys.stderr.write('Relion executable is not there: {}\n'.format(exerr))

    return errlist


def locres_filecheck(mapone, maptwo, output_path):
    """
        Check if all output from ResMap are ready
    :return: True(all file exist) or False (not all file exist
    """

    output_path = output_path
    mapname_one = os.path.basename(mapone)
    mapname_two = os.path.basename(maptwo)
    starfile = '{}/{}_{}_locres_fscs.star'.format(output_path, mapname_one, mapname_two)
    locres_name = '{}/{}_{}_locres.mrc'.format(output_path, mapname_one, mapname_two)
    locres_filtered = '{}/{}_{}_locres_filtered.mrc'.format(output_path, mapname_one, mapname_two)
    check = os.path.isfile(starfile) and os.path.isfile(locres_name) and os.path.isfile(locres_filtered)

    return check if check else False


def run_resmap(mapone, maptwo, output_path, resmappy_path=None):
    errlist = []
    try:
        bindisplay = os.getenv('DISPLAY')
        if bindisplay:
            assert find_executable('ResMap') is not None
            respath = find_executable('ResMap')
            resmap_cmd = '{} {} {} --noguiSplit --doBenchMarking'.format(respath, mapone, maptwo)
            print(resmap_cmd)
        else:
            if resmappy_path == None:
                raise Exception('No ResMap.py path provided.')
            else:
                resmap_cmd = '{} {} {} {} --noguiSplit --doBenchMarking'.format('python', resmappy_path, mapone, maptwo)
                print(resmap_cmd)
        create_folder(output_path)
        try:
            process = subprocess.Popen(resmap_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       cwd=output_path)
            output = process.communicate('n\n')[0]
            errqscore = 'error'
            if sys.version_info[0] >= 3:
                for item in output.decode('utf-8').split('\n'):
                    # item = cline.decode('utf-8').strip()
                    print(item)
                    if errqscore in item.lower():
                        errline = item.strip()
                        errlist.append(errline)
                        assert errqscore not in output.decode('utf-8'), errline

            else:
                for item in output.split('\n'):
                    print(item)
                    if errqscore in item.lower():
                        errline = item.strip()
                        errlist.append(errline)
                        assert errqscore not in output.decode('utf-8'), errline
        except subprocess.CalledProcessError as suberr:
            err = 'Local resolution from ResMap calculation error: {}.'.format(suberr)
            errlist.append(err)
            sys.stderr.write(err + '\n')
    except AssertionError as exerr:
        err = 'ResMap executable is not there.'
        errlist.append(err)
        sys.stderr.write('ResMap executable is not there: {}\n'.format(exerr))

    return errlist

def resmap_filecheck(mapone, output_path):
    """
        Check if all output from ResMap are ready
    :return: True(all file exist) or False (not all file exist
    """

    output_path = output_path
    mapname = os.path.basename(mapone)
    mapfile = '{}{}_ori.map'.format(output_path, os.path.splitext(mapname)[0])
    resmapname = '{}{}_ori_resmap.map'.format(output_path, os.path.splitext(mapname)[0])
    resmap_chimera = '{}{}_ori_resmap_chimera.cmd'.format(output_path, os.path.splitext(mapname)[0])
    check = os.path.isfile(mapfile) and os.path.isfile(resmapname) and os.path.isfile(resmap_chimera)

    return check if check else False


def resmap_chimerax(mapone, output_path):
    """
        Generate chimerax cmd for ResMap results
    :return:
    """

    mapname = os.path.basename(mapone)
    output_chimerax_file = '{}{}_chimerax.cxc'.format(output_path, os.path.basename(mapone))
    orgmap = '{}{}_ori.map'.format(output_path, os.path.splitext(mapname)[0])
    resmap = '{}{}_ori_resmap.map'.format(output_path, os.path.splitext(mapname)[0])
    header = mrcfile.open(mapone, mode='r', header_only=True)
    voxsizes = header.voxel_size.tolist()
    if all(element == voxsizes[0] for element in voxsizes):
        voxsize = voxsizes[0]
        mmin = round((2.2 * voxsize) / 0.1) * 0.1  # round to the nearest 0.1
        mmax = round((4.0 * voxsize) / 0.5) * 0.5  # round to the nearest 0.5
    else:
        voxsizemin = voxsizes.min()
        voxsizemax = voxsizes.max()
        mmin = round((2.2 * voxsizemin) / 0.1) * 0.1  # round to the nearest 0.1
        mmax = round((4.0 * voxsizemax) / 0.5) * 0.5  # round to the nearest 0.5
        print('Voxel sizes are not the same!!!')

    n = header.header.nx
    colors_chimerax = ['blue', 'cyan', 'green', 'yellow', 'orange', 'red']
    values_chimerax = np.linspace(mmin, mmax, len(colors_chimerax))
    colorstr = ''
    for i in range(len(colors_chimerax)):
        colorstr += '%.2f' % values_chimerax[i] + ',' + colors_chimerax[i] + ':'
    colorstr += '%.2f' % (values_chimerax[i] + 0.01) + ',' + 'gray'
    with open(output_chimerax_file, 'w') as fp:
        fp.write("windowsize 800 800\n")
        fp.write("set bg_color white\n")
        fp.write("open " + orgmap + " format ccp4" + '\n')
        fp.write("open " + resmap + " format ccp4" + '\n')
        fp.write("volume #2 hide\n")
        fp.write("color sample #1 map #2 palette " + colorstr + '\n')
        fp.write("volume #1 planes z,0 step 1 level -1 style surface\n")
        # non-perspective mode is not working with Chimerax 1.6 on headless machine
        # fp.write("camera ortho\n")
        fp.write("zoom 1.3\n")
        fp.write("view cofr True\n")
        # fp.write("camera ortho\n")
        fp.write('2dlabels text "0" xpos 0.8 ypos 0.1\n')
        # fp.write("vop gaussian #1 sDev 5 model #3")
        # fp.write("volume #3 level 0.02 step 1 color rgba(0%, 80%, 40%, 0.5)")
        # fp.write("volume #3 level 0.02 step 1 color 60,0,80,50")
        # fp.write("zoom 0.5")
        fp.write("movie record size 800,800\n")
        # fp.write('perframe "volume #1 plane z,$1" range 198,0')
        fp.write('perframe "volume #1 plane z,$1 ; 2dlabel #3.1 text $1" range 0,{},2\n'.format(n))
        fp.write("wait {}\n".format(str(round(n/2) + 2)))
        fp.write("movie encode {}_zplanes_noloop.png quality high\n\n\n\n".format(resmap))

        # X
        fp.write("close session\n")
        fp.write("set bg_color white\n")
        fp.write("open " + orgmap + " format ccp4" + '\n')
        fp.write("open " + resmap + " format ccp4" + '\n')
        fp.write("volume #2 hide\n")
        fp.write("color sample #1 map #2 palette " + colorstr + '\n')
        fp.write("turn -x 90\n")
        fp.write("turn -y 90\n")
        fp.write("volume #1 planes x,0 step 1 level -1 style surface\n")
        # fp.write("camera ortho\n")
        fp.write("zoom 1.3\n")
        fp.write("view cofr True\n")
        # fp.write("view orient\n")
        # non-perspective mode is not working with Chimerax 1.6 on headless machine
        # fp.write("camera ortho\n")
        fp.write('2dlabels text "0" xpos 0.8 ypos 0.1\n')
        # fp.write("vop gaussian #1 sDev 5 model #3")
        # fp.write("volume #3 level 0.02 step 1 color rgba(0%, 80%, 40%, 0.5)")
        # fp.write("volume #3 level 0.02 step 1 color 60,0,80,50")
        # fp.write("zoom 0.5")
        fp.write("movie record size 800,800\n")
        # fp.write('perframe "volume #1 plane z,$1" range 198,0')
        fp.write('perframe "volume #1 plane x,$1 ; 2dlabel #3.1 text $1" range 0,{},2\n'.format(n))
        fp.write("wait {}\n".format(str(round(n/2) + 2)))
        fp.write("movie encode {}_xplanes_noloop.png quality high\n".format(resmap))

        # Y
        fp.write("close session\n")
        fp.write("set bg_color white\n")
        fp.write("open " + orgmap + " format ccp4" + '\n')
        fp.write("open " + resmap + " format ccp4" + '\n')
        fp.write("volume #2 hide\n")
        fp.write("color sample #1 map #2 palette " + colorstr + '\n')
        fp.write("turn x 90\n")
        fp.write("turn z 90\n")
        fp.write("volume #1 planes y,0 step 1 level -1 style surface\n")
        # non-perspective mode is not working with Chimerax 1.6 on headless machine
        # fp.write("camera ortho\n")
        fp.write("zoom 1.3\n")
        fp.write("view cofr True\n")
        # fp.write("view orient\n")
        # fp.write("camera ortho\n")
        fp.write('2dlabels text "0" xpos 0.8 ypos 0.1\n')
        # fp.write("vop gaussian #1 sDev 5 model #3")
        # fp.write("volume #3 level 0.02 step 1 color rgba(0%, 80%, 40%, 0.5)")
        # fp.write("volume #3 level 0.02 step 1 color 60,0,80,50")
        # fp.write("zoom 0.5")
        fp.write("movie record size 800,800\n")
        # fp.write('perframe "volume #1 plane z,$1" range 198,0')
        fp.write('perframe "volume #1 plane y,$1 ; 2dlabel #3.1 text $1" range 0,{},2\n'.format(n))
        fp.write("wait {}\n".format(str(round(n/2) + 2)))
        fp.write("movie encode {}_yplanes_noloop.png quality high\n".format(resmap))
        fp.write('close all\n')
        fp.write('exit')
        fp.close()

        return output_chimerax_file

def run_resmap_chimerax(bindisplay, locCHIMERA, cxcfile):
    """

    :return:
    """
    errlist = []
    try:
        if not bindisplay:
            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + cxcfile, cwd=os.path.dirname(cxcfile),
                                  shell=True)
            print('Animated PNG for ResMap result has been produced.')
        else:
            subprocess.check_call(locCHIMERA + " " + cxcfile, cwd=os.path.dirname(cxcfile), shell=True)
            print('Animated PNG for ResMap result has been produced.')
    except subprocess.CalledProcessError as suberr:
        err = 'Saving ResMap local resolution animated png error: {}.'.format(suberr)
        errlist.append(err)
        sys.stderr.write(err + '\n')

    return errlist

def save_imagestojson(resmapname, output_filename):
    """

    :return:
    """
    basename = os.path.basename(resmapname)
    x_local = '{}_xplanes_noloop.png'.format(resmapname)
    y_local = '{}_yplanes_noloop.png'.format(resmapname)
    z_local = '{}_zplanes_noloop.png'.format(resmapname)
    x_localo = '{}_xplanes.png'.format(resmapname)
    y_localo = '{}_yplanes.png'.format(resmapname)
    z_localo = '{}_zplanes.png'.format(resmapname)
    make_apng_looping(x_local, x_localo)
    make_apng_looping(y_local, y_localo)
    make_apng_looping(z_local, z_localo)
    org_xyz_pngs = os.path.isfile(x_local) and os.path.isfile(y_local) and os.path.isfile(z_local)
    org_xyz_pngs_scaled = False
    if org_xyz_pngs:
        x_local_scaled = '{}_scaled_xplanes.png'.format(resmapname)
        y_local_scaled = '{}_scaled_yplanes.png'.format(resmapname)
        z_local_scaled = '{}_scaled_zplanes.png'.format(resmapname)
        size = (300,300)
        resize_apng(x_localo, x_local_scaled, size)
        resize_apng(y_localo, y_local_scaled, size)
        resize_apng(z_localo, z_local_scaled, size)
        org_xyz_pngs_scaled = os.path.isfile(x_local_scaled) and os.path.isfile(y_local_scaled) and \
                              os.path.isfile(z_local_scaled)

    if org_xyz_pngs and org_xyz_pngs_scaled:
        result_dict = {'local_resolution': {'ResMap': {'original': {'x': os.path.basename(x_local),
                                                                    'y': os.path.basename(y_local),
                                                                    'z': os.path.basename(z_local)}},
                                                        'scaled': {'x': os.path.basename(x_local_scaled),
                                                                   'y': os.path.basename(y_local_scaled),
                                                                   'z': os.path.basename(z_local_scaled)}}}
        try:
            with codecs.open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f)
        except:
            sys.stderr.write(
                'Saving ResMap view to JSON error: {}.\n'.format(sys.exc_info()[1]))
    else:
        print('Missing ResMap result images.')


def make_apng_looping(input_file, output_file):
    """
        Chimerax give animated png for 1 loop need to change to 0 make a infinite loop
    :param input_file:
    :param output_file:
    :return:
    """

    image = Image.open(input_file)
    if image.info['loop'] != 0:
        image.info['loop'] = 0
    image.save(output_file, save_all=True)


def resize_apng(input_file, output_file, size):
    # Open the APNG file
    input_apng = Image.open(input_file)

    # Create a list to store resized frames
    resized_frames = []

    # Iterate over each frame of the APNG
    for frame in ImageSequence.Iterator(input_apng):
        # Resize the frame's image
        resized_image = frame.copy().resize(size, Image.Resampling.LANCZOS)
        resized_frames.append(resized_image)

    # Save the resized frames as an APNG
    resized_frames[0].save(output_file, save_all=True, append_images=resized_frames[1:], optimize=False,
                           duration=input_apng.info.get('duration', 100), loop=input_apng.info.get('loop', 0))


def get_masked_indices(input_mask):

    try:
        masked_map = mrcfile.open(input_mask)
        masked_map_data = masked_map.data > 0.5
        # masked_map_indices = np.argwhere(masked_map_data > 0.5)

        return masked_map_data
    except Exception as e:
        sys.stderr.write('Error in reading masked map: {}.\n'.format(e))
        return None


def localres_histogram(mapone, primary_mapname, resolution=None):
    """
        local resolution histogram
    """

    mapname = os.path.basename(mapone)
    output_path = os.path.dirname(mapone)
    file_pattern = '{}/{}_relion/*_locres.mrc'.format(output_path, primary_mapname)
    resmapname_glob = glob.glob(file_pattern)
    resmapname = resmapname_glob[0] if len(resmapname_glob) > 0 else None
    mask_file = f'{output_path}/{primary_mapname}_relion/mask/{primary_mapname}_mask.mrc'
    bin_mask = get_masked_indices(mask_file)
    final_dict = {}
    unmasked_localres = {}
    masked_localres = {}

    if resmapname and os.path.isfile(resmapname):
        with mrcfile.open(resmapname, permissive=True) as inmap:
            map_data = inmap.data[inmap.data != 0]
            tmasked_map_data = inmap.data*bin_mask
            masked_map_data = tmasked_map_data[tmasked_map_data != 0]
            hist, bin_edges = np.histogram(map_data, bins=50)
            masked_hist, masked_bin_edges = np.histogram(masked_map_data, bins=50)

            unmasked_localres['values'] = bin_edges.tolist()
            unmasked_localres['counts'] = hist.tolist()
            unmasked_localres['minmax'] = {'min': keep_three_significant_digits(min(bin_edges).astype(float)),
                                       'max': keep_three_significant_digits(max(bin_edges).astype(float))}
            masked_localres['values'] = masked_bin_edges.tolist()
            masked_localres['counts'] = masked_hist.tolist()
            masked_localres['minmax'] = {'min': keep_three_significant_digits(min(masked_bin_edges).astype(float)),
                                           'max': keep_three_significant_digits(max(masked_bin_edges).astype(float))}

            # Plot the histogram
            plt.figure(figsize=(8, 6))
            plt.hist(map_data, bins=50, color='green', edgecolor='black')
            plt.hist(masked_map_data, bins=50, color='orange', edgecolor='black')
            final_dict['masked'] = masked_localres
            final_dict['unmasked'] = unmasked_localres

            if resolution:
                vertical_lines = [resolution]  # Example vertical lines at x=3 and x=5
                for line in vertical_lines:
                    plt.axvline(x=line, color='red', linestyle='solid', linewidth=2)
                    plt.text(line, plt.ylim()[1] - 0.038 * (plt.ylim()[1] - plt.ylim()[0]), f' Claimed resolution={line} Å', color='red', va='bottom', ha='left')

            plt.ylabel('Voxel counts')
            plt.xlabel('Local resolution ')

            localres_histogram_plot = '{}/{}_localres_histogram.png'.format(output_path, primary_mapname)
            # Save the plot
            plt.savefig(localres_histogram_plot)

    return final_dict



