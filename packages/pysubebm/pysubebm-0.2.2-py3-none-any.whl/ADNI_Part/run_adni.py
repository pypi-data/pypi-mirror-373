import sys 
import os 
sys.path.append(os.getcwd())

import os 
from pysubebm import run_subebm
import utils_adni
import yaml
import json 
import numpy as np 

meta_data = ['PTID', 'DX_bl', 'VISCODE', 'COLPROT']

'''
Cognition: MoCA (global), Trails B (executive), Digit Span (attention/WM), Logical Memory (episodic).

Function: FAQ (daily living skills).

Imaging: FDG-PET (metabolism, cross-disease marker).
'''

select_biomarkers = [
    'MMSE_bl', 'Ventricles_bl', 'WholeBrain_bl', 'MidTemp_bl', 
    'Fusiform_bl', 'Entorhinal_bl', 'Hippocampus_bl', 'ADAS13_bl', 
    'PTAU_bl', 'TAU_bl', 'ABETA_bl', 'RAVLT_immediate_bl', 
    'ICV_bl', 
]

diagnosis_list = ['CN', 'EMCI', 'LMCI', 'AD']

raw = f'pysubebm/test/notebooks/data/ADNIMERGE.csv'

if __name__ == "__main__":
    # Get directories correct
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current working directory: {base_dir}")

    OUTPUT_DIR = os.path.join(base_dir, 'adni_norm_results')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rng = np.random.default_rng(42)
    random_state = rng.integers(0, 2**32 - 1)

    # raw = os.path.join(base_dir, raw)

    # adni_filtered = utils_adni.get_adni_filtered(raw, meta_data, select_biomarkers, diagnosis_list)
    # debm_output, data_matrix, df_long, participant_dx_dict, ordered_biomarkers = utils_adni.process_data(adni_filtered, ventricles_log=False, tau_log=False)
    # df = debm_output.rename(columns={'PTID': 'participant'})
    # df.drop(columns=['Diagnosis'], inplace=True)
    # df['diseased'] = data_matrix[:,-1].astype(bool)
                                     
    # df.to_csv('adni.csv', index=False)

    results = run_subebm(
        data_file=os.path.join(base_dir, 'adni.csv'),
        n_subtypes=2,
        output_dir=OUTPUT_DIR,
        n_iter=10000,
        n_shuffle=2,
        n_subtype_shuffle=2,
        burn_in=100,
        thinning=1,
        seed=random_state, ## 42 turns out to be the best
        save_results=True
    )
