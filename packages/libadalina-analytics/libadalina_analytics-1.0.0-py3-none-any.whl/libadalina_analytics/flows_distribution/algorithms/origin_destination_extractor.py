import networkx as nx
from libadalina_core.sedona_utils import DataFrame, to_spark_dataframe, DEFAULT_EPSG
import pyspark.sql as ps
from pyspark import Row
from pyspark.sql import functions as func
from pyspark.sql.functions import udf
from pyspark.sql.types import StructType, StringType, NumericType, IntegerType, LongType
from sedona.sql import ST_Intersects, ST_Distance, ST_Centroid, ST_SetSRID, ST_SRID

@udf(returnType=LongType())
def first_item_udf(value: Row):
    if value:
        return value._1
    return -1


def get_shape_node(
        graph: nx.Graph,
        shape_df: DataFrame,
        index_column: str,
        columns_to_keep: list[str] = None
) -> ps.DataFrame:
    """
    """
    shape_df = to_spark_dataframe(shape_df)

    # Convert nodes to spark DataFrame
    edges_df = (shape_df.sparkSession.createDataFrame(
        (((p1, p2), data['geometry']) for p1, p2, data in graph.edges(data=True)),
        ['edge', 'geometry']
    ))
    edges_df = edges_df.withColumn('geometry', ST_SetSRID(edges_df.geometry, DEFAULT_EPSG.value))

    shape_df = (shape_df
            .join(edges_df, on=ST_Intersects(shape_df.geometry, edges_df.geometry), how='inner')
            .select('*', ST_Distance(ST_Centroid(shape_df.geometry), edges_df.geometry).alias('distance_to_centroid'))
            .groupBy(shape_df[index_column])
                .agg(
                    *(func.first(c).alias(c) for c in (shape_df.columns if columns_to_keep is None else columns_to_keep) if c != 'geometry'),
                    func.min_by(edges_df.edge, 'distance_to_centroid').alias('closest_edge')
                )
            .select('*', first_item_udf(func.col('closest_edge')).alias('closest_node'))
            )

    if columns_to_keep is not None and 'geometry' not in columns_to_keep:
        shape_df = shape_df.drop('geometry')
    return shape_df
