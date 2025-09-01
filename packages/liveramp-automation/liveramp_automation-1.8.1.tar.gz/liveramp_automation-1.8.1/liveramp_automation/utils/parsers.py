from pytest_bdd.parsers import StepParser
import parse as base_parse

EXTRA_TYPES = {}  # Custom extra types for parsing, if needed


class ParseUtils(StepParser):
    """
    Step parser utility for parsing BDD scenario steps.

    This class follows the Factory Method pattern and provides methods to parse and match BDD scenario step names.

    Usage:
    parse_util = ParseUtils("step_pattern")
    arguments = parse_util.parse_arguments("step_name")
    is_matching = parse_util.is_matching("step_name")

    :param name: The step pattern for parsing.
    :type name: str
    :param args: Additional arguments for parse expression compilation.
    :type args: tuple
    """

    def __init__(self, name, *args):
        """
        Initialize the ParseUtils with a step pattern and compile the parse expression.

        :param name: The step pattern for parsing.
        :param args: Additional arguments for parse expression compilation.
        """
        super(ParseUtils, self).__init__(name)
        self.parser = base_parse.compile(self.name, *args, extra_types=EXTRA_TYPES)

    def parse_arguments(self, name: str):
        """
        Parse the step name and return the named arguments.

        :param name: The step name to parse.
        :return: Named arguments extracted from the step name.
        """
        return self.parser.parse(name).named

    def is_matching(self, name):
        """
        Check if the given step name matches the step pattern.

        :param name: The step name to match.
        :return: True if the step name matches the pattern, False otherwise.
        """
        try:
            return bool(self.parser.parse(name))
        except ValueError:
            return False
