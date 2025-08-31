from pysubebm import generate, get_params_path
import numpy as np 
import json 
import re 
import os 
import yaml

def extract_components(filename):
    pattern = r'^j(\d+)_r([\d.]+)_E(.*?)_m(\d+)$'
    match = re.match(pattern, filename)
    if match:
        return match.groups()  # returns tuple (J, R, E, M)
    return None

def convert_np_types(obj):
    """Convert numpy types in a nested dictionary to Python standard types."""
    if isinstance(obj, dict):
        return {k: convert_np_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return convert_np_types(obj.tolist())
    else:
        return obj


if __name__ == '__main__':
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    rng = np.random.default_rng(53)
    cwd = os.path.dirname(__file__)

    OUTPUT_DIR = os.path.join(cwd, "my_data")
    # # Get path to default parameters
    params_file = get_params_path()

    # USE ADNI PARAMS OBTAINED FROM UCL GMM, and ordering obtained from PYSUSTAIN
    # params_file = f'{cwd}/ADNI_PYSUSTAIN.json'
    # SUBTYPE_RANKINGS = np.array([[10,  0,  2,  1,  3,  7,  6,  9, 11,  8,  5,  4],
    #    [10,  3,  5,  4,  0,  2,  1,  7,  9, 11,  8,  6]])

    # USE SAEBM PARAMS AND PYSUBEBM ORDERINGS
    # params_file = f'{cwd}/ADNI_SAEBM.json'
    # SUBTYPE_RANKINGS = np.array([
    #         [5, 6, 4, 3, 2, 1, 11, 7, 10, 0, 9, 8],
    #         [6, 4, 5, 8, 11, 10, 3, 0, 1, 9, 2, 7]
    #     ])

    with open(params_file) as f:
        params = json.load(f)

    JS = [100, 500, 1000]
    RS = [0.1, 0.5, 0.9]
    MS = range(1, 20)

    all_exp_dicts = []
    for exp_name in config['EXPERIMENT_NAMES']:
        random_state = rng.integers(0, 2**32 - 1)
        exp_dict = generate(
            experiment_name = exp_name,
            # params_file=params_file,
            params=params,
            js = config['JS'],
            rs = config['RS'],
            num_of_datasets_per_combination=config['N_VARIANTS'],
            output_dir=OUTPUT_DIR,
            seed=random_state,
            keep_all_cols = False,
            temperature_lo=config['TEMPERATURE_LO'],
            temperature_hi=config['TEMPERATURE_HI'],
            n_sub_lo=config['N_SUB_LO'],
            n_sub_hi=config['N_SUB_HI'],
            subtype_dirichlet_priors=config['GEN_DIRICHLET_PRIORS'],
            subtype_length_lo=config['SUBTYPE_LENGTH_LO'],
            # provided_subtype_orders=SUBTYPE_RANKINGS
        )
        all_exp_dicts.append(exp_dict)

    # flatten the dictionaries
    combined = {k: v for d in all_exp_dicts for k, v in d.items()}
    # convert numpy types to python standards types in order to save to json
    combined = convert_np_types(combined)

    # Dump the JSON
    with open(f"{cwd}/true_order_and_stages.json", "w") as f:
        json.dump(combined, f, indent=2)

    