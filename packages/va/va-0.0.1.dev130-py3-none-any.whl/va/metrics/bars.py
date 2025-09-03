import os.path
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scipy.stats
from multiprocessing import Pool, cpu_count

CONFIG_FILE = os.path.expanduser('~/.va_config.json')

def load_config():
    """Load configuration from the JSON file.

    Returns:
        dict: The configuration loaded from the JSON file, or an empty dict if the file does not exist.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    else:
        return {}

def save_config(cfg):
    """Save the configuration dictionary to the JSON config file.

    Args:
        cfg (dict): The configuration dictionary to save.
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

def load_score(input_file, new_entry, score_type):
    """Loads a score into a DataFrame by appending a new entry and removing duplicates.

    Args:
        input_file (str): Path to the CSV file containing existing scores.
        new_entry (dict): Dictionary representing the new score entry to add.
        score_type (str): The key in the entry and DataFrame representing the score column.

    Returns:
        pd.DataFrame: DataFrame with the new entry added and duplicates removed, sorted by score_type.
    """

    type_dict = {'id': str, 'resolution': float, 'name': str, score_type: float}
    df_nonew = pd.read_csv(input_file, dtype=type_dict)
    new_entry_df = pd.DataFrame([new_entry])
    df = pd.concat([df_nonew, new_entry_df], ignore_index=True)
    # df_without_nan = df[~df.isnull().any(axis=1)].sort_values(by=score_type).reset_index()
    df_without_nan = df[~df[score_type].isnull()].sort_values(by=score_type).reset_index()
    subsets = ['id', 'resolution', 'name', score_type]
    df_without_nan = df_without_nan.drop_duplicates(subsets)

    return df_without_nan


def get_score(df, input_value, score_type):
    """Given a DataFrame, returns the minimum and maximum values of the specified score column,
    and the counts of items smaller than or equal to, and greater than, the input value.

    Args:
        df (pd.DataFrame): The DataFrame containing the scores.
        input_value (float): The value to compare against the score column.
        score_type (str): The name of the score column.

    Returns:
        tuple: A tuple containing:
            - (min, max): The minimum and maximum values of the score column.
            - (small, large): The counts of items with scores <= input_value and > input_value.
    """

    qmin = None
    qmax = None
    small = None
    large = None
    if not df.empty:
        qmin = df[score_type].min()
        qmax = df[score_type].max()
        large = df[df[score_type] > input_value].shape[0]
        small = df[df[score_type] <= input_value].shape[0]

    return (qmin, qmax), (small, large)


def match_to_newscale(original_scale, target_scale, original_value):
    """
    Scale the original_value based in the original_scale to target_scale
    """

    original_min = original_scale[0]
    original_max = original_scale[1]

    target_min = target_scale[0]
    target_max = target_scale[1]

    target_value = ((original_value - original_min) / (original_max - original_min)) * (
                target_max - target_min) + target_min

    return target_value


def get_nearest_onethousand(new_entry, df, n, score_type):
    """
    Sort the score based on resolution and then return the nearest 1000 center at the
    new_entry
    """

    # Find the index of the nearest row to the target value
    cdf = df.sort_values(by='resolution').reset_index()
    # nearest_index = (cdf['qscore'] - new_entry['qscore']).abs().idxmin()
    # nearest_index = cdf[cdf['id'] == new_entry['id']].index.to_list()[0]
    # As the new entry added into the df, use all the 4 columns to identify the row index
    mask = (cdf['id'] == new_entry['id']) & (cdf['resolution'] == new_entry['resolution']) & (
                cdf['name'] == new_entry['name']) & (cdf[score_type] == new_entry[score_type])
    nearest_index = cdf[mask].index[0]

    # Get the 1000 rows centered around the nearest index
    start = max(nearest_index - n, 0)
    end = min(nearest_index + n, len(df))
    df_nearest = cdf.iloc[start:end + 1]

    return df_nearest


