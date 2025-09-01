Amelia integration
==================

*libadalina-core* can be easily integrated within the *Amelia* platform since both are designed to
work with pandas DataFrames.

*libadalina-core* can be installed in an *Amelia* Jupyter Notebook environment using :code:`pip` and
then it can be referenced to use its functionalities.

In the following example, a dataset is read from *Amelia* using te :code:`ameliadp_sql_toolkit` package
and then processed using *libadalina-core* to obtain polygons from the lines of a road map.

.. WARNING::

   Package :code:`ameliadp_sql_toolkit` is not publicly available at the moment, so this example
   can be run only in an *Amelia* Jupyter Notebook environment.

.. toctree::

   /_collections/notebooks/amelia_integration.ipynb
