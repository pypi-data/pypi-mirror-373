BiSO
====

Class to generate a BISO report.

By default the report contains the following visualizations:

* AnrProjects
* Chapters
* CollaborationMap: name = "world", countries_to_ignore = ["France"]
* CollaborationMap: name = "europe", resolution = 50, map_zoom = True
* CollaborationNames
* Conferences
* EuropeanProjects
* Journals
* OpenAccessWorks
* WorksType


This comes from the default value of ``default_visualizations`` :

.. code-block:: python

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
        "OpenAccessWorks": [{}],
        "WorksType": [{}],
    }


When needing statistics values to be printed in the report, you can export variables with the argument
``stats_to_save``.
You need to provide a dictionary with the keys being the name of the variables returned by the plotting library and the
values being the name of the variable in the report (aka the name of the macro in the LaTeX report).
In the above example, ``collaborations_nb`` is the key of the variable in the dictionary returned by the plotting
library and and ``collaborationsnb`` is the name of the LaTeX macro containing the value of the variable for the report,
callable with ``\collaborationsnb``.
The plotting library needs to return those variables in a dictionary returned by the method ``fetch_data()``.

The BiSO Class
--------------

.. autoclass:: dibisoreporting.biso.Biso
   :members:
   :show-inheritance:
   :inherited-members:
   :undoc-members:
   :exclude-members: class_mapping
