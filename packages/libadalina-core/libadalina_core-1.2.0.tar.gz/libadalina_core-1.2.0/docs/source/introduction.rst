
************
Introduction
************

*libadalina-core* is a Python library for spatial data processing and analysis providing utilities for reading,
writing, and processing geospatial data,
with a focus on spatial joins and aggregations.

It makes it easier to work with geospatial data in Python by providing a high-level interface
to Apache Sedona, a powerful geospatial processing engine, and integrates nicely with other well-known libraries
such as *geopandas* and *pandas*.

*libadalina-core* is part of the `ADaLinA project <https://expertise.unimi.it/resource/project/PNRR%5FBAC24ACESE%5F01>`__
that aims to develop a set of tools for the analysis of large-scale spatial data
to be integrated into the `Amelia homepage`_ platform.

The online documentation is available ad `<https://libadalinacore-6b2a95.gitlab.io>`__.

*libadalina-core* is partially funded by the European Union - Next Generation EU, Mission 4, Component 1 CUP J33C22002910001 - GRINS foundation, Project ADALINA.

Features
--------

* Reading and writing geospatial data from various formats
* Spatial joins between datasets
* Spatial aggregations
* Utilities for working with Apache Sedona
* Configuration helpers for setting up Apache Sedona

Requirements
------------

*libadalina-core* requires Python 3.10 and depends on the following libraries:

* apache-sedona
* pyspark
* pandas
* geopandas
* install-jdk

*libadalina-core* has been tested with OpenJDK 17.

.. _Amelia homepage: https://grins.it/progetto/piattaforma-amelia