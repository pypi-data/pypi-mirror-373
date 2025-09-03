from typing import TYPE_CHECKING, Optional, Sequence, Union

if TYPE_CHECKING:
    import pandas as pd
    import pyspark.sql
    from google.oauth2.credentials import Credentials


PROJECT_ID = "skt-datahub"
TEMP_DATASET = "temp_1d"
TEMP_GCS_BUCKET = "temp-seoul-7d"
LOCATION = "asia-northeast3"
CREDENTIALS_SECRET_PATH = "gcp/skt-datahub/dataflow"


def get_credentials() -> "Credentials":
    from .gcp_credentials import get_gcp_credentials

    return get_gcp_credentials()


def get_credentials_json_with_base64() -> str:
    import base64

    from .gcp_credentials import get_gcp_credentials_json_string

    return base64.b64encode(get_gcp_credentials_json_string().encode()).decode()


def get_bigquery_storage_client(credentials=None):
    from google.cloud import bigquery_storage

    if credentials is None:
        credentials = get_credentials()

    return bigquery_storage.BigQueryReadClient(credentials=credentials)


def _get_result_schema(sql, bq_client=None, project_id=PROJECT_ID):
    from google.cloud.bigquery.job import QueryJobConfig

    if bq_client is None:
        bq_client = get_bigquery_client(project_id=project_id)

    job_config = QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = bq_client.query(sql, job_config=job_config)
    return {"fields": [col.to_api_repr() for col in query_job.schema]}


def _get_result_column_type(sql, column, bq_client=None, project_id=PROJECT_ID):
    schema = _get_result_schema(sql, bq_client=bq_client, project_id=project_id)
    fields = schema["fields"]
    r = [field["type"] for field in fields if field["name"] == column]
    if r:
        return r[0]
    else:
        raise ValueError(f"Cannot find column {column} in {sql}")


def _print_query_job_results(query_job):
    try:
        t = query_job.destination
        dest_str = f"{t.project}.{t.dataset_id}.{t.table_id}" if t else "no destination"
        print(
            f"query: {query_job.query}\n"
            f"destination: {dest_str}\n"
            f"total_rows: {query_job.result().total_rows}\n"
            f"slot_secs: {query_job.slot_millis / 1000}\n"
        )
    except Exception as e:
        print("Warning: exception on print statistics")
        print(e)


def bq_insert_overwrite_table(sql, destination, project_id=PROJECT_ID):
    from google.cloud.bigquery import QueryJobConfig

    bq = get_bigquery_client(
        project_id=project_id,
    )

    table = bq.get_table(destination)
    if table.time_partitioning or table.range_partitioning:
        load_query_result_to_partitions(sql, destination, project_id)
    else:
        config = QueryJobConfig(
            destination=destination,
            write_disposition="WRITE_TRUNCATE",
            create_disposition="CREATE_NEVER",
            clustering_fields=table.clustering_fields,
        )
        job = bq.query(sql, config)
        job.result()
        _print_query_job_results(job)
        bq.close()


def bq_ctas(sql, destination=None, partition_by=None, clustering_fields=None, project_id=PROJECT_ID):
    """
    create new table and insert results
    """
    from google.cloud.bigquery import (
        PartitionRange,
        QueryJobConfig,
        RangePartitioning,
        TimePartitioning,
    )

    bq = get_bigquery_client(project_id=project_id)
    if partition_by:
        partition_type = _get_result_column_type(sql, partition_by, bq_client=bq, project_id=project_id)
        if partition_type == "DATE":
            qjc = QueryJobConfig(
                destination=destination,
                write_disposition="WRITE_EMPTY",
                create_disposition="CREATE_IF_NEEDED",
                time_partitioning=TimePartitioning(field=partition_by),
                clustering_fields=clustering_fields,
            )
        elif partition_type == "INTEGER":
            qjc = QueryJobConfig(
                destination=destination,
                write_disposition="WRITE_EMPTY",
                create_disposition="CREATE_IF_NEEDED",
                range_partitioning=RangePartitioning(
                    PartitionRange(start=200001, end=209912, interval=1), field=partition_by
                ),
                clustering_fields=clustering_fields,
            )
        else:
            raise Exception(f"Partition column[{partition_by}] is neither DATE or INTEGER type.")
    else:
        qjc = QueryJobConfig(
            destination=destination,
            write_disposition="WRITE_EMPTY",
            create_disposition="CREATE_IF_NEEDED",
            clustering_fields=clustering_fields,
        )

    job = bq.query(sql, qjc)
    job.result()
    _print_query_job_results(job)
    bq.close()

    return job.destination


