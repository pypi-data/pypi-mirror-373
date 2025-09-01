import json
import os
import yaml
from liveramp_automation.utils.log import Logger


class FileHelper:

    @staticmethod
    def read_json_report(path) -> dict:
        """Read the content of a JSON file.

        :param path: Path to the JSON file.
        :return: Dictionary containing the JSON data.
        """
        try:
            with open(path, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            Logger.error(f"File '{path}' not found.")
            return {}
        except json.JSONDecodeError as e:
            Logger.error(f"An error occurred while parsing JSON: {e}")
            return {}

    @staticmethod
    def _process_init_line(line, current_module, data_dict):
        """
        Helper method to process a single line from the init file.
        :param line: The line to process.
        :param current_module: The current module section.
        :param data_dict: The dictionary being built.
        :return: Updated current_module.
        """
        line = line.strip()
        if not line or line.startswith("#"):
            return current_module
        if line.startswith("[") and line.endswith("]"):
            current_module = line[1:-1].strip()
            data_dict[current_module] = {}
        elif "=" in line and current_module:
            key, value = line.split("=", 1)
            data_dict[current_module][key.strip()] = value.strip()
        return current_module

    @staticmethod
    def read_init_file(file_path, file_name, file_mode="r") -> dict:
        """Read the content of an initialization file.
        :param file_path: Path to the directory containing the file.
        :param file_name: Name of the initialization file.
        :param file_mode: File mode (default is 'r').
        :return: Dictionary containing the initialization data.
        """
        try:
            full_path = os.path.join(file_path, file_name)
            with open(full_path, mode=file_mode) as file:
                data_dict = {}
                current_module = None
                for line in file:
                    current_module = FileHelper._process_init_line(line, current_module, data_dict)
            return data_dict
        except FileNotFoundError:
            Logger.error(f"File '{file_name}' not found in the specified path: '{file_path}'.")
            return {}
        except PermissionError:
            Logger.error(f"Permission denied to read the file '{file_name}' in the specified path: '{file_path}'.")
            return {}
        except Exception as e:
            Logger.error(f"An error occurred while reading the file: {e}")
            return {}

    @staticmethod
    def load_env_yaml(path, file_prefix, env):
        """
        Read environment-specific resources from a YAML file.

        :param path: Path to the directory containing the YAML file.
        :param file_prefix: Prefix of the YAML file name.
        :param env: Environment name.
        :return: Dictionary containing the loaded data.
        """
        file_name = f"{file_prefix}.{env}.yaml"
        full_path = os.path.join(path, file_name)
        try:
            with open(full_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            Logger.error(f"File '{full_path}' not found.")
            return None
        except yaml.YAMLError as e:
            Logger.error(f"An error occurred while parsing YAML: {e}")
            return None

    @staticmethod
    def read_testcase_json(file_path):
        """Read the testcase.json file and return the testcase object.

        :param file_path: Path to the testcase.json file.
        :return: Dictionary representing the testcase.
        """

        try:
            with open(file_path, "r") as file:
                item = json.load(file)["tests"]
            if len(item) > 0:
                item = item[0]
            node_id = item["nodeid"]
            outcome = item["outcome"]
            groupName = node_id.split("/")[1]
            testcase = {}
            testcase["groupName"] = groupName
            testcase["className"] = node_id.split("/")[2].split("::")[0]
            testcase["caseName"] = node_id.split("/")[-1].split("::")[-1]
            if outcome.upper() == "FAILED":
                flag = 0
                error_message = str(item["call"]["crash"])
            else:
                flag = 1
                error_message = None
            testcase["flag"] = flag
            testcase["errorMessage"] = error_message
            testcase["duration"] = float(item["call"]["duration"])
            return testcase
        except FileNotFoundError:
            Logger.error(f"File '{file_path}' not found.")
            return None
        except json.JSONDecodeError as e:
            Logger.error(f"An error occurred while parsing JSON: {e}")
            return None
        except KeyError as e:
            Logger.error(f"Key not found in JSON: {e}")
            return None
        except Exception as e:
            Logger.error(f"An error occurred: {e}")
            return None

    @staticmethod
    def read_junit_xml_report(path):
        """
        Read the junit.xml file and return the result_dict.

        :param path: Path to the junit.xml file.
        :return: Dictionary containing test result information.
        """
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(path)
            root = tree.getroot()
            test_cases = int(root.attrib.get('tests', 0))
            failures = int(root.attrib.get('failures', 0))
            errors = int(root.attrib.get('errors', 0))
            skipped = int(root.attrib.get('skipped', 0))
            result_dict = {
                "Cases": test_cases,
                "Failures": failures,
                "Errors": errors,
                "Skipped": skipped
            }
            return result_dict
        except FileNotFoundError:
            Logger.error(f"File '{path}' not found.")
            return None
        except ET.ParseError as e:
            Logger.error(f"An error occurred while parsing XML: {e}")
            return None
        except KeyError as e:
            Logger.error(f"Key not found in XML: {e}")
            return None
        except Exception as e:
            Logger.error(f"An error occurred: {e}")
            return None

    @staticmethod
    def files_under_folder_with_suffix_xlsx(path_string):
        """
        Get a list of Excel files with ".xlsx" suffix in the specified folder.

        :param path_string: Path to the folder.
        :return: List of filenames with ".xlsx" suffix.
        """
        return FileHelper.files_under_folder_with_suffix(".xlsx", path_string)

    @staticmethod
    def files_under_folder_with_suffix_csv(path_string):
        """
        Get a list of CSV files with ".csv" suffix in the specified folder.

        :param path_string: Path to the folder.
        :return: List of filenames with ".csv" suffix.
        """
        return FileHelper.files_under_folder_with_suffix(".csv", path_string)

    @staticmethod
    def files_under_folder_with_suffix(file_suffix, path_string):
        """
        Get a list of files with the specified suffix in the specified folder.

        :param file_suffix: Suffix of the files to search for (e.g., ".txt").
        :param path_string: Path to the folder.
        :return: List of filenames with the specified suffix.
        """
        try:
            default_directory = os.path.join(os.getcwd(), path_string)
            files = os.listdir(default_directory)
            matching_files = [file for file in files if file.endswith(file_suffix)]
            return matching_files
        except FileNotFoundError:
            Logger.error(f"Directory '{default_directory}' not found.")
            return []
        except PermissionError:
            Logger.error(f"Permission denied to read files in '{default_directory}'.")
            return []
        except Exception as e:
            Logger.error(f"An error occurred: {e}")
            return []
