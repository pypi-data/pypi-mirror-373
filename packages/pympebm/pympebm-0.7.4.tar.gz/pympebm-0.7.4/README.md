# `pympebm`


## Installation


```bash
pip install pympebm
```


## Data generation

To run `gen.py` first. Then to generate partial ordering datasets. `gen_partial.py`. 

## Change Log

- 2025-07-16 (V 0.0.6)
    - Added `mp_method = BT` in `algorithm.py` and `run.py`. 
    - Added `PL`. 
    - Fixed the bug in `generate_data.py`. 

- 2025-07-19 (V 0.0.7)
    - Added the class of `PlackettLuce`. 

- 2025-07-20 (V 0.0.15)
    - Updated the definition and implementation of conflict and certainty. 
    - Made sure `data` folder exists after uploading to pypi. 
    - Made sure `fixed_biomarker_order = True` if we use mixed patholgy in data generation. 
    - Fixed a bug in the calculation of `conflict`. 
    - Made sure the `algorithm.py` is using the correct energy calculation functions. 
    - Added entropy and certainty calculation in `MCMC` sampler. 
    - Made sure in `generate_data.py`, `certainty` is calculated based upon the `mp_method`.
    - Made sure in `generate_data.py`, we can tweak the paramter of `mcmc_iterations`, otherwise it will super slow. This is because the time complexity is `mcmc_iterations * sample_count`. 
    - Tested obtaining `ordering_array` from separate disease data files. Made some modifcations in `algorithm.py` to allow this. 

- 2025-07-23 (V 0.0.16 -- didn't push to Pypi)
    - Implemented the conflict version of using only discordant pairs. 

- 2025-07-25 (V 0.0.16)
    - Updated `algorithm.py` to reflect changes in the class of `PlackettLuce`. 

- 2025-07-26 (V 0.0.17)
    - Updated `generate_data.py` to skip calculating certainty and conflict if `sample_count <= 1`. 
  
- 2025-08-04 (V 0.1.7)
    - Use `fastsaebm` codes. 
    - Finished testing and data generation. 
    - With `m_{variant}` when number of repitition is 1. 
    - Fixed overflow bug in `prob_accept=min(1.0, np.exp(current_energy - new_energy))`. 
  
- 2025-08-04 (V 0.2.9)
    - Implemented the new certainty measure.  
    - Used the same `rng` all throughout in generate data. 
    - Added `save_details` to `run.py`.
    - Solved the logic bug of `save_details` and `save_results`.
    - Ensured the randomness again in `generate_data.py`.
  
- 2025-08-09 (V 0.3.1)
    - Used 15 biomarkers. 
    - Dynamically adjust dirichlet multinomial alpha array based on the number of biomarkers.
  
- 2025-08-10 (V 0.3.3)
    - Use numpy and numba (whenever possible) in `mp_utils.py`.

- 2025-08-11 (V 0.3.6)
    - Updated numba version
- 2025-08-12 (V 0.3.9)
    - Kept improving the numba version. Now it's faster. 
    - Include MCMC in PL sampling as well. 

- 2025-08-11 (V 0.4.0)
    - Add RMJ distance mallows.
  
- 2025-08-16 (V 0.4.2)
    - Try all `njit` in `mp_utils.py`. I want to test it on CHTC.

- 2025-08-17 (V 0.4.4)
    - I know using `np.random` is not helpful in `shuffle_order` func. Change back to the slow version.

- 2025-08-18 (V 0.4.10)
    - Try to use rng in func of `obtain_affected_and_non_clusters`.  
    - In mallows, use BT for central ranking sampling. 
    - Added `theta = 100` in mallows.
    - Added `mp_method = 'random'` in `generate_data.py`. 
    - Remobed `recodes` folder when running mp-ebm.

- 2025-08-19 (V 0.4.19)
    - Corrected an error: in data generation, for experiment 9, the noise_std should be max_length * noise_std_parameter rather than its square root. This is imprtant because after using square root, the noise_std in fact become larger, not smaller. For example, in our example where N = 10, the noise_std should be N*0.05 = 0.5, but after square root, it becomes 0.7. If N = 4, then std should be 02, but becomes 0.45 after square root. 
    - Added the `temperature` parameter for mallows sampling.
    - Reuse params inferred from individual diseases.
    - Used biomarkers and theta/phi params obtained from NACC data analysis.

- 2025-08-20 (v 0.5.1)
    - Used biomarkers and their theta/phi from both ADNI only.
    - Changed `'random'` to `'Random'` in `generate_data.py`.
    - Randomly choose two floats for new theta params for overlapping biomarkers.

- 2025-08-21 (V 0.5.4)
    - Try only 12 biomarkers for params.
    - Try 18 biomarkers for params.
    - Add rnadom pertubations to overlapped biomarkers params. 

- 2025-08-22 (V 0.5.6)
    - Try scaling factor for energy in `mh.py`

- 2025-08-23 (V 0.5.9)
    - Test differetn energy influence.
    - `use_scaling`
 
- 205-08-25 (V 0.6.0)
   - Test `percentile`.
  
- 205-08-26 (V 0.6.2)
  - Added analysis about `alignment` and `effect_size`. 


- 2025-08-27 (V 0.6.7)
  - Added `energy_prior` and `model_prior`. 
  - Mapped `energy_prior` to `mallows_temperature`.

- 2025-08-28 (V 0.6.9)
  - Removed `energy_prior`. Only use model `calibration`. 

- 2025-08-32 (V 0.7.3)
  - Modified the data generation just like in subtypes. 

- 2025-09-01 (V 0.7.4)
  - Removed the forcing range of `event times`. 
  