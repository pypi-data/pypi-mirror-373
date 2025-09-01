import os
import uuid
from google.cloud import bigquery
from liveramp_automation.utils.log import Logger
from liveramp_automation.utils.time import MACROS
from liveramp_automation.helpers.file import FileHelper
from liveramp_automation.helpers.bucket import BucketHelper


class reportUtils:

    def __init__(self, report_folder="reports", report_cucumber_path="reports/cucumber.json"):
        self.projectId = None
        self.bucket_name = None
        self.path_name = None
        self.report_folder = report_folder
        self.report_cucumber_path = report_cucumber_path

    def upload_report_files_to_gcs_bucket(self,
                                          project_id="liveramp-eng-qa-reliability",
                                          bucket_name=os.getenv("BUCKET_NAME", "bbm-e2e-tests"),
                                          path_name=os.getenv("BUCKET_PATH_NAME", "default_bucket")
                                          ):
        self.projectId = project_id
        self.bucket_name = bucket_name
        self.path_name = path_name
        BucketHelper(self.projectId, self.bucket_name).upload_file(self.report_folder, self.path_name)

    def bigquery_ref_tables(self,
                            project_id="liveramp-eng-qa-reliability",
                            dataset_id="customer_impact_hours",
                            round_table="bbm_round_table",
                            feature_table="bbm_feature_table",
                            scenario_table="bbm_scenario_table",
                            step_table="bbm_step_table"):
        self.round_table_ref = f"{project_id}.{dataset_id}.{round_table}"
        self.feature_table_ref = f"{project_id}.{dataset_id}.{feature_table}"
        self.scenario_table_ref = f"{project_id}.{dataset_id}.{scenario_table}"
        self.step_table_ref = f"{project_id}.{dataset_id}.{step_table}"

    def insert_from_pytest_bdd_cucumber_report(self):
        report_context = FileHelper.read_json_report(self.report_cucumber_path)
        if len(report_context) > 0 :
            client = bigquery.Client()
            unique_id = str(uuid.uuid4())
            rounds = []
            features = []
            scenarios = []
            steps = []

            for feature in report_context:
                feature_row = {"id": str(uuid.uuid4()),
                               "feature_round_id": unique_id,
                               "feature_id": feature["id"],
                               "feature_uri": feature["uri"],
                               "feature_name": feature["name"],
                               "feature_description": feature["description"],
                               "feature_line": feature["line"],
                               "feature_keyword": feature["keyword"],
                               "feature_timestamp": MACROS["now_readable"]
                               }

                feature_scenarios, feature_steps = self._get_scenarios_steps_from_feature_(feature, unique_id)
                scenarios = scenarios + feature_scenarios
                steps = steps + feature_steps

                feature_row["feature_scenarios"] = ",".join(map(lambda x: x["id"], feature_scenarios))
                Logger.debug(f'Feature Row: {feature_row}')
                features.append(feature_row)

            round_execution_result = "PASS"
            failed_count = 0
            failed_step_id = set()
            for step in steps:
                if step["step_status"].lower() == "failed" and step["step_scenario_id"] not in failed_step_id:
                    failed_count += 1
                    failed_step_id.add(step["step_scenario_id"])

            if failed_count > 0:
                round_execution_result = "FAIL"
            test_round = {"id": unique_id,
                          "round_id": unique_id,
                          "round_execution_env": os.environ.get('ENVCHOICE', 'PROD').upper(),
                          "round_suite_name": os.environ.get('PRODUCTNAME', '').upper(),
                          "round_execution_time": MACROS["now"],
                          "round_timestamp": MACROS["now_readable"],
                          "round_feature_ids": ",".join(map(lambda x: x["id"], features)),
                          "round_execution_result": round_execution_result,
                          "round_scenario_count": len(scenarios),
                          "round_step_failed_count": failed_count
                          }
            rounds.append(test_round)
            round_table = client.get_table(self.round_table_ref)
            round_table_errors = client.insert_rows(round_table, rounds)
            if round_table_errors:
                Logger.error(f'Round Table errors: {str(round_table_errors)}')
                return -1

            feature_table = client.get_table(self.feature_table_ref)
            feature_errors = client.insert_rows(feature_table, features)
            if feature_errors:
                Logger.error(f'Feature Table errors: {str(feature_errors)}')
                return -1

            scenario_table = client.get_table(self.scenario_table_ref)
            scenario_errors = client.insert_rows(scenario_table, scenarios)
            if scenario_errors:
                Logger.error(f'Scenario table errors: {str(scenario_errors)}')
                return -1

            step_table = client.get_table(self.step_table_ref)
            for step in steps:
                if "step_scenario_id" in step:
                    del step["step_scenario_id"]

            step_errors = client.insert_rows(step_table, steps)
            if step_errors:
                Logger.error(f'Step Table errors: {str(step_errors)}')
                return -1
            return 0
        return -1

    def _get_scenarios_steps_from_feature_(self, feature, unique_id):
        scenarios = []
        steps = []
        for scenario in feature["elements"]:
            scenario_row = {"id": str(uuid.uuid4()),
                            "scenario_round_id": unique_id,
                            "scenario_id": scenario["id"],
                            "scenario_name": scenario["name"],
                            "scenario_description": scenario["description"],
                            "scenario_line": scenario["line"],
                            "scenario_keyword": scenario["keyword"],
                            "scenario_timestamp": MACROS["now_readable"],
                            "scenario_tags": ",".join(map(lambda x: x["name"], scenario["tags"]))}
            scenario_steps = self._get_steps_from_scenario_(scenario, unique_id)
            step_ids = map(lambda x: x["id"], scenario_steps)
            scenario_row['scenario_steps'] = ",".join(step_ids)
            steps = steps + scenario_steps
            scenarios.append(scenario_row)
        return scenarios, steps

    def _get_steps_from_scenario_(self, scenario, unique_id):
        steps = []
        for step in scenario["steps"]:
            step_row = {"id": str(uuid.uuid4()),
                        "step_scenario_id": scenario["id"],
                        "step_round_id": unique_id,
                        "step_name": step["name"],
                        "step_keyword": step["keyword"],
                        "step_line": step["line"],
                        # "step_status": step["result"]["status"],
                        "step_status": step["result"].get("status", "passed"),
                        "step_duration": step["result"]["duration"],
                        "step_location": step["match"]["location"],
                        "step_timestamp": MACROS["now_readable"]}
            if "error_message" in step["result"]:
                step_row["step_error_message"] = step["result"]["error_message"]
            steps.append(step_row)
        return steps