def get_resolution_range(new_entry, df, score_type, column='resolution', resbin=0.5):
    """
    Sort the df based on the resolution and then find the nearest +1-1 resolution df
    """

    if new_entry[column]:
        # Find the index of the nearest row to the target value
        cdf = df.sort_values(by=column).reset_index()
        # nearest_index = (cdf['qscore'] - new_entry['qscore']).abs().idxmin()
        # nearest_index = cdf[cdf['id'] == new_entry['id']].index.to_list()[0]
        # As the new entry added into the df, use all the 4 columns to identify the row index
        mask = (cdf['id'] == new_entry['id']) & (cdf[column] == new_entry[column]) & (
                    cdf['name'] == new_entry['name']) & (cdf[score_type] == new_entry[score_type])
        nearest_index = cdf[mask].index

        # Get the 1000 rows centered around the nearest index
        start = float(new_entry[column]) - resbin if float(new_entry[column]) >= resbin else 0.
        end = float(new_entry[column]) + resbin
        df_resbin = cdf[(cdf[column] >= start) & (cdf[column] <= end)]

        return df_resbin
    else:
        return None


def plot_bar_mat(a, b, qmin, qmax, qscore, work_dir, plot_name, score_type):
    """
    This function here using matplotlib to produce the Q-score bar image
    """

    a = a*1.5 if a else None
    b = b*1.5 if b else None
    a = a/200 if a else None
    b = b/200 if b else None
    # Create a color scale from 0 to 1
    color_scale = np.linspace(0, 1, 199)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 2), dpi=300)
    plt.rcParams['font.family'] = 'Times New Roman'

    # Reverse the color map
    cmap = plt.get_cmap("bwr")
    reversed_cmap = cmap.reversed()
    # Plot the color scale with a thinner aspect ratio
    ax.imshow([color_scale], cmap=reversed_cmap, aspect=0.05, extent=[0, 1.5, 0, 1])

    # Calculate the height and half-width of the diamonds
    diamond_height = 0.65
    diamond_half_width = 0.01

    # Add diamond-shaped marker for 'a'
    if a != b:
        ax.fill(
            [a - diamond_half_width, a, a + diamond_half_width, a],
            [0.5, 0.5 + diamond_height, 0.5, 0.5 - diamond_height],
            color='Black', edgecolor='black'
        )

        # Add diamond-shaped marker for 'b'
        ax.fill(
            [b - diamond_half_width, b, b + diamond_half_width, b],
            [0.5, 0.5 + diamond_height, 0.5, 0.5 - diamond_height],
            facecolor='none', edgecolor='black'
        )
    else:
        # ax.fill(
        #     [b - diamond_half_width, b, b + diamond_half_width, b],
        #     [0.5, 0.5 + diamond_height, 0.5, 0.5 - diamond_height],
        #     facecolor='yellow', edgecolor='black'
        # )
        top = np.array([[b-diamond_half_width, 0.5], [b, 0.5 + diamond_height], [b + diamond_half_width, 0.5], [b, 0.5]])
        bottom = np.array([[b-diamond_half_width, 0.5], [b, 0.5], [b + diamond_half_width, 0.5], [b, 0.5 - diamond_height]])
        top_patch = patches.Polygon(top, closed=True, facecolor='black', edgecolor='black')
        bottom_patch = patches.Polygon(bottom, closed=True, facecolor='none', edgecolor='black')
        ax.add_patch(top_patch)
        ax.add_patch(bottom_patch)

    # add four values as annotationso
    worse = r'$\it{Worse}$'
    better = r'$\it{Better}$'
    ax.annotate(worse, (0, -0.9), color='black', ha='left', fontsize=10, )
    ax.annotate(better, (1.5, -0.9), color='black', ha='right', fontsize=10)
    ax.annotate(f'{qscore:.3f}', (1.58, 0.2), color='black', ha='center', fontsize=12)

    if score_type == 'ccc':
        ax.annotate('CCC', (-0.11, 0.2), color='black', ha='center', fontsize=12)
    elif score_type == 'ai':
        ax.annotate('Atom inclusion', (-0.20, 0.2), color='black', ha='center', fontsize=12)
    elif score_type == 'smco':
        ax.annotate('SMOC', (-0.11, 0.2), color='black', ha='center', fontsize=12)
    elif score_type == 'qscore':
        ax.annotate('Q-score', (-0.11, 0.2), color='black', ha='center', fontsize=12)
    else:
        ax.annotate(score_type.upper(), (-0.11, 0.2), color='black', ha='center', fontsize=12)

    ax.annotate('Metric', (-0.11, 1.7), color='black', ha='center', fontsize=14)
    ax.annotate('Percentile Ranks', (0.75, 1.7), color='black', ha='center', fontsize=14)
    title = plot_name[:-8]
    ax.annotate(title, (0.75, 3.3), color='black', ha='center', fontsize=14, fontweight='bold')
    ax.annotate('Value', (1.58, 1.7), color='black', ha='center', fontsize=14)
    # if a >= b:
    #    ax.annotate(f'{a*100/1.5:.2f}%', (a, 1.4), color='black', ha='left', fontsize=10)
    #    #ax.annotate(f'{b:.2f}', (b, -0.8), color='black', ha='center', fontsize=10)
    #    #ax.annotate(f'{a*100:.2f}%', (a, 1.4), color='black', ha='center', fontsize=10)
    #    ax.annotate(f'{b*100/1.5:.2f}%', (b, 1.4), color='black', ha='right', fontsize=10)
    # else:
    #    ax.annotate(f'{a*100/1.5:.2f}%', (a, 1.4), color='black', ha='right', fontsize=10)
    #    #ax.annotate(f'{b:.2f}', (b, -0.8), color='black', ha='center', fontsize=10)
    #    #ax.annotate(f'{a*100:.2f}%', (a, 1.4), color='black', ha='center', fontsize=10)
    #    ax.annotate(f'{b*100/1.5:.2f}%', (b, 1.4), color='black', ha='left', fontsize=10)

    # Customize the plot
    ax.set_xlim(-0.4, 1.7)
    # ax.set_ylim(-4.3, 1.8)
    # to fit the EMD id
    ax.set_ylim(-4.3, 3.6)
    ax.set_yticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Remove the left and bottom axis lines (optional)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    if a != b:
        # Add diamond-shaped marker for legend
        wa = 0.01
        ha = -2.0
        ax.fill(
            [wa - diamond_half_width, wa, wa + diamond_half_width, wa],
            [ha, ha + diamond_height, ha, ha - diamond_height],
            color='black', edgecolor='black'
        )
        ax.annotate(f'Percentile relative to all EM structures', (wa + 3 * diamond_half_width, ha - 0.25),
                    color='black', ha='left', fontsize=11)

        bwa = 0.01
        bha = -3.6
        ax.fill(
            [bwa - diamond_half_width, bwa, bwa + diamond_half_width, bwa],
            [bha, bha + diamond_height, bha, bha - diamond_height],
            facecolor='none', edgecolor='black'
        )
        ax.annotate('Percentile relative to EM structures of $\pm$1 $\mathrm{\AA}$ (resolution)',
                    (bwa + 3 * diamond_half_width, bha - 0.25), color='black', ha='left', fontsize=11)
        # ax.annotate(f'Percentile relative to EM structures of nearest 1000 (resolution)', (bwa + 3*diamond_half_width, bha-0.25), color='black', ha='left', fontsize=11)
    else:
        # Add diamond-shaped marker for legend
        wa = 0.01
        ha = -2.0
        ax.fill(
            [wa - diamond_half_width, wa, wa + diamond_half_width, wa],
            [ha, ha + diamond_height, ha, ha - diamond_height],
            color='black', edgecolor='black'
        )
        ax.annotate('Percentile relative to all EM structures (overlapped)', (wa + 3 * diamond_half_width, ha - 0.25),
                    color='black', ha='left', fontsize=11)
        # ax.annotate('Percentile relative to all EM structures (overlapped)', (wa + 3*diamond_half_width, ha-0.25), color='black', ha='left', fontsize=11)

        bwa = 0.01
        bha = -3.6
        ax.fill(
            [bwa - diamond_half_width, bwa, bwa + diamond_half_width, bwa],
            [bha, bha + diamond_height, bha, bha - diamond_height],
            facecolor='none', edgecolor='black'
        )
        ax.annotate('Percentile relative to EM structures of $\pm$1 $\mathrm{\AA}$ (resolution)',
                    (bwa + 3 * diamond_half_width, bha - 0.25), color='black', ha='left', fontsize=11)
        # ax.annotate(f'Percentile relative to EM structures of nearest 1000 (resolution)', (bwa + 3*diamond_half_width, bha-0.25), color='black', ha='left', fontsize=11)

    ax.tick_params(axis='both', which='both', length=0)
    plt.gca().set_xticklabels([])
    # Show the plot
    plot_name = '{}{}'.format(work_dir, plot_name)
    plt.savefig(plot_name)
    plt.close()


