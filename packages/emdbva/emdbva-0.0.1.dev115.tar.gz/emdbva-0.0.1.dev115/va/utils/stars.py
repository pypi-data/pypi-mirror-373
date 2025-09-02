from math import pi
from va.utils.misc import *
import matplotlib.pyplot as plt


class GetStars:



    def __init__(self, star_file):
        self.star_file_name = os.path.basename(star_file)
        self.va_dir = os.path.dirname(os.path.dirname(os.path.dirname(star_file)))
        self.star_file = star_file
        self.star_blocks = self.read_star_file()


    def read_star_file(self):
        """
        find the data block which defined by 'block'
        """

        star_data = {}
        current_block = None

        with open(self.star_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("data_"):
                    current_block = line
                    star_data[current_block] = []
                elif current_block is not None and line:
                    star_data[current_block].append(line)

        return star_data


    def data_general_block(self):
        """
        Get the data_general block
        """

        data_general_block = {}
        for line in self.star_blocks['data_general']:
            if line.startswith('# version'):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                key, value = parts
                data_general_block[key] = float(value.strip()) if value.isdigit() else value

        return data_general_block

    def randomise_from(self):
        """
            Get the resolution value that Relion is use for the phase randomization calculation
        """

        return float(self.data_general_block()['_rlnRandomiseFrom'])

    def final_resolution(self):
        """
            Get the final resolution value from the data_general block
        """

        return float(self.data_general_block()['_rlnFinalResolution'])

    def data_fsc_block(self):
        """
        Get the data_fsc block
        """

        data_fsc_block = {}
        useful_data = self.star_blocks['data_fsc'][1:-2]
        header = [line.split(maxsplit=1)[0][4:] for line in useful_data[:8]]
        data = useful_data[8:]
        column_data_list = [row.split() for row in data]
        new_data_list = list(map(list, zip(*column_data_list)))
        # data_list = [[float(value) for value in sublist] for sublist in data_list]
        data_list = []
        for sublist in new_data_list:
            column_data_list = []
            for value in sublist:
                column_data_list.append(keep_three_significant_digits(float(value)))
            data_list.append(column_data_list)

        if len(header) == len(data_list):
            for header, data_list in zip(header, data_list):
                data_fsc_block[header] = data_list

        return data_fsc_block

    def data_extra(self, data_fsc_block):
        """
        Add half bit, one-bit and 3-sigma to data_fsc_block
        """

        indices = data_fsc_block['SpectralIndex']
        asym = 1.0
        half_bit = []
        one_bit = []
        for i in range(0, len(indices)):
            volume_diff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
            novox_ring = volume_diff / (1 ** 3)
            effno_vox = (novox_ring * ((1.5 * 0.66) ** 2)) / (2 * asym)
            if effno_vox < 1.0: effno_vox = 1.0
            sqreffno_vox = np.sqrt(effno_vox)

            bit_value = (0.2071 + 1.9102 / sqreffno_vox) / (1.2071 + 0.9102 / sqreffno_vox)
            half_bit.append(keep_three_significant_digits(bit_value))
            onebit_value = (0.5 + 2.4142 / sqreffno_vox) / (1.5 + 1.4142 / sqreffno_vox)
            one_bit.append(keep_three_significant_digits(onebit_value))

        gold_line = [0.143] * len(indices)
        half_line = [0.5] * len(indices)
        half_bit.insert(0, 1)
        one_bit.insert(0, 1)

        data_fsc_block['halfbit'] = half_bit[:-1]
        data_fsc_block['onebit'] = one_bit[:-1]
        data_fsc_block['0.5'] = half_line
        data_fsc_block['0.143'] = gold_line

        return data_fsc_block

    def _xy_check(self, x, y):
        """
        check the x, y value and return the results
        """

        if x.size == 0 and y.size == 0:
            return None, None
        else:
            x = np.round(x[0][0], 4)
            y = np.round(y[0][0], 4)
            return x, y

    def all_intersection(self, data_fsc_block):
        """
        Get all intersections from data_fsc_block
        """

        x = data_fsc_block['Resolution']
        correlation = data_fsc_block['FourierShellCorrelationUnmaskedMaps']
        half_bit = data_fsc_block['halfbit']
        gold = data_fsc_block['0.143']
        half = data_fsc_block['0.5']
        masked = data_fsc_block['FourierShellCorrelationMaskedMaps']
        corrected = data_fsc_block['FourierShellCorrelationCorrected']

        x_gold, y_gold = interpolated_intercept(x, correlation, gold)
        x_half, y_half = interpolated_intercept(x, correlation, half)
        x_half_bit, y_half_bit = interpolated_intercept(x, correlation, half_bit)
        x_masked, y_masked = interpolated_intercept(x, masked, gold)
        x_corrected, y_corrected = interpolated_intercept(x, corrected, gold)
        x_masked_half, y_masked_half = interpolated_intercept(x, masked, half)
        x_corrected_half, y_corrected_half = interpolated_intercept(x, corrected, half)
        x_masked_halfbit, y_masked_halfbit = interpolated_intercept(x, masked, half_bit)
        x_corrected_halfbit, y_corrected_halfbit = interpolated_intercept(x, corrected, half_bit)

        x_gold, y_gold = self._xy_check(x_gold, y_gold)
        x_half, y_half = self._xy_check(x_half, y_half)
        x_half_bit, y_half_bit = self._xy_check(x_half_bit, y_half_bit)
        x_masked, y_masked = self._xy_check(x_masked, y_masked)
        x_corrected, y_corrected = self._xy_check(x_corrected, y_corrected)
        x_masked_half, y_masked_half = self._xy_check(x_masked_half, y_masked_half)
        x_corrected_half, y_corrected_half = self._xy_check(x_corrected_half, y_corrected_half)
        x_masked_halfbit, y_masked_halfbit = self._xy_check(x_masked_halfbit, y_masked_halfbit)
        x_corrected_halfbit, y_corrected_halfbit = self._xy_check(x_corrected_halfbit, y_corrected_halfbit)

        if not x_gold or not y_gold:
            print('!!! No intersection between FSC and 0.143 curves.')
        if not x_half or not y_half:
            print('!!! No intersection between FSC and 0.5 curves.')
        if not x_half_bit or not y_half_bit:
            print('!!! No intersection between FSC and half-bit curves.')
        if not x_masked or not y_masked:
            print('!!! No intersection between FSC and masked curves.')
        if not x_corrected or not y_corrected:
            print('!!! No intersection between FSC and corrected curves.')
        if not x_masked_half or not y_masked_half:
            print('!!! No intersection between Masked and 0.5 curves.')
        if not x_corrected_half or not y_corrected_half:
            print('!!! No intersection between Corrected and 0.5 curves.')
        if not x_masked_halfbit or not y_masked_halfbit:
            print('!!! No intersection between Maksed and half-bit curves.')
        if not x_corrected_halfbit or not y_corrected_halfbit:
            print('!!! No intersection between Corrected and half-bit curves.')

        intersections = {'intersections': {
            'halfbit': {'x': x_half_bit, 'y': y_half_bit},
            '0.5': {'x': x_half, 'y': y_half},
            '0.143': {'x': x_gold, 'y': y_gold},
            'masked': {'x': x_masked, 'y': y_masked},
            'corrected': {'x': x_corrected, 'y': y_corrected},
            'masked_half': {'x': x_masked_half, 'y': y_masked_half},
            'corrected_half': {'x': x_corrected_half, 'y': y_corrected_half},
            'masked_halfbit': {'x': x_masked_halfbit, 'y': y_masked_halfbit},
            'corrected_halfbit': {'x': x_corrected_halfbit, 'y': y_corrected_halfbit}
        }
        }

        return intersections


    def all_curves(self, data_fsc_block):
        """
        Get all curves from data_fsc_block
        """

        curve_mapping = {
            'fsc': 'FourierShellCorrelationUnmaskedMaps',
            'onebit': 'onebit',
            'halfbit': 'halfbit',
            '0.5': '0.5',
            '0.143': '0.143',
            'level': 'Resolution',
            'angstrom_resolution': 'AngstromResolution',
            'phaserandmization': 'CorrectedFourierShellCorrelationPhaseRandomizedMaskedMaps',
            'phaserandomization': 'CorrectedFourierShellCorrelationPhaseRandomizedMaskedMaps',
            'fsc_masked': 'FourierShellCorrelationMaskedMaps',
            'fsc_corrected': 'FourierShellCorrelationCorrected'
        }
        curves = {key: data_fsc_block[value] for key, value in curve_mapping.items() if value in data_fsc_block}
        final_curves = {'curves': curves}

        return final_curves


    @staticmethod
    def intersections_into_curve(intersections, levels, corrected_curve, phase_rand_curve):
        """
            After getting the intersections and insert them into these curves
        :param intersections: list of data pairs containing intersections
        :param levels: list of x value of two intersect curves
        :param corrected_curve: list of value of correction curve correlation values
        :param phase_rand_curve: list of value of phase rand curve correlation
        """

        for a, b in intersections:

            exists = np.any(levels == a)
            if not exists:
                index = np.searchsorted(levels, a)
                levels = np.insert(levels, index, a)
                corrected_curve = np.insert(corrected_curve, index, b)
                phase_rand_curve = np.insert(phase_rand_curve, index, b)
            else:
                print(a, b)
                print('Intersection point on curve data')

        return levels, corrected_curve, phase_rand_curve

    def plot_fsc(self, data_curves, other_curves=None, other_curves_lable='Provided FSC'):
        """
            Plot Relion FSC curve
        :param intersections: list of tuples containing intersections in (x,y) coordinates
        :param levels: list of frequency values
        :param corrected_curve: list of corrected FSC value from Relion Star file
        :param phase_rand_curve: list of phase randomized FSC value from Relion
        """

        all_curves = None
        if 'curves' in data_curves.keys():
            all_curves = data_curves['curves']

        levels = None
        corrected_curve = None
        phase_rand_curve = None
        masked_curve = None
        unmasked_curve = None
        golden_line = None
        if all_curves:
            if 'level' in all_curves.keys():
                levels = np.array(all_curves['level'])
            if 'fsc_corrected' in all_curves.keys():
                corrected_curve = np.array(all_curves['fsc_corrected'])
            if 'phaserandmization' in all_curves.keys():
                phase_rand_curve = np.array(all_curves['phaserandmization'])
            if 'phaserandomization' in all_curves.keys():
                phase_rand_curve = np.array(all_curves['phaserandomization'])
            if 'fsc_masked' in all_curves.keys():
                masked_curve = np.array(all_curves['fsc_masked'])
            if 'fsc' in all_curves.keys():
                unmasked_curve = np.array(all_curves['fsc'])
            if '0.143' in all_curves.keys():
                golden_line = np.array(all_curves['0.143'])
            if other_curves:
                other_curve_x = other_curves[0]
                other_curve_y = other_curves[1]
                plt.plot(other_curve_x, other_curve_y, label=other_curves_lable)

            plt.plot(levels, unmasked_curve, label='FSC')
            plt.plot(levels, masked_curve, label='FSC (masked)')
            plt.plot(levels, corrected_curve, label='FSC (corrected)')
            plt.plot(levels, phase_rand_curve, label='Phaserandomization')
            plt.plot(levels, golden_line, linestyle='-.',  label='0.143')
            plt.legend(loc='upper right', fontsize='x-small')
            plt.savefig(self.va_dir + '/current_Relion_fsc.png')
            plt.close()

    def plot_feature_zone(self, intersections, levels, corrected_curve, phase_rand_curve):
        """
            Plot feature zone and save to image
        :param intersections: list of tuples containing intersections in (x,y) coordinates
        :param levels: list of frequency values
        :param corrected_curve: list of corrected FSC value from Relion Star file
        :param phase_rand_curve: list of phase randomized FSC value from Relion
        """

        frequency = 1 / self.randomise_from()
        plt.plot(levels, corrected_curve, color='red', label='t')
        plt.plot(levels, phase_rand_curve, color='blue', label='correlation')
        feature_area = 0
        for i in range(len(intersections)):
            if i == len(intersections) - 1:
                idx_start = np.where(levels == intersections[i][0])[0][0]
                idx_end = len(levels)
            else:
                idx_start = np.where(levels == intersections[i][0])[0][0]
                idx_end = np.where(levels == intersections[i + 1][0])[0][0]
            print(
                f'plt.fill_between(levels[{idx_start}:{idx_end}], corrected_curve[{idx_start}:{idx_end}], phase_rand_curve[{idx_start}:{idx_end}], where=(corrected_curve[{idx_start}:{idx_end}] >= phase_rand_curve[{idx_start}:{idx_end}]), color="gray", alpha=0.5)')
            plt.fill_between(levels[idx_start:idx_end], corrected_curve[idx_start:idx_end], phase_rand_curve[idx_start:idx_end],
                             where=(corrected_curve[idx_start:idx_end] >= phase_rand_curve[idx_start:idx_end]), color='pink', alpha=0.5)

            status = all(x >= y for x, y in zip(corrected_curve[idx_start:idx_end], phase_rand_curve[idx_start:idx_end]))

            if status:
                cur_area = np.trapz(corrected_curve[idx_start:idx_end] - phase_rand_curve[idx_start:idx_end], levels[idx_start:idx_end])
                feature_area += cur_area
                # validation area
                # area_one = np.trapz(corrected_curve[idx_start:idx_end], levels[idx_start:idx_end])
                # area_two = np.trapz(phase_rand_curve[idx_start:idx_end], levels[idx_start:idx_end])
                # print(area_one - area_two)
                # print(cur_area)

        closest_idx = min(range(len(levels)), key=lambda t: abs(levels[t] - frequency))
        y_values = [0] * (len(levels) - closest_idx)
        overfit_area = np.trapz(phase_rand_curve[closest_idx:], levels[closest_idx:])
        plt.fill_between(levels[closest_idx:], phase_rand_curve[closest_idx:],
                         y_values,
                         where=(phase_rand_curve[closest_idx:] >= 0),
                         color='blue', alpha=0.5)
        zone_image = f'{self.va_dir}/feature_zone.png'
        plt.savefig(zone_image)
        plt.close()

        return feature_area, overfit_area
    @staticmethod
    def area_difference(curve_one, curve_two, levels):
        """
            Calculates the area difference between two curves share common x axis (levels)
        :param curve_one: array 0f curve one
        :param curve_two: array 0f curve two
        :param levels: array 0f levels
        """
        area = np.trapz(curve_one - curve_two, levels)

        return area

    def feature_zone(self, data_curves):
        """
            By given two curves get the feature zone based on the intersections
            return quantified area of that zone
            :param data_curves: dictionary contains all curves
        """

        zones = {}
        result = {}
        all_curves = None
        if 'curves' in data_curves.keys():
            all_curves = data_curves['curves']

        levels = None
        corrected_curve = None
        phase_rand_curve = None
        masked_curve = None
        unmasked_curve = None
        if all_curves:
            if 'level' in all_curves.keys():
                levels = np.array(all_curves['level'])
            if 'fsc_corrected' in all_curves.keys():
                corrected_curve = np.array(all_curves['fsc_corrected'])
            if 'phaserandmization' in all_curves.keys():
                phase_rand_curve = np.array(all_curves['phaserandmization'])
            if 'phaserandomization' in all_curves.keys():
                phase_rand_curve = np.array(all_curves['phaserandomization'])
            if 'fsc_masked' in all_curves.keys():
                masked_curve = np.array(all_curves['fsc_masked'])
            if 'fsc' in all_curves.keys():
                unmasked_curve = np.array(all_curves['fsc'])

        if isinstance(levels, np.ndarray) and isinstance(corrected_curve, np.ndarray) and isinstance(phase_rand_curve, np.ndarray):
            xs, ys = interpolated_intercepts_general(levels, corrected_curve, phase_rand_curve)
            intersections = remove_duplicate_intersections(xs, ys)
            nlevels, ncorrected_curve, phase_rand_curve = self.intersections_into_curve(intersections, levels, corrected_curve, phase_rand_curve)
            feature_area, overfit_area = self.plot_feature_zone(intersections, nlevels, ncorrected_curve, phase_rand_curve)
            masking_area = self.area_difference(masked_curve, corrected_curve, levels)
            corrected_unmasked_difference = sum(corrected_curve - unmasked_curve)
            corrected_masked_difference = sum(masked_curve - corrected_curve)
            if corrected_unmasked_difference == 0:
                print('Corrected is the same as the unmasked.')
                masking_area_ratio = 999
            else:
                masking_area_ratio = abs(corrected_masked_difference / corrected_unmasked_difference)
            zones['feature_zone'] = keep_three_significant_digits(feature_area)
            zones['overfit_zone'] = keep_three_significant_digits(overfit_area)
            zones['masking_area'] = keep_three_significant_digits(masking_area)
            zones['masking_area_ratio'] = keep_three_significant_digits(masking_area_ratio)
            zones['feature_zone_ratio'] = keep_three_significant_digits(zones['feature_zone'] / (zones['feature_zone'] + zones['overfit_zone']))
            result['feature_zones'] = zones

        return result