def _bq_query_to_new_table(sql, destination=None, project_id=PROJECT_ID):
    return bq_ctas(sql, destination, project_id=project_id)


def _bq_query_to_existing_table(sql, destination, project_id=PROJECT_ID):
    from google.cloud.bigquery.job import QueryJobConfig

    bq = get_bigquery_client(project_id=project_id)
    table = bq.get_table(destination)
    config = QueryJobConfig(
        destination=destination,
        write_disposition="WRITE_TRUNCATE",
        create_disposition="CREATE_NEVER",
        time_partitioning=table.time_partitioning,
        range_partitioning=table.range_partitioning,
        clustering_fields=table.clustering_fields,
    )
    job = bq.query(sql, config)
    job.result()
    bq.close()

    return job.destination


def _bq_table_to_pandas(table, project_id=PROJECT_ID):
    credentials = get_credentials()
    bq = get_bigquery_client(credentials=credentials, project_id=project_id)
    bqstorage_client = get_bigquery_storage_client(credentials=credentials)
    row_iterator = bq.list_rows(table)
    df = row_iterator.to_dataframe(bqstorage_client=bqstorage_client, progress_bar_type="tqdm")
    bq.close()

    return df


def _bq_cell_magic(line, query):
    import time

    from google.cloud.bigquery.magics.magics import _cell_magic, context
    from IPython.core import magic_arguments

    context.credentials = get_credentials()

    start = time.time()
    args = magic_arguments.parse_argstring(_cell_magic, line)

    if args.project is None:
        line = f"{line} --project {PROJECT_ID}"

    if args.params is not None:
        try:
            import ast

            from google.cloud.bigquery.dbapi import _helpers

            params = _helpers.to_query_parameters(ast.literal_eval("".join(args.params)), {})
            query_params = dict()
            for p in params:
                query_params[p.name] = p.value
            query = query.format(**query_params)
        except Exception:
            raise SyntaxError("--params is not a correctly formatted JSON string or a JSON " "serializable dictionary")
    result = _cell_magic(line, query)
    print(f"BigQuery execution took {int(time.time() - start)} seconds.")
    return result


def _load_bq_ipython_extension(ipython):
    ipython.register_magic_function(_bq_cell_magic, magic_kind="cell", magic_name="bq")


def set_gcp_credentials():
    import os
    import tempfile

    from .vault_utils import get_secrets

    key = get_secrets(CREDENTIALS_SECRET_PATH)["config"]
    key_file_name = tempfile.mkstemp()[1]
    with open(key_file_name, "wb") as key_file:
        key_file.write(key.encode())
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file.name


# deprecated
def import_bigquery_ipython_magic():
    load_bigquery_ipython_magic()


def load_bigquery_ipython_magic():
    from .notebook_utils import is_in_notebook

    if is_in_notebook():
        from IPython import get_ipython

        _load_bq_ipython_extension(get_ipython())
    else:
        raise Exception("Cannot import bigquery magic. Because execution is not on ipython.")


