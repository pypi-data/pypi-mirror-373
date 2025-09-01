import pytest
from unittest.mock import patch
from liveramp_automation.utils.parsers import ParseUtils
from liveramp_automation.utils.parsers import EXTRA_TYPES
import parse as base_parse


@pytest.fixture
def setup_parser_simple():
    return ParseUtils("I want to test {str} cases")


def mocked_unit_test_throw_exception(*args, **kwargs):
    raise ValueError("Test")


def test_is_matching_simple(setup_parser_simple):
    assert setup_parser_simple.is_matching('I want to test all cases')
    assert setup_parser_simple.is_matching('I want to test "all" cases')
    assert setup_parser_simple.is_matching('I want to test {all} cases')
    assert setup_parser_simple.is_matching('I want to test the first and third cases')


def test_parse_arguments_simple_with_quotes(setup_parser_simple):
    args = setup_parser_simple.parse_arguments('I want to test "{some}" cases')
    assert args == {'str': '"{some}"'}


def test_parse_arguments_simple_without_quotes(setup_parser_simple):
    args = setup_parser_simple.parse_arguments('I want to test {some} cases')
    assert args == {'str': '{some}'}


@pytest.fixture
def setup_parser_with_curly_brace():
    return ParseUtils("I search {keywords} from the box")


def test_parse_arguments_with_curly_brace(setup_parser_with_curly_brace):
    args = setup_parser_with_curly_brace.parse_arguments('I search {username} from the box')
    assert args == {'keywords': '{username}'}


def test_is_matching_with_curly_brace(setup_parser_with_curly_brace):
    assert setup_parser_with_curly_brace.is_matching('I search {username} from the box')
    assert setup_parser_with_curly_brace.is_matching('I search {username} and password from the box')
    assert setup_parser_with_curly_brace.is_matching('I search {5} from the box')


@patch('builtins.bool', side_effect=mocked_unit_test_throw_exception)
def test_is_matching_with_curly_brace_exception(mock, setup_parser_with_curly_brace):
    assert setup_parser_with_curly_brace.is_matching('I search {username} from the box') is False
    assert setup_parser_with_curly_brace.is_matching('I search {username} and password from the box') is False
    assert setup_parser_with_curly_brace.is_matching('I search {5} from the box') is False


@pytest.fixture
def setup_parser_with_digital():
    return ParseUtils("I have {number:d} apples")


def test_parse_arguments(setup_parser_with_digital):
    args = setup_parser_with_digital.parse_arguments("I have 5 apples")
    assert args == {"number": 5}


def test_is_matching(setup_parser_with_digital):
    assert setup_parser_with_digital.is_matching("I have 5 apples")
    assert not setup_parser_with_digital.is_matching("I have five apples")
    assert not setup_parser_with_digital.is_matching("I have 5")


@pytest.fixture
def setup_parser_quotes():
    return ParseUtils('I typed "{keywords}" into the box')


def test_parse_arguments_with_quotes(setup_parser_quotes):
    args = setup_parser_quotes.parse_arguments('I typed "{username}" into the box')
    assert args == {'keywords': '{username}'}


def test_is_matching_with_quotes(setup_parser_quotes):
    assert setup_parser_quotes.is_matching('I typed "{username}" into the box')
    assert not setup_parser_quotes.is_matching('I typed "{username}" and password into the box')
    assert setup_parser_quotes.is_matching('I typed "{5}" into the box')


def test_init_valid_step_pattern():
    parse_util = ParseUtils("I have a {number:d} thing")
    assert parse_util.parser is not None


def test_is_matching_empty_string():
    parser = ParseUtils("I want to test {str} cases")
    assert not parser.is_matching("")


def test_init_with_custom_type():
    """
    Test that ParseUtils constructor correctly handles custom types in EXTRA_TYPES.
    """
    def parse_yes(text):
        return text == "yes"

    EXTRA_TYPES["Yes"] = parse_yes

    try:
        parser = ParseUtils("The answer is {answer:Yes}")
        assert parser is not None
    finally:
        # Clean up EXTRA_TYPES to avoid side effects on other tests
        del EXTRA_TYPES["Yes"]