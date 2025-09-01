import json

import allure


def allure_page_screenshot(page, attach_name):
    """
    Capture and attach a screenshot to Allure report using Playwright.
    :param page: Playwright page object.
    :param attach_name: Descriptive name for the screenshot attachment.
    :return: None
    """
    attachment_title = f"Screenshot: {attach_name}"
    allure.attach(body=page.screenshot(), name=attachment_title, attachment_type=allure.attachment_type.PNG)


def allure_drive_screenshot(driver, attach_name):
    """
    Capture and attach a screenshot to Allure report using Selenium WebDriver.
    :param driver: Selenium WebDriver instance.
    :param attach_name: Descriptive name for the screenshot attachment.
    :return: None
    """
    attachment_title = f"Screenshot: {attach_name}"
    allure.attach(body=driver.get_screenshot_as_png(), name=attachment_title,
                  attachment_type=allure.attachment_type.PNG)


def allure_attach_video(attach_name, path):
    """
    Attach a video file to an Allure report.
    :param path: Path to the video file.
    :param attach_name: Descriptive name for the video attachment.
    :return: None
    """
    allure.attach.file(path, name=attach_name, attachment_type=allure.attachment_type.WEBM)


def allure_attach_text(title, content):
    """
    Attach text content to an Allure report.
    :param content: The text content to be attached.
    :param title: Description or title for the attached text.
    :return: None
    """
    allure.attach(body=content, name=title, attachment_type=allure.attachment_type.TEXT)


def allure_attach_json(title, json_content):
    """
    Attach JSON content to an Allure report.
    :param json_content: The JSON content to be attached.
    :param title: Title or description for the attached JSON.
    :return: None
    """
    allure.attach(body=json.dumps(json_content), name=title, attachment_type=allure.attachment_type.JSON)
