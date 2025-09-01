from enum import Enum

from .single_table_operators import bounding_box, cut_features
import pyspark.sql as ps
import pyspark.sql.functions as func

from libadalina_core.sedona_utils import to_spark_dataframe, DataFrame
from sedona.sql import ST_Intersects, ST_Intersection, ST_GeomFromWKT
from shapely import intersection
from shapely.geometry import Polygon


class JoinType(Enum):
    """Enumerate the types of joins that can be performed on two DataFrames."""

    INNER = 'inner'
    """Inner join returns only the matching records from both tables."""
    LEFT = 'left'
    """Left join returns all records from left table and matching records from right table."""
    RIGHT = 'right'
    """Right join returns all records from right table and matching records from left table."""
    FULL = 'full'
    """Full join returns all records from both tables, matching where possible."""

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

def spatial_join(
        left_table: DataFrame,
        right_table: DataFrame,
        join_type: JoinType = JoinType.INNER
    ) -> ps.DataFrame:
    """
    Perform a spatial join between two DataFrames based on the intersection of their geometries.

    Parameters
    ----------
    left_table : DataFrame
        DataFrame containing the left table of the join
    right_table : DataFrame
        DataFrame containing the right table of the join
    join_type : JoinType
        Type of the join to perform

    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame containing the result of the spatial join.
    """

    left_table = to_spark_dataframe(left_table)
    right_table = to_spark_dataframe(right_table)

    return (left_table
              .withColumnRenamed('geometry', 'geometry_left')
              .join(right_table.withColumnRenamed('geometry', 'geometry_right'),
                    on=ST_Intersects(func.col('geometry_left'), func.col('geometry_right')), how=join_type.value)
              )

def make_bounding_box_intersection(
    df1: DataFrame,
    df2: DataFrame,
) -> (ps.DataFrame, ps.DataFrame):
    """
    Make a bounding box intersection of two DataFrames and cut away
    the features that do not belong to the intersection.

    Parameters
    ----------
    df1 : DataFrame
        First DataFrame to intersect
    df2 : DataFrame
        Second DataFrame to intersect

    Returns
    -------
    pyspark.sql.DataFrame, pyspark.sql.DataFrame
        Two DataFrames that are cut to the intersection of their bounding boxes.
    """
    df1 = to_spark_dataframe(df1)
    df2 = to_spark_dataframe(df2)
    bbox1 = bounding_box(df1)
    bbox2 = bounding_box(df2)

    bbox_intersection = Polygon(intersection(bbox1, bbox2).exterior)

    df1_cut = cut_features(df1, bbox_intersection)
    df2_cut = cut_features(df2, bbox_intersection)
    return df1_cut, df2_cut