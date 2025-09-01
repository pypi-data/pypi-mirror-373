# libadalina-core

A Python library for spatial data processing.
It makes it easier to work with geospatial data in Python by providing a high-level interface
to Apache Sedona, a powerful geospatial processing engine, and integrates nicely with other well-known libraries
such as *geopandas* and *pandas*.

## Installation

liabadalina-core can be installed using pip:
```
pip install libadalina-core
```

If `JAVA_HOME` environment variable is not set a suitable JDK will be downloaded in `$HOME/.jre` and used automatically.
Not all JRE are supported, so if you encounter issues, you can try the automatically installed version.

## Usage

You can find the documentation and example at [libadalina-core documentation](https://libadalinacore-6b2a95.gitlab.io/).

## Features


* Reading and writing geospatial data from various formats
* Spatial joins between datasets
* Spatial aggregations
* Utilities for working with Apache Sedona
* Configuration helpers for setting up Apache Sedona

## Requirements

- Python 3.10
- Dependencies:
  - apache-sedona[spark]
  - pyspark
  - pandas
  - geopandas
  - install-jdk