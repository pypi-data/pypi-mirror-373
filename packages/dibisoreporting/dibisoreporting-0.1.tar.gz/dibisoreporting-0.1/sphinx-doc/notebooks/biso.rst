BiSO
====

Example to generate a BiSO report (Bilan de la Science Ouverte:
Open-Science report).

This generates the report for the Université Paris-Salcay, year 2024,
and limits the number of works to the value set by
``default_max_entities`` (1000) in the library ``dibisoplot``.

.. code:: ipython3

    from dibisoreporting import Biso
    
    biso_reporting = Biso(
        "UNIV-PARIS-SACLAY",
        2024,
        lab_acronym = "UPSaclay",
        lab_full_name = "Université Paris-Saclay",
        latex_main_file_url = "https://raw.githubusercontent.com/dibiso-upsaclay/dibiso-latex-templates/refs/heads/main/examples/biso/biso-main.tex",
        latex_template_url = "https://github.com/dibiso-upsaclay/dibiso-latex-templates/releases/latest",
        max_entities = 10,
        root_path = "test_report",
        watermark_text = "DUMMY DATA",
    )
    
    biso_reporting.generate_report()

| Romain THOMAS 2025
| DiBISO - Université Paris-Saclay
