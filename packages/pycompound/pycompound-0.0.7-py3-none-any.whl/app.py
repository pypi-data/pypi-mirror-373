
from shiny import App, ui, reactive, render
from pycompound_fy7392.spec_lib_matching import run_spec_lib_matching_on_HRMS_data 
from pycompound_fy7392.spec_lib_matching import run_spec_lib_matching_on_NRMS_data 
from pycompound_fy7392.spec_lib_matching import tune_params_on_HRMS_data
from pycompound_fy7392.spec_lib_matching import tune_params_on_NRMS_data
from pycompound_fy7392.plot_spectra import generate_plots_on_HRMS_data
from pycompound_fy7392.plot_spectra import generate_plots_on_NRMS_data
from pathlib import Path
import subprocess
import traceback
import asyncio
import io
import matplotlib.pyplot as plt


def plot_spectra_ui(platform: str):
    # Base inputs common to all platforms
    base_inputs = [
        ui.input_file("query_data", "Upload query dataset (mgf, mzML, cdf, msp, or csv):"),
        ui.input_file("reference_data", "Upload reference dataset (mgf, mzML, cdf, msp, or csv):"),
        ui.input_text("spectrum_ID1", "Input ID of one spectrum to be plotted:", None),
        ui.input_text("spectrum_ID2", "Input ID of another spectrum to be plotted:", None),
        ui.input_select("similarity_measure", "Select similarity measure:", ["cosine","shannon","renyi","tsallis","mixture","jaccard","dice","3w_jaccard","sokal_sneath","binary_cosine","mountford","mcconnaughey","driver_kroeber","simpson","braun_banquet","fager_mcgowan","kulczynski","intersection","hamming","hellinger"]),
        ui.input_select(
            "high_quality_reference_library",
            "Indicate whether the reference library is considered high quality. "
            "If True, filtering and noise removal are only applied to the query spectra.",
            [False, True],
        ),
    ]

    # Extra inputs depending on platform
    if platform == "HRMS":
        extra_inputs = [
            ui.input_text(
                "spectrum_preprocessing_order",
                "Sequence of characters for preprocessing order (C, F, M, N, L, W). M must be included, C before M if used.",
                "FCNMWL",
            ),
            ui.input_numeric("window_size_centroiding", "Centroiding window-size:", 0.5),
            ui.input_numeric("window_size_matching", "Matching window-size:", 0.5),
        ]
    else:
        extra_inputs = [
            ui.input_text(
                "spectrum_preprocessing_order",
                "Sequence of characters for preprocessing order (F, N, L, W).",
                "FNLW",
            )
        ]

    # Numeric inputs
    numeric_inputs = [
        ui.input_numeric("mz_min", "Minimum m/z for filtering:", 0),
        ui.input_numeric("mz_max", "Maximum m/z for filtering:", 99999999),
        ui.input_numeric("int_min", "Minimum intensity for filtering:", 0),
        ui.input_numeric("int_max", "Maximum intensity for filtering:", 999999999),
        ui.input_numeric("noise_threshold", "Noise removal threshold:", 0.0),
        ui.input_numeric("wf_mz", "Mass/charge weight factor:", 0.0),
        ui.input_numeric("wf_int", "Intensity weight factor:", 1.0),
        ui.input_numeric("LET_threshold", "Low-entropy threshold:", 0.0),
        ui.input_numeric("entropy_dimension", "Entropy dimension (Renyi/Tsallis only):", 1.1),
    ]

    # Y-axis transformation select input
    select_input = ui.input_select(
        "y_axis_transformation",
        "Transformation to apply to intensity axis:",
        ["normalized", "none", "log10", "sqrt"],
    )

    # Run and Back buttons
    run_button = ui.input_action_button("run_btn", "Run", style="font-size:16px; padding:15px 30px; width:200px; height:80px")
    back_button = ui.input_action_button("back", "Back to main menu", style="font-size:16px; padding:15px 30px; width:200px; height:80px")

    #print(len(extra_inputs))
    # Layout base_inputs and extra_inputs in columns
    if platform == "HRMS":
        inputs_columns = ui.layout_columns(
            ui.div(base_inputs[0:5], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div([base_inputs[5:6], *extra_inputs], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div(numeric_inputs[0:5], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div([numeric_inputs[5:10], select_input], style="display:flex; flex-direction:column; gap:10px;"),
            col_widths=(3, 3, 3, 3),
        )
    elif platform == "NRMS":
        inputs_columns = ui.layout_columns(
            ui.div(base_inputs[0:5], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div([base_inputs[5:6], *extra_inputs], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div(numeric_inputs[0:5], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div([numeric_inputs[5:10], select_input], style="display:flex; flex-direction:column; gap:10px;"),
            col_widths=(3, 3, 3, 3),
        )

    # Combine everything
    return ui.div(
        ui.TagList(
            ui.h2("Plot Spectra"),
            inputs_columns,
            run_button,
            back_button
        ),
    )



def run_spec_lib_matching_ui(platform: str):
    # Base inputs common to all platforms
    base_inputs = [
        ui.input_file("query_data", "Upload query dataset (mgf, mzML, cdf, msp, or csv):"),
        ui.input_file("reference_data", "Upload reference dataset (mgf, mzML, cdf, msp, or csv):"),
        ui.input_select("similarity_measure", "Select similarity measure:", ["cosine","shannon","renyi","tsallis","mixture","jaccard","dice","3w_jaccard","sokal_sneath","binary_cosine","mountford","mcconnaughey","driver_kroeber","simpson","braun_banquet","fager_mcgowan","kulczynski","intersection","hamming","hellinger"]),
        ui.input_select(
            "high_quality_reference_library",
            "Indicate whether the reference library is considered high quality. "
            "If True, filtering and noise removal are only applied to the query spectra.",
            [False, True],
        ),
    ]

    # Extra inputs depending on platform
    if platform == "HRMS":
        extra_inputs = [
            ui.input_text(
                "spectrum_preprocessing_order",
                "Sequence of characters for preprocessing order (C, F, M, N, L, W). M must be included, C before M if used.",
                "FCNMWL",
            ),
            ui.input_numeric("window_size_centroiding", "Centroiding window-size:", 0.5),
            ui.input_numeric("window_size_matching", "Matching window-size:", 0.5),
        ]
    else:
        extra_inputs = [
            ui.input_text(
                "spectrum_preprocessing_order",
                "Sequence of characters for preprocessing order (F, N, L, W).",
                "FNLW",
            )
        ]

    # Numeric inputs
    numeric_inputs = [
        ui.input_numeric("mz_min", "Minimum m/z for filtering:", 0),
        ui.input_numeric("mz_max", "Maximum m/z for filtering:", 99999999),
        ui.input_numeric("int_min", "Minimum intensity for filtering:", 0),
        ui.input_numeric("int_max", "Maximum intensity for filtering:", 999999999),
        ui.input_numeric("noise_threshold", "Noise removal threshold:", 0.0),
        ui.input_numeric("wf_mz", "Mass/charge weight factor:", 0.0),
        ui.input_numeric("wf_int", "Intensity weight factor:", 1.0),
        ui.input_numeric("LET_threshold", "Low-entropy threshold:", 0.0),
        ui.input_numeric("entropy_dimension", "Entropy dimension (Renyi/Tsallis only):", 1.1),
        ui.input_numeric("n_top_matches_to_save", "Number of top matches to save:", 1),
    ]


    # Run and Back buttons
    run_button = ui.input_action_button("run_btn", "Run", style="font-size:16px; padding:15px 30px; width:200px; height:80px")
    back_button = ui.input_action_button("back", "Back to main menu", style="font-size:16px; padding:15px 30px; width:200px; height:80px")

    #print(len(extra_inputs))
    # Layout base_inputs and extra_inputs in columns
    if platform == "HRMS":
        inputs_columns = ui.layout_columns(
            ui.div(base_inputs[0:5], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div([base_inputs[5:6], *extra_inputs], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div(numeric_inputs[0:5], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div(numeric_inputs[5:10], style="display:flex; flex-direction:column; gap:10px;"),
            col_widths=(3, 3, 3, 3),
        )
    elif platform == "NRMS":
        inputs_columns = ui.layout_columns(
            ui.div(base_inputs[0:5], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div([base_inputs[5:6], *extra_inputs], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div(numeric_inputs[0:5], style="display:flex; flex-direction:column; gap:10px;"),
            ui.div(numeric_inputs[5:10], style="display:flex; flex-direction:column; gap:10px;"),
            col_widths=(3, 3, 3, 3),
        )

    # Combine everything
    return ui.div(
        ui.TagList(
            ui.h2("Run Spectral Library Matching"),
            inputs_columns,
            run_button,
            back_button
        ),
    )



app_ui = ui.page_fluid(
    ui.output_ui("main_ui"),
    ui.output_text("status_output")
)


def server(input, output, session):

    # Track which page to show
    current_page = reactive.Value("main_menu")
    
    # Track button clicks
    plot_clicks = reactive.Value(0)
    match_clicks = reactive.Value(0)
    back_clicks = reactive.Value(0)

    run_status = reactive.Value("Waiting for input...")

    @reactive.Effect
    def _():
        # Main menu buttons
        if input.plot_spectra() > plot_clicks.get():
            current_page.set("plot_spectra")
            plot_clicks.set(input.plot_spectra())
        elif input.run_spec_lib_matching() > match_clicks.get():
            current_page.set("run_spec_lib_matching")
            match_clicks.set(input.run_spec_lib_matching())
        elif hasattr(input, "back") and input.back() > back_clicks.get():
            current_page.set("main_menu")
            back_clicks.set(input.back())

    @render.image
    def image():
        from pathlib import Path

        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "www/emblem.png"), "width": "320px", "height": "250px"}
        return img

    @output
    @render.ui
    def main_ui():
        if current_page() == "main_menu":
            return ui.page_fluid(
                ui.h2("Main Menu"),
                ui.div(
                    ui.output_image("image"),
                    style=(
                        "position:fixed; top:0; left:50%; transform:translateX(-50%); "
                        "z-index:1000; text-align:center; padding:10px; background-color:white;"
                    ),
                ),
                ui.div(
                    "Overview:",
                    style="text-align:left; font-size:24px; font-weight:bold; margin-top:350px"
                ),
                ui.div(
                    "PyCompound is a Python-based tool designed for performing spectral library matching on either high-resolution mass spectrometry data (HRMS) or low-resolution mass spectrometry data (NRMS). PyCompound offers a range of spectrum preprocessing transformations and similarity measures. These spectrum preprocessing transformations include filtering on mass/charge and/or intensity values, weight factor transformation, low-entropy transformation, centroiding, noise removal, and matching. The available similarity measures include the canonical Cosine similarity measure, three entropy-based similarity measures, and a variety of binary similarity measures: Jaccard, Dice, 3W-Jaccard, Sokal-Sneath, Binary Cosine, Mountford, McConnaughey, Driver-Kroeber, Simpson, Braun-Banquet, Fager-McGowan, Kulczynski, Intersection, Hamming, and Hellinger.",
                    style="margin-top:10px; text-align:left; font-size:16px; font-weight:500"
                ),
                ui.div(
                    "Select options:",
                    style="margin-top:30px; text-align:left; font-size:24px; font-weight:bold"
                ),
                ui.div(
                    ui.input_radio_buttons("chromatography_platform", "Specify chromatography platform:", ["HRMS","NRMS"]),
                    style="font-size:18px; margin-top:10px; max-width:none"
                ),
                ui.input_action_button("plot_spectra", "Plot two spectra before and after preprocessing transformations.", style="font-size:18px; padding:20px 40px; width:550px; height:100px; margin-top:10px; margin-right:50px"),
                ui.input_action_button("run_spec_lib_matching", "Run spectral library matching to perform compound identification on a query library of spectra.", style="font-size:18px; padding:20px 40px; width:550px; height:100px; margin-top:10px; margin-right:50px"),
                ui.div(
                    "References:",
                    style="margin-top:35px; text-align:left; font-size:24px; font-weight:bold"
                ),
                ui.div(
                    "If Shannon Entropy similarity measure, low-entropy transformation, or centroiding are used:",
                    style="margin-top:10px; text-align:left; font-size:14px; font-weight:500"
                ),
                ui.div(
                    ui.HTML(
                        'Li, Y., Kind, T., Folz, J. et al. (2021) Spectral entropy outperforms MS/MS dot product similarity for small-molecule compound identification. Nat Methods, 18 1524–1531. <a href="https://doi.org/10.1038/s41592-021-01331-z" target="_blank">https://doi.org/10.1038/s41592-021-01331-z</a>.'
                    ),
                    style="text-align:left; font-size:14px; font-weight:500"
                ),
                ui.div(
                    "If Tsallis Entropy similarity measure or series of preprocessing transformations are used:",
                    style="margin-top:10px; text-align:left; font-size:14px; font-weight:500"
                ),
                ui.div(
                    ui.HTML(
                        'Dlugas, H., Zhang, X., Kim, S. (2025) Comparative analysis of continuous similarity measures for compound identification in mass spectrometry-based metabolomics. Chemometrics and Intelligent Laboratory Systems, 263, 105417. <a href="https://doi.org/10.1016/j.chemolab.2025.105417", target="_blank">https://doi.org/10.1016/j.chemolab.2025.105417</a>.'
                    ),
                    style="text-align:left; font-size:14px; font-weight:500"
                ),
                ui.div(
                    "If binary similarity measures are used:",
                    style="margin-top:10px; text-align:left; font-size:14px; font-weight:500"
                ),
                ui.div(
                    ui.HTML(
                        'Kim, S., Kato, I., & Zhang, X. (2022). Comparative Analysis of Binary Similarity Measures for Compound Identification in Mass Spectrometry-Based Metabolomics. Metabolites, 12(8), 694. <a href="https://doi.org/10.3390/metabo12080694" target="_blank">https://doi.org/10.3390/metabo12080694</a>.'
                    ),
                    style="text-align:left; font-size:14px; font-weight:500"
                ),

                ui.div(
                    "If weight factor transformation is used:",
                    style="margin-top:10px; text-align:left; font-size:14px; font-weight:500"
                ),
                ui.div(
                    ui.HTML(
                        'Kim, S., Koo, I., Wei, X., & Zhang, X. (2012). A method of finding optimal weight factors for compound identification in gas chromatography-mass spectrometry. Bioinformatics, 28(8), 1158-1163. <a href="https://doi.org/10.1093/bioinformatics/bts083" target="_blank">https://doi.org/10.1093/bioinformatics/bts083</a>.'
                    ),
                    style="margin-bottom:40px; text-align:left; font-size:14px; font-weight:500"
                ),
            )
        elif current_page() == "plot_spectra":
            return plot_spectra_ui(input.chromatography_platform())
        elif current_page() == "run_spec_lib_matching":
            return run_spec_lib_matching_ui(input.chromatography_platform())

    @reactive.effect
    @reactive.event(input.run_btn)
    def _():
        if current_page() == "plot_spectra":
            if len(input.spectrum_ID1())==0:
                spectrum_ID1 = None
            else:
                spectrum_ID1 = input.spectrum_ID1()
            if len(input.spectrum_ID2())==0:
                spectrum_ID2 = None
            else:
                spectrum_ID2 = input.spectrum_ID2()

            if input.chromatography_platform() == "HRMS":
                try:
                    fig = generate_plots_on_HRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], spectrum_ID1=spectrum_ID1, spectrum_ID2=spectrum_ID2, similarity_measure=input.similarity_measure(), spectrum_preprocessing_order=input.spectrum_preprocessing_order(), high_quality_reference_library=input.high_quality_reference_library(), mz_min=input.mz_min(), mz_max=input.mz_max(), int_min=input.int_min(), int_max=input.int_max(), window_size_centroiding=input.window_size_centroiding(), window_size_matching=input.window_size_matching(), noise_threshold=input.noise_threshold(), wf_mz=input.wf_mz(), wf_intensity=input.wf_int(), LET_threshold=input.LET_threshold(), entropy_dimension=input.entropy_dimension(), y_axis_transformation=input.y_axis_transformation(), return_plot=True)
                    plt.show()
                    run_status.set(f"✅  Plotting has finished.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")
            elif input.chromatography_platform() == "NRMS":
                try:
                    generate_plots_on_NRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], spectrum_ID1=spectrum_ID1, spectrum_ID2=spectrum_ID2, similarity_measure=input.similarity_measure(), spectrum_preprocessing_order=input.spectrum_preprocessing_order(), high_quality_reference_library=input.high_quality_reference_library(), mz_min=input.mz_min(), mz_max=input.mz_max(), int_min=input.int_min(), int_max=input.int_max(), noise_threshold=input.noise_threshold(), wf_mz=input.wf_mz(), wf_intensity=input.wf_int(), LET_threshold=input.LET_threshold(), entropy_dimension=input.entropy_dimension(), y_axis_transformation=input.y_axis_transformation(), return_plot=True)
                    plt.show()
                    run_status.set(f"✅  Plotting has finished.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")

        elif current_page() == 'run_spec_lib_matching':
            if input.chromatography_platform() == 'HRMS':
                try:
                    run_spec_lib_matching_on_HRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], likely_reference_ids=None, similarity_measure=input.similarity_measure(), spectrum_preprocessing_order=input.spectrum_preprocessing_order(), high_quality_reference_library=input.high_quality_reference_library(), mz_min=input.mz_min(), mz_max=input.mz_max(), int_min=input.int_min(), int_max=input.int_max(), window_size_centroiding=input.window_size_centroiding(), window_size_matching=input.window_size_matching(), noise_threshold=input.noise_threshold(), wf_mz=input.wf_mz(), wf_intensity=input.wf_int(), LET_threshold=input.LET_threshold(), entropy_dimension=input.entropy_dimension(), n_top_matches_to_save=input.n_top_matches_to_save(), print_id_results=False, output_identification=f'{Path.cwd()}/output_identification.csv', output_similarity_scores=f'{Path.cwd()}/')
                    run_status.set(f"✅  Spectral library matching has finished and results were written to {Path.cwd()}/output_similarity_scores.csv.")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")
            elif input.chromatography_platform() == 'NRMS':
                try:
                    run_spec_lib_matching_on_NRMS_data(query_data=input.query_data()[0]['datapath'], reference_data=input.reference_data()[0]['datapath'], likely_reference_ids=None, similarity_measure=input.similarity_measure(), spectrum_preprocessing_order=input.spectrum_preprocessing_order(), high_quality_reference_library=input.high_quality_reference_library(), mz_min=input.mz_min(), mz_max=input.mz_max(), int_min=input.int_min(), int_max=input.int_max(), noise_threshold=input.noise_threshold(), wf_mz=input.wf_mz(), wf_intensity=input.wf_int(), LET_threshold=input.LET_threshold(), entropy_dimension=input.entropy_dimension(), n_top_matches_to_save=input.n_top_matches_to_save(), print_id_results=False, output_identification=f'{Path.cwd()}/output_identification.csv', output_similarity_scores=f'{Path.cwd()}/output_similarity_scores.csv')
                    run_status.set(f"✅  Spectral library matching has finished and results were written to {Path.cwd()}/")
                except Exception as e:
                    run_status.set(f"❌ Error: {traceback.format_exc()}")


    @render.text
    def status_output():
        return run_status.get()



app = App(app_ui, server)


