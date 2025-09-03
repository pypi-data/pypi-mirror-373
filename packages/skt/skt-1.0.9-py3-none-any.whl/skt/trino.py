import os
import uuid
from typing import Union

import pandas as pd
from sqlalchemy import text

from skt.gcp import (
    PROJECT_ID,
    bq_table_exists,
    gcs_to_bq,
    get_bigquery_table_partition_info,
)


def get_trino_engine(
    cluster_name: str = None,
    host: str = "gateway-idp-prd.sktai.io",
    port: int = 443,
    connect_args: dict = None,
    user: str = None,
    password: str = None,
    extra_connect_args: dict = None,
):
    from sqlalchemy import create_engine
    from trino.sqlalchemy import URL

    nb_user = os.environ.get("NB_USER", "skt")

    # jovyan: NES로 실행 시 Jupyter 이미지일 경우 NB_USER가 jovyan으로 설정된다.
    # skt: 임의의 장소에서 패키지를 실행했을 경우 NB_USER 값이 없을 수 있는데, 이럴 경우 skt로 설정한다.

    if cluster_name is None:
        cluster_name = "aidp-cluster" if nb_user in ["jovyan", "skt"] else "aidp-interactive"

    client_tag = "NES" if nb_user in ["jovyan", "skt"] else "jupyter"

    extra_connect_args = extra_connect_args or {}
    connect_args = connect_args or {
        "extra_credential": [("cluster_name", cluster_name)],
        "http_scheme": "https",
        "client_tags": [client_tag],
        **extra_connect_args,
    }

    return create_engine(
        URL(host=host, port=port, user=user or nb_user, password=password),
        connect_args=connect_args,
    )


def init_trino(
    cluster_name: str = None,
    host: str = "gateway-idp-prd.sktai.io",
    port: int = 443,
    connect_args: dict = None,
    user: str = None,
    password: str = None,
    extra_connect_args: dict = None,
):
    engine = get_trino_engine(cluster_name, host, port, connect_args, user, password, extra_connect_args)

    try:
        from IPython import get_ipython

        ipython = get_ipython()
        if ipython:
            ipython.run_line_magic("load_ext", "sql", 1)
            ipython.run_line_magic("alias_magic", "trino sql", 1)
            ipython.run_line_magic("sql", "engine", 1)
    except ImportError:
        print("IPython not found, skipping magic commands")

    return engine


def _overwrite_trino_query_result_to_bq_table_partition(
    trino_query, temp_table_name, bigquery_dataset, bigquery_table, partition_info, project_id=PROJECT_ID
):
    engine = get_trino_engine()

    with engine.connect() as conn:
        insert_phrase = f"""create table "ye"."gcs_temp_seoul_1d"."{temp_table_name}" with (format = 'PARQUET') as\n"""
        insert_query = insert_phrase + trino_query
        gcs_temp_table_ctas_result = conn.execute(text(insert_query))
        print(gcs_temp_table_ctas_result.fetchall()[0][0], "rows overwrite")

        temp_table_range_distinct = (
            f"""select distinct({partition_info['field']}) from "ye"."gcs_temp_seoul_1d"."{temp_table_name}"\n"""
        )
        temp_table_range_distinct_proxy = conn.execute(text(temp_table_range_distinct))
        temp_table_range_distinct_values = temp_table_range_distinct_proxy.fetchall()
        temp_table_partition_values = [row[0] for row in temp_table_range_distinct_values]
        for delete_partition in temp_table_partition_values:
            if partition_info["partitioning"] == "time_partitioning":
                delete_partition_str = delete_partition.strftime("%Y-%m-%d")
                delete_query = f"""delete from "bigquery"."{bigquery_dataset}"."{bigquery_table}" where {partition_info['field']}=DATE('{delete_partition_str}')"""
                conn.execute(text(delete_query))
                print(
                    f"partition_column: {partition_info['field']}", f"overwrite partition value: {delete_partition_str}"
                )
            elif partition_info["partitioning"] == "range_partitioning":
                delete_query = f"""delete from "bigquery"."{bigquery_dataset}"."{bigquery_table}" where {partition_info['field']}={delete_partition}"""
                conn.execute(text(delete_query))
                print(f"partition_column: {partition_info['field']}", f"overwrite partition value: {delete_partition}")

        conn.commit()
        gcs_to_bq(temp_table_name, "temp-seoul-1d", bigquery_dataset, bigquery_table, overwrite=False)


def load_trino_query_result_to_bq_table(
    trino_query, bigquery_dataset, bigquery_table, overwrite=False, project_id=PROJECT_ID
):
    is_bq_table_exist = bq_table_exists(f"{bigquery_dataset}.{bigquery_table}", project_id=project_id)
    temp_table_name = "temp_" + str(uuid.uuid4()).replace("-", "_")

    if is_bq_table_exist and overwrite:
        partition_info = get_bigquery_table_partition_info(bigquery_dataset, bigquery_table)
        if partition_info:
            _overwrite_trino_query_result_to_bq_table_partition(
                trino_query, temp_table_name, bigquery_dataset, bigquery_table, partition_info
            )
        else:
            load_trino_query_result_to_ye_gcs(trino_query, temp_table_name)
            gcs_to_bq(temp_table_name, "temp-seoul-1d", bigquery_dataset, bigquery_table, overwrite=True)
            return
    else:
        load_trino_query_result_to_ye_gcs(trino_query, temp_table_name)
        gcs_to_bq(temp_table_name, "temp-seoul-1d", bigquery_dataset, bigquery_table, overwrite=False)
        return


