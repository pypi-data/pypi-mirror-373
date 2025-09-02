
from shiny import App, ui, render, reactive
from pycompound_fy7392.spec_lib_matching import run_spec_lib_matching_on_HRMS_data 
from pycompound_fy7392.spec_lib_matching import run_spec_lib_matching_on_NRMS_data 
from pycompound_fy7392.plot_spectra import generate_plots_on_HRMS_data
from pycompound_fy7392.plot_spectra import generate_plots_on_NRMS_data
from pycompound_fy7392.spec_lib_matching import tune_params_on_HRMS_data
from pycompound_fy7392.spec_lib_matching import tune_params_on_NRMS_data
import subprocess
import traceback
from pathlib import Path
import pandas as pd


def split_or_wrap(s):
    s = str(s)
    def parse(x):
        x = x.strip()
        if x.lower() == 'true':
            return True
        elif x.lower() == 'false':
            return False
        try:
            return int(x)
        except ValueError:
            try:
                return float(x)
            except ValueError:
                return x

    if ',' not in s:
        return [parse(s)]
    else:
        return [parse(item) for item in s.split(',')]


def custom_on_off_to_bool(lst):
    if lst == ['no']:
        return [False]
    elif lst == ['yes']:
        return [True]
    elif lst == ['no','yes']:
        return [False,True]
    elif lst == ['yes','no']:
        return [False,True]
    elif not lst:
        return [False]
    else:
        raise ValueError(f"Unhandled input: {lst}")



app_ui = ui.page_fluid(
        ui.div(
            ui.input_select("choice", "Choose an option:", ["Run spectral library matching to identify unknown compounds", "Tune parameters with a query library with known compound IDs", "Plot two spectra"]),
            ui.input_radio_buttons("chromatography_platform", "Choose chromatography platform:", ["HRMS","NRMS"]),
            style="width: 2000px; max-width: none;"),
        ui.output_ui("dynamic_inputs"),
        ui.output_text("status_output")
)

