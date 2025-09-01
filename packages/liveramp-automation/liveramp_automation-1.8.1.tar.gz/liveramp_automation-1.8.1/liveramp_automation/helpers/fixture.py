import os
import sys
from pathlib import Path

import pytest
from selenium import webdriver
from liveramp_automation.helpers.file import FileHelper
from liveramp_automation.utils.allure import allure_page_screenshot, allure_drive_screenshot, allure_attach_video
from liveramp_automation.utils.log import Logger
from liveramp_automation.utils.time import fixed_wait
from typing import Generator
from dotenv import load_dotenv
from playwright.sync_api import BrowserContext, sync_playwright


##############################
# Resource Prefix Management #
#############################

@pytest.fixture(scope="session")
def res():
    """Get the configuration for the test environment.

    :return: Configuration dictionary for the test environment.
    """
    load_dotenv()
    Logger.debug("It is going to import the envChoice.")
    if not os.environ.get('ENVCHOICE'):
        os.environ['ENVCHOICE'] = "prod"
    run_on_env = os.environ['ENVCHOICE']
    Logger.debug("The testing environment is {} ".format(run_on_env))
    init_dict = FileHelper.read_init_file(os.getcwd(), 'pytest.ini')
    Logger.debug(init_dict)
    resource_path = None
    resource_prefix = None
    try:
        if init_dict and init_dict['data']:
            resource_data = init_dict['data']
            if resource_data['resource_path']:
                resource_path = resource_data['resource_path']
            else:
                resource_path = 'resources'
                Logger.warning("Use the resources as the default resource_path.")
            if resource_data['resource_prefix']:
                resource_prefix = resource_data['resource_prefix']
            else:
                resource_prefix = 'res'
                Logger.warning("Use the res as the default resource_prefix.")
    except TypeError:
        resource_path = 'resources'
        resource_prefix = 'res'
        Logger.warning("Use the resource and res as the default resource_path and resource_prefix.")
    return FileHelper.load_env_yaml(resource_path, resource_prefix, run_on_env)


###############################################################################################################
# API Prefix Management # We consider it's better to add the fixture methods to your own conftest.py
##############################################################################################################


################################################
# UI Automation Testing Prefix Management #
###############################################
@pytest.fixture(scope="session")
def driver():
    """Pytest fixture that provides a Selenium WebDriver instance for testing.
        Yields:
            WebDriver: A Selenium WebDriver instance for testing purposes.
    """
    load_dotenv()
    if not os.environ.get('runEnv'):
        os.environ['runEnv'] = "remote"
    run_on_env = os.environ['runEnv']
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    config_data = FileHelper.read_init_file(os.getcwd(), "pytest.ini", "r")
    Logger.debug(config_data)
    download_dir = config_data.get('download', 'reports/download')
    default_directory = os.path.join(os.getcwd(), download_dir)
    prefs = {"download.default_directory": default_directory}
    chrome_options.add_experimental_option("prefs", prefs)
    Logger.debug("The run Env is {}".format(run_on_env))
    Logger.debug("Run WEBDriver on lang=en ")
    chrome_options.add_argument('--lang=en')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('window-size=1920x1480')

    if run_on_env == "remote":
        chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    Logger.debug("We are going to open a blank page.")
    driver.get("about:blank")
    driver.implicitly_wait(30)
    Logger.debug("Started a ChromeDriver.")
    yield driver
    driver.close()
    Logger.debug("Closed the ChromeDriver.Goodbye!")


@pytest.fixture(scope=os.getenv('PAGE_SCOPE', 'session'),
                params=os.getenv('BROWSER_TYPES', "chrome").split(","))
