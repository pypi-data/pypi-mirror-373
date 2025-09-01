from pyspark.sql import SparkSession
from sedona.spark import SedonaContext
import pandas as pd
from libadalina_core.sedona_configuration.jdk_installer import install_jdk_if_needed

# compatibility with Pandas
pd.DataFrame.iteritems = pd.DataFrame.items

def _add_spark_config(spark: SparkSession.Builder, spark_configs: dict[str, str] | None = None) -> SparkSession.Builder:
    spark = (spark.config(
                "spark.jars.packages",
                "org.apache.sedona:sedona-spark-3.3_2.12:1.7.1,"
                "org.datasyslab:geotools-wrapper:1.7.1-28.5",
            )
            .config(
                "spark.jars.repositories",
                "https://artifacts.unidata.ucar.edu/repository/unidata-all"
            ))
    if spark_configs is not None:
        for k, v in spark_configs.items():
            spark = spark.config(k, v)
    return spark

def _get_sedona_master_configuration(master_host: str, spark_configs: dict[str, str] | None = None) -> SparkSession:
    spark = SparkSession.builder.appName("Adalina").master(master_host)
    spark = _add_spark_config(spark, spark_configs)
    return SedonaContext.create(spark.getOrCreate())

def _sedona_configuration(spark_configs: dict[str, str] | None = None) -> SparkSession:
    config = SedonaContext.builder().appName("Adalina")
    config = _add_spark_config(config, spark_configs)
    return SedonaContext.create(config.getOrCreate())

_sedona_context: SparkSession | None = None

def init_sedona_context(
        spark_master: str | None = None,
        spark: SparkSession | None = None,
        spark_configs: dict[str, str] | None = None
):
    """
    Initialize the Sedona context for spatial data processing.

    This function can either:

    1. Create a new Sedona context with a specified Spark master,
    2. Use an existing SparkSession, or
    3. Create a default Sedona context with the default Spark configuration.

    If no parameters are provided, it will create a default Sedona context (option 3).

    If a `JAVA_HOME` environment variable is not set, it will attempt to install a compatible JDK.

    Parameters
    ----------
    spark_master : str, optional
        The Spark master URL to connect to. If provided, a new Sedona context will be created with this master.
    spark : pyspark.sql.SparkSession, optional
        An existing SparkSession to use. If provided, it will be used to create the Sedona context.

    Examples
    --------
    Initialize the global Sedona session with a default configuration

    >>> init_sedona_context()

    Initialize the global Sedona session referencing to a given Spark master

    >>> init_sedona_context(spark_master="spark://localhost:7077")

    Initialize the session using a pre-existing SparkSession

    >>> spark = SparkSession.builder.getOrCreate()
    >>> init_sedona_context(spark=spark)
    """
    global _sedona_context

    install_jdk_if_needed()

    if spark_master is not None:
        _sedona_context = _get_sedona_master_configuration(spark_master, spark_configs)
    elif isinstance(spark, SparkSession):
        _sedona_context = SedonaContext.create(spark)
    else:
        _sedona_context = _sedona_configuration(spark_configs)

def get_sedona_context() -> SparkSession:
    """
    Get the Sedona context for spatial data processing.
    This context is the one used for all spatial operations in libadalina.

    If the Sedona context has not been initialized yet with `init_sedona_context`, 
    the function `init_sedona_context` will be called to initialize it with the default configuration.

    Returns
    -------
    pyspark.sql.SparkSession
        The Sedona context as a SparkSession.
    """
    global _sedona_context

    if _sedona_context is None:
        init_sedona_context()
    return _sedona_context
