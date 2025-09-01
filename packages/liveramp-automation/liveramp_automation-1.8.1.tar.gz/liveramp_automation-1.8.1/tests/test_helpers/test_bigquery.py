from unittest.mock import patch

from liveramp_automation.helpers.bigquery import BigQueryConnector

project_id = "liveramp-eng-qa-reliability"
dataset_id = "customer_impact_hours"
table_name = "bbm_test_table"
connector = BigQueryConnector(project_id, dataset_id)
sql_query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}` where age > 1;"
output_csv_path = "tests/test_helpers/test.csv"
cucumber_json_path = "tests/resources/cucumber.json"
bucket_name = "liveramp_automation_test"
source_blob_name = "Unit/test.csv"


def mocked_requests_response_exception(*args, **kwargs):
    if len(args) > 0 and 'Finish' in args[0]:
        raise Exception("Test")
    pass


def test_connect():
    result = connector.connect()
    assert result == 0


@patch('liveramp_automation.utils.log.Logger.debug', side_effect=mocked_requests_response_exception)
def test_connect_exception(mock):
    result = connector.connect()
    assert result is None


def test_query():
    result = connector.query(sql_query)
    if result:
        for row in result:
            print(row)
    assert result


@patch('liveramp_automation.utils.log.Logger.debug', side_effect=mocked_requests_response_exception)
def test_query_exception(mock):
    result = connector.query(sql_query)
    assert result is None


def test_query_rows():
    result = connector.query_rows(sql_query)
    assert result


@patch('liveramp_automation.utils.log.Logger.debug', side_effect=mocked_requests_response_exception)
def test_query_rows_exception(mock):
    result = connector.query_rows(sql_query)
    assert result is None


def test_query_export():
    result = connector.query_export(sql_query, output_csv_path)
    assert result == 0


@patch('liveramp_automation.utils.log.Logger.debug', side_effect=mocked_requests_response_exception)
def test_query_export_exception(mock):
    result = connector.query_export(sql_query, output_csv_path)
    assert result is None


def test_dataset_tables():
    result = connector.dataset_tables()
    assert result


@patch('liveramp_automation.utils.log.Logger.debug', side_effect=mocked_requests_response_exception)
def test_dataset_tables_exception(mock):
    result = connector.dataset_tables()
    assert result is None


def test_insert_from_bucket():
    result = connector.insert_from_bucket(bucket_name, source_blob_name, table_name)
    assert result


@patch('liveramp_automation.utils.log.Logger.debug', side_effect=mocked_requests_response_exception)
def test_insert_from_bucket_exception(mock):
    result = connector.insert_from_bucket(bucket_name, source_blob_name, table_name)
    assert result is None