def bar(new_entry_dict, score_type, work_dir, score_dir, plot_name, update_bin_file=None):
    input_file = '{}/qscores.csv'.format(score_dir)
    print(f'The all {score_type} file is: {input_file}.')
    resbin = current_qscore_resolution_bin(input_file, update_bin_file)
    print(f'Current resolution bin size for {score_type} is: {resbin}.')

    # new_entry_dict = {'id': '8117', 'resolution': 2.95, 'name': '5irx.cif', 'qscore': 0.521}
    qmin = None
    qmax = None
    df = load_score(input_file, new_entry_dict, score_type)
    if score_type and new_entry_dict[score_type]:
        (qmin, qmax), original_value = get_score(df, new_entry_dict[score_type], score_type)
        target_value = int(match_to_newscale((0, sum(original_value)), (0, 199), original_value[0]))
        to_whole = round(target_value/200., 3)
        to_whole_real = round((float(original_value[0]) / float(sum(original_value))), 3)
        to_whole_counts = sum(original_value)
        whole_res_low = df['resolution'].max()
        whole_res_hight = df['resolution'].min()
    else:
        to_whole = None
        to_whole_real = None
        to_whole_counts = None
        whole_res_low = None
        whole_res_hight = None

    if new_entry_dict['resolution']:
        df1000 = get_resolution_range(new_entry_dict, df, score_type, 'resolution', resbin)
        (sqmin, sqmax), ovalue = get_score(df1000, new_entry_dict[score_type], score_type)
        target_value_two = int(match_to_newscale((0, sum(ovalue)), (0, 199), ovalue[0]))
        to_two = round(target_value_two/200., 3)
        to_two_real = round((float(ovalue[0]) / float(sum(ovalue))), 3)
        to_two_counts = sum(ovalue)
        relative_res_low = df1000['resolution'].max()
        relative_res_high = df1000['resolution'].min()
    else:
        to_two = None
        to_two_real = None
        to_two_counts = None
        relative_res_low = None
        relative_res_high = None

    if to_whole and to_two:
        plot_bar_mat(target_value, target_value_two, qmin, qmax, new_entry_dict[score_type], work_dir, plot_name, score_type)
    print(f'{score_type} to whole: {to_whole_real}, to relative resolution: {to_two_real}')

    return  ((to_whole_real, to_whole_counts, whole_res_low, whole_res_hight), (to_two_real, to_two_counts, relative_res_low, relative_res_high), resbin)


