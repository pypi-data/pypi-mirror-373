from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4

from pyspark.sql import DataFrame, SparkSession


class HashType(str, Enum):
    RAW = "raw"
    LAKE_HASH = "lake_hash"
    SHA256 = "sha256"


def skt_hash(
    ss: SparkSession,
    df: DataFrame,
    before: Union[str, HashType],
    after: Union[str, HashType],
    key_column: Optional[Union[str, List[str]]] = None,
    key_type: Optional[Union[str, List[str]]] = None,
) -> DataFrame:
    """

    Transform hashed values between different hash types (raw, lake_hash, sha256).

    Args:
        ss (SparkSession): Spark session object
        df (DataFrame): Input DataFrame containing hashed values
        before (Union[str, HashType]): Current hash type of the values
        after (Union[str, HashType]): Target hash type to convert to
        key_column (Optional[Union[str, List[str]]]): Column name(s) containing hashed values
        key_type (Optional[Union[str, List[str]]]): Type(s) of the key(s) (e.g. 'svc_mgmt_num', 'cust_num')
    Example:
    Returns:
        DataFrame: DataFrame with transformed hash values

    Raises:
        ValueError: If invalid key_type is provided

    Example:
        >>> df = skt_hash(spark, df, 'lake_hash', 'raw', 'service_id', 'svc_mgmt_num')
        # Converts lake_hash values in service_id column to raw values

        >>> df = skt_hash(
        ...     spark,
        ...     df,
        ...     'lake_hash',
        ...     'raw',
        ...     key_column=['svc_mgmt_num', 'cust_num'],
        ...     key_type=['svc_mgmt_num', 'cust_num']
        ... )
        # Converts lake_hash values in service_id and customer_id columns to raw values
    """

    def get_mapping_df(ss: SparkSession, key_type: str) -> DataFrame:
        from pyspark.sql.utils import AnalysisException

        spark = ss
        table_name = f"aidp.{key_type}_mapping"
        try:
            mapping_df = spark.sql(
                f"""
                    SELECT raw, ye_hashed, lake_hashed 
                    FROM {table_name} 
                    WHERE dt = (SELECT MAX(dt) FROM {table_name})
                """
            )
        except AnalysisException as e:
            raise ValueError(f"{key_type}: Invalid key type")
        return mapping_df

    def lake_hash_to_sha256(ss: SparkSession, source_df: DataFrame, key: str, key_type: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")
        mapping_df = get_mapping_df(ss=spark, key_type=key_type)
        mapping_df.createOrReplaceTempView("mapping_table")

        uuid_col = uuid4().hex

        result_df = spark.sql(
            f"""
                SELECT
                    a.*,
                    sha2(b.raw, 256) as {uuid_col}
                FROM
                    source_table a
                    LEFT OUTER JOIN mapping_table b
                    ON a.{key} = b.lake_hashed
            """
        )

        result_df = result_df.drop(key).withColumnRenamed(uuid_col, key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")

        return result_df

    def lake_hash_to_raw(ss: SparkSession, source_df: DataFrame, key: str, key_type: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")
        mapping_df = get_mapping_df(ss=spark, key_type=key_type)
        mapping_df.createOrReplaceTempView("mapping_table")

        uuid_col = uuid4().hex

        result_df = spark.sql(
            f"""
                SELECT
                    a.*,
                    b.raw as {uuid_col}
                FROM
                    source_table a
                    LEFT OUTER JOIN mapping_table b
                    ON a.{key} = b.lake_hashed
            """
        )

        result_df = result_df.drop(key).withColumnRenamed(uuid_col, key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")

        return result_df

    def raw_to_sha256(ss: SparkSession, source_df: DataFrame, key: str, key_type: str) -> DataFrame:
        spark = ss
        source_df.createOrReplaceTempView("source_table")

        uuid_col = uuid4().hex

        result_df = spark.sql(
            f"""
                SELECT
                    a.*,
                    sha2({key}, 256) as {uuid_col}
                FROM
                    source_table a
            """
        )

        result_df = result_df.drop(key).withColumnRenamed(uuid_col, key)

        spark.catalog.dropTempView("source_table")
        return result_df

    def raw_to_lake_hash(ss: SparkSession, source_df: DataFrame, key: str, key_type: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")
        mapping_df = get_mapping_df(ss=spark, key_type=key_type)
        mapping_df.createOrReplaceTempView("mapping_table")

        uuid_col = uuid4().hex

        result_df = spark.sql(
            f"""
                SELECT
                    a.*,
                    b.lake_hashed as {uuid_col}
                FROM
                    source_table a
                    LEFT OUTER JOIN mapping_table b
                    ON a.{key} = b.raw
            """
        )

        result_df = result_df.drop(key).withColumnRenamed(uuid_col, key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")

        return result_df

    def sha256_to_raw(ss: SparkSession, source_df: DataFrame, key: str, key_type: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")
        mapping_df = get_mapping_df(ss=spark, key_type=key_type)
        mapping_df.createOrReplaceTempView("mapping_table")

        uuid_col = uuid4().hex

        result_df = spark.sql(
            f"""
                SELECT
                    a.*,
                    b.raw as {uuid_col}
                FROM
                    source_table a
                    LEFT OUTER JOIN mapping_table b
                    ON a.{key} = b.ye_hashed
            """
        )

        result_df = result_df.drop(key).withColumnRenamed(uuid_col, key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")

        return result_df

    def sha256_to_lake_hash(ss: SparkSession, source_df: DataFrame, key: str, key_type: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")
        mapping_df = get_mapping_df(ss=spark, key_type=key_type)
        mapping_df.createOrReplaceTempView("mapping_table")

        uuid_col = uuid4().hex

        result_df = spark.sql(
            f"""
                SELECT
                    a.*,
                    b.lake_hashed as {uuid_col}
                FROM
                    source_table a
                    LEFT OUTER JOIN mapping_table b
                    ON a.{key} = b.ye_hashed
            """
        )

        result_df = result_df.drop(key).withColumnRenamed(uuid_col, key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")

        return result_df

    if isinstance(before, str):
        before = HashType(before)

    if isinstance(after, str):
        after = HashType(after)

    if key_type is None:
        key_types = ["svc_mgmt_num"]
    elif isinstance(key_type, str):
        key_types = [key_type]
    elif isinstance(key_type, list):
        key_types = key_type

    if key_column is None:
        key_columns = ["svc_mgmt_num"]
    elif isinstance(key_column, str):
        key_columns = [key_column]
    elif isinstance(key_column, list):
        key_columns = key_column

    if len(key_columns) != len(key_types):
        raise ValueError(
            f"Length of key_columns ({len(key_columns)}) and key_types ({len(key_types)}) must be the same"
        )

    conversion_func_name = f"{before.value}_to_{after.value}"

    result_df = df
    for k_col, k_type in zip(key_columns, key_types):
        result_df = eval(conversion_func_name)(ss=ss, source_df=result_df, key=k_col, key_type=k_type)

    return result_df.select(df.columns)


skt_crypto = skt_hash
