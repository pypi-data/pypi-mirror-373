import yaml
from .constants import ARTEFACTS_PARAMS_FILE
from typing import Dict, Any


def get_artefacts_param(param_type, param_name, default=None, is_ros=True):
    # TODO: requires artefacts-cli to accept non-ROS parameters
    if not is_ros:
        raise NotImplementedError(
            "Error: Non-ROS parameters are not yet supported. Exiting..."
        )

    with open(ARTEFACTS_PARAMS_FILE, "r") as file:
        try:
            params = yaml.safe_load(file)
            param = params[param_type]["ros__parameters"][param_name]
            # Ros Launch arguments need to be of type string, so convert if necessary
            if param_type == "launch" and not type(param) == str:
                param = str(param)
            return param
        except KeyError:
            if default is not None:
                return default
            raise KeyError(
                f"Error: Unable to find parameter {param_name} of type {param_type} in artefacts.yaml. Exiting..."
            )
        except Exception as e:
            raise RuntimeError(f"Error: {e}. Exiting...")


def get_artefacts_params() -> Dict[str, Any]:
    """
    Load all the artefacts parameters.
    """
    try:
        with open(ARTEFACTS_PARAMS_FILE, "r") as file:
            params = yaml.safe_load(file)
            if not isinstance(params, dict):
                raise ValueError(
                    "Error: The content of '{file}' is not a valid dictionary. Exiting...".format(
                        file=ARTEFACTS_PARAMS_FILE
                    )
                )
            return params
    except Exception as e:
        raise RuntimeError(f"Failed to load '{ARTEFACTS_PARAMS_FILE}': {e}")

def deep_merge_dicts(source, override):
    """Recursively merge two dictionaries, with values from `override` taking precedence over `source`"""
    for key, value in override.items():
        if isinstance(value, dict) and key in source:
            source[key] = deep_merge_dicts(source[key], value)
        else:
            source[key] = value
    return source

def merge_ros_params_files(source, override, destination):
    """Merge two ROS2 yaml parameter files into one, overriding the values in the first one with the values in `override`"""
    import yaml

    with open(source, "r") as f:
        source_params = yaml.safe_load(f)

    with open(override, "r") as f:
        override_params = yaml.safe_load(f)

    merged_params = deep_merge_dicts(source_params, override_params)
    with open(destination, "w") as f:
        yaml.dump(merged_params, f)