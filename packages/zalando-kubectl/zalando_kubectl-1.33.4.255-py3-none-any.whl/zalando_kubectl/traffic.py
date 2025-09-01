import json
import subprocess
import time
from datetime import datetime, timedelta

import clickclick
import dateutil.parser
import natsort
from zalando_kubectl.models.bluegreen import BlueGreen
from zalando_kubectl.models.stackset import StackSet
from zalando_kubectl.models.stackset_ingress_authoritative import StackSetIngressAuthoritative
from zalando_kubectl.utils import ExternalBinary


def kubectl_run(kubectl: ExternalBinary, *cmd):
    return kubectl.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")


def get_bluegreen(kubectl: ExternalBinary, name: str):
    try:
        ingress_def = json.loads(kubectl_run(kubectl, "get", "ingress", name, "-o", "json"))
    except subprocess.CalledProcessError:
        # When no ingress is found, try to create a StackSet with embedded traffic
        return StackSet(json.loads(kubectl_run(kubectl, "get", "stackset", name, "-o", "json")))

    # StackSet with embedded traffic
    if ingress_def["metadata"]["annotations"].get("zalando.org/traffic-authoritative") == "false":
        return StackSet(json.loads(kubectl_run(kubectl, "get", "StackSet", name, "-o", "json")))

    for ref in ingress_def["metadata"].get("ownerReferences", []):
        # StackSet with no embedded traffic
        if ref["kind"] == "StackSet":
            res = kubectl_run(kubectl, "get", "Stacks", "-l", "stackset={}".format(name), "-o", "json")
            return StackSetIngressAuthoritative(ingress_def, json.loads(res))


def print_traffic(kubectl: ExternalBinary, bluegreen: BlueGreen, timeout=0):
    """Print the stacks and their weights in table format."""

    traffic = bluegreen.get_traffic()
    old_traffic = {stack["name"]: -1 for stack in traffic}
    old_warning = ""
    period = 2
    counter = timeout

    while counter >= 0:
        switched = True
        same_traffic = True

        for stack in traffic:
            if "desired" in stack:
                if stack["desired"] != stack["actual"]:
                    switched = False
                stack["desired"] = round(stack["desired"], 1)

            stack["actual"] = round(stack.get("actual", 0.0), 1)
            if stack["actual"] != old_traffic[stack["name"]]:
                same_traffic = False

        if not same_traffic:
            clickclick.print_table(traffic[0].keys(), natsort.natsorted(traffic, key=lambda i: i["name"]))

        if switched or timeout == 0:
            return

        events = get_resource_events(kubectl, bluegreen.get_name(), "TrafficNotSwitched")
        recent_events = get_recent_events(events, timedelta(minutes=2))
        warning = get_traffic_warning(recent_events)

        if warning and warning != old_warning:
            old_warning = warning
            clickclick.secho(warning, fg="yellow", bold=True)

        old_traffic = {stack["name"]: stack["actual"] for stack in traffic}
        traffic = get_bluegreen(kubectl, bluegreen.get_name()).get_traffic()

        counter -= period
        time.sleep(period)

    clickclick.error("Timed out: traffic switching took too long", fg="red")


def get_resource_events(kubectl, stackset, reason=""):
    """Get events (json) written to a given resource, given the resource name and optionally a reason"""
    if not reason:
        cmdline = ("get", "event", "--field-selector", "involvedObject.name={}".format(stackset), "-o", "json")
    else:
        cmdline = (
            "get",
            "event",
            "--field-selector",
            "involvedObject.name={},reason={}".format(stackset, reason),
            "-o",
            "json",
        )
    data = kubectl.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
    if data:
        json_data = json.loads(data)
        return json_data.get("items", [])
    return []


def get_recent_events(events, age: timedelta):
    """Get events with lastTimestamp =< age"""
    recent_events = []
    for event in events:
        last_timestamp = event.get("lastTimestamp", "")
        five_minutes_ago = datetime.utcnow() - age

        datetime_obj = dateutil.parser.parse(last_timestamp).replace(tzinfo=None)
        if datetime_obj >= five_minutes_ago:
            recent_events.append(event)

    return recent_events


def get_traffic_warning(traffic_events):
    """returns the message from the latest 'TrafficNotSwitched' event"""

    def last_timestamp(event):
        timestamp = event.get("lastTimestamp", "")
        datetime_obj = dateutil.parser.parse(timestamp).replace(tzinfo=None)
        return datetime_obj

    # Only consider the latest message since the others are redundant
    traffic_events.sort(key=last_timestamp)
    if len(traffic_events) >= 1:
        message = traffic_events[-1].get("message", "")
        return message
    else:
        return ""
