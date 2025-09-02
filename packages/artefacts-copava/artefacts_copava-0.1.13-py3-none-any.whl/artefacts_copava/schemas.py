common_scenario_fields = {
    "output_dirs": {"type": "list"},
    "output_path": {"type": "string"},
    "metrics": {"anyof": [{"type": "string"}, {"type": "list"}]},
    "params": {"type": "dict"},
    "rosbag_record": {"type": "string"},
    "ros_testpackage": {"type": "string"},
    "ros_testfile": {"type": "string", "excludes": ["run", "launch_test_file", "pytest_file"]},
    "rosbag_postprocess": {"type": "string"},
    "run": {"type": "string", "excludes": ["ros_testfile", "launch_test_file", "pytest_file"]},
    "launch_test_file": {"type": "string", "excludes": ["ros_testfile", "run", "pytest_file"]},
    "pytest_file": {"type": "string", "excludes": ["ros_testfile", "run", "launch_test_file"]},
    "subscriptions": {"type": "dict"},
    "launch_arguments": {"type": "dict"},
}

scenarios_schema = {
    "defaults": {"type": "dict", "schema": common_scenario_fields},
    "settings": {
        "type": "list",
        "minlength": 1,
        "required": True,
        "schema": {
            "type": "dict",
            "schema": dict(
                **common_scenario_fields,
                **{"name": {"type": "string", "required": True, "empty": False}},
            ),
        },
    },
}

runtime_schema = {
    "framework": {
        "type": "string",
        "empty": True,
        "nullable": True,
        "coerce": lambda x: None if x.lower() == "none" else x,
    },
    "simulator": {"type": "string", "required": True, "empty": False},
    "pre_launch": {"type": "string", "dependencies": {"framework": "ros1:noetic"}},
    "params": {"type": "dict", "dependencies": {"framework": "ros1:noetic"}},
}

package_schema = {
    "custom": {
        "type": "dict",
        "excludes": "docker",
        "schema": {
            "os": {"type": "string", "empty": False},
            "include": {"type": "list", "minlength": 1},
            "commands": {"type": "list", "minlength": 1},
        },
    },
    "docker": {
        "type": "dict",
        "empty": False,
        "excludes": "custom",
        "schema": {
            "build": {
                "type": "dict",
                "excludes": "image",
                "schema": {
                    "dockerfile": {"type": "string", "empty": False},
                },
            },
            "image": {"type": "string", "excludes": "build", "empty": False},
        },
    },
}
