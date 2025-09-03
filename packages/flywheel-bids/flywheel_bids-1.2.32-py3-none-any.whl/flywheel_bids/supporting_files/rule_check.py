"""
Module to demystify building template rules and troubleshoot curation issues.
Classes:
    ListHandler: Custom logging handler to store log messages in a list.
Functions:
    display_rules(template_name="reproin"): Display the rules for a given template.
    display_silent_logger_messages(): Retrieve and display log messages for failed rules.
    display_project_tree(project_node): Log the structure of the project tree.
    find_name(context): Retrieve the name of the container from the context.
    find_context(all_nodes, selection_criteria: List[int, str]): Select the appropriate node from the project tree based on selection criteria.
    verbose_rule_matches(template, rule_num, context): Check and display if a context matches a specific rule in the template.
    main(fw, project_name: List[str, Path], selection_criteria, rule_number, template_name="reproin"): Main function to produce log to debug specific rule for a container.
    parse_arguments(): Parse command-line arguments.

Example usage: `python -m flywheel_bids/supporting_files/rule_check --project_name='brianne/ASL' --selection_criteria=17 --rule_number=12`
"""

import argparse
import logging
import os
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Union

import flywheel

from flywheel_bids.supporting_files import templates
from flywheel_bids.supporting_files.project_tree import (
    TreeNode,
    get_project_node,
    set_tree,
)


# Define the ListHandler class
class ListHandler(logging.Handler):
    """
    Custom logging handler to store log messages in a list for later analysis.

    This handler is specifically designed to work with the silent_logger in the BIDS
    client's rule checking system. Instead of writing logs to a file or console, it
    keeps them in memory, making them accessible programmatically for debugging purposes.

    This handler is essential for the check_and_create_rules notebook and rule_check module
    to collect and display information about why specific BIDS rules failed to match,
    helping developers troubleshoot and refine their rules.
    """

    def __init__(self):
        super().__init__()
        self.log_messages = []  # In-memory storage for log messages

    def emit(self, record: logging.LogRecord) -> None:
        """Store the formatted log message in the internal list."""
        self.log_messages.append(self.format(record))

    def get_log_messages(self) -> List[str]:
        """Retrieve the stored log messages for analysis or display."""
        return self.log_messages

    def clear_log_messages(self) -> None:
        """Clear the stored log messages."""
        self.log_messages.clear()


# Create and configure the silent_logger (see also bidsify_flywheel for similar explanation)
# This logger captures debug information about rule matching failures without displaying them directly.
# It's designed to store messages in memory via the ListHandler for later access and analysis.
# This is crucial for debugging why certain BIDS rules don't match expected files or containers.
silent_logger = logging.getLogger("silent_logger")
silent_logger.setLevel(
    logging.DEBUG
)  # Capture all levels of messages for thorough debugging
silent_logger.propagate = False  # Prevent messages from being propagated to the root logger, keeping debug info isolated
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

list_handler = ListHandler()
formatter = logging.Formatter("%(levelname)s: %(message)s")
list_handler.setFormatter(formatter)
silent_logger.addHandler(list_handler)


def display_project_tree(project_node: TreeNode) -> None:
    """Log the structure of the project tree.

    Note that 'context' is used here as it is throughout bids-client. It is not a GearContext object nor a simple container found by a lookup or search.

    Args:
        project_node (TreeNode): The root node of the project tree.
    """
    for c, context in enumerate(project_node.context_iter()):
        if context["container_type"] in ["project", "session", "acquisition"]:
            logger.info(
                f"{c} {context['container_type']}: {context.get(context['container_type']).get('label')}"
            )
        else:
            logger.info(
                f"{c}   {context['container_type']}: {context.get(context['container_type']).get('name')}"
            )


def display_rules(template_name: str = "reproin") -> templates.Template:
    """Display the rules for a given template.

    Args:
        template_name (str): The name of the template JSON to load. (reproin, bids-v1, or default)

    Returns:
        Template: The loaded template object.

    This function loads a template by its name and logst the rules contained within it.
    Each rule's ID and conditions are printed in a formatted manner.
    """
    TEMPLATE = templates.load_template(template_name=template_name)
    logger.debug("Here are the rules:")
    for r, rule in enumerate(TEMPLATE.rules):
        logger.debug(f"{r}: {rule.id}")
        pprint(rule.conditions, indent=1)
    return TEMPLATE


