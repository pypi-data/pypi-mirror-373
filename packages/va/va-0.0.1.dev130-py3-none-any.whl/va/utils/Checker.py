import os.path

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from va.utils.misc import out_json
from PIL import Image
import json

class FSCChecks:
    def __init__(self, input_data):
        try:
            self.fsc_data = input_data['curves']['fsc'][5:]
        except KeyError as e:
            raise Exception(f"Error: Required data not found in the JSON file. {e}")

    def min_value(self):
        return np.min(self.fsc_data)

    def end_value(self):
        return self.fsc_data[-1]

    def min_final_diff_value(self):
        return self.end_value() - self.min_value()

    def large_drop_check(self, window_size=5, drop_threshold=0.7):
        max_gradient_change = 0
        for i in range(window_size, len(self.fsc_data)):
            window_data = self.fsc_data[i - window_size: i]
            if abs(window_data[-1] - window_data[0]) > drop_threshold:
                differences = np.diff(window_data)
                average_difference = np.mean(differences)
                max_gradient_change = max(max_gradient_change, abs(average_difference))
        return max_gradient_change

    def max_gradient_check(self, window_size=5):
        max_change = float('-inf')
        for i in range(window_size, len(self.fsc_data)):
            window_data = self.fsc_data[i - window_size: i]
            differences = np.diff(window_data)
            average_difference = np.mean(differences)
            max_change = max(max_change, abs(average_difference))
        return max_change

    def peak_finder(self, window_size=5):
        # smoothed_data = lowess(self.fsc_data, range(len(self.fsc_data)), frac=0.05)[:, 1]
        smoothed_data = np.convolve(self.fsc_data, np.ones(window_size) / window_size, mode='valid')
        peaks, _ = find_peaks(smoothed_data, distance=5, prominence=0.1)
        return len(peaks)

    def fsc_plotter(self, filepath):
        plt.figure()
        plt.plot(range(len(self.fsc_data)), self.fsc_data)
        plt.axhline(y=0, color='red', linestyle='--', label='Zero Line')
        plt.axhline(y=0.143, color='orange', linestyle='--', label='0.143 Line')
        plt.title(filepath)
        plt.savefig('{}.png'.format(filepath))
        plt.close()

    def fsc_checks(self, output_json):
        fsc_check = {}
        fsc_check['FSC'] = {}
        fsc_check['FSC']['minValue'] = self.min_value()
        fsc_check['FSC']['endValue'] = self.end_value()
        fsc_check['FSC']['peaks'] = self.peak_finder()
        fsc_check['FSC']['largestGradient'] = self.max_gradient_check()
        out_json(fsc_check, output_json)


