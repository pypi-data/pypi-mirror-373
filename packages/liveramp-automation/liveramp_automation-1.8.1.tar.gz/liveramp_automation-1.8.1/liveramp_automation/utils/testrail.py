import os
import json
import base64
import configparser
from liveramp_automation.utils import request
import yaml


class TestRailUtils:
    url = ''
    run_url = ''
    suite_config_file = ""
    report_file = ""
    project_id = 0
    suite_config = {}
    filtered_case_ids = []
    include_all = True
    user = os.getenv('TESTRAIL_USERNAME', default=None)
    password = os.getenv('TESTRAIL_API_KEY', default=None)

    auth = str(
        base64.b64encode(
            bytes('%s:%s' % (user, password), 'utf-8')
        ),
        'ascii'
    ).strip()
    headers = {'Authorization': 'Basic ' + auth, 'Content-Type': 'application/json'}

    def __init__(self):
        self.read_configuration()

    def read_configuration(self):
        print("read_configuration")
        config = configparser.ConfigParser()
        try:
            with open("pytest.ini", 'r') as file:
                config.read_file(file)
                try:
                    self.url = config.get('testrail', 'url')
                except (configparser.NoSectionError, configparser.NoOptionError):
                    self.url = 'https://liveramp.testrail.io/index.php?/api/v2/'
                try:
                    self.run_url = config.get('testrail', 'run_url')
                except (configparser.NoSectionError, configparser.NoOptionError):
                    self.run_url = 'https://liveramp.testrail.io/index.php?/runs/view/'
                try:
                    self.report_file = config.get('testrail', 'report_file')
                except (configparser.NoSectionError, configparser.NoOptionError):
                    self.report_file = './reports/report.json'
                try:
                    self.suite_config_file = config.get('testrail', 'suite_config_file')
                    self.read_suite_config_file()
                except (configparser.NoSectionError, configparser.NoOptionError):
                    self.suite_config_file = ""
                    self.suite_config = {}
                try:
                    self.project_id = int(config.get('testrail', 'project_id'))
                except (configparser.NoSectionError, configparser.NoOptionError):
                    self.project_id = 0
        except FileNotFoundError:
            self.url = 'https://liveramp.testrail.io/index.php?/api/v2/'
            self.run_url = 'https://liveramp.testrail.io/index.php?/runs/view/'
            self.report_file = './reports/report.json'

    def read_suite_config_file(self):
        if "yml" in self.suite_config_file or "yaml" in self.suite_config_file:
            with open(self.suite_config_file, 'r') as file:
                print(file)
                self.suite_config = yaml.safe_load(file)

    def add_run(self, test_suite):
        response = request.request_post(
            self.url + 'add_run/' + str(self.project_id), self.headers, None, self.get_json_data_for_run(test_suite)
        )
        self.verify_response(response)
        return response.json()['id']

    def get_json_data_for_run(self, test_suite):

        suite_data = None

        if "test_suites" in self.suite_config:
            for suite_info in self.suite_config["test_suites"]:
                if suite_info["name"] == test_suite:
                    suite_data = suite_info
                    break

        # no suite data
        if suite_data is None:
            raise APIError('Test suite not found in suite config file')

        json_data = {
            "suite_id": None,
            "name": "Run name not set",
            "description": "Run description not set",
            "include_all": True
        }
        self.include_all = True
        self.filtered_case_ids = []
        # only suite data
        if "suite_id" in suite_data:
            json_data["suite_id"] = suite_data["suite_id"]
        if "run_name" in suite_data:
            json_data["name"] = os.path.expandvars(suite_data["run_name"])
        if "description" in suite_data:
            json_data["description"] = os.path.expandvars(suite_data["description"])

        # default to all test cases, we don't need the call to retrieve the cases
        if not ("priority_id" in suite_data or "type_id" in suite_data or "query" in suite_data):
            return json_data

        case_ids = self.get_case_id_list(suite_data)

        if case_ids is not None:
            json_data["include_all"] = False
            json_data["case_ids"] = case_ids
            self.include_all = False
            self.filtered_case_ids.extend(case_ids)

        return json_data

    def verify_response(self, response):
        if response.status_code > 201:
            try:
                error = response.json()
            except:  # response.content not formatted as JSON
                error = str(response.content)
            raise APIError('TestRail API returned HTTP %s (%s)' % (response.status_code, error), response.status_code)

    def get_case_id_list(self, suite_data):
        query = ""
        if "query" in suite_data:
            query = suite_data["query"]
        else:
            if "suite_id" in suite_data:
                query = query + "&suite_id=" + str(suite_data["suite_id"])
            if "priority_id" in suite_data:
                query = query + "&priority_id=" + str(suite_data["priority_id"])
            if "type_id" in suite_data:
                query = query + "&type_id=" + str(suite_data["type_id"])

        return self.get_case_id_by_query(query)

    def get_case_id_by_query(self, query):
        response = request.request_get(
            self.url + 'get_cases/' + str(self.project_id) + query,
            self.headers
        )
        self.verify_response(response)

        cases_data = response.json()["cases"]
        cases = []
        for case in cases_data:
            cases.append(case['id'])
        return cases

    # This file helps to share the report URL to slack.
    def export_test_run_url(self, test_run_id):
        with open("test_run_url.txt", "w") as f:
            f.write(self.run_url + str(test_run_id) + '\n')

    def contains_case_id(self, test):
        return any(item.startswith('Case') for item in test['keywords'])

    def create_case_dict(self, case_id, test_result):
        status_id = 1 if test_result['outcome'] == 'passed' else 5
        case_dict = {
            "case_id": case_id,
            "status_id": status_id,
            "environment": "iwe"
        }
        return case_dict

    def add_case_to_list(self, test_result, results_list):
        # Case IDs are in the format 'Case:1234'
        case_ids = list(x for x in test_result['keywords'] if x.startswith('Case'))
        case_ids = map(lambda x: int(x.split(':')[1]), case_ids)
        for case_id in case_ids:
            if (self.include_all is True
                    or case_id in self.filtered_case_ids
                    or len(self.filtered_case_ids) == 0):
                results_list.append(self.create_case_dict(case_id, test_result))

    def get_results_from_report(self):
        print(os.getcwd())
        with open(self.report_file, 'r') as file:
            report = json.load(file)

        tests_with_case_id_iterator = filter(self.contains_case_id, report['tests'])
        tests_with_case_id = list(tests_with_case_id_iterator)
        results_list = []
        for test in tests_with_case_id:
            self.add_case_to_list(test, results_list)

        return results_list

    def add_results_for_cases(self, run_id, results):
        print(results)
        response = request.request_post(
            self.url + 'add_results_for_cases/' + str(run_id), self.headers, None,
            {
                "results": results
            }
        )
        self.verify_response(response)

    def upload_results(self, test_suite):
        try:
            test_run_id = self.add_run(test_suite)
            print("Test run created successfully, ID: " + str(test_run_id))
            print(self.run_url + str(test_run_id))
            self.export_test_run_url(test_run_id)
            self.add_results_for_cases(test_run_id, self.get_results_from_report())
            print('Uploaded results to test run successfully')

        except APIError as e:
            print('Error: Failed to upload results', e)

        print("************Upload Results to Test Rail Has Completed.******************")


class APIError(Exception):
    pass