def get_bigquery_client(credentials=None, project_id=PROJECT_ID, location=LOCATION):
    import json
    import os

    from google.cloud import bigquery

    if credentials is None:
        credentials = get_credentials()

    job_config_labels = {
        "nes_client_id": str(os.environ.get("CLIENT_ID", "")),
        "jupyterhub_user": str(os.environ.get("JUPYTERHUB_USER", "")),
    }

    nes_client_context = os.environ.get("CLIENT_CONTEXT")
    if nes_client_context:
        nes_client_context_dict = json.loads(nes_client_context)
        job_config_labels.update(nes_client_context_dict)

    for k, v in job_config_labels.items():
        job_config_labels.update({k: v.lower().replace(".", "_") if v else v})

    return bigquery.Client(
        credentials=credentials,
        project=project_id,
        location=location,
        default_query_job_config=bigquery.QueryJobConfig(
            labels=job_config_labels,
        ),
    )


def bq_table_exists(table, project_id=PROJECT_ID):
    from google.cloud import exceptions

    try:
        get_bigquery_client(project_id=project_id).get_table(table)
        return True
    except exceptions.NotFound:
        return False


def get_unhidden_partitions(table_name, project_id=PROJECT_ID):
    parts = filter(
        lambda x: x not in ["__NULL__", "__UNPARTITIONED__"],
        get_bigquery_client(project_id=project_id).list_partitions(table_name),
    )
    return parts


def _get_partition_filter(
    dataset: str,
    table_name: str,
    partition: str,
    project_id: Optional[str] = PROJECT_ID,
):
    table = get_bigquery_client(project_id=project_id).get_table(f"{dataset}.{table_name}")
    if table.time_partitioning:
        partition_column_name = table.time_partitioning.field
        return f"{partition_column_name} = '{partition}'"
    elif table.range_partitioning:
        partition_column_name = table.range_partitioning.field
        return f"{partition_column_name} = {partition}"
    else:
        return ""


def bq_to_pandas(sql, large=False, project_id=PROJECT_ID):
    destination = None
    if large:
        destination = get_temp_table(project_id=project_id)
    destination = _bq_query_to_new_table(sql, destination, project_id=project_id)
    return _bq_table_to_pandas(destination, project_id=project_id)


def _bq_query_to_df(
    query: str,
    spark: Optional["pyspark.sql.SparkSession"] = None,
    project_id=PROJECT_ID,
) -> "pyspark.sql.DataFrame":
    from .ye import get_spark

    spark = spark or get_spark()

    df = (
        spark.read.format("bigquery")
        .option("credentials", get_credentials_json_with_base64())
        .option("parentProject", project_id)
        .option("project", project_id)
        .option("viewsEnabled", "true")
        .option("materializationProject", project_id)
        .option("materializationDataset", TEMP_DATASET)
        .load(query)
    )
    return df


def _bq_table_to_df(
    dataset: str,
    table_name: str,
    col_list: Union[str, Sequence["pyspark.sql.Column"]],
    partition: Optional[str] = None,
    where: Optional[Union["pyspark.sql.Column", str]] = None,
    spark: Optional["pyspark.sql.SparkSession"] = None,
    project_id: Optional[str] = PROJECT_ID,
) -> "pyspark.sql.DataFrame":
    from .ye import get_spark

    if not spark:
        spark = get_spark()

    df = (
        spark.read.format("bigquery")
        .option("credentials", get_credentials_json_with_base64())
        .option("parentProject", project_id)
        .option("project", project_id)
        .option("table", f"{project_id}:{dataset}.{table_name}")
    )

    if partition:
        df_filter = _get_partition_filter(
            dataset=dataset,
            table_name=table_name,
            partition=partition,
            project_id=project_id,
        )

        if df_filter:
            df = df.option("filter", df_filter)

    df = df.load().select(col_list)

    if where:
        df.where(where)

    return df


def bq_to_df(
    query: str,
    spark_session: Optional["pyspark.sql.SparkSession"] = None,
    project_id=PROJECT_ID,
) -> "pyspark.sql.DataFrame":
    return _bq_query_to_df(
        query=query,
        spark=spark_session,
        project_id=project_id,
    )


