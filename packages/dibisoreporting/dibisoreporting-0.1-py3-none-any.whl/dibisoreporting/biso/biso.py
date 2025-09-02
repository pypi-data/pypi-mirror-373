from datetime import datetime

from dibisoplot.biso import AnrProjects
from dibisoplot.biso import Chapters
from dibisoplot.biso import CollaborationMap
from dibisoplot.biso import CollaborationNames
from dibisoplot.biso import Conferences
from dibisoplot.biso import EuropeanProjects
from dibisoplot.biso import Journals
from dibisoplot.biso import OpenAccessWorks
from dibisoplot.biso import WorksType

from dibisoreporting import DibisoReporting


class Biso(DibisoReporting):
    """
    Class to generate the BiSO report

    :cvar class_mapping: Dictionary that maps class names to actual classes
    :cvar default_visualizations: Dictionary contains each type of plot to include in the report with the parameters of
        each plot.
    """

    # Map class names to actual classes
    class_mapping = {
        "AnrProjects": AnrProjects,
        "Chapters": Chapters,
        "CollaborationMap": CollaborationMap,
        "CollaborationNames": CollaborationNames,
        "Conferences": Conferences,
        "EuropeanProjects": EuropeanProjects,
        "Journals": Journals,
        "OpenAccessWorks": OpenAccessWorks,
        "WorksType": WorksType
    }

    # an empty list means that the visualization won't be done, an empty dictionary in a list means that the
    # visualization will be done with the default values
    default_visualizations =  {
        "AnrProjects": [{}],
        "Chapters": [{}],
        "CollaborationMap": [
            {
                "name": "world",
                "countries_to_ignore": ["France"],
                "stats_to_save": {
                    "collaborations_nb": "collaborationsnb",
                    "institutions_nb": "institutionsnb",
                    "countries_nb": "countriesnb"
                }
            },
            { "name": "europe", "resolution": 50, "map_zoom": True }
        ],
        "CollaborationNames": [{}],
        "Conferences": [{}],
        "EuropeanProjects": [{}],
        "Journals": [],
        "OpenAccessWorks": [
            {
                "stats_to_save": {
                    "oa_works_period": "oaworksperiod"
                }
            }
        ],
        "WorksType": [{}],
    }


    def __init__(
            self,
            entity_id,
            year: int | None = None,
            lab_acronym: str = "",
            lab_full_name: str = "",
            latex_main_file_path: str | None = None,
            latex_main_file_url: str | None = None,
            latex_template_path: str | None = None,
            latex_template_url: str | None = None,
            max_entities: int | None = 1000,
            max_plotted_entities: int = 25,
            root_path: str | None = None,
            watermark_text: str = "",
    ):
        """
        Initialize the Biso class with the given parameters.

        :param entity_id: The HAL collection identifier. This usually refers to the lab acronym.
        :type entity_id: str
        :param year: The year for which to fetch data. If None, uses the current year.
        :type year: int | None, optional
        :param lab_acronym: The full acronym of the lab. Default to entity_id.
        :type lab_acronym: str
        :param lab_full_name: The full name of the lab.
        :type lab_full_name: str
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
            For example, when creating the collaboration map, it limits the number of works to query from HAL to extract the
            collaborating institutions from.
        :type max_entities: int | None, optional
        :param max_plotted_entities: Maximum number of bars in the plot or rows in the table. Default to 25.
        :type max_plotted_entities: int, optional
        :param root_path: Path to the root directory where the report and figures will be generated.
        :type root_path: str
        :param watermark_text: The text to be used as a watermark in the report. Default to "" (no watermark).
        :type watermark_text: str
        """

        super().__init__(
            entity_id,
            year,
            latex_main_file_path=latex_main_file_path,
            latex_main_file_url=latex_main_file_url,
            latex_template_path=latex_template_path,
            latex_template_url=latex_template_url,
            max_entities=max_entities,
            max_plotted_entities=max_plotted_entities,
            root_path = root_path
        )

        if not lab_acronym:
            lab_acronym = str(entity_id)
        self.lab_acronym = lab_acronym
        self.lab_full_name = lab_full_name
        self.watermark_text = watermark_text

        self.data_fetch_date = datetime.now().strftime("%d/%m/%Y")


    def add_marco(self, name, value):
        self.macros.append("\\newcommand{\\" + name + "}{" + str(value) + "}")


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

        self.add_marco("reportyear", self.year)
        self.add_marco("labacronym", self.lab_acronym)
        self.add_marco("labfullname", self.lab_full_name)
        self.add_marco("datafetchdate", self.data_fetch_date)
        self.add_marco("watermarktext", self.watermark_text)
        self.macros.append("")

        super().generate_report(visualizations_to_make, import_default_visualizations)


