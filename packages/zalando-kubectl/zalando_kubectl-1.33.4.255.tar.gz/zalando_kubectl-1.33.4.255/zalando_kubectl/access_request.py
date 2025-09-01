import click
import json
import os

from datetime import datetime, timedelta, timezone
from pathlib import Path
from rich import console
from rich.table import Table
from rich.prompt import Prompt
from time import sleep
import urllib.parse
import requests
import zalando_kubectl.utils

from zalando_kubectl.utils import auth_headers, Environment

from . import kube_config, registry

console = console.Console()

APPROVED_STATUS = "PROVISIONED"


def get_privileged_access_api(config):
    try:
        return config["privileged_access_api"].rstrip("/")
    except KeyError:
        raise Exception(
            "Privileged Access API URL missing, please reconfigure zkubectl by running `zalando-cli-bundle configure`"
        )


def emergency_service_url(env: Environment) -> str:
    # emergency-access service URL isn't stored anywhere in the cluster metadata,
    # so we need to build it manually by taking the API server URL and replace the first
    # component with emergency-access.
    api_server_host = urllib.parse.urlparse(zalando_kubectl.utils.get_api_server_url(env)).hostname
    _, cluster_domain = api_server_host.split(".", 1)
    return "https://emergency-access-service.{}".format(cluster_domain)


def _update_token(env, current_cluster, okta_auth_client_id):
    kube_config.get_auth_token(env, current_cluster, okta_auth_client_id, True)


def _wait_for_approval(env, current_cluster, response, auth_header, wait_for_approval, timeout, okta_auth_client_id):
    """Polls until the request in the response is approved, then refreshes the token"""

    # return early if the request was already approved. This can happen in case the emergency-access-service is using
    # the emergency by-pass-flow.
    status = response.get("result", {}).get("request_status", "")
    if status == APPROVED_STATUS:
        click.echo(f"\nYour access request is approved!")
        _update_token(env, current_cluster, okta_auth_client_id)
        return True

    request_key = response["result"]["request_key"]
    request_url = response["result"]["_links"]["request_status"]["href"]

    # Get the status of the access request.
    status = _get_request_status(request_url, auth_header)

    base_cmd = "zkubectl"
    if env.kube_context:
        base_cmd += f" --context {env.kube_context}"

    click.echo(f"\nCheck the status of your request:\n")
    click.echo(f"  {base_cmd} cluster-access list --request-key {request_key}\n")
    click.echo(f"You can send the following command to your co-worker to approve the request:\n")
    if current_cluster:
        click.echo(f"  {base_cmd} login {current_cluster} && {base_cmd} cluster-access approve {request_key}\n")
    else:
        click.echo(f"  {base_cmd} cluster-access approve {request_key}\n")

    if not wait_for_approval:
        return False

    click.echo("Waiting for the request to be approved...")

    # Wait for the access request to be approved or until the timeout hits.
    check_interval, waited_time = 10, 0
    while status != APPROVED_STATUS:
        sleep(check_interval)
        waited_time += check_interval

        # Get the status of the access request.
        status = _get_request_status(request_url, auth_header)

        if waited_time > timeout:
            break

    if status == APPROVED_STATUS:
        click.echo(f"\nYour access request is approved!")
        _update_token(env, current_cluster, okta_auth_client_id)
        return True
    else:
        click.echo(f"\nYour access request was not approved yet! You can try again at any time.")
        return False


def _has_any_state_file(cluster):
    """Check if the cluster has any of the state files present"""

    return _has_state_file("privileged", cluster) or _has_state_file("emergency", cluster)


def _has_state_file(access_type, cluster):
    """When state file exists, check if it is older than 1 hour"""

    file = _get_state_file_name(access_type, cluster)
    if file.exists():
        state_file = json.loads(file.open().read())
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=1)
        request_time = state_file.get("request_time", None)
        if request_time is None:
            return False
        request_time = datetime.fromisoformat(request_time).replace(tzinfo=timezone.utc)
        if start <= request_time <= end:
            return True
        else:
            file.unlink()  # Delete state file if older than 1 hour.
            return False
    else:
        return False