def bq_table_to_df(
    dataset: str,
    table_name: str,
    col_list: Union[str, Sequence["pyspark.sql.Column"]],
    partition: Optional[str] = None,
    where: Optional[Union["pyspark.sql.Column", str]] = None,
    spark_session: Optional["pyspark.sql.SparkSession"] = None,
    project_id: Optional[str] = PROJECT_ID,
) -> "pyspark.sql.DataFrame":
    return _bq_table_to_df(
        dataset=dataset,
        table_name=table_name,
        col_list=col_list,
        partition=partition,
        where=where,
        spark=spark_session,
        project_id=project_id,
    )


def bq_table_to_parquet(
    dataset: str,
    table_name: str,
    output_dir: str,
    col_list: Union[str, Sequence[str]] = "*",
    partition: Optional[str] = None,
    where: Optional[Union["pyspark.sql.Column", str]] = None,
    mode: str = "overwrite",
    project_id: Optional[str] = PROJECT_ID,
):
    bq_table_to_df(
        dataset=dataset,
        table_name=table_name,
        col_list=col_list,
        partition=partition,
        where=where,
        project_id=project_id,
    ).write.mode(mode).parquet(path=output_dir)


def bq_table_to_pandas(dataset, table_name, col_list="*", partition=None, where=None, project_id=PROJECT_ID):
    col_list_str = ", ".join(col_list) if isinstance(col_list, list) else col_list
    query = f"SELECT {col_list_str} FROM {dataset}.{table_name} "
    if partition or where:
        query += "WHERE "
        conditions = []
        if partition:
            conditions.append(f" {_get_partition_filter(dataset, table_name, partition, project_id=project_id)} ")
        if where:
            conditions.append(f" {where} ")
        query += " AND ".join(conditions)
    return bq_to_pandas(sql=query, project_id=project_id)


def _df_to_bq_table(
    df: "pyspark.sql.DataFrame",
    dataset: str,
    table_name: str,
    partition: Optional[str] = None,
    partition_field: Optional[str] = None,
    clustering_fields: Optional[Sequence[str]] = None,
    mode: str = "overwrite",
    project_id: Optional[str] = PROJECT_ID,
):
    table = f"{dataset}.{table_name}${partition}" if partition else f"{dataset}.{table_name}"

    df = (
        df.write.format("bigquery")
        .option("credentials", get_credentials_json_with_base64())
        .option("parentProject", project_id)
        .option("project", project_id)
        .option("table", table)
        .option("temporaryGcsBucket", TEMP_GCS_BUCKET)
    )
    if partition_field:
        df = df.option("partitionField", partition_field)

    if clustering_fields:
        df = df.option("clusteredFields", ",".join(clustering_fields))

    df.save(mode=mode)


def df_to_bq_table(
    df: "pyspark.sql.DataFrame",
    dataset: str,
    table_name: str,
    partition: Optional[str] = None,
    partition_field: Optional[str] = None,
    clustering_fields: Optional[Sequence[str]] = None,
    mode: str = "overwrite",
    project_id: Optional[str] = PROJECT_ID,
):
    _df_to_bq_table(
        df=df,
        dataset=dataset,
        table_name=table_name,
        partition=partition,
        partition_field=partition_field,
        clustering_fields=clustering_fields,
        mode=mode,
        project_id=project_id,
    )


def parquet_to_bq_table(
    parquet_dir: str,
    dataset: str,
    table_name: str,
    partition: Optional[str] = None,
    partition_field: Optional[str] = None,
    clustering_fields: Optional[Sequence[str]] = None,
    mode: str = "overwrite",
    project_id: Optional[str] = PROJECT_ID,
    spark: Optional["pyspark.sql.SparkSession"] = None,
):
    from .ye import get_spark

    if not spark:
        spark = get_spark()

    df = spark.read.format("parquet").load(parquet_dir)
    _df_to_bq_table(
        df=df,
        dataset=dataset,
        table_name=table_name,
        partition=partition,
        partition_field=partition_field,
        clustering_fields=clustering_fields,
        mode=mode,
        project_id=project_id,
    )


