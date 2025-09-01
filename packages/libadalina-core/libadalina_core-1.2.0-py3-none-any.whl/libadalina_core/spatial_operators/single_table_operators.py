from enum import Enum
from dataclasses import dataclass
from sedona.sql import ST_Area, ST_Intersection, ST_Union, ST_Buffer, ST_GeometryType, ST_Dump, ST_Intersects, ST_XMin, \
    ST_XMax, ST_YMax, ST_YMin, ST_GeomFromWKT
from libadalina_core.sedona_utils import to_spark_dataframe, DEFAULT_EPSG, DataFrame
import pyspark.sql.functions as func
import pyspark.sql as ps
from shapely import Polygon

def bounding_box(df: DataFrame) -> Polygon:
    """
    Calculate the bounding box of the geometries in a DataFrame.

    Parameters
    ----------
    df : DataFrame
        Either a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame containing geometries.

    Returns
    -------
    shapely.geometry.Polygon
        A Polygon representing the bounding box of the geometries in the DataFrame.
    """
    table = to_spark_dataframe(df)
    bounds = table.select(
        func.min(ST_XMin(table.geometry)).alias('min_x'),
        func.min(ST_YMin(table.geometry)).alias('min_y'),
        func.max(ST_XMax(table.geometry)).alias('max_x'),
        func.max(ST_YMax(table.geometry)).alias('max_y')
    ).first()

    return Polygon([(bounds.min_x, bounds.min_y), (bounds.max_x, bounds.min_y),
                    (bounds.max_x, bounds.max_y), (bounds.min_x, bounds.max_y)])


def cut_features(df: DataFrame, cut_geometry: Polygon) -> ps.DataFrame:
    """
    Cut the features of a DataFrame that do not intersect with a given geometry.

    This function will cut the geometries in the DataFrame by the provided cut geometry,
    returning only the parts of the geometries that intersect with the cut geometry.

    Parameters
    ----------
    df : DataFrame
        Either a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame containing geometries.
    cut_geometry : Polygon
        The geometry to use for cutting the features.

    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame with only the geometries that intersect with the cut geometry.
    """
    table = to_spark_dataframe(df)

    table = table.withColumn('cutting_geometry', ST_GeomFromWKT(func.lit(cut_geometry.wkt)))

    return table.select('*').where(
        ST_Intersects(table.geometry, func.col('cutting_geometry'))).drop('cutting_geometry')


def polygonize(df: DataFrame, radius_meters: float) -> ps.DataFrame:
    """
    Transform lines and points into polygons by buffering them with a given radius.

    Each line (or multi-line) is transformed into a polygon by buffering it on both sides,
    while points are buffered to create a circular area around them.

    Geometries are implicitly converted to DEFAULT_EPSG.

    Parameters
    ----------
    df : DataFrame
        The input DataFrame containing geometries.
    radius_meters : float
        The radius in meters to use for buffering points and lines.

    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame with a new column 'polygonized_geometry' containing the buffered geometries.

    Examples
    --------
    >>> df = pd.DataFrame({'geometry': ['POINT(1 1)', 'LINESTRING(0 0, 1 1, 2 2)']})
    >>> polygonized_df = polygonize(df, radius_meters=10)

    """
    table = to_spark_dataframe(df)
    return table.select("*", func
                        .when(ST_GeometryType(table.geometry).like('%Point%'),
                              ST_Buffer(func.col('geometry'), radius_meters, func.lit(True)))
                        .when(ST_GeometryType(func.col('geometry')).like('%LineString%'),
                              ST_Union(
                                  ST_Buffer(func.col('geometry'), radius_meters, func.lit(True),
                                            parameters=func.lit('endcap=flat side=left')),
                                  ST_Buffer(func.col('geometry'), radius_meters, func.lit(True),
                                            parameters=func.lit('endcap=flat side=right'))
                              ))
                        .otherwise(table.geometry)
                        .alias('polygonized_geometry')
                        )