def display_silent_logger_messages() -> None:
    """Retrieve log messages for failed rules."""
    log_messages = list_handler.get_log_messages()
    for message in log_messages:
        logger.info(message)
    list_handler.clear_log_messages()


def find_name(context: Dict) -> str:
    """Retrieve the name of the container from the context.

    The context object has a lot of information, more than a simple container object returns from a lookup or search.

    Args:
        context (dict): The context dictionary containing container information.

    Returns:
        str: The name or label of the container.
    """
    if context["container_type"] in ["project", "session", "acquisition"]:
        return context.get(context["container_type"]).get("label")
    else:
        return context.get(context["container_type"]).get("name")


def find_context(all_nodes: TreeNode, selection_criteria: Union[int, str]) -> Dict:
    """Select the appropriate node from the project tree based on selection criteria.

    When running `display_project_tree` in a notebook, one can see both the index of the node and the human-readable name. This function allows for selection of the node based on either the index or the name.

    Args:
        all_nodes (TreeNode): The root node of the project tree.
        selection_criteria (Union[int, str]): The criteria to select the node (index or name).

    Returns:
        dict: The selected context dictionary.
    """
    if isinstance(selection_criteria, int):
        for c, context in enumerate(all_nodes.context_iter()):
            if c == selection_criteria:
                return context
    else:
        for context in all_nodes.context_iter():
            name = find_name(context)
            if (
                context["container_type"] in ["project", "session", "acquisition"]
                and selection_criteria in name
            ):
                return context
            elif context["container_type"] == "file" and selection_criteria in name:
                return context
            elif not context.get("container_type"):
                logger.error("Something went very wrong. Check project_node")
    return None


def verbose_rule_matches(
    template: templates.Template, rule_num: int, context: Dict
) -> None:
    """Check and display if a context matches a specific rule in the template.

    Args:
        template (Template): The template containing the rules.
        rule_num (int): The index of the rule to check.
        context (dict): The context dictionary to test against the rule.
    """
    rule = template.rules[rule_num]
    name = find_name(context)
    logger.debug(f"\n\nChecking {rule.id} rule.")
    pprint(rule.conditions)
    if rule.test(context):
        logger.info(f"Verdict: {name} matches the rule")
    else:
        logger.debug(name)
        for k, v in rule.conditions.items():
            templates.resolve_where_clause({k: v}, context)
            display_silent_logger_messages()


def main(
    fw: flywheel.Client,
    project_name: Union[str, Path],
    selection_criteria: str,
    rule_number: int,
    template_name: str = "reproin",
) -> None:
    """Produce log to debug specific rule for a container.

    Args:
        fw (Flywheel Client): The Flywheel Client.
        project_name (Union[str, Path]): The name or path of the project.
        selection_criteria (Union[int, str]): The criteria to select the node (index or name).
        rule_number (int): The index of the rule to check.
        template_name (str): The name of the template to use.
    """
    project = fw.lookup(project_name)
    project_node = get_project_node(fw, project.id)

    # The subjects, sessions, and acquisitions still need to be added.
    for subj in project.subjects.iter():
        set_tree(fw, project_node, subj)
    template = display_rules(template_name)
    context = find_context(project_node, selection_criteria)
    verbose_rule_matches(template, rule_number, context)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--api_key", type=str, default=None, help="Flywheel API key")
    parser.add_argument(
        "project_name", type=str, help="Name of the project, as `fw.lookup` would use."
    )
    parser.add_argument(
        "selection_criteria",
        type=str,
        help="Selection criteria (index or name)",
    )
    parser.add_argument("rule_number", type=int, help="Rule number")
    parser.add_argument(
        "--template_name",
        type=str,
        default="reproin",
        help="Name of the template to use",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    if not args.api_key:
        fw = flywheel.Client(os.environ.get("FW_latest"))

    # Convert selection_criteria to int if it is a digit
    try:
        selection_criteria = int(args.selection_criteria)
    except ValueError:
        selection_criteria = args.selection_criteria

    main(
        fw,
        args.project_name,
        args.selection_criteria,
        args.rule_number,
        template_name=args.template_name,
    )