def pandas_to_bq_table(
    pd_df: "pd.DataFrame",
    dataset: str,
    table_name: str,
    partition: Optional[str] = None,
    partition_field: Optional[str] = None,
    clustering_fields: Optional[Sequence[str]] = None,
    mode: str = "overwrite",
    project_id: Optional[str] = PROJECT_ID,
    spark: Optional["pyspark.sql.SparkSession"] = None,
):
    from .ye import get_spark

    if not spark:
        spark = get_spark()

    spark_df = spark.createDataFrame(pd_df)
    _df_to_bq_table(
        df=spark_df,
        dataset=dataset,
        table_name=table_name,
        partition=partition,
        partition_field=partition_field,
        clustering_fields=clustering_fields,
        mode=mode,
        project_id=project_id,
    )


def pandas_to_bq(
    pd_df,
    destination,
    partition=None,
    clustering_fields=None,
    overwrite=True,
    project_id=PROJECT_ID,
):
    from google.cloud.bigquery import (
        PartitionRange,
        RangePartitioning,
        TimePartitioning,
    )
    from google.cloud.bigquery.job import LoadJobConfig

    range_partitioning = None
    time_partitioning = None

    bq = get_bigquery_client(project_id=project_id)

    if bq_table_exists(destination, project_id=project_id):
        target_table = bq.get_table(destination)
        range_partitioning = target_table.range_partitioning
        time_partitioning = target_table.time_partitioning
    else:
        if partition:
            import datetime

            from pandas.core.dtypes.common import is_integer_dtype

            if is_integer_dtype(pd_df[partition][0]):
                range_partitioning = RangePartitioning(
                    PartitionRange(start=200001, end=209912, interval=1), field=partition
                )
            elif isinstance(pd_df[partition][0], datetime.date):
                time_partitioning = TimePartitioning(field=partition)
            else:
                raise Exception("Partition type must be either date or range.")

    if time_partitioning or range_partitioning:
        if time_partitioning:
            input_partitions = [(p.strftime("%Y%m%d"), p) for p in set(pd_df[partition])]
        elif range_partitioning:
            input_partitions = [(p, p) for p in set(pd_df[partition])]
        else:
            input_partitions = []
        for part, part_val in input_partitions:
            bq.load_table_from_dataframe(
                dataframe=pd_df[pd_df[partition] == part_val],
                destination=f"{destination}${part}",
                job_config=LoadJobConfig(
                    create_disposition="CREATE_IF_NEEDED",
                    write_disposition="WRITE_TRUNCATE" if overwrite else "WRITE_APPEND",
                    time_partitioning=time_partitioning,
                    range_partitioning=range_partitioning,
                    clustering_fields=clustering_fields,
                ),
            ).result()
    else:
        bq.load_table_from_dataframe(
            dataframe=pd_df,
            destination=destination,
            job_config=LoadJobConfig(
                create_disposition="CREATE_IF_NEEDED",
                write_disposition="WRITE_TRUNCATE" if overwrite else "WRITE_APPEND",
            ),
        ).result()
    bq.close()


# decorator for rdd to pandas in mapPartitions in Spark
def rdd_to_pandas(func):
    def _rdd_to_pandas(rdd_):
        import pandas as pd
        from pyspark.sql import Row

        rows = (row_.asDict() for row_ in rdd_)
        pdf = pd.DataFrame(rows)
        result_pdf = func(pdf)
        return [Row(**d) for d in result_pdf.to_dict(orient="records")]

    return _rdd_to_pandas


