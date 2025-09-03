import logging

from . import classifications, templates, utils
from .project_tree import TreeNode


class ListHandler(logging.Handler):
    """
    A custom logging handler that stores log messages in a list instead of outputting them.

    This handler is designed to work with the silent_logger to capture debug messages
    in memory rather than printing them to console or writing to a file. This allows
    for programmatic access to log messages for later analysis, especially helpful when
    debugging rule matching failures and for integration with notebooks like
    check_and_create_rules.ipynb.

    The stored messages can be retrieved with get_log_messages() and cleared with
    clear_log_messages(), making it ideal for debugging rule application where
    we need to understand why rules didn't match as expected.
    """

    def __init__(self):
        super().__init__()
        self.log_messages = []  # Initialize empty list to store log messages

    def emit(self, record):
        """Store the formatted log record in the internal list."""
        self.log_messages.append(self.format(record))

    def get_log_messages(self):
        """Return all stored log messages."""
        return self.log_messages

    def clear_log_messages(self):
        """Clear all stored log messages."""
        self.log_messages.clear()


# Create a silent logger to capture debug messages for when a container does not match any rules.
# Unlike standard loggers that output to console or files, the silent_logger captures messages
# in memory for later analysis or display through the ListHandler.
# This is particularly useful for debugging why certain rules are not matching as expected.
# As part of the logging/debugging process, messages are added to and deleted from the list (if the rule did not apply). The goal is to narrow down which rules did not match and why the rule did not match without having to step through.
silent_logger = logging.getLogger("silent_logger")
silent_logger.setLevel(logging.DEBUG)  # Capture all debug-level messages and above
silent_logger.propagate = False  # Prevent messages from being propagated to the root logger, keeping them isolated
# Custom handler that stores log messages in a list instead of outputting them
list_handler = (
    ListHandler()
)  # ListHandler stores messages in memory rather than writing to streams
formatter = logging.Formatter("%(levelname)s: %(message)s")
list_handler.setFormatter(formatter)
silent_logger.addHandler(list_handler)  # Connect the handler to the logger

logger = logging.getLogger("curate-bids")


def determine_enum(theproperty, key, classification):
    """obj:  {'Task': '', 'Run': '', 'Filename': '', 'Acq': '', 'Rec': '', 'Path': '', 'Folder': 'func', 'Echo': ''}
    property: {'default': 'bold', 'enum': ['bold', 'sbref', 'stim', 'physio'], 'type': 'string', 'label': 'Modality Label'}
    classification:  {u'Intent': u'Functional'}.

    """
    # Use the default value
    enum_value = theproperty.get("default", "")
    # If the default value is '', try and determine if from 'enum' list
    if not enum_value:
        # If key is modality, iterate over classifications dict
        if key in ["Modality", "Suffix"]:
            for data_type in classifications.classifications.keys():
                # Loops through the enum values in the propdef, allows for prioritization
                for enum_value in theproperty.get("enum", []):
                    enum_req = classifications.classifications[data_type].get(
                        enum_value
                    )
                    if enum_req and utils.dict_match(enum_req, classification):
                        return enum_value

    return enum_value


def add_properties(properties, obj, classification):
    """
     Create properties to add or update in the BIDS.info blob based on the BIDS curation rule that potentially matches the container.

    Args:
        properties (dict): A dictionary containing property definitions. Each key in the dictionary
                           represents a property name, and the value is another dictionary with
                           details about the property, such as its type, default value, and possible
                           enum values.
        obj (dict): The object to which properties will be added or updated.
        classification (str): A classification string used to determine enum values.
    Returns:
        dict: The updated object with properties added or modified based on the properties dictionary.
    """

    for key in properties:
        proptype = properties[key]["type"]
        if proptype == "string":
            # If 'enum' in properties, seek to determine the value from enum list
            if "enum" in properties[key]:
                obj[key] = determine_enum(properties[key], key, classification)
            elif "default" in properties[key]:
                obj[key] = properties[key]["default"]
            else:
                obj[key] = "default"
        elif proptype == "object":
            obj[key] = properties[key].get("default", {})
        elif "default" in properties[key]:
            obj[key] = properties[key]["default"]
    return obj


def get_container_label(context, container):
    """Get the label of the container based on its type."""
    if context["container_type"] == "file":
        return container.get("name", "")
    return container.get("label", "")


