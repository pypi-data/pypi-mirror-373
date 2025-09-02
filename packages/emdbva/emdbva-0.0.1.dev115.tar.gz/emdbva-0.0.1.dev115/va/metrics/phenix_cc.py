import subprocess
import sys
import os
from distutils.spawn import find_executable
import pandas as pd

def create_folder(output_path):
    """
        create emringer output folder inside va directory

    :return: model related path of strudel folder
    """

    fullname = '{}'.format(output_path)

    if not os.path.isdir(fullname):
        os.mkdir(fullname, mode=0o777)
    else:
        print('{} is exist'.format(fullname))


def run_phenixcc(full_modelpath, full_mappath, resolution, output_path):
    """

        Phenix score

    :return:
    """

    errlist = []
    try:
        assert find_executable('phenix.map_model_cc') is not None
        phenixpath = find_executable('phenix.map_model_cc')
        create_folder(output_path)
        phenixcc_cmd = '{} {} {} resolution={}'.format(phenixpath, full_modelpath, full_mappath, resolution)
        print(phenixcc_cmd)
        try:
            process = subprocess.Popen(phenixcc_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=output_path)
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
            # post_phenixcc()
        except subprocess.CalledProcessError as suberr:
            err = 'Phenix residue-wise CCC calculation error: {}.'.format(suberr)
            errlist.append(err)
            sys.stderr.write(err + '\n')
    except AssertionError as exerr:
        err = 'Phenix executable is not there.'
        errlist.append(err)
        sys.stderr.write('Phenix executable is not there: {}\n'.format(exerr))

    return errlist


def read_cc(cc_per_residue_log, errlist):
    """
        Read the residue-wise CCC from the output of Phenix results
    :param: cc_per_residue_log input file cc_per_residue.log file(full path name) from Phenix CC calculation
    :return:
    """

    if not errlist and os.path.isfile(cc_per_residue_log):
        df = pd.read_csv(cc_per_residue_log, delim_whitespace=True, header=None)
        print(df)
    else:
        df = None

    return df


def _floatohex(numlist):
    """
        Todo: make this function into utlis
        Produce hex color between red and green
    :param numlist: A list of RGB values
    :return: A list of hex value between R and G with B = 0
    """

    numlist = [-1 if i < 0 else i for i in numlist]
    rgbs = [[122, int(num * 255), int(num * 255)] if num >= 0 else [255, 0, 255] for num in numlist]
    resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]

    return resultlist

def ccdf_todict(ccdf):
    """
        Given the Phenix CC result in dataframe and output the dict to be save in json
    :param ccdf: phenix cc_per_residue.log result into dataframe
    :return: dict which contain CC per residue results
    """

    finaldict = {}
    averagecc = ccdf[3].mean()
    averagecc_color = _floatohex([averagecc])[0]
    numberofresidues = ccdf.shape[0]
    colors = _floatohex(ccdf[3])
    ccscores = ccdf[3]
    chain_ccscores = ccdf.groupby(0).agg(value=(3, 'mean'))
    chain_ccscores['color'] = chain_ccscores.apply(lambda x: _floatohex([x['value']])[0], axis=1)
    chain_ccdict = {str(row.name): {'value': row['value'], 'color': row['color']} for _, row in chain_ccscores.iterrows()}

    def abc(a, b, c):
        return '{}:{} {}'.format(a, b, c)
    residue = ccdf.apply(lambda x: abc(x[0], x[2], x[1]), axis=1)
    finaldict = {'averagecc': round(averagecc, 3), 'averagecc_color': averagecc_color,
                         'numberofresidues': numberofresidues, 'color': colors,
                         'ccscore': ccscores.tolist(), 'residue': residue.tolist(), 'chainccscore': chain_ccdict}

    return finaldict