def load_query_result_to_table(dest_table, query, part_col_name=None, clustering_fields=None, project_id=PROJECT_ID):
    from google.cloud.bigquery import (
        PartitionRange,
        QueryJobConfig,
        RangePartitioning,
        TimePartitioning,
    )

    bq_client = get_bigquery_client(project_id=project_id)
    print(query)
    if bq_table_exists(dest_table, project_id=project_id):
        table = bq_client.get_table(dest_table)
        qjc = QueryJobConfig(
            destination=dest_table,
            write_disposition="WRITE_TRUNCATE",
            create_disposition="CREATE_IF_NEEDED",
            time_partitioning=table.time_partitioning,
            range_partitioning=table.range_partitioning,
            clustering_fields=table.clustering_fields,
        )
        job = bq_client.query(query, job_config=qjc)
        job.result()
    else:
        temp_table_name = get_temp_table(project_id=project_id)
        bq_client.query(f"CREATE OR REPLACE TABLE {temp_table_name} AS {query}").result()
        if part_col_name:
            schema = bq_client.get_table(temp_table_name).schema
            partition_type = [f for f in schema if f.name.lower() == part_col_name.lower()][0].field_type
            if partition_type == "DATE":
                qjc = QueryJobConfig(
                    destination=dest_table,
                    write_disposition="WRITE_TRUNCATE",
                    create_disposition="CREATE_IF_NEEDED",
                    time_partitioning=TimePartitioning(field=part_col_name),
                    clustering_fields=clustering_fields,
                )
            elif partition_type == "INTEGER":
                qjc = QueryJobConfig(
                    destination=dest_table,
                    write_disposition="WRITE_TRUNCATE",
                    create_disposition="CREATE_IF_NEEDED",
                    range_partitioning=RangePartitioning(
                        PartitionRange(start=200001, end=209912, interval=1), field=part_col_name
                    ),
                    clustering_fields=clustering_fields,
                )
            else:
                print(partition_type)
                raise Exception(f"Partition column[{part_col_name}] is neither DATE or INTEGER type.")
        else:
            qjc = QueryJobConfig(
                destination=dest_table,
                write_disposition="WRITE_TRUNCATE",
                create_disposition="CREATE_IF_NEEDED",
            )
        bq_client.query(f"SELECT * FROM {temp_table_name}", job_config=qjc).result()


def get_temp_table(project_id=PROJECT_ID):
    import uuid

    table_id = str(uuid.uuid4()).replace("-", "_")
    full_table_id = f"{project_id}.{TEMP_DATASET}.{table_id}"

    return full_table_id


def gcs_to_bq(table_name, bucket_name, bigquery_dataset, bigquery_table, overwrite=True, project_id=PROJECT_ID):
    from google.cloud.bigquery import LoadJobConfig, SourceFormat, WriteDisposition

    job_config = None
    if overwrite:
        job_config = LoadJobConfig(
            write_disposition=WriteDisposition.WRITE_TRUNCATE,
            source_format=SourceFormat.PARQUET,
        )
    else:
        job_config = LoadJobConfig(
            write_disposition=WriteDisposition.WRITE_APPEND,
            source_format=SourceFormat.PARQUET,
        )

    bigquery_path = f"{bigquery_dataset}.{bigquery_table}"
    client = get_bigquery_client(project_id=project_id)
    uri = f"gs://{bucket_name}/{table_name}/*"
    load_job = client.load_table_from_uri(uri, bigquery_path, job_config=job_config)
    load_job.result()


def _get_partition_name(table):
    if table.range_partitioning:
        return table.range_partitioning.field
    elif table.time_partitioning:
        return table.time_partitioning.field
    else:
        raise Exception(f"Table[{table}] is not partitioned.")


def get_bigquery_table_partition_info(dataset, table_name, project_id=PROJECT_ID):
    client = get_bigquery_client(project_id=project_id)
    bigquery_path = f"{dataset}.{table_name}"
    table_info = client.get_table(bigquery_path)
    if table_info.range_partitioning:
        return {
            "partitioning": "range_partitioning",
            "field": table_info.range_partitioning.field,
            "start": table_info.range_partitioning.range_.start,
            "end": table_info.range_partitioning.range_.end,
            "interval": table_info.range_partitioning.range_.interval,
        }
    elif table_info.time_partitioning:
        return {
            "partitioning": "time_partitioning",
            "field": table_info.time_partitioning.field,
            "type": table_info.time_partitioning.type_,
        }
    else:
        return None