def get_template_name(container, namespace="BIDS"):
    """Get the template name matching the rule blob."""

    try:
        return container["info"][namespace].get("template")
    except KeyError:
        # Happens when the curation is reset? Recurated?
        try:
            return container["original_info"][namespace].get("template")
        except KeyError:
            # Happens at the project level and, perhaps, others
            # logger.error("Could not match an info key to any of: %s", container.keys())
            None


def info_bids_missing(container, namespace):
    """Check if rule matching is needed for the container.

    If "BIDS" is not available in the file/container .info, then the container has not been curated and needs rule matching.
    """

    if "info" not in container:
        return True
    if "BIDS" not in container["info"]:
        return True


def update_properties(properties, context, obj):
    """Updates object values for items in properties list containing an 'auto_update' attribute.

    This is done ony after the properties have been initialized using the context so values from the
    BIDS namespace can be used.

    The basic 'auto_update' is specified using a string type containing tags to be replaced from values
    in the 'context' object.  If 'auto_update' is a dictionary, '$process', '$value' and '$format' can be
    used to do more complicated things.

    If 'auto_update' is an 'object' type, the properties therein are processed recursively.

    :param properties: (dict) Properties of the template to be updated.
    :param context: (dict) the current container or file where property values can be found.
    :param obj: (dict) the result being updated.
    :return: obj
    """
    for key in properties:
        proptype = properties[key]["type"]
        if proptype == "string":
            if "auto_update" in properties[key]:
                auto_update = properties[key]["auto_update"]
                if isinstance(auto_update, dict):
                    if auto_update.get("$process"):
                        value = utils.process_string_template(
                            auto_update["$value"], context
                        )
                    else:
                        value = utils.dict_lookup(context, auto_update["$value"])
                    obj[key] = utils.format_value(auto_update["$format"], value)
                else:
                    obj[key] = utils.process_string_template(auto_update, context)

                logger.debug(f"Setting <{key}> to <{obj[key]}>")
        elif proptype == "array":
            pass  # so far, no need to auto_update any arrays
        elif proptype == "object":
            obj[key] = update_properties(properties[key]["properties"], context, {})
        else:
            logger.error("Unsupported property type <{proptype}>")

    return obj


# process_matching_templates(context, template)
# Accepts a context object that represents a Flywheel container and related parent containers
# and looks for matching templates in namespace.
# Matching templates define rules for adding objects to the container's info object if they don't already exist
# Matching templates with 'auto_update' rules will update existing info object values each time it is run.


