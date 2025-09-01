import json

from zalando_kubectl.models.stackset import StackSet

import pytest


def mock_get_stackset(name: str):
    stackset_def = {
        "apiVersion": "zalando.org/v1",
        "kind": "StackSet",
        "metadata": {"labels": {"application": name}, "name": name},
        "spec": {
            "traffic": [
                {"stackName": "{}-v1".format(name), "weight": 60},
                {"stackName": "{}-v2".format(name), "weight": 40},
                {"stackName": "{}-v3".format(name), "weight": 0},
            ]
        },
        "status": {
            "traffic": [
                {
                    "stackName": "{}-v1".format(name),
                    "serviceName": "{}-v1".format(name),
                    "servicePort": 80,
                    "weight": 70,
                },
                {
                    "stackName": "{}-v2".format(name),
                    "serviceName": "{}-v2".format(name),
                    "servicePort": 80,
                    "weight": 30,
                },
                {
                    "stackName": "{}-v3".format(name),
                    "serviceName": "{}-v3".format(name),
                    "servicePort": 80,
                    "weight": 0,
                },
            ]
        },
    }

    if name == "old-stackset":
        del stackset_def["status"]["traffic"]
        del stackset_def["spec"]["traffic"]
    elif name == "nostatus-stackset":
        del stackset_def["status"]["traffic"]
    elif name == "unusedstacks-stackset":
        del stackset_def["spec"]["traffic"][2]
    elif name == "singlestack-traffic":
        single_stack_traffic = [
            {"stackName": "{}-v1".format(name), "weight": 100},
            {"stackName": "{}-v2".format(name), "weight": 0},
            {"stackName": "{}-v3".format(name), "weight": 0},
        ]
        stackset_def["spec"]["traffic"] = single_stack_traffic

    return StackSet(stackset_def)


def test_get_traffic_stackset():
    stackset_name = "standard-stackset"
    expected = {
        "{}-v1".format(stackset_name): {"name": "{}-v1".format(stackset_name), "desired": 60, "actual": 70},
        "{}-v2".format(stackset_name): {"name": "{}-v2".format(stackset_name), "desired": 40, "actual": 30},
        "{}-v3".format(stackset_name): {"name": "{}-v3".format(stackset_name), "desired": 0, "actual": 0},
    }
    stackset = mock_get_stackset(stackset_name)

    traffic = stackset.get_traffic()
    assert len(traffic) == len(expected)
    for stack in traffic:
        for key in stack:
            assert stack[key] == expected[stack["name"]][key]


def test_get_traffic_unused_stacks():
    stackset_name = "unusedstacks-stackset"
    expected = {
        "{}-v1".format(stackset_name): {"name": "{}-v1".format(stackset_name), "desired": 60, "actual": 70},
        "{}-v2".format(stackset_name): {"name": "{}-v2".format(stackset_name), "desired": 40, "actual": 30},
        "{}-v3".format(stackset_name): {"name": "{}-v3".format(stackset_name), "desired": 0, "actual": 0},
    }
    stackset = mock_get_stackset(stackset_name)

    traffic = stackset.get_traffic()
    assert len(traffic) == len(expected)
    for stack in traffic:
        for key in stack:
            assert stack[key] == expected[stack["name"]][key]


def test_get_traffic_no_status():
    stackset_name = "nostatus-stackset"
    expected = {
        "{}-v1".format(stackset_name): {"name": "{}-v1".format(stackset_name), "actual": 0, "desired": 60},
        "{}-v2".format(stackset_name): {"name": "{}-v2".format(stackset_name), "actual": 0, "desired": 40},
        "{}-v3".format(stackset_name): {"name": "{}-v3".format(stackset_name), "actual": 0, "desired": 0},
    }
    stackset = mock_get_stackset(stackset_name)

    traffic = stackset.get_traffic()
    for stack in traffic:
        for key in stack:
            assert stack[key] == expected[stack["name"]][key]


def test_set_traffic_weight():
    stackset_name = "standard-stackset"
    expected = {
        "{}-v1".format(stackset_name): {"name": "{}-v1".format(stackset_name), "desired": 80, "actual": 70},
        "{}-v2".format(stackset_name): {"name": "{}-v2".format(stackset_name), "desired": 20, "actual": 30},
        "{}-v3".format(stackset_name): {"name": "{}-v3".format(stackset_name), "desired": 0, "actual": 0},
    }

    stackset = mock_get_stackset(stackset_name)
    stackset.set_traffic_weight("standard-stackset-v1", 80)

    traffic = stackset.get_traffic()
    for stack in traffic:
        for key in stack:
            assert stack[key] == expected[stack["name"]][key]


def test_set_traffic_weight_for_version():
    stackset_name = "standard-stackset"
    expected = {
        "{}-v1".format(stackset_name): {"name": "{}-v1".format(stackset_name), "desired": 80, "actual": 70},
        "{}-v2".format(stackset_name): {"name": "{}-v2".format(stackset_name), "desired": 20, "actual": 30},
        "{}-v3".format(stackset_name): {"name": "{}-v3".format(stackset_name), "desired": 0, "actual": 0},
    }

    stackset = mock_get_stackset(stackset_name)
    stackset.set_traffic_weight("v1", 80)

    traffic = stackset.get_traffic()
    for stack in traffic:
        for key in stack:
            assert stack[key] == expected[stack["name"]][key]


def test_set_traffic_weight_to_unused_stack():
    stackset_name = "unusedstacks-stackset"
    expected = {
        "{}-v1".format(stackset_name): {"name": "{}-v1".format(stackset_name), "desired": 0, "actual": 70},
        "{}-v2".format(stackset_name): {"name": "{}-v2".format(stackset_name), "desired": 0, "actual": 30},
        "{}-v3".format(stackset_name): {"name": "{}-v3".format(stackset_name), "desired": 100, "actual": 0},
    }

    stackset = mock_get_stackset(stackset_name)
    stackset.set_traffic_weight("{}-v3".format(stackset_name), 100)

    traffic = stackset.get_traffic()
    for stack in traffic:
        for key in stack:
            assert stack[key] == expected[stack["name"]][key]


def test_set_traffic_weight_to_single_stack():
    stackset_name = "singlestack-traffic"
    stackset = mock_get_stackset(stackset_name)

    with pytest.raises(ValueError):
        stackset.set_traffic_weight("{}-v1".format(stackset_name), 95)


def test_traffic_distribution():
    stackset_name = "standard-stackset"
    expected = {
        "{}-v1".format(stackset_name): {"name": "{}-v1".format(stackset_name), "desired": 48, "actual": 70},
        "{}-v2".format(stackset_name): {"name": "{}-v2".format(stackset_name), "desired": 32, "actual": 30},
        "{}-v3".format(stackset_name): {"name": "{}-v3".format(stackset_name), "desired": 20, "actual": 0},
    }

    stackset = mock_get_stackset(stackset_name)
    stackset.set_traffic_weight("standard-stackset-v3", 20)

    traffic = stackset.get_traffic()
    for stack in traffic:
        for key in stack:
            assert stack[key] == expected[stack["name"]][key]


def test_get_traffic_cmd():
    stackset_name = "standard-stackset"
    stackset = mock_get_stackset(stackset_name)

    _, _, name, _, _, patch = stackset.get_traffic_cmd()
    assert name == stackset_name
    expected = {
        "spec": {
            "traffic": [
                {"stackName": "standard-stackset-v1", "weight": 60},
                {"stackName": "standard-stackset-v2", "weight": 40},
                {"stackName": "standard-stackset-v3", "weight": 0},
            ]
        }
    }
    assert json.loads(patch) == expected