def page(request) -> Generator[BrowserContext, None, None]:
    """ Pytest fixture that provides a Playwright BrowserContext for testing.
       Args:
           request: request params .
       Yields:
           BrowserContext: A Playwright BrowserContext for testing purposes.
    """
    os.environ.setdefault('runEnv', "remote")
    config_data = FileHelper.read_init_file(os.getcwd(), "pytest.ini", "r")
    Logger.debug(config_data)

    playwright = sync_playwright().start()
    download_dir = config_data.get('download', 'reports/download')
    reports_dir = config_data.get('download', 'reports')
    default_directory = os.path.join(os.getcwd(), download_dir)
    recording_directory = os.path.join(os.getcwd(), reports_dir, request.param)
    headless = os.environ['runEnv'] == "remote"
    recording_broken_flag = os.getenv('PAGE_SCOPE', 'session') == "session" and len(
        os.getenv('BROWSER_TYPES', "chrome").split(",")) > 1

    # Determine if the browser type should use a specific channel or not.
    launch_kwargs = {
        "downloads_path": default_directory,
        "record_video_dir": recording_directory,
        "record_video_size": {"width": 1920, "height": 1080},
        "viewport": {"width": 1920, "height": 1080}
    }

    if request.param == "firefox":
        browser_context = getattr(playwright, request.param).launch_persistent_context("",
                                                                                       headless=headless,
                                                                                       **launch_kwargs)
    else:
        launch_kwargs["args"] = ['--lang=en']
        if request.param in ["webkit"]:
            browser_context = getattr(playwright, request.param).launch_persistent_context("",
                                                                                           headless=headless,
                                                                                           **launch_kwargs)
        else:
            launch_kwargs["channel"] = request.param
            browser_context = playwright.chromium.launch_persistent_context("",
                                                                            headless=headless,
                                                                            **launch_kwargs)

    # Start tracing before creating / navigating a page.
    browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)

    # Get browser version and name from the browser object
    # For persistent context, we need to access the browser through the context
    browser = browser_context.browser
    if browser:
        browser_version = browser.version
        browser_name = browser.browser_type.name
    else:
        # Fallback values if browser is not accessible
        browser_version = "Unknown"
        browser_name = request.param

    allure_dir = Path("reports/allure_results")
    allure_dir.mkdir(exist_ok=True)
    env_file = allure_dir / "environment.properties"

    with env_file.open("w", encoding="utf-8") as f:
        f.write(f"Browser.Name={browser_name}\n")
        f.write(f"OS={os.uname().sysname} {os.uname().release}\n")
        # Add common testing environment variables
        test_env_vars = [
            'CONNECT_URL', 'ENVCHOICE', 'runEnv', 'PYTEST_ADDOPTS', 'LANG', 'LC_ALL', 'TZ',
            'BROWSER_TYPES', 'PAGE_SCOPE', 'TEST_ENV'
        ]

        for env_var in test_env_vars:
            value = os.getenv(env_var)
            if value:
                f.write(f"{env_var}={value}\n")

        f.write(f"Python.Version={sys.version}\n")
        f.write(f"Working.Directory={os.getcwd()}\n")
        f.write(f"User={os.getenv('USER', 'Unknown')}\n")
        f.write(f"Home={os.getenv('HOME', 'Unknown')}\n")

    page = browser_context.pages[0]
    page.set_default_timeout(60000)
    yield page
    page.close()
    browser_context.tracing.stop(path=os.path.join(os.getcwd(), recording_directory, request.param + "_trace.zip"))
    browser_context.close()
    playwright.stop()
    # Handling of recorded video files.
    fixed_wait()
    files = os.listdir(recording_directory)
    webm_files = [file for file in files if file.endswith(".webm")]
    if webm_files and recording_broken_flag is not True:
        for index, webm_file in enumerate(webm_files):
            recording_path = os.path.join(os.getcwd(), recording_directory, webm_file)
            recording_name = "Recording_video_{}_{}".format(request.param, index)
            allure_attach_video(recording_name, recording_path)
            os.remove(recording_path)


@pytest.hookimpl(hookwrapper=True)
def pytest_bdd_step_error(feature, scenario, step, step_func_args, exception):
    """
    This hook is called when there is an error during the execution of a step.
    It takes a screenshot of the current page if the step fails.
    """
    try:
        outcome = yield
        Logger.debug(f"Step error in scenario '{outcome.excinfo}'.")
        Logger.error(f"Step error in scenario '{scenario.name}' at step '{step.keyword} {step.name}': {exception}")
        screenshot_name = f"screenshot_{feature.name}_{scenario.name}_{step.keyword}_{step.name}"
        if 'page' in step_func_args.keys():
            allure_page_screenshot(step_func_args['page'], screenshot_name)
        elif 'driver' in step_func_args.keys():
            allure_drive_screenshot(step_func_args['driver'], screenshot_name)
        else:
            Logger.debug("No need to take screenshot")
    except exception:
        pass


@pytest.hookimpl(hookwrapper=True)
def pytest_bdd_before_scenario(request, feature, scenario):
    outcome = yield
    os.environ["SCENARIO_NAME"] = scenario.name


@pytest.fixture(scope="session")
def request_config():
    return {
        "request_url": None,
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "Method": "Get",
        "request_body": None,
        "response_body": None
    }