def create_with_okta(
    env: Environment,
    access_type,
    reference_url,
    reason,
    okta_auth_client_id,
    account_name,
    wait_for_approval,
    timeout,
    force_new_request,
):
    priv_api = get_privileged_access_api(env.config)
    current_cluster = kube_config.get_context(env)
    if okta_auth_client_id is None:
        okta_auth_client_id = kube_config.get_okta_auth_client_id(env, current_cluster)
    okta_token = kube_config.get_auth_token(env, current_cluster, okta_auth_client_id)
    auth_header = {"Authorization": f"Bearer {okta_token}"}
    state_file = _get_state_file_name(access_type, current_cluster)

    if account_name is None:
        registry_url = zalando_kubectl.main.get_registry_url(env.config)
        cluster_metadata = registry.get_cluster_by_id_or_alias(registry_url, current_cluster)
        account_metadata = registry.get_account_with_id(registry_url, cluster_metadata["infrastructure_account"])
        account_name = account_metadata["name"]

    click.echo("Sending a request for privileged access...")

    if not force_new_request and _has_state_file(access_type, current_cluster):
        state_file_content = json.loads(state_file.open().read())
        success = _wait_for_approval(
            env,
            current_cluster,
            state_file_content["privileged_access_api_response"],
            auth_header,
            wait_for_approval,
            timeout,
            okta_auth_client_id,
        )
        if success:
            _remove_state_file(access_type, current_cluster)
        return

    request = zalando_kubectl.priv_api.PrivRequest(
        account_name=account_name,
        business_justification=reason,
        access_type=access_type,
        reference_url=reference_url,
    )

    response = zalando_kubectl.priv_api.post_request(priv_api, auth_header, request)
    _handle_http_error(response)

    state_file_content = {
        "privileged_access_api_response": response.json(),
        "request_time": datetime.now(timezone.utc).isoformat(),
    }
    state_file.write_text(json.dumps(state_file_content))

    success = _wait_for_approval(
        env, current_cluster, response.json(), auth_header, wait_for_approval, timeout, okta_auth_client_id
    )
    if success:
        _remove_state_file(access_type, current_cluster)


def approve_with_okta(env: Environment, request_key, okta_auth_client_id, skip_prompt):
    priv_api = get_privileged_access_api(env.config)
    current_cluster = kube_config.get_context(env)
    if okta_auth_client_id is None:
        okta_auth_client_id = kube_config.get_okta_auth_client_id(env, current_cluster)
    okta_token = kube_config.get_auth_token(env, current_cluster, okta_auth_client_id)
    auth_header = {"Authorization": f"Bearer {okta_token}"}

    console.print(f"[yellow]Listing access request with request key {request_key}.")

    table = Table(show_edge=True, show_lines=False, header_style="r")
    table.add_column("RequestKey", justify="left", style="green", no_wrap=True)
    table.add_column("Account", justify="left", style="green", no_wrap=True)
    table.add_column("AccessRole", justify="left", style="green", no_wrap=True)
    table.add_column("Requestor", justify="left", style="green", no_wrap=False)
    table.add_column("Approvers", justify="left", style="green", no_wrap=False)
    table.add_column("Reason", justify="left", style="green", no_wrap=False)
    table.add_column("Status", justify="left", style="green", no_wrap=True)

    list_request = zalando_kubectl.priv_api.ListRequests(
        requestor=None,
        account_name=None,
        request_key=request_key,
    )

    response = zalando_kubectl.priv_api.list_requests(priv_api, auth_header, list_request)
    _handle_http_error(response)

    if len(response.json()) != 1:
        raise ValueError("Could not fetch details about access request {}".format(request_key))

    response_dict = response.json()[0]

    table.add_row(
        response_dict.get("request_key"),
        response_dict.get("account_name"),
        response_dict.get("access_role"),
        response_dict.get("requestor"),
        _approvers_str(response_dict.get("approvers")),
        response_dict.get("business_justification"),
        response_dict.get("request_status"),
    )

    console.print(table)

    if response_dict.get("request_status") == APPROVED_STATUS:
        console.print("The request is already approved.")
        return

    if skip_prompt:
        decision = "APPROVED"
        approver_comment = ""
    else:
        approve_reject = Prompt.ask("Would you like to approve this request?", choices=["y", "n"])

        if approve_reject == "y":
            decision = "APPROVED"
        else:
            decision = "REJECTED"

        approver_comment = Prompt.ask("Please enter comment to this request, if you like?", default="")

    request = zalando_kubectl.priv_api.PrivApprove(
        request_key=request_key,
        requestor=response_dict.get("requestor"),
        account_name=response_dict.get("account_name"),
        business_justification=response_dict.get("business_justification"),
        decision=decision,
        approver_comment=approver_comment,
    )

    response = zalando_kubectl.priv_api.post_approve(priv_api, auth_header, request)
    _handle_http_error(response)

    if decision == "APPROVED":
        console.print("Request was approved.")
    else:
        console.print("Request was rejected.")


