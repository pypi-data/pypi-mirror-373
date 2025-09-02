
from pycompound_fy7392.spec_lib_matching import tune_params_on_HRMS_data
from pycompound_fy7392.spec_lib_matching import tune_params_on_NRMS_data
from pathlib import Path
import os

print('\n\ntest #1:')
tune_params_on_HRMS_data(query_data=f'{Path.cwd()}/data/tuning/lcms_query_library.csv', reference_data=f'{Path.cwd()}/data/lcms_reference_library.csv', output_path=f'{Path.cwd()}/tuning_param_output_test1.csv')

print('\n\ntest #2:')
tune_params_on_HRMS_data(query_data=f'{Path.cwd()}/data/tuning/lcms_query_library.csv', reference_data=f'{Path.cwd()}/data/lcms_reference_library.csv', grid={'similarity_measure':['cosine'], 'spectrum_preprocessing_order':['FCNMWL'], 'mz_min':[0], 'mz_max':[9999999], 'int_min':[0], 'int_max':[99999999], 'window_size_centroiding':[0.5], 'window_size_matching':[0.1,0.5], 'noise_threshold':[0.0], 'wf_mz':[0.0], 'wf_int':[1.0], 'LET_threshold':[0.0], 'entropy_dimension':[1.1], 'high_quality_reference_library':[False]}, output_path=f'{Path.cwd()}/tuning_param_output_test2.csv')

print('\n\ntest #3:')
tune_params_on_NRMS_data(query_data=f'{Path.cwd()}/data/tuning/gcms_query_library.csv', reference_data=f'{Path.cwd()}/data/gcms_reference_library.csv', output_path=f'{Path.cwd()}/tuning_param_output_test3.csv')

print('\n\ntest #4:')
tune_params_on_NRMS_data(query_data=f'{Path.cwd()}/data/tuning/gcms_query_library.csv', reference_data=f'{Path.cwd()}/data/gcms_reference_library.csv', grid={'similarity_measure':['cosine','shannon'], 'spectrum_preprocessing_order':['FNLW'], 'mz_min':[0], 'mz_max':[9999999], 'int_min':[0], 'int_max':[99999999], 'noise_threshold':[0.0,0.1], 'wf_mz':[0.0], 'wf_int':[1.0], 'LET_threshold':[0.0,3.0], 'entropy_dimension':[1.1], 'high_quality_reference_library':[False]}, output_path=f'{Path.cwd()}/tuning_param_output_test4.csv')