def server(input, output, session):
    run_status = reactive.Value("Waiting for input...")

    @output
    @render.ui
    def dynamic_inputs():
        if input.choice() == "Run spectral library matching to identify unknown compounds":
            if input.chromatography_platform() == "HRMS":
                return ui.TagList(
                        ui.input_file("query_data", "Upload query dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_file("reference_data", "Upload reference dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_select("similarity_measure", "Select similarity measure:", ["cosine", "shannon", "renyi", "tsallis"]),
                        ui.input_select("high_quality_reference_library", "Indicate whether the reference library is considered to be of high quality. If true, then the spectrum preprocessing transformations of filtering and noise removal are performed only on the query spectrum/spectra.", [False,True]),
                        ui.input_text("spectrum_preprocessing_order", "Input a sequence of characters denoting the order in which spectrum preprocessing transformations should be applied. Available characters/transformations are C (centroiding), F (filtering), M (matching), N (noise removal), L (low-entropy transformation), and W (weight factor transformation. M must be in sequence, and if C is performed, then C must be performed before M.", "FCNMWL"),
                        ui.input_numeric("mz_min", "Enter numeric value for minimum mass/charge ratio for filtering:", 0),
                        ui.input_numeric("mz_max", "Enter numeric value for minimum mass/charge ratio for filtering:", 99999999),
                        ui.input_numeric("int_min", "Enter numeric value for minimum intensity for filtering:", 0),
                        ui.input_numeric("int_max", "Enter numeric value for maximum intensity for filtering:", 999999999),
                        ui.input_numeric("window_size_centroiding", "Enter numeric value for the centroiding window-size:", 0.5),
                        ui.input_numeric("window_size_matching", "Enter numeric value for the matching window-size:", 0.5),
                        ui.input_numeric("noise_threshold", "Enter numeric value for the noise removal threshold:", 0.0),
                        ui.input_numeric("wf_mz", "Enter numeric value for the mass/charge weight factor:", 0.0),
                        ui.input_numeric("wf_int", "Enter numeric value for the intensity weight factor:", 1.0),
                        ui.input_numeric("LET_threshold", "Enter non-negative numeric value for the low-entropy threshold:", 0.0),
                        ui.input_numeric("entropy_dimension", "Enter non-negative, non-unity numeric value for the entropy dimension (only applicable to Renyi and Tsallis):", 1.1),
                        ui.input_numeric("n_top_matches_to_save", "Enter positive integer for the number of top matches to save:", 1),
                        ui.input_text("output_identification", "Path to identification output:", f'{Path.cwd()}/output_identification.csv'),
                        ui.input_text("output_similarity_scores", "Path to output file of similarity scores:", f'{Path.cwd()}/output_similarity_scores.csv'),
                        ui.input_action_button("run_btn", "Run"))
            else:
                return ui.TagList(
                        ui.input_file("query_data", "Upload query dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_file("reference_data", "Upload reference dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_select("similarity_measure", "Select similarity measure:", ["cosine", "shannon", "renyi", "tsallis"]),
                        ui.input_select("high_quality_reference_library", "Indicate whether the reference library is considered to be of high quality. If true, then the spectrum preprocessing transformations of filtering and noise removal are performed only on the query spectrum/spectra.", [False,True]),
                        ui.input_text("spectrum_preprocessing_order", "Input a sequence of characters denoting the order in which spectrum preprocessing transformations should be applied. Available characters/transformations are F (filtering), N (noise removal), L (low-entropy transformation), and W (weight factor transformation).", "FNLW"),
                        ui.input_numeric("mz_min", "Enter numeric value for minimum mass/charge ratio for filtering:", 0),
                        ui.input_numeric("mz_max", "Enter numeric value for minimum mass/charge ratio for filtering:", 99999999),
                        ui.input_numeric("int_min", "Enter numeric value for minimum intensity for filtering:", 0),
                        ui.input_numeric("int_max", "Enter numeric value for maximum intensity for filtering:", 999999999),
                        ui.input_numeric("noise_threshold", "Enter numeric value for the noise removal threshold:", 0.0),
                        ui.input_numeric("wf_mz", "Enter numeric value for the mass/charge weight factor:", 0.0),
                        ui.input_numeric("wf_int", "Enter numeric value for the intensity weight factor:", 1.0),
                        ui.input_numeric("LET_threshold", "Enter non-negative numeric value for the low-entropy threshold:", 0.0),
                        ui.input_numeric("entropy_dimension", "Enter non-negative, non-unity numeric value for the entropy dimension (only applicable to Renyi and Tsallis):", 1.1),
                        ui.input_numeric("n_top_matches_to_save", "Enter positive integer for the number of top matches to save:", 1),
                        ui.input_text("output_identification", "Path to identification output:", f'{Path.cwd()}/output_identification.csv'),
                        ui.input_text("output_similarity_scores", "Path to output file of similarity scores:", f'{Path.cwd()}/output_similarity_scores.csv'),
                        ui.input_action_button("run_btn", "Run"))

        elif input.choice() == "Tune parameters with a query library with known compound IDs":
            if input.chromatography_platform() == "HRMS":
                return ui.TagList(
                        ui.input_file("query_data", "Upload query dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_file("reference_data", "Upload reference dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_checkbox_group("similarity_measure", "Select similarity measure(s):", ["cosine", "shannon", "renyi", "tsallis"]),
                        ui.input_checkbox_group("high_quality_reference_library", "Indicate whether the reference library is considered to be of high quality. If True, then the spectrum preprocessing transformations of filtering and noise removal are performed only on the query spectrum/spectra.", ["no","yes"]),
                        ui.input_text("spectrum_preprocessing_order", "Input a sequence of characters denoting the order in which spectrum preprocessing transformations should be applied. Available characters/transformations are C (centroiding), F (filtering), M (matching), N (noise removal), L (low-entropy transformation), and W (weight factor transformation. M must be in sequence, and if C is performed, then C must be performed before M. If multiple spectrum preprocessing orders are to be tried, separate by comma.", "FCNMWL"),
                        ui.input_text("mz_min", "Enter numeric value(s) for minimum mass/charge ratio for filtering. Separate multiple entries with comma.", 0),
                        ui.input_text("mz_max", "Enter numeric value(s) for minimum mass/charge ratio for filtering. Separate multiple entries with comma.", 99999999),
                        ui.input_text("int_min", "Enter numeric value(s) for minimum intensity for filtering. Separate multiple entries with comma.", 0),
                        ui.input_text("int_max", "Enter numeric value(s) for maximum intensity for filtering. Separate multiple entries with comma.", 999999999),
                        ui.input_text("window_size_centroiding", "Enter numeric value(s) for the centroiding window-size. Separate multiple entries with comma.", 0.5),
                        ui.input_text("window_size_matching", "Enter numeric value(s) for the matching window-size. Separate multiple entries with comma.", 0.5),
                        ui.input_text("noise_threshold", "Enter numeric value(s) for the noise removal threshold. Separate multiple entries with comma.", 0.0),
                        ui.input_text("wf_mz", "Enter numeric value(s) for the mass/charge weight factor. Separate multiple entries with comma.", 0.0),
                        ui.input_text("wf_int", "Enter numeric value(s) for the intensity weight factor. Separate multiple entries with comma.", 1.0),
                        ui.input_text("LET_threshold", "Enter non-negative numeric value(s) for the low-entropy threshold. Separate multiple entries with comma.", 0.0),
                        ui.input_text("entropy_dimension", "Enter non-negative, non-unity numeric value(s) for the entropy dimension (only applicable to Renyi and Tsallis). Separate multiple entries with comma.", 1.1),
                        ui.input_text("output_path", "Path to parameter tuning output:", f'{Path.cwd()}/output_parameter_tuning.csv'),
                        ui.input_action_button("run_btn", "Run"))
            else:
                return ui.TagList(
                        ui.input_file("query_data", "Upload query dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_file("reference_data", "Upload reference dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_checkbox_group("similarity_measure", "Select similarity measure(s):", ["cosine", "shannon", "renyi", "tsallis"]),
                        ui.input_checkbox_group("high_quality_reference_library", "Indicate whether the reference library is considered to be of high quality. If True, then the spectrum preprocessing transformations of filtering and noise removal are performed only on the query spectrum/spectra.", ["no","yes"]),
                        ui.input_text("spectrum_preprocessing_order", "Input a sequence of characters denoting the order in which spectrum preprocessing transformations should be applied. Available characters/transformations are F (filtering), N (noise removal), L (low-entropy transformation), and W (weight factor transformation).", "FNLW"),
                        ui.input_text("mz_min", "Enter numeric value(s) for minimum mass/charge ratio for filtering. Separate multiple entries with comma.", 0),
                        ui.input_text("mz_max", "Enter numeric value(s) for minimum mass/charge ratio for filtering. Separate multiple entries with comma.", 99999999),
                        ui.input_text("int_min", "Enter numeric value(s) for minimum intensity for filtering. Separate multiple entries with comma.", 0),
                        ui.input_text("int_max", "Enter numeric value(s) for maximum intensity for filtering. Separate multiple entries with comma.", 999999999),
                        ui.input_text("noise_threshold", "Enter numeric value(s) for the noise removal threshold. Separate multiple entries with comma.", 0.0),
                        ui.input_text("wf_mz", "Enter numeric value(s) for the mass/charge weight factor. Separate multiple entries with comma.", 0.0),
                        ui.input_text("wf_int", "Enter numeric value(s) for the intensity weight factor. Separate multiple entries with comma.", 1.0),
                        ui.input_text("LET_threshold", "Enter non-negative numeric value(s) for the low-entropy threshold. Separate multiple entries with comma.", 0.0),
                        ui.input_text("entropy_dimension", "Enter non-negative, non-unity numeric value(s) for the entropy dimension (only applicable to Renyi and Tsallis). Separate multiple entries with comma.", 1.1),
                        ui.input_text("output_path", "Path to parameter tuning output:", f'{Path.cwd()}/output_parameter_tuning.csv'),
                        ui.input_action_button("run_btn", "Run"))


        elif input.choice() == "Plot two spectra":
            if input.chromatography_platform() == "HRMS":
                return ui.TagList(
                        ui.input_file("query_data", "Upload query dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_file("reference_data", "Upload reference dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_text("spectrum_ID1", "Input ID of one spectrum to be plotted:", None),
                        ui.input_text("spectrum_ID2", "Input ID of another spectrum to be plotted:", None),
                        ui.input_select("similarity_measure", "Select similarity measure:", ["cosine", "shannon", "renyi", "tsallis"]),
                        ui.input_select("high_quality_reference_library", "Indicate whether the reference library is considered to be of high quality. If True, then the spectrum preprocessing transformations of filtering and noise removal are performed only on the query spectrum/spectra.", [False,True]),
                        ui.input_text("spectrum_preprocessing_order", "Input a sequence of characters denoting the order in which spectrum preprocessing transformations should be applied. Available characters/transformations are C (centroiding), F (filtering), M (matching), N (noise removal), L (low-entropy transformation), and W (weight factor transformation. M must be in sequence, and if C is performed, then C must be performed before M. If multiple spectrum preprocessing orders are to be tried, separate by comma.", "FCNMWL"),
                        ui.input_numeric("mz_min", "Enter numeric value for minimum mass/charge ratio for filtering. Separate multiple entries with comma.", 0),
                        ui.input_numeric("mz_max", "Enter numeric value for minimum mass/charge ratio for filtering. Separate multiple entries with comma.", 99999999),
                        ui.input_numeric("int_min", "Enter numeric value for minimum intensity for filtering. Separate multiple entries with comma.", 0),
                        ui.input_numeric("int_max", "Enter numeric value for maximum intensity for filtering. Separate multiple entries with comma.", 999999999),
                        ui.input_numeric("window_size_centroiding", "Enter numeric value for the centroiding window-size. Separate multiple entries with comma.", 0.5),
                        ui.input_numeric("window_size_matching", "Enter numeric value for the matching window-size. Separate multiple entries with comma.", 0.5),
                        ui.input_numeric("noise_threshold", "Enter numeric value for the noise removal threshold. Separate multiple entries with comma.", 0.0),
                        ui.input_numeric("wf_mz", "Enter numeric value for the mass/charge weight factor. Separate multiple entries with comma.", 0.0),
                        ui.input_numeric("wf_int", "Enter numeric value for the intensity weight factor. Separate multiple entries with comma.", 1.0),
                        ui.input_numeric("LET_threshold", "Enter non-negative numeric value for the low-entropy threshold. Separate multiple entries with comma.", 0.0),
                        ui.input_numeric("entropy_dimension", "Enter non-negative, non-unity numeric value for the entropy dimension (only applicable to Renyi and Tsallis). Separate multiple entries with comma.", 1.1),
                        ui.input_select("y_axis_transformation", "Select the transformation to apply to the intensity axis of the generated plots:", ["normalized", "none", "log10", "sqrt"]),
                        ui.input_text("output_path", "Path to parameter tuning output:", f'{Path.cwd()}/output_plots.pdf'),
                        ui.input_action_button("run_btn", "Run"))
            else:
                return ui.TagList(
                        ui.input_file("query_data", "Upload query dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_file("reference_data", "Upload reference dataset (mgf, mzML, cdf, msp, or csv):"),
                        ui.input_text("spectrum_ID1", "Input ID of one spectrum to be plotted:", None),
                        ui.input_text("spectrum_ID2", "Input ID of another spectrum to be plotted:", None),
                        ui.input_select("similarity_measure", "Select similarity measure:", ["cosine", "shannon", "renyi", "tsallis"]),
                        ui.input_select("high_quality_reference_library", "Indicate whether the reference library is considered to be of high quality. If True, then the spectrum preprocessing transformations of filtering and noise removal are performed only on the query spectrum/spectra.", [False,True]),
                        ui.input_text("spectrum_preprocessing_order", "Input a sequence of characters denoting the order in which spectrum preprocessing transformations should be applied. Available characters/transformations are F (filtering), N (noise removal), L (low-entropy transformation), and W (weight factor transformation).", "FNLW"),
                        ui.input_numeric("mz_min", "Enter numeric value for minimum mass/charge ratio for filtering. Separate multiple entries with comma.", 0),
                        ui.input_numeric("mz_max", "Enter numeric value for minimum mass/charge ratio for filtering. Separate multiple entries with comma.", 99999999),
                        ui.input_numeric("int_min", "Enter numeric value for minimum intensity for filtering. Separate multiple entries with comma.", 0),
                        ui.input_numeric("int_max", "Enter numeric value for maximum intensity for filtering. Separate multiple entries with comma.", 999999999),
                        ui.input_numeric("noise_threshold", "Enter numeric value for the noise removal threshold. Separate multiple entries with comma.", 0.0),
                        ui.input_numeric("wf_mz", "Enter numeric value for the mass/charge weight factor. Separate multiple entries with comma.", 0.0),
                        ui.input_numeric("wf_int", "Enter numeric value for the intensity weight factor. Separate multiple entries with comma.", 1.0),
                        ui.input_numeric("LET_threshold", "Enter non-negative numeric value for the low-entropy threshold. Separate multiple entries with comma.", 0.0),
                        ui.input_numeric("entropy_dimension", "Enter non-negative, non-unity numeric value for the entropy dimension (only applicable to Renyi and Tsallis). Separate multiple entries with comma.", 1.1),
                        ui.input_select("y_axis_transformation", "Select the transformation to apply to the intensity axis of the generated plots:", ["normalized", "none", "log10", "sqrt"]),
                        ui.input_text("output_path", "Path to parameter tuning output:", f'{Path.cwd()}/output_plot.pdf'),
                        ui.input_action_button("run_btn", "Run"))


    @reactive.effect
    @reactive.event(input.run_btn)
    def _():
        choice = input.choice()

        if choice == "Run spectral library matching to identify unknown compounds":
            if input.chromatography_platform() == "HRMS":
                try:
                    run_spec_lib_matching_on_HRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], likely_reference_ids=None, similarity_measure=input.similarity_measure(), spectrum_preprocessing_order=input.spectrum_preprocessing_order(), high_quality_reference_library=input.high_quality_reference_library(), mz_min=input.mz_min(), mz_max=input.mz_max(), int_min=input.int_min(), int_max=input.int_max(), window_size_centroiding=input.window_size_centroiding(), window_size_matching=input.window_size_matching(), noise_threshold=input.noise_threshold(), wf_mz=input.wf_mz(), wf_intensity=input.wf_int(), LET_threshold=input.LET_threshold(), entropy_dimension=input.entropy_dimension(), n_top_matches_to_save=input.n_top_matches_to_save(), print_id_results=False, output_identification=f'{Path.cwd()}/output_identification.csv', output_similarity_scores=f'{Path.cwd()}/output_similarity_scores.csv')
                    df_identification_tmp = pd.read_csv(f'{Path.cwd()}/output_identification.csv')
                    df_similarity_scores_tmp = pd.read_csv(f'{Path.cwd()}/output_similarity_scores.csv')
                    df_identification_tmp.to_csv(input.output_identification(), index=False)
                    df_similarity_scores_tmp.to_csv(input.output_similarity_scores(), index=False)
                    run_status.set(f"✅  Spectral library matching has finished.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")
            elif input.chromatography_platform == "NRMS":
                try:
                    run_spec_lib_matching_on_NRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], likely_reference_ids=None, similarity_measure=input.similarity_measure(), spectrum_preprocessing_order=input.spectrum_preprocessing_order(), high_quality_reference_library=input.high_quality_reference_library(), mz_min=input.mz_min(), mz_max=input.mz_max(), int_min=input.int_min(), int_max=input.int_max(), noise_threshold=input.noise_threshold(), wf_mz=input.wf_mz(), wf_intensity=input.wf_int(), LET_threshold=input.LET_threshold(), entropy_dimension=input.entropy_dimension(), n_top_matches_to_save=input.n_top_matches_to_save(), print_id_results=False, output_identification=f'{Path.cwd()}/output_identification.csv', output_similarity_scores=f'{Path.cwd()}/output_similarity_scores.csv')
                    df_identification_tmp = pd.read_csv(f'{Path.cwd()}/output_identification.csv')
                    df_similarity_scores_tmp = pd.read_csv(f'{Path.cwd()}/output_similarity_scores.csv')
                    df_identification_tmp.to_csv(input.output_identification(), index=False)
                    df_similarity_scores_tmp.to_csv(input.output_similarity_scores(), index=False)
                    run_status.set(f"✅  Spectral library matching has finished.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")



        elif choice == "Tune parameters with a query library with known compound IDs":
            high_quality_reference_library_tmp = custom_on_off_to_bool(list(input.high_quality_reference_library()))
            if input.chromatography_platform() == "HRMS":
                try:
                    grid = {'similarity_measure':list(input.similarity_measure()),
                            'high_quality_reference_library':high_quality_reference_library_tmp,
                            'spectrum_preprocessing_order':split_or_wrap(input.spectrum_preprocessing_order()),
                            'mz_min':split_or_wrap(input.mz_min()),
                            'mz_max':split_or_wrap(input.mz_max()),
                            'int_min':split_or_wrap(input.int_min()),
                            'int_max':split_or_wrap(input.int_max()),
                            'window_size_centroiding':split_or_wrap(input.window_size_centroiding()),
                            'window_size_matching':split_or_wrap(input.window_size_matching()),
                            'noise_threshold':split_or_wrap(input.noise_threshold()),
                            'wf_mz':split_or_wrap(input.wf_mz()),
                            'wf_int':split_or_wrap(input.wf_int()),
                            'LET_threshold':split_or_wrap(input.LET_threshold()),
                            'entropy_dimension':split_or_wrap(input.entropy_dimension())}
                    tune_params_on_HRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], grid=grid, output_path=input.output_path())
                    run_status.set(f"✅  Parameter tuning has finished.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")
            elif input.chromatography_platform() == "NRMS":
                try:
                    grid = {'similarity_measure':list(input.similarity_measure()),
                            'high_quality_reference_library':high_quality_reference_library_tmp,
                            'spectrum_preprocessing_order':split_or_wrap(input.spectrum_preprocessing_order()),
                            'mz_min':split_or_wrap(input.mz_min()),
                            'mz_max':split_or_wrap(input.mz_max()),
                            'int_min':split_or_wrap(input.int_min()),
                            'int_max':split_or_wrap(input.int_max()),
                            'noise_threshold':split_or_wrap(input.noise_threshold()),
                            'wf_mz':split_or_wrap(input.wf_mz()),
                            'wf_int':split_or_wrap(input.wf_int()),
                            'LET_threshold':split_or_wrap(input.LET_threshold()),
                            'entropy_dimension':split_or_wrap(input.entropy_dimension())}
                    tune_params_on_NRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], grid=grid, output_path=input.output_path())
                    run_status.set(f"✅  Parameter tuning has finished.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")




        elif choice == "Plot two spectra":
            if len(input.spectrum_ID1())==0:
                spectrum_ID1 = None
            if len(input.spectrum_ID2())==0:
                spectrum_ID2 = None

            if input.chromatography_platform() == "HRMS":
                try:
                    generate_plots_on_HRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], spectrum_ID1=spectrum_ID1, spectrum_ID2=spectrum_ID2, similarity_measure=input.similarity_measure(), spectrum_preprocessing_order=input.spectrum_preprocessing_order(), high_quality_reference_library=input.high_quality_reference_library(), mz_min=input.mz_min(), mz_max=input.mz_max(), int_min=input.int_min(), int_max=input.int_max(), window_size_centroiding=input.window_size_centroiding(), window_size_matching=input.window_size_matching(), noise_threshold=input.noise_threshold(), wf_mz=input.wf_mz(), wf_intensity=input.wf_int(), LET_threshold=input.LET_threshold(), entropy_dimension=input.entropy_dimension(), y_axis_transformation=input.y_axis_transformation(), output_path=input.output_path())
                    run_status.set(f"✅  Plotting has finished.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")
            elif input.chromatography_platform == "NRMS":
                try:
                    generate_plots_on_NRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], spectrum_ID1=input.spectrum_ID1(), spectrum_ID2=input.spectrum_ID2(), similarity_measure=input.similarity_measure(), spectrum_preprocessing_order=input.spectrum_preprocessing_order(), high_quality_reference_library=input.high_quality_reference_library(), mz_min=input.mz_min(), mz_max=input.mz_max(), int_min=input.int_min(), int_max=input.int_max(), noise_threshold=input.noise_threshold(), wf_mz=input.wf_mz(), wf_intensity=input.wf_int(), LET_threshold=input.LET_threshold(), entropy_dimension=input.entropy_dimension(), y_axis_transformation=input.y_axis_transformation(), output_path=input.output_path())
                    run_status.set(f"✅  Plotting has finished.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")

    @output
    @render.text
    def status_output():
        return run_status.get()


app = App(app_ui, server)