class ImageChecks:
    """
        This class is designed to run checks on the VA images.
        Each check should be added as a function and then called in RunChecksPerCheck.py
    """

    def __init__(self, input_image):
        try:
            self.input_image = input_image
            self.image_dir = os.path.dirname(input_image)
        except KeyError as e:
            raise Exception(f"Error: Required data not found in the JSON file. {e}")

    def mask_check(self):

        img = Image.open(self.input_image)
        img_array = np.array(img)
        green_pixels = np.sum(np.all(img_array == [0, 138, 0], axis=-1))
        total_pixels = img_array.shape[0] * img_array.shape[1]
        proportion_green = (green_pixels / total_pixels) * 100

        # Calculate proportions of green for halves split vertically
        mid_vertical = img_array.shape[1] // 2
        green_pixels_left_half = np.sum(np.all(img_array[:, :mid_vertical, :] == [0, 138, 0], axis=-1))
        green_pixels_right_half = np.sum(np.all(img_array[:, mid_vertical:, :] == [0, 138, 0], axis=-1))
        proportion_green_left_half = (green_pixels_left_half / (total_pixels // 2)) * 100
        proportion_green_right_half = (green_pixels_right_half / (total_pixels // 2)) * 100
        diff_vertical = proportion_green_left_half - proportion_green_right_half

        # Calculate proportions of green for halves split horizontally
        mid_horizontal = img_array.shape[0] // 2
        green_pixels_top_half = np.sum(np.all(img_array[:mid_horizontal, :, :] == [0, 138, 0], axis=-1))
        green_pixels_bottom_half = np.sum(np.all(img_array[mid_horizontal:, :, :] == [0, 138, 0], axis=-1))
        proportion_green_top_half = (green_pixels_top_half / (total_pixels // 2)) * 100
        proportion_green_bottom_half = (green_pixels_bottom_half / (total_pixels // 2)) * 100
        diff_horizontal = proportion_green_top_half - proportion_green_bottom_half

        return proportion_green, diff_vertical, diff_horizontal

    def image_check(self):

        try:
            proportion_green, diff_vertical, diff_horizontal = self.mask_check()
            result_dict = {'proportion_green': proportion_green, 'maskDiffVertical': diff_vertical,
                           'maskDiffHorizontal': diff_horizontal}
            final_dict = {'imageChecks': result_dict}
            output_file = f'{self.image_dir}/va_feature_extraction/image.json'
            out_json(final_dict, output_file)
        except Exception as e:
            print(f'The image check error is: {e}')


def mask_assessment(input_data):
    """
    Generate mask assessment
    :param input_data: Dictionary containing the input data
    """
    proportion_green = input_data.get("imageChecks", {}).get("proportion_green", 0)
    proportion_threshold = 21

    # Check if masking is detected
    masking_detected = 1 if proportion_green > proportion_threshold else 0
    message = "Possible masking detected above threshold" if masking_detected else "No masking detected"
    result = {'Masking': {"green_proportion_threshold": proportion_threshold,
                          "masking_detected": masking_detected, "message": message} }
    return result

def fsc_assessment(input_data):
    """
    Generate mask assessment
    :param input_data: Dictionary containing the input data
    """

    issue_descriptions = {
        "fsc_min_bin": "FSC min value",
        "fsc_end_bin": "FSC end value",
        "fsc_peaks_bin": "FSC peaks",
        "fsc_largest_gradient_bin": "FSC largest gradient",
        "fsc_feature_zone_bin": "FSC feature zone"
    }
    fsc_min = input_data.get('FSC', {}).get('minValue', 0)
    fsc_end = input_data.get('FSC', {}).get('endValue', 0)
    fsc_peaks = input_data.get('FSC', {}).get('peaks', 0)
    fsc_largest_gradient = input_data.get('FSC', {}).get('largestGradient', 0)
    fsc_feature_zone = input_data.get('FSC', {}).get('feature_zone_ratio', 0)
    fsc_min_bin = 1 if fsc_min < -0.1 else 0
    fsc_end_bin = 1 if fsc_end > 0.1 else 0
    fsc_peaks_bin = 1 if fsc_peaks > 2 else 0
    fsc_largest_gradient_bin = 1 if fsc_largest_gradient > 0.1 else 0
    fsc_feature_zone_bin = 1 if fsc_feature_zone < 0.4 else 0

    true_elements = {
        "fsc_min_bin": fsc_min_bin,
        "fsc_end_bin": fsc_end_bin,
        "fsc_peaks_bin": fsc_peaks_bin,
        "fsc_largest_gradient_bin": fsc_largest_gradient_bin,
        "fsc_feature_zone_bin": fsc_feature_zone_bin
    }

    true_elements = {key: value for key, value in true_elements.items() if value == 1}
    existing_issues = [issue_descriptions[key] for key in true_elements.keys()]
    issues = ', '.join(existing_issues)

    # Determine the overall result
    result = bool(true_elements)
    # Check if masking is detected
    fsc_issue_detected = 1 if result else 0
    message = f"Possible FSC issue for: {issues}" if fsc_issue_detected else "No FSC issue detected"
    result = {'FSC_issue': {"FSC_issue": fsc_issue_detected, "message": message} }

    return result

def feature_assessment(input_file, work_dir=None):
    """
    Feature assessment for the input data.
    :param input_file: Path to the input JSON file
    :param work_dir: Optional working directory for output files
    """
    try:
        # get the input_data
        with open(input_file, 'r') as file:
            input_data = json.load(file)
        # Extract proportion_green from the input data
        result = {}
        mask_result = mask_assessment(input_data)
        fsc_result = fsc_assessment(input_data)
        result.update(mask_result)
        result.update(fsc_result)

        file_prefix = input_file.split('/')[-1].split('_')[0]
        if work_dir:
            output_file = os.path.join(work_dir, f"{file_prefix}_va_feature_assessment.json")
        else:
            output_file = f"{file_prefix}_va_feature_assessment.json"

        out_json(result, output_file)

    except Exception as e:
        print(f"Feature assessment error: {e}")