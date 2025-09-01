from pytest_bdd import given, when, then
from liveramp_automation.utils.parsers import ParseUtils
import re
from liveramp_automation.utils.log import Logger
from liveramp_automation.utils.request import *
from liveramp_automation.utils.time import MACROS


@then(ParseUtils('The response status code should be {code:d}'))
@when(ParseUtils('The response status code should be {code:d}'))
def verify_endpoint_response_code(code, response_body):
    assert response_body.status_code == code, (
        "Expected code: {}, actual code: {}".format(code, response_body.status_code))


@then(ParseUtils('The response body should contain the {fields}'))
@when(ParseUtils('The response body should contain the {fields}'))
def verify_endpoint_response_exist(fields, response_body):
    response_keys = response_body.json().keys()
    assert all(key in response_keys for key in eval(fields)), \
        "Not all fields: {} in response: {}".format(fields, response_keys)



@then(ParseUtils('response key {fields}'))
def verify_request_config_response_exist_fields(fields, request_config):
    response_keys = request_config["response_body"].json().keys()
    assert fields in response_keys, f"The string '{fields}' was not found in the list "


@then(ParseUtils('response string {substring}'))
def verify_request_config_response_exist_substring(substring, request_config):
    assert substring in request_config["response_body"].text, "String: {} not in the response: {}".format(
        substring, request_config["response_body"].text)


def replace_macros(data, macros):
    """
    Replace macros in the given data structure.
    """
    if isinstance(data, dict):
        return {key: replace_macros(value, macros) for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_macros(item, macros) for item in data]
    elif isinstance(data, str):
        return data.format(**macros)
    else:
        return data


def get_dict_data(res, body_key):
    """
    Retrieve and process the request body from the configuration.
    """
    if body_key in res:
        return replace_macros(res[body_key], MACROS)
    else:
        raise KeyError(f"'{body_key}' not found in the config")


def generate_url_from_dict(data, base_url):
    """
    Generate URL string from dictionary data.
    """
    query_string = '&'.join([f"{key}={value}" for key, value in data.items()])
    return f"{base_url}?{query_string}"


# def check_values(data, substring):
#     if isinstance(data, dict):
#         return any(check_values(value, substring) for value in data.values())
#     elif isinstance(data, list):
#         return any(check_values(item, substring) for item in data)
#     elif isinstance(data, str):
#         return substring in data
#     return False


@given(ParseUtils('url {api_url}'), target_fixture='request_config')
def set_url(request_config, api_url):
    request_config["request_url"] = api_url
    return request_config


@given(ParseUtils('domain {domain} path {path}'), target_fixture='request_config')
def set_env_domain_path(res, request_config, domain, path):
    Logger.debug(res)
    domain_name = domain.format(**res)
    request_config["request_url"] = res[domain_name] + path
    Logger.debug(request_config)
    return request_config


@given(ParseUtils("headers\n{headers_str}"))
def headers(config, headers_str, token, request_config):
    # Format the string if the pattern is found
    if re.search(r"\{token\}", headers_str):
        headers_str = headers_str.format(token=token)
    # pass config to headers
    headers_str = headers_str.format(**config)

    # Strip surrounding triple quotes and split the string into lines
    lines = headers_str.strip('"""\n').split('\n')

    # Add headers to the request configuration
    request_config["headers"] = {key.strip(): value.strip() for line in lines if ':' in line for key, value in
                                 [line.split(':', 1)]}
    return request_config


@given(ParseUtils('body {body_name}'))
def set_request_body_yaml(config, request_config, body_name):
    request_config["body"] = get_dict_data(config, body_name)
    return request_config


@given(ParseUtils('body_context\n"{body_name}"'))
def set_request_body_json(config, request_config, body_name):
    print(body_name)
    request_config["body"] = body_name
    return request_config


@given(ParseUtils('parameters {url_params}'))
def set_request_url_parameter_list(config, request_config, url_params):
    url_params = get_dict_data(config, url_params)
    request_config["api_url"] = generate_url_from_dict(url_params, request_config["api_url"])
    return request_config


@given(ParseUtils('parameter {parameter}'))
def set_request_url_parameter(request_config, parameter):
    request_config["api_url"] = request_config["api_url"] + '\\' + parameter
    return request_config


@when(ParseUtils('method {api_method}'))
def define_method(request_config, api_method):
    Logger.debug(f"Method: {api_method}")
    # if api_method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]:
    api_method = api_method.upper()
    # request_config["method"] = api_method if api_method in api_methods else "GET"
    request_config["response_body"] = request_any(api_method,
                                                  request_config["api_url"],
                                                  headers=request_config["headers"],
                                                  json=request_config["body"])
    return request_config