def list_with_okta(env: Environment, request_key, okta_auth_client_id, account_name, output):
    priv_api = get_privileged_access_api(env.config)
    current_cluster = kube_config.get_context(env)
    if okta_auth_client_id is None:
        okta_auth_client_id = kube_config.get_okta_auth_client_id(env, current_cluster)
    okta_token = kube_config.get_auth_token(env, current_cluster, okta_auth_client_id)
    auth_header = {"Authorization": f"Bearer {okta_token}"}

    if account_name is None:
        registry_url = zalando_kubectl.main.get_registry_url(env.config)
        cluster_metadata = registry.get_cluster_by_id_or_alias(registry_url, current_cluster)
        account_metadata = registry.get_account_with_id(registry_url, cluster_metadata["infrastructure_account"])
        account_name = account_metadata["name"]

    if output != "json":
        table = Table(show_edge=True, show_lines=False, header_style="r")
        table.add_column("RequestKey", justify="left", style="green", no_wrap=True)
        table.add_column("Account", justify="left", style="green", no_wrap=True)
        table.add_column("AccessRole", justify="left", style="green", no_wrap=True)
        table.add_column("Requestor", justify="left", style="green", no_wrap=False)
        table.add_column("Approvers", justify="left", style="green", no_wrap=False)
        table.add_column("Reason", justify="left", style="green", no_wrap=False)
        table.add_column("Status", justify="left", style="green", no_wrap=True)

    list_request = zalando_kubectl.priv_api.ListRequests(
        requestor=None,
        account_name=account_name,
        request_key=request_key,
    )

    response = zalando_kubectl.priv_api.list_requests(priv_api, auth_header, list_request)
    _handle_http_error(response)

    if output == "json":
        print(json.dumps(response.json()))
    else:
        for item in response.json():
            table.add_row(
                item.get("request_key"),
                item.get("account_name"),
                item.get("access_role"),
                item.get("requestor"),
                _approvers_str(item.get("approvers")),
                item.get("business_justification"),
                item.get("request_status"),
            )

        console.print(table)


def _get_state_file_name(access_type, cluster):
    """Returns the name of the state file for a given access type and cluster"""

    STATE_CACHE_DIR = Path.home() / ".kube/cache/zkubectl/"

    if not os.path.exists(STATE_CACHE_DIR):
        os.makedirs(STATE_CACHE_DIR)

    return STATE_CACHE_DIR / f"zkubectl_{access_type}_access_{cluster}"


def _remove_state_file(access_type, cluster):
    """Deletes the state file for a given access type and cluster"""

    file = _get_state_file_name(access_type, cluster)
    if file.exists():
        file.unlink()


def _extract_error(response):
    error_obj = response.json()
    title = error_obj.get("title")
    detail = error_obj.get("detail")
    message = "\n".join(filter(None, [title, detail]))
    if response.status_code != 401:
        message = "[{code}] {message}".format(code=response.status_code, message=message)
    return message


def _handle_http_error(response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Try to see if we can extract a nice error message, or just raise the original error if we can't
        try:
            message = _extract_error(response)
        except Exception:
            raise e
        else:
            raise Exception(message)


def combine_request_approved(access_requests):
    """Combine pending and approved requests for the same user.

    Emergency Access Service returns both requests and approved access.
    If a request is already approved we don't want to show the request, so
    we merge the requests by user."""
    # TODO: move to server side.
    current_access = {}
    for request in access_requests:
        req = current_access.get(request["user"], request)
        if not req.get("approved", False):
            req["approved"] = request.get("approved", False)
            req["expiry_time"] = request["expiry_time"]

        if req.get("reason", "") == "":
            req["reason"] = request["reason"]

        current_access[request["user"]] = req
    return current_access


def _get_request_status(url, auth_header):
    response = requests.get(url, headers=auth_header)
    _handle_http_error(response)

    if len(response.json()) != 1:
        raise ValueError("Could not fetch details about access request: {}".format(url))

    return response.json()[0]["request_status"]


def _approvers_str(approvers):
    if not approvers:
        return ""

    if len(approvers) <= 3:
        return str(approvers)

    approvers = approvers[:2]
    approvers.append("...")
    return str(approvers)
