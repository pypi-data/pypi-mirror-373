from datetime import datetime
import logging
import os
from os.path import dirname, join, isdir, abspath, split
import re
import shutil
import subprocess
import tempfile
import warnings
import zipfile

from pypdf import PdfReader, PdfWriter
from pdfCropMargins import crop

logging.captureWarnings(True)
# define a custom logging
log = logging.getLogger(__name__)
# log.addHandler(logging.StreamHandler())
# log_oa.addHandler(logging.FileHandler(__name__ + ".log"))
log.setLevel(logging.INFO)

def fix_plotly_pdf_export(pdf_file_path):
    pdf_reader = PdfReader(pdf_file_path)
    pdf_writer = PdfWriter()
    first_page = pdf_reader.pages[0]
    pdf_writer.add_page(first_page)
    with open(pdf_file_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    tmp_pdf_file_path = join(split(pdf_file_path)[0], "tmp-" + split(pdf_file_path)[1])
    crop(["-o", tmp_pdf_file_path, "-p", "0", pdf_file_path])
    os.remove(pdf_file_path)
    os.rename(tmp_pdf_file_path, pdf_file_path)


class DibisoReporting:
    """
    Class to generate the BiSO report

    :cvar figures_dir_name: Directory where figures are stored.
    :cvar class_mapping: Dictionary that maps class names to actual classes
    :cvar default_visualizations: Dictionary contains each type of plot to include in the report with the parameters of
        each plot.
    """

    figures_dir_name = "figures"

    # Map class names to actual classes
    class_mapping = {}

    # an empty list means that the visualization won't be done, an empty dictionary in a list means that the
    # visualization will be done with the default values
    default_visualizations =  {}


    def __init__(
            self,
            entity_id = "",
            year: int | None = None,
            latex_main_file_path: str | None = None,
            latex_main_file_url: str | None = None,
            latex_template_path: str | None = None,
            latex_template_url: str | None = None,
            max_entities: int | None = 1000,
            max_plotted_entities: int = 25,
            root_path: str | None = None,
    ):
        """
        Initialize the Biso class with the given parameters.

        :param entity_id: The ID of the entity to make the report on (e.g. the HAL collection identifier).
        :type entity_id: str
        :param year: The year of the report. If None, uses the current year.
        :type year: int | None, optional
        :param latex_main_file_path: Path to a single LaTeX main file. This file is the one to use to compile the
            report. It will copy the main file to root_path. Default to None. If None, doesn't try getting the main file
            from the path. If both latex_main_file_path and latex_main_file_url are not None, the library will first try
            to get the main file from the path.
        :type latex_main_file_path: str | None, optional
        :param latex_main_file_url: URL to download a single LaTeX main file. It will download the file directly
            to root_path. Default to None. If None, doesn't try getting the main file from the URL.
        :type latex_main_file_url: str | None, optional
        :param latex_template_path: Path to the LaTeX template files. It will copy the templates files to root_path.
            Default to None. If None, doesn't try getting the template from the path. If both latex_template_path and
            latex_template_url are not None, the library will first try to get the template from the path.
        :type latex_template_path: str | None, optional
        :param latex_template_url: URL to a GitHub repository containing the template. It will get the latest repository
            release and extract it to get the template files. Default to None. If None, doesn't try getting the template
            from the URL.
        :type latex_template_url: str | None, optional
        :param max_entities: Default maximum number of entities used to create the plot. Default 1000.
            Set to None to disable the limit. This value limits the number of queried entities when doing analysis.
            For example, when creating the collaboration map, it limits the number of works to query from HAL to extract
            the collaborating institutions from.
        :type max_entities: int | None, optional
        :param max_plotted_entities: Maximum number of bars in the plot or rows in the table. Default to 25.
        :type max_plotted_entities: int, optional
        :param root_path: Path to the root directory where the report and figures will be generated.
        :type root_path: str
        """

        self.entity_id = entity_id
        if year is None:
            # get current year
            self.year = datetime.now().year
        else:
            self.year = year
        self.latex_main_file_path = latex_main_file_path
        self.latex_main_file_url = latex_main_file_url
        self.latex_template_path = latex_template_path
        self.latex_template_url = latex_template_url
        self.max_entities = max_entities
        self.max_plotted_entities = max_plotted_entities
        if root_path is None:
            raise AttributeError('root_path cannot be None')
        if isdir(dirname(abspath(root_path))):
           os.makedirs(root_path, exist_ok=True)
        else:
            raise ValueError(f"Unable to find path: {dirname(abspath(root_path))}")
        self.root_path = abspath(root_path)
        self.fig_dir_path = join(self.root_path, self.figures_dir_name)
        os.makedirs(self.fig_dir_path, exist_ok=True)

        self.macros_variables = {} # variables to include in the macros for the report generation
        self.macros = [] # macros to include for the report generation


    def get_latex_main_file_from_path(self):
        """
        Get the LaTeX main file from a local path.
        It copies the main file from the specified path to the root path of the project.
        """
        if self.latex_main_file_path is None:
            raise ValueError("No LaTeX main file path provided")

        if not os.path.exists(self.latex_main_file_path):
            raise FileNotFoundError(f"LaTeX main file path does not exist: {self.latex_main_file_path}")

        if not os.path.isfile(self.latex_main_file_path):
            raise ValueError(f"LaTeX main file path is not a file: {self.latex_main_file_path}")

        try:
            # Get the filename from the source path
            filename = os.path.basename(self.latex_main_file_path)
            dest_file = os.path.join(self.root_path, filename)

            # Copy the file to the root path
            shutil.copy2(self.latex_main_file_path, dest_file)

            log.info(f"Successfully got the LaTeX main file from the path")

        except Exception as e:
            raise RuntimeError(f"Failed to copy LaTeX main file from path: {e}")


    def get_latex_main_file_from_url(self):
        """
        Get the LaTeX main file from a URL.
        It downloads the file directly from the URL and saves it to the root path of the project.
        """
        if self.latex_main_file_url is None:
            raise ValueError("No LaTeX main file URL provided")

        try:
            log.info(f"Downloading LaTeX main file from {self.latex_main_file_url}...")

            # Extract filename from URL or use a default name
            filename = os.path.basename(self.latex_main_file_url.split('?')[0])
            if not filename or not filename.endswith('.tex'):
                filename = "main.tex"

            dest_file = os.path.join(self.root_path, filename)

            # Download the file using wget
            wget_cmd = f"wget -q -O {dest_file} {self.latex_main_file_url}"
            subprocess.run(wget_cmd, shell=True, check=True)

            log.info(f"Successfully downloaded the LaTeX main file")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to execute wget command: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to download LaTeX main file: {e}")


    def get_latex_template_from_path(self):
        """
        Get the LaTeX template from a local path.
        It copies the template files from the specified path to the root path of the project.
        """
        if self.latex_template_path is None:
            raise ValueError("No LaTeX template path provided")

        if not os.path.exists(self.latex_template_path):
            raise FileNotFoundError(f"LaTeX template path does not exist: {self.latex_template_path}")

        if not os.path.isdir(self.latex_template_path):
            raise ValueError(f"LaTeX template path is not a directory: {self.latex_template_path}")

        try:
            # Copy all files and directories from the template path to the root path
            for item in os.listdir(self.latex_template_path):
                source_item = os.path.join(self.latex_template_path, item)
                dest_item = os.path.join(self.root_path, item)

                if os.path.isdir(source_item):
                    if os.path.exists(dest_item):
                        shutil.rmtree(dest_item)
                    shutil.copytree(source_item, dest_item)
                else:
                    shutil.copy2(source_item, dest_item)

            log.info(f"Successfully got the LaTeX template from the path and extracted it")

        except Exception as e:
            raise RuntimeError(f"Failed to copy LaTeX template from path: {e}")


    def get_latex_template_from_github(self):
        """
        Get the LaTeX template either from a GitHub repository release.
        It saves the template in the root path of the project.
        """
        if self.latex_template_url is None:
            raise ValueError("No LaTeX template URL provided")

        try:
            # Convert GitHub releases page URL to API URL
            if "github.com" in self.latex_template_url and "/releases/latest" in self.latex_template_url:
                # Extract owner and repo from URL like https://github.com/owner/repo/releases/latest
                url_parts = self.latex_template_url.replace("https://github.com/", "").replace("/releases/latest", "")
                api_url = f"https://api.github.com/repos/{url_parts}/releases/latest"
            else:
                api_url = self.latex_template_url
            log.info(f"Using GitHub release URL: {self.latex_template_url}")
            log.info(f"Downloading LaTeX template from {api_url}...")

            # Get the download URL using the curl command
            cmd = f"curl -s {api_url} | grep \"browser_download_url.*zip\" | cut -d '\"' -f 4"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            download_url = result.stdout.strip()

            if not download_url:
                raise ValueError("No zip download URL found in the GitHub API response")

            # Create a temporary directory for downloading and extracting
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "template.zip")

                # Download the zip file using wget (uses -q to suppress output)
                wget_cmd = f"wget -q -O {zip_path} {download_url}"
                subprocess.run(wget_cmd, shell=True, check=True)

                # Extract the zip file
                extract_dir = os.path.join(temp_dir, "extracted")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                # Find the extracted contents (usually in a subdirectory)
                extracted_contents = os.listdir(extract_dir)
                if len(extracted_contents) == 1 and os.path.isdir(os.path.join(extract_dir, extracted_contents[0])):
                    source_dir = os.path.join(extract_dir, extracted_contents[0])
                else:
                    source_dir = extract_dir

                # Copy all files from the extracted directory to the root path
                for item in os.listdir(source_dir):
                    source_item = os.path.join(source_dir, item)
                    dest_item = os.path.join(self.root_path, item)

                    if os.path.isdir(source_item):
                        if os.path.exists(dest_item):
                            shutil.rmtree(dest_item)
                        shutil.copytree(source_item, dest_item)
                    else:
                        shutil.copy2(source_item, dest_item)

            log.info(f"Successfully downloaded and extracted the LaTeX template")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to execute command: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to download or extract LaTeX template: {e}")


    def generate_report(
            self,
            visualizations_to_make: dict[str, list[dict]] | None = None,
            import_default_visualizations = True
    ):
        """
        Generate the report by calling the specified functions with their parameters to create the desired
        visualizations. To select which visualization to make and configure them, you can use `visualizations_to_make`
        as follows:

        .. code-block:: python

            visualizations_to_make = {
                "AnrProjects": [
                    { "name": "anr1", "param1": "value1", "param2": "value2" },
                    { "name": "anr2", "param1": "value3", "param2": "value4" }
                ],
                "Chapters": [
                    { "name": "chapter1", "param1": "value1", "param2": "value2" }
                ],
                "CollaborationMap": [
                    { "name": "collab1", "max_entities": 1000, "resolution": 50, "map_zoom": True },
                    { "name": "collab2", "max_entities": 500, "resolution": 100, "map_zoom": False }
                ],
                "CollaborationNames": [
                    {}
                ],
                "Conferences": []
            }

        This example, will create:
          * 2 AnrProjects visualizations (with the parameters defined in the dictionaries)
          * 1 Chapters visualization
          * 2 CollaborationMaps visualizations
          * 1 Conferences CollaborationNames (with the default parameters as there is one empty dictionary)
          * 0 Conferences visualizations (as the list is empty)

        :param visualizations_to_make: A dictionary specifying which visualizations to make and their parameters.
        :type visualizations_to_make: list[dict[str, Any]]
        :param import_default_visualizations: Whether to import default visualizations settings. Defaults to True.
            To not generate a plot, set its dictionary in import_default_visualizations to an empty list.
            Example: If you don't want to generate the Conferences visualization, you can set
            import_default_visualizations as follows: ``import_default_visualizations = {"Conferences": []}``.
        :type import_default_visualizations: bool
        """
        if visualizations_to_make is None:
            visualizations_to_make = {}
        # merge default_visualizations and visualizations_to_make:
        if import_default_visualizations:
            for viz_type, configs in self.default_visualizations.items():
                # if the config is not defined in visualizations_to_make, we add it
                if viz_type not in visualizations_to_make.keys():
                    visualizations_to_make[viz_type] = configs
                else:
                    # for each config in default_visualizations
                    for config in configs:
                        # search if the config is provided in visualizations_to_make
                        for provided_config in visualizations_to_make[viz_type]:
                            if 'name' in config.keys():
                                if config['name'] == provided_config.get('name'):
                                    for config_key, config_val in config:
                                        # if keys are in default config and visualizations_to_make, we keep the value in
                                        # visualizations_to_make
                                        if config_key not in provided_config.keys():
                                            visualizations_to_make[viz_type][config_key] = config_val
                                    break
                            # we match configs when they both have empty name or no name
                            elif (('name' not in config.keys() or config['name'] == '') and
                                  ('name' not in provided_config.keys() or provided_config['name'] == '')):
                                for config_key, config_val in config:
                                    # if keys are in default config and visualizations_to_make, we keep the value in
                                    # visualizations_to_make
                                    if config_key not in provided_config.keys():
                                        visualizations_to_make[viz_type][config_key] = config_val
                                break
                        else:
                            # will be called if the previous loop did not end with a `break`, aka we didn't find a
                            # config match in visualizations_to_make and self.default_visualizations
                            visualizations_to_make[viz_type].append(config)

        # make visualizations:
        for viz_type, configs in visualizations_to_make.items():
            if not configs:
                continue
            if viz_type not in self.class_mapping.keys():
                warnings.warn(f"{viz_type} is not a valid visualization type for {self.__class__.__name__}")
                continue  # Skip unknown visualization types

            viz_class = self.class_mapping[viz_type]

            for config in configs:
                # Extract name and parameters
                name = config.get("name", "")
                stats_to_save = config.get("stats_to_save", {})
                params = {k: v for k, v in config.items() if k != "name" and k != "stats_to_save"}
                if "lab" not in params:
                    params["lab"] = self.entity_id
                if "year" not in params:
                    params["year"] = self.year
                if "max_entities" not in params:
                    params["max_entities"] = self.max_entities
                if "max_plotted_entities" not in params:
                    params["max_plotted_entities"] = self.max_plotted_entities

                # Generate the figure
                viz = viz_class(**params)
                stats = viz.fetch_data()
                fig = viz.get_figure()

                # Determine the file name
                if name:
                    file_name = re.sub( '(?<!^)(?=[A-Z])', '_', viz_class.__name__).lower() + "_" + name
                else:
                    file_name = re.sub( '(?<!^)(?=[A-Z])', '_', viz_class.__name__).lower()

                # Save the figure
                if viz_class.figure_file_extension == "tex":
                    file_name += ".tex"
                    output_file = join(self.fig_dir_path, file_name)
                    with open(output_file, "w") as f:
                        f.write(fig)
                # figure format is pdf:
                else:
                    file_name += ".pdf"
                    output_file = join(self.fig_dir_path, file_name)
                    fig.write_image(output_file)

                    # Fix PDF export if necessary
                    if viz_type == "CollaborationMap":
                        fix_plotly_pdf_export(join(self.fig_dir_path, file_name))

                # save stats:
                for var in stats_to_save.items():
                    name = var[1]
                    val = stats.get(var[0])
                    if name in self.macros_variables.keys():
                        warnings.warn(f"Macro variable {name} already exists. Overwriting.")
                    self.macros_variables[name] = val

        for macro_name, macro_value in self.macros_variables.items():
            if macro_value is None:
                macro_value = "None"
            self.add_marco(str(macro_name), macro_value)
        self.macros.append("")
        self.macros.append("")
        macros_text = '\n'.join(self.macros)

        with open(join(self.root_path, "names_and_macros.tex"), 'w') as f:
            f.write(macros_text)

        # get the main file
        try:
            self.get_latex_main_file_from_path()
        except:
            try:
                self.get_latex_main_file_from_url()
            except:
                if self.latex_main_file_url is not None or self.latex_main_file_path is not None:
                    warnings.warn(
                        "Could not find the LaTeX main file from the path or the URL. "
                        "The report will be produced without the LaTeX main file."
                    )

        # get the template
        try:
            self.get_latex_template_from_path()
        except:
            try:
                self.get_latex_template_from_github()
            except:
                if self.latex_template_url is not None or self.latex_template_url is not None:
                    warnings.warn(
                        "Could not find the LaTeX template from the path or the github repository. "
                        "The report will be produced withtout the LaTeX template."
                    )
