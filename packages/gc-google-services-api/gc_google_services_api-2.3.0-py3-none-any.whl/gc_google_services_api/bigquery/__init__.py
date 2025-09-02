import logging

from google.api_core.exceptions import NotFound
from google.api_core.retry import Retry
from google.cloud import bigquery

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def wait_for_job(query_job):
    retry = Retry()
    retry(query_job.result)


def execute_query(query="", error_value=[]):
    """
    DEPRECATED: Now use BigQueryManager class instead this method.
    """
    client = bigquery.Client()
    query_job = client.query(query)

    try:
        wait_for_job(query_job)
        return query_job.result()
    except Exception as e:
        logging.error(
            f"[ERROR - (deprecated) execute_query]: {e} with query: {query}"
        )  # noqa: E501
        return error_value


def insert_batch(
    rows_to_insert=[], project_id="", dataset_id="", table_name=""
):  # noqa: E501
    """
    DEPRECATED: Now use BigQueryManager class instead this method.
    """
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

    table_ref = client.dataset(dataset_id, project_id).table(table_name)
    load_job = client.load_table_from_json(
        json_rows=rows_to_insert,
        destination=table_ref,
        job_config=job_config,
    )

    load_job.result()
    is_process_complete = load_job.state == "DONE"

    if is_process_complete:
        logging.info("Load batch data successfully.")
    else:
        logging.error("Error loading data:", load_job.errors)

    return is_process_complete


class BigQueryManager:
    def __init__(self, project_id, dataset_id):
        self.project_id = project_id
        self.dataset_id = dataset_id

        self.client = bigquery.Client(project=project_id)

    def create_table_if_not_exists(self, table_id, schema={}):
        def _parse_schemas():
            schema_fields = []
            for field_name, field_type in schema.items():
                schema_fields.append(
                    bigquery.SchemaField(
                        field_name,
                        field_type,
                    )
                )

            return schema_fields

        try:
            self.client.get_table(
                f"{self.project_id}.{self.dataset_id}.{table_id}",
            )
        except NotFound:
            table_ref = self.client.dataset(self.dataset_id).table(table_id)
            table = bigquery.Table(table_ref, schema=_parse_schemas())
            self.client.create_table(table)

    def wait_for_job(self, query_job):
        retry = Retry()
        retry(query_job.result)

    def execute_query(self, query="", error_value=[]):
        query_job = self.client.query(query)

        try:
            self.wait_for_job(query_job)

            return query_job.result()
        except Exception as e:
            logging.error(f"[ERROR - execute_query]: {e} with query: {query}")
            return error_value

    def load_massive_data(self, rows_to_insert, table_name):
        job_config = bigquery.LoadJobConfig()
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

        table_ref = self.client.dataset(self.dataset_id).table(table_name)

        load_job = self.client.load_table_from_json(
            json_rows=rows_to_insert,
            destination=table_ref,
            job_config=job_config,
        )

        load_job.result()
        is_process_complete = load_job.state == "DONE"

        if is_process_complete:
            logging.info("Load batch data successfully.")
        else:
            logging.error("Error loading data:", load_job.errors)

        return is_process_complete