def score_whole(new_entry, df, score_type='qscore'):
    """
    Calculate the whole score based on the new entry and the dataframe.

    Args:
        new_entry (dict): The new entry containing score information.
        Df (pd.DataFrame): DataFrame containing all entries.
        Score_type (str): The type of score to use (e.g., 'qscore').

    Returns:
        float: The whole score calculated as the percentile rank of the new entry.
    """

    (tmin, tmax), (tsmall, tlarge) = get_score(df, new_entry[score_type], score_type)
    q_whole = tsmall / (tsmall + tlarge)

    return q_whole


def score_relative(new_entry, df, score_type='qscore', column='resolution', bin=0.5):
    df_relative = get_resolution_range(new_entry, df, score_type, column, bin)
    if df_relative.empty:  # Handle case where df_relative is empty
        return 0., 0.  # Return NaN for q_relative and an empty list for row_indices
    rows = df_relative.shape[0]
    (tmin, tmax), (tsmall, tlarge) = get_score(df_relative, new_entry[score_type], score_type)
    q_relative = tsmall / (tsmall + tlarge)

    return q_relative, rows

def score_relative_wrapper(args):
    x, df, score_type, column, bin = args
    return score_relative(x, df, score_type, column, bin)

def fast_qscore_resolution_bin(df_resolution_sorted, score_type='qscore'):
    values = [round(x, 1) for x in np.arange(0.1, 1.6, 0.1)]
    for value in values:
        args_list = [
            (row, df_resolution_sorted, score_type, 'resolution', value)
            for _, row in df_resolution_sorted.iterrows()
        ]
        with Pool(processes=cpu_count()) as pool:
            results = pool.map(score_relative_wrapper, args_list)
        df_resolution_sorted[f'q_relative_{value}'], df_resolution_sorted[f'df_relative_{value}_rows'] = zip(*results)
    return df_resolution_sorted

def find_optimal_correlation_index(arr):
    arr = np.asarray(arr)
    mask = arr > -0.3
    if not np.any(mask):
        return None  # No value larger than -0.3
    filtered = arr[mask]
    closest_value = filtered[np.argmin(np.abs(filtered + 0.3))]
    return np.where(arr == closest_value)[0][0]

