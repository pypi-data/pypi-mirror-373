import collections
import logging
import os
import re
import subprocess
import sys
from builtins import input

import six

logger = logging.getLogger(__name__)

BIDS_VALIDATOR_PATHS = ["/usr/bin/bids-validator", "/usr/local/bin/bids-validator"]


def validate_bids(dirname):
    """Run bids-validator locally if it is installed, warn if not."""
    found_validator = False
    for val_path in BIDS_VALIDATOR_PATHS:
        if os.path.isfile(val_path):
            found_validator = True

            # first just get version
            cmd = [val_path, "--version"]
            proc = subprocess.Popen(
                cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate()
            returncode = proc.returncode
            logger.info("Validating BIDS directory, bids-validator version %s", stdout)

            # now do for real
            cmd = [val_path, dirname]
            proc = subprocess.Popen(
                cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate()
            returncode = proc.returncode

            if returncode == 0:
                logger.info("stderr: " + str(stderr))
                logger.info("stdout: " + str(stdout))
            else:
                logger.error("returncode: %d" % returncode)
                logger.error("stderr: " + str(stderr))
                logger.error("stdout: " + str(stdout))

    if not found_validator:
        logger.error(
            "Skipping validation, bids-validator could not be found " + "in %s",
            str(BIDS_VALIDATOR_PATHS),
        )
        logger.error(
            "Please install the command line bids-validator via npm "
            "(see https://www.npmjs.com/package/bids-validator)."
        )


def validate_project_label(fw, project_label, group_id=None):
    """ """
    # Find project id
    # exhaustive=True is needed because site-admin users won't
    # find projects they have not been explicitly added to

    #### KEEP THIS IN TO AVOID UNEXPECTED BEHAVIOR ####
    is_admin = False
    if hasattr(fw, "auth_info"):
        is_admin = fw.auth_info.is_admin
    else:
        auth_status = fw.get_auth_status()
        is_admin = auth_status.user_is_admin
    kwargs = {"exhaustive": True} if is_admin else {}
    if group_id:
        projects = fw.projects.find(f"group={group_id},label={project_label}", **kwargs)
    else:
        projects = fw.projects.find(f"label={project_label}", **kwargs)

    num_projects = len(projects)
    if num_projects > 1:
        raise ValueError(
            "Found %d projects with label %s.  Use the --group-id option to specify a group id"
            % (num_projects, project_label)
        )
    elif num_projects < 1:
        raise ValueError(f"Could not find project with label {project_label}")

    project = projects[0]
    return project.id


def get_project_id_from_subject_id(fw, subject_id):
    """ """
    # Find project id from subject
    subject = fw.get_subject(subject_id)
    if not subject:
        logger.error("Could not load subject %s." % subject_id)
        sys.exit(1)

    return subject["project"]


def get_project_id_from_session_id(fw, session_id):
    """ """
    # Find project id from session
    session = fw.get_session(session_id)
    if not session:
        logger.error("Could not load session %s." % session_id)
        sys.exit(1)

    return session["project"]


def get_extension(fname):
    """Get extension.

    If search returns a result, get value
    else, ext is None

    """
    ext = re.search(r"\.[a-zA-Z]*[\.]?[A-Za-z0-9]+$", fname)
    if ext:
        ext = ext.group()
    return ext


def dict_lookup(obj, value, default=None):
    """
    Recursively looks up a value in a nested dictionary or list using a dot-separated string.

    Args:
        obj (dict or list): The dictionary or list to search.
        value (str): The dot-separated string representing the path to the value.
        default: The value to return if the path does not exist. Defaults to None.

    Returns:
        The value found at the specified path, or the default value if the path does not exist.
    """
    # For now, we don't support escaping of dots
    parts = value.split(".")
    curr = obj
    for part in parts:
        if isinstance(curr, (dict, collections.abc.Mapping)) and part in curr:
            curr = curr[part]
        elif isinstance(curr, list) and int(part) < len(curr):
            curr = curr[int(part)]
        else:
            curr = default
            break
    return curr


def dict_set(obj, key, value):
    parts = key.split(".")
    curr = obj
    for part in parts[:-1]:
        if isinstance(curr, (dict, collections.abc.Mapping)) and part in curr:
            curr = curr[part]
        elif isinstance(curr, list) and int(part) < len(curr):
            curr = curr[int(part)]
        else:
            raise ValueError("Could not set value for key: " + key)
    curr[parts[-1]] = value


def dict_match(matcher, matchee):
    """Returns True if each key,val pair is present in the matchee."""
    for key, val in matcher.items():
        if not matchee.get(key):
            return False
        elif not isinstance(matchee.get(key), list):
            mval = [matchee.get(key)]
        else:
            mval = matchee.get(key)
        if isinstance(val, list):
            for item in val:
                if item not in mval:
                    return False
        elif val not in mval:
            return False

    return True


def normalize_strings(obj):
    if isinstance(obj, six.string_types):
        return str(obj)
    if isinstance(obj, collections.abc.Mapping):
        return dict(map(normalize_strings, obj.items()))
    if isinstance(obj, collections.abc.Iterable):
        return type(obj)(map(normalize_strings, obj))
    return obj


# process_string_template(template, context)
# finds values in the context object and substitutes them into the string template
# Use <path> for cases where you want the result converted to lowerCamelCase
# Use {path} for cases where you want a literal value substitution
# path uses dot notation to navigate the context for desired values
# path examples:  <session.label>  returns session.label withou _ and -
#                 {file.info.BIDS.Filename} returns the value of file.info.BIDS.Filename
#                 {file.info.BIDS.Modality} returns Modality without modification
# example template string:
#       'sub-<subject.code>_ses-<session.label>_acq-<acquisition.label>_{file.info.BIDS.Modality}.nii.gz'


def process_string_template(template, context):
    tokens = re.compile(r"[^\[][A-Za-z0-9\.><}{-]+|\[[/A-Za-z0-9><}{_\.-]+\]")
    values = re.compile(r"[{<][A-Za-z0-9\.-]+[>}]")

    for token in tokens.findall(template):
        if values.search(token):
            replace_tokens = values.findall(token)
            for replace_token in replace_tokens:
                # Remove the {} or <> surrounding the replace_token
                path = replace_token[1:-1]
                # Get keys, if replace token has a . in it
                keys = path.split(".")
                result = context
                for key in keys:
                    if key in result:
                        result = result[key]
                    else:
                        result = None
                        break
                # If value found replace it
                if result:
                    # If replace token is <>, need to check if in BIDS
                    if replace_token[0] == "<":
                        # Check if result is already in BIDS format...
                        #   if so, split and grab only the label
                        if re.match("(sub|ses)-[a-zA-Z0-9]+", result):
                            label, result = result.split("-")
                        # If not, take the entire result and remove underscores and dashes
                        else:
                            result = "".join(
                                x
                                for x in result.replace("_", " ").replace("-", " ")
                                if x.isalnum()
                            )
                    # Replace the token with the result
                    template = template.replace(replace_token, str(result))
                # If result not found, but the token is option, remove the token from the template
                elif token[0] == "[":
                    template = template.replace(token, "")

                # TODO: Determine approach
                # Else the value hasn't been found AND field is required, and so let's replace with 'UNKNOWN'
                # elif token[0] != '[':
                #    result = 'UNKNOWN'
                #    template = template.replace(replace_token, result)
        else:
            pass

    # Replace any [] from the string
    processed_template = re.sub(r"\[|\]", "", template)

    return processed_template


def get_pattern(format_params):
    return format_params.get("$pattern")


def format_value(params, value):
    """Formats a string value based on list of given parameters i.e. [{"$replace": {"$pattern": "ab", "$replacement": "c"}}]
    will return "dcf" from "dabf".
    """
    for param in params:
        if "$replace" in param:
            value = re.sub(
                get_pattern(param["$replace"]),
                param["$replace"].get("$replacement"),
                value,
            )
        elif "$lower" in param:
            if isinstance(param["$lower"], dict) and get_pattern(param["$lower"]):
                value = re.sub(
                    get_pattern(param["$lower"]), lambda m: m.group(0).lower(), value
                )
            else:
                value = value.lower()
        elif "$upper" in param:
            if isinstance(param["$upper"], dict) and get_pattern(param["$upper"]):
                value = re.sub(
                    get_pattern(param["$upper"]), lambda m: m.group(0).upper(), value
                )
            else:
                value = value.upper()
        elif "$camelCase" in param:
            if isinstance(param["$camelCase"], dict) and get_pattern(
                param["$camelCase"]
            ):
                patterns = get_pattern(param["$camelCase"])
                if not isinstance(patterns, list):
                    patterns = [patterns]
                for pattern in patterns:
                    value = value.replace(pattern, " ")
                value = "".join(x for x in value.title() if x.isalnum())
                value = value[0].lower() + value[1:]
            else:
                # Best to not process string with <...> with $camelCase : true
                value = "".join(
                    x
                    for x in value.replace("_", " ").replace("-", " ").title()
                    if x.isalnum()
                )
                value = value[0].lower() + value[1:]

    return value


def confirmation_prompt(message):
    """Continue prompting at the terminal for a yes/no repsonse.

    Arguments:
        message (str): The prompt message

    Returns:
        bool: True if the user responded yes, otherwise False
    """
    responses = {"yes": True, "y": True, "no": False, "n": False}
    while True:
        six.print_("{} (yes/no): ".format(message), end="")
        choice = input().lower()
        if choice in responses:
            return responses[choice]
        six.print_('Please respond with "yes" or "no".')


class RunCounter:
    def __init__(self):
        self.current = 0
        self.used = set()

    def next(self):  # only used for + or =
        self.current = self.current + 1
        self.used.add(self.current)
        return str(self.current)

    def current(self):  # only used for + or =
        self.used.add(self.current)
        return str(self.current)

    def increment_if_used(
        self, current_str
    ):  # only used for digits in handle_run_counter_initializer()
        new_value = int(current_str)

        while new_value in self.used:
            new_value += 1

        if new_value != int(current_str):
            logger.warning(
                "run_counter %s has already been used, using %s instead",
                current_str,
                new_value,
            )

        self.current = new_value
        self.used.add(new_value)

        return f"{int(new_value):0>{len(current_str)}}"


class RunCounterMap:
    def __init__(self):
        self.entries = {}

    def __getitem__(self, key):
        if key not in self.entries:
            self.entries[key] = RunCounter()
        return self.entries[key]

    def __contains__(self, key):
        return True