def load_trino_query_result_to_ye_gcs(trino_query, ye_table_name, ye_schema_name="gcs_temp_seoul_1d") -> str:
    engine = get_trino_engine()
    tables_list_df = show_tables("ye", ye_schema_name)
    table_list = list(tables_list_df["Table"])
    insert_phrase = None
    if ye_table_name in table_list:
        insert_phrase = f"""insert into "ye"."{ye_schema_name}"."{ye_table_name}"\n"""
    else:
        insert_phrase = f"""create table "ye"."{ye_schema_name}"."{ye_table_name}" with (format = 'PARQUET') as\n"""
    insert_query = insert_phrase + trino_query
    with engine.connect() as conn:
        conn.execute(text(insert_query))
        conn.commit()

    return f'''"ye"."{ye_schema_name}"."{ye_table_name}"'''


def get_trino_query_execution_result(query: str, cluster_name: str = None) -> pd.DataFrame:
    query_text = text(query)
    engine = get_trino_engine(cluster_name=cluster_name)
    with engine.begin() as conn:
        result = conn.execute(query_text)
        columns = result.keys()
        data = result.fetchall()
        df = pd.DataFrame(data, columns=columns)

    return df


def execute_trino_query(query: str, cluster_name: str = None):
    query_text = text(query)
    engine = get_trino_engine(cluster_name=cluster_name)
    with engine.connect() as conn:
        conn.execute(query_text)
        conn.commit()

    return


def show_catalogs(cluster_name: str = None) -> pd.DataFrame:
    query = "show catalogs"
    print(query)
    return get_trino_query_execution_result(query, cluster_name)


def show_schemas(catalog_name: str, cluster_name: str = None) -> pd.DataFrame:
    query = f'''show schemas from "{catalog_name}"'''
    print(query)
    return get_trino_query_execution_result(query, cluster_name)


def show_tables(catalog_name: str, schema_name: str, cluster_name: str = None) -> pd.DataFrame:
    query = f'''show tables from "{catalog_name}"."{schema_name}"'''
    print(query)
    return get_trino_query_execution_result(query, cluster_name)


def show_table(catalog_name: str, schema_name: str, table_name: str, cluster_name: str = None) -> pd.DataFrame:
    query = f'''show tables from "{catalog_name}"."{schema_name}"."{table_name}"'''
    print(query)
    return get_trino_query_execution_result(query, cluster_name)


def create_iceberg_table_from_trino_query_result(
    trino_query: str, catalog_name: str, schema_name: str, table_name: str, partition_column: Union[str, list] = None
):
    partition_column_string = None
    if partition_column is None:
        pass
    elif isinstance(partition_column, list):
        partition_column_string = ", ".join(f"'{str(col)}'" for col in partition_column)
    elif isinstance(partition_column, str):
        partition_column_string = f"'{partition_column}'"
    else:
        raise ValueError("partition_column should be either a string or a list")

    create_table_phrase = f'''create table "{catalog_name}"."{schema_name}"."{table_name}"'''
    if partition_column:
        create_table_phrase += f""" WITH(
        partitioning = ARRAY[{partition_column_string}])"""
    query = create_table_phrase + f""" AS\n{trino_query}"""
    get_trino_query_execution_result(query)


def load_trino_query_result_to_bingo(trino_query: str, bingo_schema_name: str, bingo_table_name: str, overwrite=False):
    tables = show_tables("bingo", bingo_schema_name)
    table_list = list(tables["Table"])
    # 테이블 미 존재시, 생성
    if bingo_table_name not in table_list:
        create_iceberg_table_from_trino_query_result(trino_query, "bingo", bingo_schema_name, bingo_table_name)
        return

    if overwrite:
        delete_query = f'''delete from "bingo"."{bingo_schema_name}"."{bingo_table_name}"'''
        execute_trino_query(delete_query)
        query = f"""insert into "bingo"."{bingo_schema_name}"."{bingo_table_name}"\n{trino_query}"""
        execute_trino_query(query)
    else:
        query = f"""insert into "bingo"."{bingo_schema_name}"."{bingo_table_name}"\n{trino_query}"""
        execute_trino_query(query)


def load_trino_query_result_to_onprem_backup(trino_query: str, table_name: str, overwrite=False):
    tables = show_tables("bingo", "cold_archive")
    table_list = list(tables["Table"])
    # 테이블 미 존재시, 생성
    if table_name not in table_list:
        create_iceberg_table_from_trino_query_result(trino_query, "bingo", "cold_archive", table_name)
        return

    if overwrite:
        delete_query = f'''delete from "bingo"."cold_archive"."{table_name}"'''
        execute_trino_query(delete_query)
        query = f"""insert into "bingo"."cold_archive"."{table_name}"\n{trino_query}"""
        execute_trino_query(query)
    else:
        query = f"""insert into "bingo"."cold_archive"."{table_name}"\n{trino_query}"""
        execute_trino_query(query)


def get_trino_query_result_column_distinct_values(trino_query: str, column_name: str) -> list:
    temp_table_name = "temp_" + str(uuid.uuid4()).replace("-", "_")
    create_iceberg_table_from_trino_query_result(trino_query, "bingo", "temp_1d", temp_table_name)
    query = f'''select distinct "{column_name}" from "bingo"."temp_1d"."{temp_table_name}"'''
    result = get_trino_query_execution_result(query)
    value_list = list(result[column_name])
    return value_list
