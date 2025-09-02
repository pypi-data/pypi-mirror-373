import logging
import re
from typing import Tuple, Union, Optional, Dict

from .schemas import *
from .constants import *

logging.basicConfig()
logging.getLogger().setLevel("INFO")


class Validator:
    def check(self, config: dict) -> dict:
        errors = {}

        if config is None:
            errors["meta"] = ["Invalid argument: None"]
        else:
            try:
                version = config["version"]
                if version == "0.1.0":
                    errors.update(V0_1_0().process(config))
                else:
                    errors["version"] = ["Unsupported configuration version"]
            except KeyError:
                errors["version"] = ["Missing configuration version"]
            except TypeError as e:
                if "NoneType" in str(e):
                    errors["version"] = ["Invalid configuration argument"]
                else:
                    raise e

        return errors


class V:
    def process(self, config: dict) -> dict:
        raise NotImplementedError(self.__class__.__name__)


class V0_1_0(V):
    def process(self, config: dict) -> dict:
        errors = {}

        #
        # Meta block
        #
        try:
            project = config["project"]
            if project is None or len(project) == 0:
                errors["project"] = ["Invalid project name"]
        except KeyError:
            errors["project"] = ["Missing project name"]

        try:
            job_specs = config["jobs"]
            if job_specs is None or len(job_specs) == 0:
                job_specs = {}
                errors["jobs"] = {"block": ["Empty jobs definition"]}
        except KeyError:
            job_specs = {}
            errors["jobs"] = {"block": ["Missing jobs definition"]}

        jobs = {}
        for job_name, job in job_specs.items():
            job_errors = {}

            #
            # Type
            #
            try:
                job_type = job["type"]
                if job_type is None or job_type != "test":
                    job_errors["type"] = ["Invalid job type"]
            except KeyError:
                job_errors["type"] = ["Missing job type"]

            #
            # Runtime block
            #
            try:
                runtime_errors = self._validate_specs(job["runtime"], runtime_schema)
                if len(runtime_errors) > 0:
                    job_errors["runtime"] = runtime_errors
            except KeyError:
                job_errors["runtime"] = {"block": ["Missing runtime information"]}

            #
            # Package block
            #
            # Detect if runtime based on a supported framework/sim combination,
            # as it currently modulates packaging options.
            try:
                image_exists, attempted_image = self.__check_for_base_image(
                    job["runtime"]["framework"], job["runtime"]["simulator"]
                )
            except KeyError:
                image_exists, attempted_image = False, None

            if "package" in job:
                package_errors = self._validate_specs(job["package"], package_schema)
                if len(package_errors) > 0:
                    job_errors["package"] = package_errors
            elif image_exists:
                logging.info("No packaging information, will use Artefacts images")
            else:
                if attempted_image:
                    error_string = f"using an unsupported framework/simulator combination: Could not find '{attempted_image}'"
                else:
                    error_string = "no runtime framework"

                job_errors["package"] = {
                    "block": f"Missing package information, necessary when {error_string}"
                }

            #
            # Scenarios block
            #
            try:
                scenarios_errors = self._validate_specs(
                    job["scenarios"], scenarios_schema
                )
                if len(scenarios_errors) > 0:
                    job_errors["scenarios"] = scenarios_errors
            except KeyError:
                job_errors["scenarios"] = {"block": ["Missing scenarios information"]}

            if len(job_errors) > 0:
                try:
                    errors["jobs"][job_name] = job_errors
                except KeyError:
                    errors["jobs"] = {job_name: job_errors}

        return errors

    def _validate_specs(self, specs: dict, schema: dict) -> dict:
        errors = {}
        if not VALIDATOR.validate(specs, schema):
            errors_list = []
            schema_errors = self.__get_errors_list(VALIDATOR.errors, errors_list)
            for schema_error in schema_errors:
                errors.update(
                    {schema_error["block"]: self.__get_error_message(schema_error)}
                )
        return errors

    # Recursive, and the joys that come with that.
    # Takes in an empty list first, then keeps calling back on itself
    # until all config errors are added in.
    # If validation errors gets buggy, this is a good place to start.
    def __get_errors_list(
        self, errors: dict, errors_list: list, block: str = ""
    ) -> list:
        for field, suberrors in errors.items():
            for suberror in suberrors:
                if isinstance(suberror, dict):
                    # The "." is here so the functions knows how deep into a dict it is
                    # and is normalized in the normalize_block function below.
                    self.__get_errors_list(suberror, errors_list, f"{block}.{field}")
                else:
                    errors_list.append(
                        {
                            # remove the prepending "."
                            "block": self.__normalize_block(
                                block.replace(".", "", 1), field
                            ),
                            "field": field,
                            "error": suberror,
                        }
                    )
        return errors_list

    def __get_error_message(self, config_errors: dict) -> Union[Dict[str, str], str]:
        field, error = config_errors["field"], config_errors["error"]
        # If field == block it is a top level error
        return error if field == config_errors["block"] else {field: error}

    def __normalize_block(self, block: str, field: str) -> str:
        # 1. If no block, we know it is at the top level
        if not block:
            return field

        # 2. Checks if block where error occured is a list, and if so
        # wraps the element in brackets while removing the "." seperator
        # E.g settings.0 -> settings[0]
        block_takes_list = re.search(r"\.(\d+)$", block)
        if block_takes_list:
            number = block_takes_list.group(1)
            block = block[: -len(number) - 1] + "[" + number + "]"

        # 3. Any remaining "." denotes additional nesting of fields, so
        # change to : for humans to read
        block = block.replace(".", ":")

        return block

    def __check_for_base_image(
        self, framework: str, simulator: str
    ) -> Tuple[bool, Optional[str]]:
        if not framework:
            return False, None

        if simulator == "turtlesim":
            simulator_version = "turtlesim"
        else:
            try:
                simulator_version = simulator.split(":")[1]
                # E.g. "11" is too general for gazebo:11, so we want gazebo11
                if simulator_version.isnumeric():
                    simulator_version = simulator.replace(":", "")
            except IndexError:
                simulator_version = simulator
        base_image = f"{framework}-{simulator_version}"
        # Returns True/False and what it attempted to find
        return base_image in ARTEFACTS_BASE_IMAGES, base_image