def process_matching_templates(
    context: TreeNode, template: templates.Template, upload=False
):
    """Upload or update container following BIDS rules from a template JSON.

    Identify whether the container already exists. If not, try to match
    (1) upload_rules, if they exist, (2) rules from the template. Reports
    back if the template is non-existent or rules are not available for the
    container.
    If the container exists, attempt to update info.{BIDS} section of metadata

    Args:
        context (TreeNode): Dictionary of the container with the original Flywheel info blob.
        template (templates.Template): Information from the selected or provided template JSON file.
        upload (bool): If True, include any "upload_rules" defined in the template. These rules will
          only used when using bids import Default is False.
    Return:
        dict: Flywheel container with info fields defined per the designated template and rules.
        context: TreeNode, template: templates.Template, upload=False
    """
    try:
        # Default values
        namespace = template.namespace
        templateDef = None
        # Track if any rule matches
        rule_matched = False

        container_type = context["container_type"]
        container = context[container_type]

        if container.get("info", {}).get(namespace) == "NA":
            logger.debug(f"info.{namespace} is NA")
            return container

        label = get_container_label(context, container)
        template_name = get_template_name(container, namespace)

        if info_bids_missing(container, namespace):
            # add objects based on template if they don't already exist
            silent_logger.debug(
                f"'info' not in container OR "
                f"{namespace} not in 'info' OR "
                f"'container template' not in info.{namespace}.  "
                f"Performing rule matching\n\n"
            )

            # Do initial rule matching
            rules = template.rules
            # If matching on upload, test against upload_rules as well
            # The upload_rule may be as simple as {'container_type': 'file', 'parent_container_type': 'acquisition'}
            if upload:
                logger.debug("Matching on upload, testing against upload_rules\n")
                rules = rules + template.upload_rules

            # TODO: Prioritize the rules with modality type that matches label
            for r, rule in enumerate(rules):
                if rule_matches(rule, context, label):
                    # rule.template is under rule.id in JSON and refers to the name to look for in the definitions section of the JSON that defines the way the container will be handled, if it matches the rule
                    templateDef = template.definitions.get(rule.template)
                    if templateDef is None:
                        raise Exception(
                            "Unknown container template: {0}".format(rule.template)
                        )
                    else:
                        # templateDef["properties"] is from the definitions portion of the JSON matching the "template" key in the rule. These properties guide how the BIDS.info object will be created/updated.
                        match_info = create_match_info_update(
                            rule,
                            context,
                            container,
                            templateDef["properties"],
                            namespace,
                        )
                        # Processing of the template JSON is explained in templates.apply_initializers
                        rule.initializeProperties(match_info, context)
                        if rule.id:
                            template.apply_custom_initialization(
                                rule.id, match_info, context
                            )
                        logger.debug(
                            "%s matched rule %i: '%s' from %s template",
                            label,
                            r,
                            rule.id,
                            template.json_name,
                        )
                    rule_matched = True
                    # Remove the custom handler
                    logger.removeHandler(list_handler)
                    break

            # If no rules are matched, report rule matching evaluation process
            if not rule_matched:
                debug_messages = []
                for handler in silent_logger.handlers:
                    if hasattr(handler, "get_log_messages"):
                        debug_messages.extend(handler.get_log_messages())
                for message in debug_messages:
                    logger.info(message)

        else:
            logger.info(
                "Using template definitions from a previous curation process for %s.",
                label,
            )
            templateDef = template.definitions.get(template_name)

        # Unify the process of updating properties for (1) containers that did not need matching because of previous curation or (2) just matched.
        if not info_bids_missing(container, namespace) or rule_matched:
            # Do auto_updates
            try:
                data = update_properties(templateDef["properties"], context, {})
                container["info"][namespace].update(data)
            except AttributeError:
                logger.warning(
                    "Template %s not found in template definitions in according to %s JSON.",
                    template_name,
                    template.json_name,
                )

    finally:
        # Remove the custom handler
        logger.removeHandler(list_handler)

    return container


def rule_matches(rule: templates.Rule, context: TreeNode, label: str):
    """:param rule: Template rule being examined
    :param context (TreeNode): dictionary of the container with the original, Flywheel info blob
    :param label (str): container name or label, depending on Flywheel hierarchy level
    :return: match_status (Boolean)
    """

    if rule.test(context):
        silent_logger.handlers[0].clear_log_messages()
        return True
    else:
        silent_logger.debug(
            "%s failed the %s rule.\nRule criteria:\n%s",
            label,
            rule.id,
            rule.conditions,
        )
        return False


def create_match_info_update(rule, context, container, template_properties, namespace):
    """
    Prepare a dictionary for metadata update related to BIDS curation per the specific rule.

    These fields follow the definitions in the top portion of the JSON file.
    The corresponding metadata become the BIDS.info blobs.

    Args:
        rule (object): The rule object containing the template and id attributes.
        context (dict): The context dictionary containing the container type.
        container (dict): The container dictionary where the metadata will be updated.
        template_properties (dict): The properties to be added to the template.
        namespace (str): The namespace under which the metadata will be stored.

    Returns:
        dict: The updated match information dictionary with the applied rule and properties.
    """

    if "info" not in container:
        container["info"] = {}

    match_info = container["info"].get(namespace, {})
    match_info["template"] = rule.template
    match_info["rule_id"] = rule.id
    container["info"][namespace] = add_properties(
        template_properties, match_info, container.get("classification")
    )
    if context["container_type"] in ["session", "acquisition", "file"]:
        match_info["ignore"] = False
    return match_info


def process_resolvers(context: TreeNode, template: templates.Template):
    """Perform second stage path resolution based on template rules.

    Args:
        session (TreeNode): The session node to search within
        context (dict): The context to perform path resolution on (dictionary of the container with the original, Flywheel info blob)
        template (Template): The template
    """
    namespace = template.namespace

    container_type = context["container_type"]
    container = context[container_type]

    if (
        ("info" not in container)
        or (namespace not in container["info"])
        or ("template" not in container["info"][namespace])
    ):
        return

    # Determine the applied template name
    template_name = container["info"][namespace]["template"]
    # Get a list of resolvers that apply to this template
    resolvers = template.resolver_map.get(template_name, [])

    # Apply each resolver
    for resolver in resolvers:
        resolver.resolve(context)
