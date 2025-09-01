from danoan.journal_manager.core import api, exceptions
from danoan.journal_manager.cli import utils

import argparse
from typing import List, Optional

# -------------------- API --------------------


def show(template_name: str, attribute_names: List[str]):
    """
    Get attribute data from a registered template.

    Args:
        template_name: The template name.
        attribute_names (optional): List of attribute names which values one wants to show.
    Returns:
        The attribute value if a single attribute was requested. For two or more
        attributes, several strings are returned. One for line requested attribute.
        The string has the format "attribute_name: attribute_value".
    Raises:
        InvalidName if the template name is invalid.
        InvalidAttribute if an attribute name is invalid.
    """
    template_list_file = api.get_template_list_file()

    template = api.find_template_by_name(template_list_file, template_name)
    if template:
        if len(attribute_names) == 0:
            attribute_names = list(template.__dict__.keys())

        if len(attribute_names) == 1:
            attribute_name = attribute_names[0]
            if attribute_name not in template.__dict__.keys():
                raise exceptions.InvalidAttribute(attribute_name)
            yield template.__dict__[attribute_name]
        else:
            for name in attribute_names:
                yield f"{name}:{template.__dict__[name]}"
    else:
        raise exceptions.InvalidName(template_name)


# -------------------- CLI --------------------


def __show_template__(
    template_name: str, attribute_names: Optional[List[str]] = None, **kwargs
):
    if attribute_names is None:
        attribute_names = []

    if len(attribute_names) > 0 and attribute_names[0] is None:
        attribute_names.remove(None)

    utils.ensure_configuration_file_exists()
    try:
        for value in show(template_name, attribute_names):
            print(value)
    except exceptions.InvalidName:
        print(f"The template name: {template_name} does not exist.")
    except exceptions.InvalidAttribute as ex:
        print(f"The attribute name: {ex.msg} does not exist.")


def get_parser(subparser_action=None):
    command_name = "show"
    command_description = show.__doc__ if show.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            formatter_class=argparse.RawTextHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument("template_name", help="Template name")
    parser.add_argument(
        "attribute_names",
        action="append",
        nargs="?",
        help="Attribute name which value one wants to show.",
    )
    parser.set_defaults(func=__show_template__)

    return parser
