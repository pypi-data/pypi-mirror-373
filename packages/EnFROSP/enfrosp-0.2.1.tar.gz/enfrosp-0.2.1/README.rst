=================================================
EnFROSP — EnMAP Fast Retrieval Of Snow Properties
=================================================

EnFROSP is a Python package for advanced atmospheric correction of EnMAP hyperspectral satellite
data over snow and ice. It implements several snow parameter retrieval algorithms originally
developed in FORTRAN by Alexander Kokhanovsky, enabling the retrieval of key snow properties
such as grain size, albedo, and impurities for both clean and polluted snow. EnFROSP takes
the official EnMAP L1C data product, provided by the German Aerospace Center (DLR), as input and
delivers the retrieval results as ENVI BSQ files.

* Free software: Apache Software License 2.0
* Documentation: https://EnMAP.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enfrosp/doc/



Status
------

|badge1| |badge2| |badge3| |badge4| |badge5| |badge6| |badge7| |badge8| |badge9|

.. |badge1| image:: https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enfrosp/badges/main/pipeline.svg
    :target: https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enfrosp/pipelines
    :alt: Pipelines

.. |badge2| image:: https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enfrosp/badges/main/coverage.svg
    :target: https://EnMAP.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enfrosp/coverage/
    :alt: Coverage

.. |badge3| image:: https://img.shields.io/static/v1?label=Documentation&message=GitLab%20Pages&color=orange
    :target: https://EnMAP.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enfrosp/doc/
    :alt: Documentation

.. |badge4| image:: https://img.shields.io/pypi/v/enfrosp.svg
    :target: https://pypi.python.org/pypi/enfrosp

.. |badge5| image:: https://img.shields.io/conda/vn/conda-forge/enfrosp.svg
        :target: https://anaconda.org/conda-forge/enfrosp

.. |badge6| image:: https://img.shields.io/pypi/l/enfrosp.svg
    :target: https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enfrosp/-/blob/main/LICENSE

.. |badge7| image:: https://img.shields.io/pypi/pyversions/enfrosp.svg
    :target: https://img.shields.io/pypi/pyversions/enfrosp.svg

.. |badge8| image:: https://img.shields.io/pypi/dm/enfrosp.svg
    :target: https://pypi.python.org/pypi/enfrosp

.. |badge9| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.16967937.svg
   :target: https://doi.org/10.5281/zenodo.16967937

See also the latest coverage_ report and the pytest_ HTML report.


Feature overview
----------------

* Retrieval of snow properties from the EnMAP L1C product such as:

  * clean snow grain size
  * polluted snow albedo impurities
  * polluted snow broadband albedo


History / Changelog
-------------------

You can find the protocol of recent changes in the EnFROSP package
`here <https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enfrosp/-/blob/main/HISTORY.rst>`__.


Credits
-------

This software was developed within the context of the EnMAP project supported by the DLR Space Administration with
funds of the German Federal Ministry of Economic Affairs and Energy (on the basis of a decision by the German
Bundestag: 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.

This package was created with Cookiecutter_ and the `danschef/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`danschef/cookiecutter-pypackage`: https://github.com/danschef/cookiecutter-pypackage
.. _coverage: https://EnMAP.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enfrosp/coverage/
.. _pytest: https://EnMAP.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enfrosp/test_reports/report.html