def load_query_result_to_partitions(query, dest_table, project_id=PROJECT_ID):
    from google.cloud.bigquery import DatasetReference, QueryJobConfig, TableReference

    bq = get_bigquery_client(project_id=project_id)
    table = bq.get_table(dest_table)

    """
    Destination 이 파티션일 때는 임시테이블 만들지 않고 직접 저장
    """
    if "$" in dest_table:
        qjc = QueryJobConfig(
            destination=table,
            write_disposition="WRITE_TRUNCATE",
            create_disposition="CREATE_IF_NEEDED",
            time_partitioning=table.time_partitioning,
            range_partitioning=table.range_partitioning,
            clustering_fields=table.clustering_fields,
        )
        job = bq.query(query, job_config=qjc)
        job.result()
        _print_query_job_results(job)
        return dest_table

    temp_table_id = get_temp_table(project_id=project_id)
    qjc = QueryJobConfig(
        destination=temp_table_id,
        write_disposition="WRITE_TRUNCATE",
        create_disposition="CREATE_IF_NEEDED",
        time_partitioning=table.time_partitioning,
        range_partitioning=table.range_partitioning,
        clustering_fields=table.clustering_fields,
    )
    bq.query(query, job_config=qjc).result()
    partitions = bq.list_partitions(temp_table_id)
    for p in partitions:
        part_name = _get_partition_name(table)
        if p == "__NULL__":
            if table.range_partitioning:
                columns = ["NULL" if f.name.lower() == part_name.lower() else f.name for f in table.schema]
            elif table.time_partitioning:
                columns = ["DATE(NULL)" if f.name.lower() == part_name.lower() else f.name for f in table.schema]
            job = bq.query(
                f"""
                DELETE FROM `{dest_table}` WHERE {part_name} IS NULL
                ;
                INSERT INTO `{dest_table}`
                SELECT {', '.join(columns)}
                FROM   `{temp_table_id}`
                WHERE  {part_name} IS NULL
            """
            )
            job.result()
            _print_query_job_results(job)
        else:
            project_id, dataset_id, table_id = dest_table.split(".")
            ref = TableReference(DatasetReference(project_id, dataset_id), f"{table_id}${p}")
            qjc = QueryJobConfig(
                destination=ref,
                write_disposition="WRITE_TRUNCATE",
                create_disposition="CREATE_IF_NEEDED",
                time_partitioning=table.time_partitioning,
                range_partitioning=table.range_partitioning,
                clustering_fields=table.clustering_fields,
            )
            if table.range_partitioning:
                query = f"select * from {temp_table_id} where {part_name}={p}"
            elif table.time_partitioning:
                partition = f"{p[:4]}-{p[4:6]}-{p[6:8]}"
                query = f"select * from {temp_table_id} where {part_name}='{partition}'"
            job = bq.query(query, job_config=qjc)
            job.result()
            _print_query_job_results(job)

    return partitions


def get_max_part(table_name, project_id=PROJECT_ID):
    from datetime import datetime

    bq_client = get_bigquery_client(project_id=project_id)
    parts = get_unhidden_partitions(table_name, project_id=project_id)

    if not parts:
        raise Exception("Max partition value is invalid or null.")

    max_part_value = max(parts)

    table = bq_client.get_table(table_name)
    if table.time_partitioning:
        return datetime.strptime(max_part_value, "%Y%m%d").strftime("%Y-%m-%d")
    elif table.range_partitioning:
        return int(max_part_value)
    else:
        raise Exception("Partition column is neither DATE or INTEGER type.")


