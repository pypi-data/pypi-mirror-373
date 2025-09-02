import os
from datetime import datetime
from pathlib import Path
import json

from cerberus import Validator as CerberusValidator, errors
import requests

ARTEFACTS_REPOSITORIES = ["ros2", "ros1"]
if os.environ.get("AWS_EXECUTION_ENV"):
    ARTEFACTS_IMAGE_CACHE_DIR = Path("/tmp/artefacts/cache")
else:
    ARTEFACTS_IMAGE_CACHE_DIR = Path.home() / Path(".artefacts") / Path("cache")
ARTEFACTS_IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
ARTEFACTS_IMAGE_CACHE_FRESHNESS_SEC = 300


# Used with Cerberus to customize error messages.
class CustomErrorHandler(errors.BasicErrorHandler):
    messages = errors.BasicErrorHandler.messages.copy()
    # Mutually Exclusive Fields
    messages[errors.EXCLUDES_FIELD.code] = (
        "Mutually Exclusive: {0} cannot be used together with '{field}'"
    )
    # Empty Lists -> This may need changing if we check for minimum lengths
    # other than lists in future.
    messages[errors.MIN_LENGTH.code] = (
        "Empty: '{field}' must be of type 'list' with minimum length {constraint}"
    )
    messages[errors.DEPENDENCIES_FIELD_VALUE.code] = (
        "'{field}' is only supported with {constraint}"
    )


def get_artefacts_base_images() -> list:
    # Cache management
    cache_file = ARTEFACTS_IMAGE_CACHE_DIR / Path("known_base_images.json")
    if cache_file.exists():
        if (
            # pyre being strict on st_ctime
            cache_file.stat().st_ctime # pyre-ignore[16]
            < datetime.now().timestamp() - ARTEFACTS_IMAGE_CACHE_FRESHNESS_SEC
        ):
            # Cache is old, so rebuild.
            cache_file.unlink()
        else:
            # Cache is fresh, let's load and not hit APIs.
            return json.loads(cache_file.read_text(encoding="UTF-8"))

    # Build list
    images = set()
    for repository in ARTEFACTS_REPOSITORIES:
        result = requests.post(
            "https://api.us-east-1.gallery.ecr.aws/describeImageTags",
            json={"registryAliasName": "artefacts", "repositoryName": repository},
            headers={"Content-Type": "application/json"},
        )
        subset = set(
            repository + ":" + "-".join(v["imageTag"].split("-", 2)[:2])
            for v in result.json()["imageTagDetails"]
        )
        images.update(subset)
    images = list(images)

    # Cache the list
    with cache_file.open("w", encoding="UTF-8") as target:
        json.dump(images, target)

    return images


VALIDATOR = CerberusValidator(error_handler=CustomErrorHandler)
ARTEFACTS_BASE_IMAGES = get_artefacts_base_images()