def explode_multi_geometry(df: DataFrame) -> ps.DataFrame:
    """
    Explode multi-geometry features into individual geometries in such a way that each element
    of the multi-geometry is represented as a separate row in the DataFrame.

    Parameters
    ----------
    df : DataFrame
        Either a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame containing geometries.

    Returns
    -------
    pyspark.sql.DataFrame
        The input DataFrame with an additional column that contains the exploded geometries.
    """
    table = to_spark_dataframe(df)

    return table.select("*", func
                        .when(df.geometry.isNull(), func.array())
                        .when(ST_GeometryType(df.geometry).like('%Multi%'),
                              func.explode(ST_Dump(df.geometry)))
                        .otherwise(df.geometry)
                        )


class AggregationType(Enum):
    """Functions that can be used to aggregate data in a DataFrame."""

    COUNT = 'count'
    """Count the number of rows in a group."""
    SUM = 'sum'
    """Sum the values in a column for each group."""
    AVG = 'avg'
    """Calculate the average of the values in a column for each group."""
    MIN = 'min'
    """Find the minimum value in a column for each group."""
    MAX = 'max'
    """Find the maximum value in a column for each group."""

    def to_spark_func(self):
        if self == AggregationType.COUNT:
            return func.count
        elif self == AggregationType.SUM:
            return func.sum
        elif self == AggregationType.AVG:
            return func.avg
        elif self == AggregationType.MIN:
            return func.min
        elif self == AggregationType.MAX:
            return func.max
        return func.count  # Default to count if none matched

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

@dataclass
class AggregationFunction:
    """Dataclass representing an aggregation function to be applied to a column in a DataFrame."""

    column: str
    """The name of the column to aggregate."""
    aggregation_type: AggregationType
    """The function to use for aggregation."""
    alias: str | None = None
    """Optional alias for the aggregated column."""
    proportional: str | None = None
    """Optional column to use for proportional aggregation. If specified, the aggregation will be weighted by the area of the intersection with this column's geometry."""

def spatial_aggregation(table: DataFrame,
                        aggregate_functions: list[AggregationFunction],
                        group_by_column: str = 'geometry'
                        ) -> ps.DataFrame:
    """
    Perform spatial aggregation on a DataFrame based on specified aggregation functions.
    Entries are aggregated by either the geometries in the DataFrame or the column given as input, and the specified aggregation functions are applied
    to the other grouped columns.

    Parameters
    ----------
    table : DataFrame
        Either a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame containing geometries.
    aggregate_functions : list[AggregationFunction]
        List of aggregation functions to apply to the DataFrame grouped columns.
    group_by_column : str, optional
        The name of the column to group by. Default is 'geometry'.

    Returns
    -------
    pyspark.sql.DataFrame
        A DataFrame with aggregated results based on the specified aggregation functions.
        All columns that are not specified in the aggregation functions will be aggregated using the first value found in each group.
    """
    table = to_spark_dataframe(table)

    columns_to_aggregate = [c.column for c in aggregate_functions]
    projection_of_not_aggregated_columns = (
        func.first(c).alias(c) for c in table.columns if c != group_by_column and c not in columns_to_aggregate
    )

    columns_with_no_proportional_aggregation = [c for c in aggregate_functions if c.proportional is None]
    columns_with_proportional_aggregation = [c for c in aggregate_functions if c.proportional is not None]

    projection_of_aggregated_columns = (
        agg_func.aggregation_type.to_spark_func()(func.col(agg_func.column)).alias(
            f"{agg_func.aggregation_type.value}({agg_func.column})" if agg_func.alias is None else agg_func.alias
        ) for agg_func in columns_with_no_proportional_aggregation if agg_func.column in table.columns
    )

    projection_of_proportional_aggregated_columns = (
        agg_func.aggregation_type.to_spark_func()(func.col(agg_func.column) * ST_Area(ST_Intersection(func.col('geometry'), func.col(agg_func.proportional))) / ST_Area(func.col(agg_func.proportional))).alias(
            f"{agg_func.aggregation_type.value}({agg_func.column})" if agg_func.alias is None else agg_func.alias
        ) for agg_func in columns_with_proportional_aggregation if agg_func.column in table.columns
    )

    # Group by geometry and aggregate other columns
    return (table
                    .groupby(group_by_column)
                    .agg(
                        # from the columns for which is not specified an aggregation function, take the first value
                        *projection_of_not_aggregated_columns,
                        # apply the aggregation functions to the other columns
                        *projection_of_aggregated_columns,
                        *projection_of_proportional_aggregated_columns
                    ))