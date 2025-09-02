import os
import sys
import timeit
import json
import codecs
import cv2
import numpy as np
from math import ceil
from scipy import ndimage
from mrcfile.mrcfile import MrcFile
import inspect
from va.utils.misc import out_json

class Projections:
    def __init__(self, primary_map, rawmap=None, workdir=None, platform=None):
        self.map = primary_map
        self.rawmap = rawmap
        self.workdir = workdir
        self.platform = platform
        self.errlist = []

    def mapincheck(self, mapin, workdirin):
        frame = inspect.currentframe()
        func = inspect.getframeinfo(frame.f_back).function
        map, workdir = None, None

        if mapin is not None:
            if isinstance(mapin, str):
                if os.path.isfile(mapin):
                    map = MrcFile(mapin, mode='r')
                    map.fullname = mapin
                else:
                    print('Map does not exist.')
            elif isinstance(mapin, MrcFile):
                map = mapin
            else:
                print(f'Function:{func} only accepts a string of the full map name or a TEMPy Map object as input.')

        if workdirin is not None:
            if isinstance(workdirin, str):
                if os.path.isdir(workdirin):
                    workdir = workdirin
                else:
                    print('Output directory does not exist.')
            else:
                print(f'Function:{func} only accepts a string as the directory parameter.')

        return map, workdir

    def resize_img(self, input_arr, output_img):
        height, width = input_arr.shape[0:2]
        if width >= height:
            largerscaler = 300. / width
            newheight = int(ceil(largerscaler * height))
            resized_img = cv2.resize(input_arr, (300, newheight), interpolation=cv2.INTER_LANCZOS4)
        else:
            largerscaler = 300. / height
            newwidth = int(ceil(largerscaler * width))
            resized_img = cv2.resize(input_arr, (newwidth, 300), interpolation=cv2.INTER_LANCZOS4)

        cv2.imwrite(output_img, resized_img)

    def scale_img(self, projection):
        onevalue = True if projection.min() == projection.max() else False
        if onevalue:
            rescaled = np.full((projection.shape), 0.0).astype('uint8')
        else:
            rescaled = (((projection - projection.min()) * 255.0) / (projection.max() - projection.min())).astype('uint8')
        return rescaled

    def get_projection(self, map, type, axis):
        mapdata = map.data
        ind = None
        if type == 'projection':
            projection = np.sum(mapdata, axis=axis)
        elif type == 'max':
            projection = np.amax(mapdata, axis=axis)
        elif type == 'min':
            projection = np.amin(mapdata, axis=axis)
        elif type == 'std':
            projection = np.std(mapdata, axis=axis)
        elif type == 'median':
            projection = np.median(mapdata, axis=axis)
        elif type == 'central':
            projection = map.data[:, :, int(map.header.nx / 2)] if axis == 2 else \
                         map.data[:, int(map.header.ny / 2), :] if axis == 1 else \
                         map.data[int(map.header.nz / 2), :, :] if axis == 0 else None
            if axis == 2:
                ind = {'x': int(map.header.nx / 2)}
            elif axis == 1:
                ind = {'y': int(map.header.ny / 2)}
            elif axis == 0:
                ind = {'z': int(map.header.nz / 2)}
            else:
                ind = None

        elif type == 'largestvariance':
            if axis == 2:
                xvar = [ndimage.variance(map.data[:, :, i]) for i in range(map.data.shape[2])]
                xlargeind = int(np.argmax(xvar))
                ind = {'x': xlargeind}
                projection = map.data[:, :, xlargeind]
            elif axis == 1:
                yvar = [ndimage.variance(map.data[:, i, :]) for i in range(map.data.shape[1])]
                ylargeind = int(np.argmax(yvar))
                ind = {'y': ylargeind}
                projection = map.data[:, ylargeind, :]
            elif axis == 0:
                zvar = [ndimage.variance(map.data[i, :, :]) for i in range(map.data.shape[0])]
                zlargeind = int(np.argmax(zvar))
                ind = {'z': zlargeind}
                projection = map.data[zlargeind, :, :]
            else:
                projection = None
        else:
            projection = None
            print('Wrong type. Use one of: projection, max, min, std, median, central, largestvariance.')
        return projection, ind


    def output_filename(self, axis_letter, mapname, type, proc_fun=None):
        if proc_fun:
            suffix = 'glow_' if proc_fun == self.glowimage else ''
        else:
            suffix = ''

        if type == 'central' or type == 'largestvariance':
            output_name = f'{self.workdir}{mapname}_{axis_letter}{type}_slice.jpeg'
            scaled_output_name = f'{self.workdir}{mapname}_scaled_{axis_letter}{type}_slice.jpeg'
        else:
            output_name = f'{self.workdir}{mapname}_{suffix}{axis_letter}{type}.jpeg'
            scaled_output_name = f'{self.workdir}{mapname}_scaled_{suffix}{axis_letter}{type}.jpeg'

        return output_name, scaled_output_name

    def save_scale(self, reposition, output_name, scaled_output_name, errlist):

        try:
            cv2.imwrite(output_name, reposition)
        except IOError as ioerr:
            err = f'Saving {output_name} projection err: {ioerr}'
            errlist.append(err)
            sys.stderr.write(err + '\n')

        try:
            self.resize_img(reposition, scaled_output_name)
        except Exception as e:
            err = f'Saving scaled {scaled_output_name} image err: {e}'
            errlist.append(err)
            sys.stderr.write(err + '\n')

    def map_to_img(self, map, axis, type, errlist, proc_fun=None):
        projection, ind = self.get_projection(map, type, axis)
        org = {}
        scale = {}
        if projection is not None:
            rescaled = self.scale_img(projection)
            if axis == 2:
                reposition = np.flipud(rescaled)
                axis_letter = 'x'
            elif axis == 1:
                reposition = np.rot90(rescaled)
                axis_letter = 'y'
            elif axis == 0:
                reposition = np.flipud(rescaled)
                axis_letter = 'z'
            else:
                return None

            mapname = os.path.basename(map.fullname)
            output_name, scaled_output_name = self.output_filename(axis_letter, mapname, type, proc_fun)
            org[axis_letter] = os.path.basename(output_name)
            scale[axis_letter] = os.path.basename(scaled_output_name)

            self.save_scale(reposition, output_name, scaled_output_name, errlist)
            if proc_fun:
                glowimage = proc_fun(reposition)
                self.save_scale(glowimage, output_name, scaled_output_name, errlist)

        return ind, org, scale

    def orthogonal_projections(self, mapin=None, workdir=None, type=None, label=''):
        map, workdir = self.mapincheck(mapin, workdir)
        if map is not None and workdir is not None:
            start = timeit.default_timer()
            self.errlist = []
            mapname = os.path.basename(map.fullname)
            if not type:
                types = ['projection', 'max', 'min', 'std', 'median', 'central', 'largestvariance']
            else:
                types = [type]
            result_dict = {}
            for type in types:
                ind_result = {}
                org_result = {}
                scale_result = {}
                final_org = {}
                final_scale = {}
                final_ind = {}
                glow_ind_result = {}
                glow_org_result = {}
                glow_scale_result = {}
                for axis in range(2, -1, -1):
                    ind, org, scale = self.map_to_img(map, axis, type, self.errlist)
                    org_result.update(org)
                    scale_result.update(scale)
                    if type == 'central' or type == 'largestvariance':
                        ind_result.update(ind)
                    if type == 'max' or type == 'projection' or type == 'std':
                        glow_ind, glow_org, glow_scale = self.map_to_img(map, axis, type, self.errlist, self.glowimage)
                        glow_org_result.update(glow_org)
                        glow_scale_result.update(glow_scale)
                        # if type == 'central' or type == 'largestvariance':
                        #     glow_ind_result.update(glow_ind)
                    # if type == 'central' or type == 'largestvariance':
                    #     ind_result.update(ind)
                final_org['original'] = org_result
                final_scale['scaled'] = scale_result
                if type == 'central' or type == 'largestvariance':
                    final_ind['indices'] = ind_result

                if type == 'largestvariance':
                    result_dict['largest_variance_slice'] = {**final_org, **final_scale, **final_ind}
                elif type == 'central':
                    result_dict['central_slice'] = {**final_org, **final_scale, **final_ind}
                else:
                    result_dict[f'orthogonal_{type}'] = {**final_org, **final_scale}

            if len(types) == 1:
                json_file = f'{self.workdir}{mapname}_{type}.json'
            else:
                if not label:
                    json_file = f'{self.workdir}{mapname}_primary_projections.json'
                else:
                    json_file = f'{self.workdir}{mapname}_raw_projections.json'

            out_json(result_dict, json_file)
            end = timeit.default_timer()
            print(f'Projections and their glow projections time for {mapname}: {end - start}')
            print('------------------------------------')
        else:
            print('No orthogonal projections without proper map input and the output directory information.')

    def rawmap_projections(self):
        if self.rawmap is not None:
            self.orthogonal_projections(self.rawmap, self.workdir, 'rawmap_')
        else:
            print('No raw map to calculate orthogonal projections.')


    def save_to_json(self, errlist, mapname, workdir, label):
        bothjson = {}
        projectionjson = {}
        orgprojectionjson = {}

        for axis_letter in ['x', 'y', 'z']:
            projectionjson[axis_letter] = {}
            orgprojectionjson[axis_letter] = {}

        for axis in range(3):
            for type in ['projection', 'max', 'min', 'std', 'median', 'central', 'largestvariance']:
                for axis_letter in ['x', 'y', 'z']:
                    projection_name = f'{workdir}{mapname}_{axis_letter}{type}.jpeg'
                    scaled_projection_name = f'{workdir}{mapname}_scaled_{axis_letter}{type}.jpeg'
                    projectionjson[axis_letter][type] = os.path.basename(projection_name) if os.path.isfile(projection_name) else None
                    orgprojectionjson[axis_letter][type] = os.path.basename(scaled_projection_name) if os.path.isfile(scaled_projection_name) else None

        bothjson['original'] = orgprojectionjson
        bothjson['scaled'] = projectionjson

        if errlist:
            bothjson['err'] = {'orthogonal_median_err': errlist}
        finaldict = {label + 'orthogonal_median': bothjson}

        try:
            with codecs.open(f'{workdir}{mapname}_median.json', 'w', encoding='utf-8') as f:
                json.dump(finaldict, f)
        except IOError as ioerr:
            jsonerr = f'Saving median projection into json error: {ioerr}'
            sys.stderr.write(jsonerr + '\n')

    def glowimage(self, im_gray):
        """Applies a glow color map using cv2.applyColorMap()"""

        # Create the LUT:
        lut = np.zeros((256, 1, 3), dtype=np.uint8)
        lut[:, 0, 2] = [0, 1, 1, 2, 2, 3, 4, 6, 8, 11, 13, 15, 18,
                        21, 23, 24, 27, 30, 31, 33, 36, 37, 40, 42, 45, 46,
                        49, 51, 53, 56, 58, 60, 62, 65, 68, 70, 72, 74, 78,
                        80, 82, 84, 86, 89, 91, 93, 96, 98, 100, 102, 104, 106,
                        108, 110, 113, 115, 117, 119, 122, 125, 127, 129, 132, 135, 135,
                        137, 140, 141, 142, 145, 148, 149, 152, 154, 156, 157, 158, 160,
                        162, 164, 166, 168, 170, 171, 173, 174, 176, 178, 179, 180, 182,
                        183, 185, 186, 189, 192, 193, 193, 194, 195, 195, 196, 198, 199,
                        201, 203, 204, 204, 205, 206, 207, 209, 211, 211, 211, 211, 213,
                        215, 216, 216, 216, 216, 218, 219, 219, 219, 220, 222, 223, 223,
                        223, 223, 224, 224, 226, 227, 227, 227, 227, 228, 229, 231, 231,
                        231, 231, 231, 231, 231, 232, 233, 234, 234, 234, 234, 234, 234,
                        235, 237, 238, 238, 238, 238, 238, 238, 238, 238, 239, 240, 242,
                        242, 242, 242, 242, 242, 242, 242, 242, 243, 245, 246, 246, 246,
                        246, 245, 245, 245, 245, 245, 245, 245, 247, 248, 249, 249, 249,
                        249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249,
                        249, 250, 252, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 0]

        lut[:, 0, 1] = [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2,
                        2, 2, 2, 2, 3, 3, 3, 3, 4, 5, 5, 5, 5,
                        6, 6, 6, 7, 7, 8, 9, 9, 9, 9, 10, 10, 11,
                        12, 13, 14, 14, 14, 14, 15, 16, 16, 17, 18, 19, 19,
                        19, 20, 21, 22, 23, 24, 24, 25, 27, 28, 28, 28, 29,
                        31, 32, 32, 33, 35, 36, 36, 37, 39, 40, 40, 41, 42,
                        43, 45, 46, 47, 48, 50, 51, 52, 54, 55, 56, 57, 59,
                        62, 63, 65, 66, 68, 70, 71, 73, 74, 75, 77, 79, 81,
                        83, 85, 87, 89, 92, 93, 96, 98, 99, 100, 103, 105, 107,
                        109, 111, 113, 116, 117, 119, 121, 123, 125, 126, 128, 130, 132,
                        135, 137, 139, 140, 142, 144, 145, 147, 148, 150, 152, 154, 156,
                        158, 160, 161, 162, 164, 166, 168, 171, 172, 172, 174, 176, 177,
                        179, 180, 182, 183, 185, 187, 188, 189, 191, 192, 192, 192, 196,
                        200, 201, 201, 202, 203, 204, 206, 208, 210, 212, 213, 213, 214,
                        215, 217, 218, 220, 221, 222, 223, 224, 225, 226, 226, 227, 228,
                        229, 231, 232, 233, 234, 235, 236, 237, 238, 239, 239, 239, 239,
                        241, 242, 243, 243, 243, 244, 245, 247, 247, 247, 247, 247, 247,
                        248, 249, 250, 251, 251, 251, 252, 252, 252, 252, 252, 252, 252,
                        252, 252, 252, 252, 252, 252, 253, 253, 0]

        lut[:, 0, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 4, 4,
                        4, 4, 4, 4, 3, 3, 3, 3, 4, 6, 6, 6, 6,
                        6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                        6, 6, 6, 6, 6, 6, 6, 6, 5, 5, 7, 9, 10,
                        10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
                        10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
                        9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8,
                        8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 7, 7, 7,
                        7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6,
                        6, 6, 6, 6, 7, 10, 12, 12, 12, 12, 12, 12, 13,
                        15, 17, 18, 18, 19, 20, 22, 23, 23, 24, 26, 27, 27,
                        28, 30, 32, 33, 34, 35, 37, 39, 40, 41, 43, 45, 46,
                        48, 50, 52, 54, 55, 57, 58, 61, 63, 65, 67, 70, 72,
                        73, 76, 79, 80, 83, 86, 88, 89, 92, 95, 96, 99, 102,
                        104, 107, 108, 110, 113, 116, 120, 121, 123, 125, 127, 129, 132,
                        135, 137, 140, 143, 146, 149, 150, 153, 155, 158, 160, 162, 165,
                        168, 171, 173, 175, 178, 180, 183, 186, 188, 191, 192, 195, 198,
                        201, 203, 206, 209, 210, 213, 215, 218, 221, 223, 225, 228, 231,
                        233, 236, 238, 241, 244, 246, 250, 252, 255]

        im_color = cv2.applyColorMap(im_gray, lut)
        return im_color

# Example usage:
# rawmap = MrcFile("/Users/zhe/Downloads/tests/VA/nfs/msd/work2/emdb/development/staging/em/81/8117/va/emd_8117_rawmap.map")
# workdir = "/Users/zhe/Downloads/tests/VA/nfs/msd/work2/emdb/development/staging/em/81/8117/va"
# op = Projections(rawmap, workdir)
# op.rawmap_projections()
# op.rawmap_median()
