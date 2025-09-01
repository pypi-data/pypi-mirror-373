from google.cloud import bigquery, storage
from liveramp_automation.utils.log import Logger


class BigQueryConnector:
    def __init__(self, project_id="liveramp-eng-qa-reliability", dataset_id="customer_impact_hours"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)

    def connect(self):
        """Connect with specific dataset.

        :return: None."""
        Logger.debug("Start connect")
        try:
            self.client.get_dataset(self.dataset_id)
            Logger.debug(f"Project = {self.project_id} on Dataset = {self.dataset_id}")
            Logger.debug("Finish connect")
            return 0
        except Exception as e:
            Logger.error(f'Error BigQuery Connection: {str(e)}')
            return None

    def query(self, sql_query):
        """Obtain the rows from a SQL.

        :param sql_query: string of SQL sentence.
        :return: list of dictionaries with the rows."""
        Logger.debug("Start query")
        try:
            Logger.debug(f"SQL = {sql_query}")
            query_job = self.client.query(sql_query)
            results = query_job.result()
            result_rows = [row for row in results]
            Logger.debug(result_rows)
            Logger.debug("Finish connect")
            return result_rows
        except Exception as e:
            Logger.error(f'Error SQL Query: {str(e)}')
            return None

    def query_rows(self, sql_query):
        """Obtain the number of rows from a SQL.

        :param sql_query: string of SQL sentence.
        :return: integer with the number of rows."""
        Logger.debug("Start query_rows")
        try:
            Logger.debug(f"SQL = {sql_query}")
            query_job = self.client.query(sql_query)
            results = query_job.result().total_rows
            Logger.debug(results)
            Logger.debug("Finish query_rows")
            return results
        except Exception as e:
            Logger.error(f'Error SQL Query: {str(e)}')
            return None

    def query_export(self, sql_query, output_csv_path):
        """Export the rows from a SQL.

        :param sql_query: string of SQL sentence.
        :param output_csv_path: string of the path for download file.
        :return: integer with the number of rows."""
        Logger.debug("Start query_export")
        try:
            Logger.debug(f"SQL = {sql_query} to  path {output_csv_path}")
            query_job = self.client.query(sql_query)
            df = query_job.to_dataframe()
            df.to_csv(output_csv_path, index=False)
            Logger.debug(df)
            Logger.debug("Finish query_export")
            return 0
        except Exception as e:
            Logger.error(f'Error SQL Query Download: {str(e)}')
            return None

    def dataset_tables(self):
        """Obtain the list with the tables in the dataset.

        :return: list with the names of the tables."""
        Logger.debug("Start dataset_tables")
        try:
            Logger.debug(f"dataset = {self.dataset_id}")
            dataset_ref = self.client.get_dataset(self.dataset_id)
            tables = self.client.list_tables(dataset_ref)
            table_names = [table.table_id for table in tables]
            Logger.debug(table_names)
            Logger.debug("Finish dataset_tables")
            return table_names
        except Exception as e:
            Logger.error(f'Error on dataset info: {str(e)}')
            return None

    def insert_from_bucket(self, bucket_name, source_blob_name, destination_table_name):
        """Insert into table info comes from bucket csv file.

        :param bucket_name: string of bucket name files csv comes from.
        :param source_blob_name: string of the path from csv file in the bucket.
        :param destination_table_name: string of table name.
        :return: None."""
        Logger.debug("Start insert_from_bucket")
        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(source_blob_name)

            dataset_ref = self.client.get_dataset(self.dataset_id)
            table_ref = dataset_ref.table(destination_table_name)

            job_config = bigquery.LoadJobConfig()
            job_config.source_format = bigquery.SourceFormat.CSV
            job_config.skip_leading_rows = 1

            load_job = self.client.load_table_from_uri(
                blob.public_url,
                table_ref,
                job_config=job_config
            )

            result = load_job.result()

            Logger.debug(result)
            Logger.debug(f'Data loaded in table "{destination_table_name}" from bucket "{bucket_name}"')
            Logger.debug("Finish insert_from_bucket")
            return result
        except Exception as e:
            Logger.error(f'Error on load data: {str(e)}')
            return None
