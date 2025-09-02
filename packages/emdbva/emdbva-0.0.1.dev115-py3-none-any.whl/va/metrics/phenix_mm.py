import subprocess
import sys
from math import pi
from distutils.spawn import find_executable
import pandas as pd
from va.utils.misc import *


def run_phenixmmfsc(full_modelpath, full_mappath, output_path):
    """

        Phenix score

    :return:
    """

    errlist = []
    try:
        assert find_executable('phenix.mtriage') is not None
        phenixpath = find_executable('phenix.mtriage')
        create_directory(output_path)
        phenixmmfsc_cmd = '{} {} {} fsc_curve_model=True d_fsc_model_05=True'.format(phenixpath, full_mappath, full_modelpath)
        print(phenixmmfsc_cmd)
        try:
            process = subprocess.Popen(phenixmmfsc_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=output_path)
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
            err = 'Phenix map-model FSC calculation error: {}.'.format(suberr)
            errlist.append(err)
            sys.stderr.write(err + '\n')
    except AssertionError as exerr:
        err = 'Phenix executable is not there.'
        errlist.append(err)
        sys.stderr.write('Phenix executable is not there: {}\n'.format(exerr))

    return errlist

def read_mmfsc(mmfsc_log, errlist):
    """
        Read the residue-wise CCC from the output of Phenix results
    :param: cc_per_residue_log input file cc_per_residue.log file(full path name) from Phenix CC calculation
    :return:
    """

    if not errlist and os.path.isfile(mmfsc_log):
        df = pd.read_csv(mmfsc_log, delim_whitespace=True, header=None)
    else:
        df = None

    return df


def data_extra(data_extra):
    """
    Add half bit, one-bit and 3-sigma to data_fsc_block
    """

    frequencies = data_extra['level']
    asym = 1.0
    half_bit = []
    one_bit = []
    for i in range(0, len(frequencies)):
        volume_diff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
        novox_ring = volume_diff / (1 ** 3)
        effno_vox = (novox_ring * ((1.5 * 0.66) ** 2)) / (2 * asym)
        if effno_vox < 1.0: effno_vox = 1.0
        sqreffno_vox = np.sqrt(effno_vox)

        bit_value = (0.2071 + 1.9102 / sqreffno_vox) / (1.2071 + 0.9102 / sqreffno_vox)
        half_bit.append(keep_three_significant_digits(bit_value))
        onebit_value = (0.5 + 2.4142 / sqreffno_vox) / (1.5 + 1.4142 / sqreffno_vox)
        one_bit.append(keep_three_significant_digits(onebit_value))

    gold_line = [0.143] * len(frequencies)
    half_line = [0.5] * len(frequencies)
    half_bit.insert(0, 1)
    one_bit.insert(0, 1)

    data_extra['halfbit'] = half_bit[:-1]
    data_extra['onebit'] = one_bit[:-1]
    data_extra['0.5'] = half_line
    data_extra['0.143'] = gold_line

    return data_extra

def _xy_check(x, y):
    """
    check the x, y value and return the results
    """

    if x.size == 0 and y.size == 0:
        return None, None
    else:
        x = np.round(x[0][0], 4)
        y = np.round(y[0][0], 4)
        return x, y
def all_intersection(allcurves):
    """
    Get all intersections from data_fsc_block
    """

    mmfsc = allcurves['level']
    correlation = allcurves['fsc']
    half_bit = allcurves['halfbit']
    gold = allcurves['0.143']
    half = allcurves['0.5']

    x_gold, y_gold = interpolated_intercept(mmfsc, correlation, gold)
    x_half, y_half = interpolated_intercept(mmfsc, correlation, half)
    x_half_bit, y_half_bit = interpolated_intercept(mmfsc, correlation, half_bit)

    x_gold, y_gold = _xy_check(x_gold, y_gold)
    x_half, y_half = _xy_check(x_half, y_half)
    x_half_bit, y_half_bit = _xy_check(x_half_bit, y_half_bit)
    if not x_gold or not y_gold:
        print('!!! No intersection between FSC and 0.143 curves.')
    if not x_half or not y_half:
        print('!!! No intersection between FSC and 0.143 curves.')
    if not x_half_bit or not y_half_bit:
        print('!!! No intersection between FSC and 0.143 curves.')

    intersections = {'halfbit': {'x': x_half_bit, 'y': y_half_bit},
                      '0.5': {'x': x_half, 'y': y_half},
                      '0.143': {'x': x_gold, 'y': y_gold}}

    return intersections

def mmfscdf_todict(mmfscdf, nyquist):
    """
        Given the Phenix CC result in dataframe and output the dict to be save in json
    :param ccdf: phenix cc_per_residue.log result into dataframe
    :return: dict which contain CC per residue results
    """

    real_mmfscdf = mmfscdf[mmfscdf[0] <= nyquist].round(3).drop_duplicates()
    skip = (len(real_mmfscdf) - 2) / (96 - 1)

    # Select the rows based on the calculated skip value
    indices = [0]  # Include the first row
    indices.extend(int(i * skip) + 1 for i in range(1, 95))  # Select evenly distributed rows
    indices.append(len(real_mmfscdf) - 1)  # Include the last row
    df_evenly = real_mmfscdf.iloc[indices]
    x = df_evenly.iloc[:, 0].tolist()
    y = df_evenly.iloc[:, 1].tolist()
    curves = {}
    curves['fsc'] = y
    curves['level'] = x
    allcurves = data_extra(curves)
    intersections = all_intersection(allcurves)

    finaldict = {'curves': curves, 'intersections': intersections}

    return finaldict