def resolution_qrelative_correlation(df_resolution_sorted, values, score_type='qscore'):
    correlation_below_5 = []
    correlation_above_5 = []
    col_names = []
    for i, value in enumerate(values):
        if score_type == 'qscore':
            col_name = f'q_relative_{value}'  # Dynamically create the column name
        # Filter the data for resolution < 5 Å and > 5 Å
        data_below_5 = df_resolution_sorted[df_resolution_sorted['resolution'] <= 5]
        data_above_5 = df_resolution_sorted[df_resolution_sorted['resolution'] > 5]

        # Calculate correlation for resolution <= 5 Å
        corr_below_5, _ = scipy.stats.pearsonr(data_below_5['resolution'], data_below_5[col_name])

        # Calculate correlation for resolution > 5 Å
        corr_above_5, _ = scipy.stats.pearsonr(data_above_5['resolution'], data_above_5[col_name])
        correlation_below_5.append(corr_below_5)
        correlation_above_5.append(corr_above_5)
        col_names.append(col_name)
        print(corr_below_5, corr_above_5, col_name)

    return correlation_below_5, correlation_above_5, col_names

def get_resolution_bin_size_fromva(score_file):
    df = pd.read_csv(score_file, dtype={'id': str, 'resolution': float, 'name': str, 'qscore': float}, usecols=[0, 1, 2, 3])
    df = df.dropna()
    df_resolution_sorted = df.sort_values(by='resolution')
    current_qscore_resolution_bin = df_resolution_sorted['resolution_bin_size'].mode()[0]

    return float(current_qscore_resolution_bin)

def get_resolution_bin_size_fromfile(input_score_file, score_type='qscore'):
    """
        Get the resolution bin size from the input score file
    """
    df = pd.read_csv(input_score_file, dtype={'id': str, 'resolution': float, 'name': str, 'qscore': float},
                     usecols=[0, 1, 2, 3])
    df = df.dropna()
    df_resolution_sorted = df.sort_values(by='resolution')
    # create Q_whole in the df
    df_resolution_sorted['q_whole'] = df_resolution_sorted.apply(
        lambda x: score_whole(x, df_resolution_sorted, score_type), axis=1)

    # Create Q_relative in the df
    df_resolution_sorted = fast_qscore_resolution_bin(df_resolution_sorted, score_type=score_type)
    # Calculate correlation for resolution <= 5 Å and > 5 Å
    values = [round(x, 1) for x in np.arange(0.1, 1.6, 0.1)]
    correlatioin_below_5, correlation_above_5, col_names = resolution_qrelative_correlation(df_resolution_sorted,
                                                                                            values, score_type='qscore')
    optimal_index = find_optimal_correlation_index(correlatioin_below_5)
    optimal_resolution_bin = col_names[optimal_index].replace('q_relative_', '') if optimal_index is not None else None

    return float(optimal_resolution_bin)

def current_qscore_resolution_bin(score_file, update_resolution_bin_file=None):
    """
    Calculate the Q-score resolution bin based on the current all qscore in csv.
    """
    def save_and_log(cfg, bin_size, source):
        cfg['resolution_bin_size'] = bin_size
        try:
            save_config(cfg)
            print(f'Resolution bin size from file:{source}.')
            print(f'Current resolution bin size is saved in {CONFIG_FILE}.')
        except Exception as e:
            print(f'Error saving config file {CONFIG_FILE}: {e}')

    if not os.path.exists(CONFIG_FILE):
        cfg = {'resolution_bin_size': 0.5}
        save_config(cfg)
        print(f'Config file {CONFIG_FILE} created.')
    else:
        cfg = load_config()

    resolution_bin_size = cfg.get('resolution_bin_size')

    if update_resolution_bin_file is not None:
        resolution_bin_size = get_resolution_bin_size_fromfile(update_resolution_bin_file)
        save_and_log(cfg, resolution_bin_size, update_resolution_bin_file)
        return resolution_bin_size

    if resolution_bin_size is not None:
        print(f'Load resolution bin size {resolution_bin_size} from config file {CONFIG_FILE}')
        return resolution_bin_size

    print('No resolution bin size found in config file, will calculate from score file.')
    resolution_bin_size = get_resolution_bin_size_fromfile(score_file)
    save_and_log(cfg, resolution_bin_size, score_file)
    return resolution_bin_size
