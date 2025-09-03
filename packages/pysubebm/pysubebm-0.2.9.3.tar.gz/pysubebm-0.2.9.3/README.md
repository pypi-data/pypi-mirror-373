# `pysubebm`


## Installation

```bash
pip install git+https://github.com/noxtoby/awkde
pip install git+https://github.com/hongtaoh/ucl_kde_ebm
pip install git+https://github.com/hongtaoh/pySuStaIn
```


```bash
pip install pysubebm
```

## Changelogs

- 2025-08-21 (V 0.0.3)
    - Did the `generate_data.py`.
- 2025-08-22 (V 0.0.5)
    - Did the `mh.py`
    - Correct conjugate_priors implementation.
- 2025-08-23 (V 0.1.2)
    - Improved functions in `utils.py`.
- 2025-08-29 (V 0.1.3)
    - Didn't change much. 
- 2025-08-30 (V 0.1.8)
    - Optimized `compute_likelihood_and_posteriors` such that we only calculate healthy participants' ln likelihood once every time. 
    - Made sure subtype assignment accuracy does not apply to healthy participants at all. 
    - Fixed a major bug in data generation. The very low subtype assignment might be due to this error.
    - Included both subtype accuracy in `run.py`. 
- 2025-08-31 (V 0.2.5)
    - Resacle event times and disease stages for exp7-9 such that max(event_times) = max_stage -1, and max(disease_stages) = max_stage. 
    - Changed the experiments and some of the implementation. 
    - Forcing `max(event_times) = max_stage -1`, but not forcing disease stages. 
- 2025-09-01 (V 0.2.9)
    - REMOVED THE Forcing `max(event_times) = max_stage -1`
    - Modified the `run.py`.
- 2025-09-02 (V 0.2.9.2)
    - Redid the staging and subtyping. 