def bq_insert_overwrite(sql, destination, suffixes=None, partition=None, clustering_fields=None, project_id=PROJECT_ID):
    if suffixes:
        bq_insert_overwrite_with_suffixes(
            sql, destination, suffixes, partition, clustering_fields, project_id=project_id
        )
    else:
        bq_insert_overwrite_without_suffixes(sql, destination, partition, clustering_fields, project_id=project_id)


def bq_insert_overwrite_with_suffixes(
    sql, destination, suffixes, partition=None, clustering_fields=None, project_id=PROJECT_ID
):
    temp_table = get_temp_table(project_id=project_id)
    bq_ctas(sql, temp_table, partition_by=partition, clustering_fields=clustering_fields, project_id=project_id)
    bq = get_bigquery_client(project_id=project_id)
    r = bq.query(f"""select distinct {', '.join(suffixes)} from {temp_table}""")
    for cols in r:
        suffix = "".join([f"__{col}" for col in cols])
        select_clause = f"select * except({', '.join(suffixes)}) from {temp_table}"
        where_clause = " and ".join([f"{x[0]} = '{x[1]}'" for x in zip(suffixes, cols)])
        target = "".join([destination, suffix])
        sub_sql = f"{select_clause} where {where_clause}"
        bq_insert_overwrite_without_suffixes(
            sub_sql, target, partition=partition, clustering_fields=clustering_fields, project_id=project_id
        )
    bq.close()


def bq_insert_overwrite_without_suffixes(
    sql, destination, partition=None, clustering_fields=None, project_id=PROJECT_ID
):
    if bq_table_exists(destination, project_id=project_id):
        bq_insert_overwrite_table(sql, destination, project_id=project_id)
    else:
        bq_ctas(sql, destination, partition_by=partition, clustering_fields=clustering_fields, project_id=project_id)


def get_storage_client(credentials=None, project_id=PROJECT_ID):
    from google.cloud import storage

    if credentials is None:
        credentials = get_credentials()

    return storage.Client(credentials=credentials, project=project_id)


def storage_create_json(filename, storage_client=None, bucket_name=None, json_object=""):
    import json

    if storage_client is None:
        raise Exception("storage_client is None")

    if bucket_name is None or _storage_bucket_exist(storage_client, bucket_name) is False:
        raise Exception("storage bucket is Not exist")

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)

    return blob.upload_from_string(data=json.dumps(json_object), content_type="application/json")


def storage_create_text(filename, storage_client=None, bucket_name=None, text=""):
    if storage_client is None:
        raise Exception("storage_client is None")

    if bucket_name is None or _storage_bucket_exist(storage_client, bucket_name) is False:
        raise Exception("storage bucket is Not exist")

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    return blob.upload_from_string(data=text, content_type="application/text")


def storage_object_exist(filename, storage_client=None, bucket_name=None):
    if storage_client is None:
        raise Exception("storage_client is None")

    if bucket_name is None or _storage_bucket_exist(storage_client, bucket_name) is False:
        raise Exception("storage bucket is Not exist")

    bucket = storage_client.get_bucket(bucket_name)
    return bucket.blob(filename).exists()


def storage_object_remove(filename, storage_client=None, bucket_name=None):
    from google.cloud import exceptions

    if storage_client is None:
        raise Exception("storage_client is None")

    if bucket_name is None or _storage_bucket_exist(storage_client, bucket_name) is False:
        raise Exception("storage bucket is Not exist")

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    try:
        blob.delete()
    except exceptions.NotFound:
        pass

    if storage_object_exist(filename, storage_client, bucket_name):
        return False
    return True


def storage_object_load(filename, storage_client=None, bucket_name=None):
    if storage_client is None:
        raise Exception("storage_client is None")

    if bucket_name is None or _storage_bucket_exist(storage_client, bucket_name) is False:
        raise Exception("storage bucket is Not exist")

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    return blob.download_as_string()


def _storage_bucket_exist(storage_client, bucket_name):
    from google.cloud.storage import Bucket

    exists = Bucket(storage_client, bucket_name).exists()

    return exists
