import atexit
import base64
import datetime
import os
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from itertools import chain
from pathlib import Path

import click
import clickclick
import humanize
import jinja2
import requests
import yaml
import zalando_kubectl
import zalando_kubectl.kube_permissions
import zalando_kubectl.secrets
import zalando_kubectl.traffic
import zalando_kubectl.priv_api
import zalando_kubectl.utils as utils
from clickclick import Action, info, print_table, OutputFormat
from dateutil.parser import parse
from dateutil.tz import tzutc
from zalando_kubectl.models.deployment import Deployment
from zalando_kubectl.models.stackset_ingress_authoritative import StackSetIngressAuthoritative
from zalando_kubectl.utils import (
    DecoratingGroup,
    Environment,
    PortMappingParamType,
    auth_headers,
    auth_token,
    current_user,
)

from . import access_request
from . import completion as comp
from . import generate as gen
from . import kube_config, registry
from .templating import copy_template, prepare_variables, read_senza_variables

UPDATE_BLOCK_CONFIG_ITEM = "cluster_update_block"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
OKTA_AUTH_CLIENT_ID_PREFIX = "kubernetes.cluster."
OKTA_AUTH_CLIENT_ID_KEY = "okta_auth_client_id"

STYLES = {
    "REQUESTED": {"fg": "yellow", "bold": True},
    "APPROVED": {"fg": "green"},
}
MAX_COLUMN_WIDTHS = {
    "reason": 50,
}


class ClusterAccessUnsupported(Exception):
    pass


def global_options(fn):
    """Attaches hidden '-n/--namespace' and '--context' options to the command that updates the namespace on the
    Environment object in the context."""

    def callback(ctx, param, value):
        if not ctx.obj:
            ctx.obj = Environment()
        if value is not None:
            # kubectl allows -s=bar in addition to --long=bar, which Click parses
            # as -s "=bar". Since neither of these can start with a '=' anyway,
            # let's just trim it.
            if value.startswith("="):
                value = value[1:]

            if param.name == "namespace":
                ctx.obj.set_namespace(value)
            elif param.name == "context":
                ctx.obj.set_kube_context(value)

    ns = click.option(
        "--namespace",
        "-n",
        help="If present, the namespace scope for this CLI request",
        required=False,
        expose_value=False,
        callback=callback,
    )
    conf = click.option(
        "--context",
        help="The name of the kubeconfig context to use",
        required=False,
        expose_value=False,
        callback=callback,
    )
    return conf(ns(fn))


@click.group(cls=DecoratingGroup, context_settings=CONTEXT_SETTINGS)
@global_options
@click.pass_obj
@click.pass_context
def click_cli(ctx, env: Environment):
    if ctx.invoked_subcommand != completion.name:
        env.kubectl.download()
        env.kubelogin.download()
    pass


click_cli.decorator = global_options


def get_registry_url(config):
    try:
        return config["cluster_registry"].rstrip("/")
    except KeyError:
        raise Exception(
            "Cluster registry URL missing, please reconfigure zkubectl by running `zalando-cli-bundle configure`"
        )


def fix_url(url):
    # strip potential whitespace from prompt
    url = url.strip()
    if url and not url.startswith("http"):
        # user convenience
        url = "https://" + url
    return url


def alias_from_url(url):
    m = re.match(r"https://[a-z0-9-]+.([a-z0-9-]+).zalan.do", url)
    if m:
        return m.group(1)
    else:
        return None


@click_cli.command("completion", context_settings={"help_option_names": [], "ignore_unknown_options": True})
@click.argument("kubectl-arg", nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
@click.pass_context
def completion(ctx, env: Environment, kubectl_arg):
    """Output shell completion code for the specified shell"""
    if not env.kubectl.exists():
        raise Exception("zkubectl: completions not yet available, run any zkubectl command to finish setting up")

    cmdline = ["completion"]
    cmdline.extend(kubectl_arg)
    stdout = env.kubectl.run(cmdline, stdout=subprocess.PIPE).stdout.decode("utf-8")

    lines = [line.rstrip().replace("kubectl", "zkubectl") for line in stdout.split("\n")]
    lines = comp.extend(lines, click_cli, ctx)

    print("\n".join(lines))


def looks_like_url(alias_or_url: str):
    if alias_or_url.startswith("http:") or alias_or_url.startswith("https:"):
        # https://something
        return True
    elif len(alias_or_url.split(".")) > 2:
        # foo.example.org
        return True
    return False


def configure_zdeploy(cluster):
    try:
        import zalando_deploy_cli.api

        zalando_deploy_cli.api.configure_for_cluster(cluster)
    except ImportError:
        pass


def login(config, cluster_or_url: str):
    if not cluster_or_url:
        cluster_or_url = click.prompt("Cluster ID or URL of Kubernetes API server")

    alias = None
    okta_auth_client_id = None
    ca = None

    if looks_like_url(cluster_or_url):
        url = fix_url(cluster_or_url)
        alias = alias_from_url(url)
        okta_auth_client_id = f"{OKTA_AUTH_CLIENT_ID_PREFIX}{alias}"
        print("URL", url, "ALIAS", alias, "OIDC Client ID", okta_auth_client_id)
        if "eks" in cluster_or_url:
            raise ClusterAccessUnsupported("EKS clusters via URL are not supported by zkubectl yet")
    else:
        cluster = registry.get_cluster_by_id_or_alias(get_registry_url(config), cluster_or_url)
        url = cluster["api_server_url"]
        alias = cluster["alias"]
        okta_auth_client_id = f"{OKTA_AUTH_CLIENT_ID_PREFIX}{alias}"
        if cluster["provider"] == "zalando-eks":
            cluster = registry.get_cluster_by_id_or_alias(get_registry_url(config), cluster_or_url, verbose=True)
            url = cluster["config_items"]["eks_endpoint"]
            ca = cluster["config_items"]["eks_certificate_authority_data"]
            if OKTA_AUTH_CLIENT_ID_KEY in cluster["config_items"]:
                okta_auth_client_id = cluster["config_items"][OKTA_AUTH_CLIENT_ID_KEY]
        configure_zdeploy(cluster)

    return url, alias, okta_auth_client_id, ca


@click_cli.command("configure")
@click.option("--cluster-registry", required=False, help="Cluster registry URL")
@click.option("--okta-auth", required=False, help="Okta Auth URL")
@click.option("--privileged-access-api", required=False, help="Privileged Access API URL")
@click.pass_obj
def configure(env: Environment, cluster_registry, okta_auth, privileged_access_api):
    """Set the Cluster Registry, Okta OIDC Issuer URL or Privileged Access API URL."""
    if not any([cluster_registry, okta_auth, privileged_access_api]):
        print(
            "Missing arguments. Provide at least one of Cluster Registry, Okta OIDC Issuer URL or "
            + "Privileged Access API URL. Alternatively you can run `zalando-cli-bundle configure`."
        )

    if cluster_registry:
        env.config["cluster_registry"] = cluster_registry
    if okta_auth:
        env.config["okta_auth"] = okta_auth
    if privileged_access_api:
        env.config["privileged_access_api"] = privileged_access_api

    env.store_config()


@click_cli.command("dashboard")
@click.pass_obj
def dashboard(env: Environment):
    """Open the kube-web-view dashbord in the browser"""
    import webbrowser

    url = "https://kube-web-view.zalando.net/"
    info("\nOpening {} ..".format(url))
    webbrowser.open(url)


def _open_kube_ops_view_in_browser():
    import webbrowser

    # sleep some time to make sure "kubectl proxy" and kube-ops-view run
    url = "http://localhost:8080/"
    with Action("Waiting for Kubernetes Operational View..") as act:
        while True:
            time.sleep(0.1)
            try:
                requests.get(url, timeout=2)
            except Exception:
                act.progress()
            else:
                break
    info("\nOpening {} ..".format(url))
    webbrowser.open(url)


@click_cli.command("opsview")
@click.pass_obj
def opsview(env: Environment):
    """Open the Kubernetes Operational View (kube-ops-view) in the browser"""
    import threading

    # pre-pull the kube-ops-view image
    image_name = "hjacobs/kube-ops-view:0.10"
    subprocess.check_call(["docker", "pull", image_name])

    thread = threading.Thread(target=_open_kube_ops_view_in_browser, daemon=True)
    # start short-lived background thread to allow running "kubectl proxy" in main thread
    thread.start()
    if sys.platform == "darwin":
        # Docker for Mac: needs to be slightly different in order to navigate the VM/container inception
        opts = ["-p", "8080:8080", "-e", "CLUSTERS=http://docker.for.mac.localhost:8001"]
    else:
        opts = ["--net=host"]
    subprocess.Popen(["docker", "run", "--rm", "-i"] + opts + [image_name])
    kube_config.update_token(env)
    env.kubectl.exec("proxy", "--accept-hosts=.*")


@click_cli.command("logtail", context_settings=dict(ignore_unknown_options=True, help_option_names=[]))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
def logtail(env: Environment, args):
    """Tail multiple pods and containers"""
    kube_config.update_token(env)
    env.stern.exec(*args)


def do_list_clusters(config):
    cluster_registry = get_registry_url(config)

    response = requests.get(
        "{}/kubernetes-clusters".format(cluster_registry),
        params={"lifecycle_status": "ready", "verbose": "false"},
        headers=auth_headers(),
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    rows = []
    for cluster in data["items"]:
        status = cluster.get("status", {})

        next_version = status.get("next_version")
        if next_version and next_version != status.get("current_version"):
            cluster["status"] = "updating"
        else:
            cluster["status"] = "ready"

        rows.append(cluster)
    rows.sort(key=lambda c: (c["alias"], c["id"]))
    print_table("id alias environment channel status".split(), rows)
    return rows


@click_cli.command("list-clusters")
@click.pass_obj
def list_clusters(env: Environment):
    """List all Kubernetes cluster in "ready" state"""
    do_list_clusters(env.config)


@click_cli.command("list")
@click.pass_context
def list_clusters_short(ctx):
    '''Shortcut for "list-clusters"'''
    ctx.forward(list_clusters)


@click_cli.command("credentials")
@click.argument("cluster", required=True)
@click.option("--okta-auth-client-id", help="Okta client ID to use for authentication")
@click.pass_obj
def credentials(env: Environment, cluster, okta_auth_client_id=None):
    # if no custom Okta client ID is provided, infer it from the cluster alias
    if not okta_auth_client_id:
        okta_auth_client_id = f"{OKTA_AUTH_CLIENT_ID_PREFIX}{cluster}"

    kube_config.get_auth(env, okta_auth_client_id, access_request._has_any_state_file(cluster))


@click_cli.command("login")
@click.argument("cluster", required=False)
@click.option(
    "--force-refresh/--no-force-refresh",
    default=False,
    help="Refresh the token regardless of its expiration time",
)
@click.pass_obj
def do_login(env: Environment, cluster, force_refresh):
    """Login to a specific cluster"""
    url, alias, okta_auth_client_id, ca = login(env.config, cluster)
    env.store_config()

    token = kube_config.get_auth_token(env, alias, okta_auth_client_id, force_refresh)

    with Action("Writing kubeconfig for {}..".format(url)):
        kube_config.update(url, alias, okta_auth_client_id, token, ca=ca)


@click_cli.command("encrypt")
@click.option("--cluster", help="Cluster ID or alias")
@click.option("--strip/--no-strip", default=True, help="Remove the trailing newline from the data, enabled by default")
@click.option("--kms-keyid", help="The KMS key ID that should be used to encrypt the payload, optional")
@click.option("--role", help="The role to use in the target account, optional")
@click.pass_obj
def encrypt(env: Environment, cluster, kms_keyid, strip, role):
    """Encrypt a value for use in a deployment configuration"""
    registry_url = get_registry_url(env.config)
    if cluster:
        cluster_metadata = registry.get_cluster_by_id_or_alias(registry_url, cluster)
    else:
        cluster_metadata = registry.get_cluster_with_params(registry_url, alias=utils.get_cluster_alias(env))

    account_metadata = registry.get_account_with_id(registry_url, cluster_metadata["infrastructure_account"])

    if click.get_text_stream("stdin").isatty():
        plain_text = click.prompt("Data to encrypt", hide_input=True).encode()
    else:
        plain_text = sys.stdin.buffer.read()

    if strip:
        plain_text = plain_text.rstrip(b"\r\n")

    encrypted = (
        zalando_kubectl.secrets.encrypt_with_okta(env, account_metadata, kms_keyid, role, strip, plain_text)
        .decode("utf-8")
        .strip()
    )

    print(encrypted)


@click_cli.command("decrypt")
@click.argument("encrypted_value", required=True)
@click.option("--role", help="The role to use in the target account, optional")
@click.pass_obj
def decrypt(env: Environment, role, encrypted_value):
    """Decrypt a value encrypted with zkubectl encrypt"""
    decrypted = zalando_kubectl.secrets.decrypt_with_okta(env, role, encrypted_value)
    decrypted = decrypted.rstrip(b"\n")

    return sys.stdout.buffer.write(decrypted)


def _validate_weight(_ctx, _param, value):
    if value is None:
        return None
    elif not 0.0 <= value <= 100.0:
        raise click.BadParameter("Weight must be between 0 and 100")
    else:
        return value


@click_cli.command("traffic", help="""Print or update stack traffic weights of a StackSet.""")
@click.option(
    "--force",
    "-f",
    help="Flag to force the traffic change without waiting for the stackset controller",
    default=False,
    is_flag=True,
)
@click.option(
    "--no-wait", help="Flag to avoid waiting for the traffic switching to finish", default=False, is_flag=True
)
@click.option(
    "--timeout",
    "-t",
    help="Duration, in seconds, to wait for traffic switching to finish",
    default=600,
    required=False,
    type=int,
)
@click.argument("stackset_name", required=True)
@click.argument("stack", required=False)
@click.argument("weight", required=False, type=float, callback=_validate_weight)
@click.pass_obj
def traffic(env: Environment, force, no_wait, timeout, stackset_name, stack, weight):
    kube_config.update_token(env)

    try:
        if stack is None:
            bluegreen = zalando_kubectl.traffic.get_bluegreen(env.kubectl, stackset_name)

            if not bluegreen.get_traffic():
                raise click.UsageError("No traffic information found for {} {}".format(type(bluegreen), stackset_name))

            zalando_kubectl.traffic.print_traffic(env.kubectl, bluegreen)

        elif weight is None:
            raise click.UsageError("You must specify the new weight")

        else:
            bluegreen = zalando_kubectl.traffic.get_bluegreen(env.kubectl, stackset_name)
            bluegreen.set_traffic_weight(stack, weight)
            if type(bluegreen) == StackSetIngressAuthoritative and force:
                bluegreen.force_traffic_weight()

            zalando_kubectl.traffic.kubectl_run(env.kubectl, *bluegreen.get_traffic_cmd())

            timeout_param = 0 if no_wait else timeout
            zalando_kubectl.traffic.print_traffic(env.kubectl, bluegreen, timeout_param)

    except subprocess.CalledProcessError as e:
        click_exc = click.ClickException(e.stderr.decode("utf-8"))
        click_exc.exit_code = e.returncode
        raise click_exc


@click_cli.command(
    "generate",
    help="""Generate boilerplate of kubernetes manifests. Implemented types:

    - deployment # generate deployment resource with CLI input

    - fabric     # generate fabricgateway resource with CLI input and from API repository

    - ingress    # generate ingress resource with CLI input

    - stackset   # generate stackset resource with CLI input
""",
)
@click.argument("typ", required=True)
@click.option(
    "--application",
    "-a",
    help="Application ID",
    required=True,
)
@click.option(
    "--component",
    "-c",
    help="Component to add as label",
    required=False,
)
@click.option(
    "--host",
    help="Ingress hosts as comma separated list, that will be exposed by DNS",
    required=False,
)
@click.option(
    "--backendport",
    help="Ingress backendport to generate your Ingress with service",
    required=False,
)
@click.option(
    "--scopes",
    help="Ingress tokeninfo scopes as comma separated list to allow to access (defaults to uid, which means all valid zalando employees and services)",
    required=False,
)
@click.option(
    "--ui",
    help="Ingresss to a UI Application for employees",
    required=False,
    is_flag=True,
)
@click.option(
    "--team",
    "-t",
    help="Radical Agility Team name that is used to find team members to generate fabricgateway admin access",
    required=False,
)
@click.option(
    "--file",
    "-f",
    help="File to OpenAPI Spec to generate fabricgateway",
    required=False,
)
@click.option(
    "--image",
    help="docker image",
    required=False,
)
@click.option(
    "--cpu",
    help="CPU resource requests",
    required=False,
)
@click.option(
    "--memory",
    help="Memory resource requests",
    required=False,
)
@click.option(
    "--cluster",
    help="Cluster Alias name for example: 'fashion-store'",
    required=False,
)
@click.option(
    "--config",
    help="generate configmap",
    required=False,
    is_flag=True,
)
@click.option(
    "--secret",
    help="generate static secret config",
    required=False,
    is_flag=True,
)
@click.option(
    "--autoscaling",
    help="generate horizontal pod autoscaling",
    required=False,
    is_flag=True,
)
@click.option(
    "--mock",
    help="generate mock response for fabric from your OpenAPI Spec",
    required=False,
    is_flag=True,
)
@click.option(
    "--debug",
    "-d",
    help="Enable debug",
    required=False,
    is_flag=True,
)
@click.pass_obj
def generate(
    env: Environment,
    typ,
    application,
    component,
    host,
    backendport,
    scopes,
    ui,
    team,
    file,
    image,
    cpu,
    memory,
    cluster,
    config,
    secret,
    autoscaling,
    mock,
    debug,
):
    try:
        if typ is None:
            raise click.UsageError("No typ information found")

        if application is None:
            raise click.UsageError("You must specify the application")

        if typ == "fabric":
            token = auth_token()
            gen.fabric(token, application, component, team, backendport, file, mock, debug)

        elif typ == "ingress":
            if not host:
                raise click.UsageError("--host required for ingress")
            gen.ingress(application, component, team, host, backendport, scopes, ui, debug)

        elif typ == "deployment":
            gen.deployment(
                application,
                component,
                team,
                backendport,
                scopes,
                image,
                cpu,
                memory,
                cluster,
                config,
                secret,
                autoscaling,
                debug,
            )

        elif typ == "stackset":
            if not host:
                raise click.UsageError("--host required for stackset")
            gen.stackset(
                application,
                component,
                team,
                host,
                backendport,
                scopes,
                image,
                cpu,
                memory,
                cluster,
                config,
                secret,
                ui,
                autoscaling,
                debug,
            )

        else:
            raise click.UsageError("Wrong typ information found: {}".format(typ))

    except subprocess.CalledProcessError as e:
        click_exc = click.ClickException(e.stderr.decode("utf-8"))
        click_exc.exit_code = e.returncode
        raise click_exc


@click_cli.group(
    name="cluster-update",
    cls=DecoratingGroup,
    context_settings=CONTEXT_SETTINGS,
    help="Cluster update related commands",
)
def cluster_update():
    pass


@cluster_update.command("status")
@click.pass_obj
def cluster_update_status(env: Environment):
    """Show the cluster update status"""
    registry_url = get_registry_url(env.config)
    cluster_alias = utils.get_cluster_alias(env)
    cluster_metadata = registry.get_cluster_with_params(registry_url, verbose=True, alias=cluster_alias)

    update_block_reason = cluster_metadata.get("config_items", {}).get(UPDATE_BLOCK_CONFIG_ITEM)
    if update_block_reason is not None:
        clickclick.warning("Cluster updates for {} are blocked: {}".format(cluster_alias, update_block_reason))
    else:
        status = cluster_metadata.get("status", {})
        current_version = status.get("current_version")
        next_version = status.get("next_version")

        if next_version and next_version != current_version:
            clickclick.warning("Cluster {} is being updated".format(cluster_alias))
        else:
            print("Cluster {} is up-to-date".format(cluster_alias))


@cluster_update.command("block")
@click.pass_obj
def block_cluster_update(env: Environment):
    """Block the cluster from updating"""
    registry_url = get_registry_url(env.config)
    current_cluster = kube_config.get_context(env)
    cluster_metadata = registry.get_cluster_with_params(registry_url, verbose=True, alias=current_cluster)

    current_reason = cluster_metadata.get("config_items", {}).get(UPDATE_BLOCK_CONFIG_ITEM)
    if current_reason is not None:
        if not click.confirm("Cluster updates already blocked: {}. Overwrite?".format(current_reason)):
            return

    reason = click.prompt("Blocking cluster updates for {}, reason".format(current_cluster))
    reason = "{} ({})".format(reason, current_user())

    registry.update_config_item(registry_url, cluster_metadata["id"], UPDATE_BLOCK_CONFIG_ITEM, reason)
    print("Cluster updates blocked")


@cluster_update.command("unblock")
@click.pass_obj
def unblock_cluster_update(env: Environment):
    """Allow updating the cluster"""
    registry_url = get_registry_url(env.config)
    current_cluster = kube_config.get_context(env)
    cluster_metadata = registry.get_cluster_with_params(registry_url, verbose=True, alias=current_cluster)

    current_reason = cluster_metadata.get("config_items", {}).get(UPDATE_BLOCK_CONFIG_ITEM)
    if current_reason is not None:
        if click.confirm("Cluster update for {} was blocked: {}. Unblock?".format(current_cluster, current_reason)):
            registry.delete_config_item(registry_url, cluster_metadata["id"], UPDATE_BLOCK_CONFIG_ITEM)
            print("Cluster updates unblocked")
    else:
        print("Cluster updates aren't blocked")


@click_cli.command("tunnel")
@click.option("--address", help="Addresses to listen on (comma separated), similar to kubectl port-forward")
@click.argument("target", required=True)
@click.argument("ports", required=True, nargs=-1, type=PortMappingParamType())
@click.pass_obj
def tunnel(env: Environment, address, target, ports):
    """Forward a local port to a remote endpoint through the cluster.

    The command starts a socat pod in your cluster that forwards a port to
    your specified target host and port.

    It then uses kubectl port-forward to forward a local port to the pod in
    your cluster, thus allowing you to tunnel to your destination.

    For example, a non-public RDS instance that is accessible by pods in your
    cluster can be made available on localhost by using the following command:

        $ zkubectl tunnel database-1...eu-central-1.rds.amazonaws.com 5432

    You can then use `psql -h 127.0.0.1 -U postgres` to connect to it.

    The ports argument supports the same syntax as kubectl. That means you can
    tunnel through multiple ports and remap them on your local host.

    Tunnel to google.com via local ports 80 and 443:

        $ zkubectl tunnel google.com 80 443

    Tunnel to google.com's 80 and 443 via local ports 8080 and 8443:

        $ zkubectl tunnel google.com 8080:80 8443:443

    Usage:

        $ zkubectl tunnel TARGET [LOCAL_PORT:]REMOTE_PORT [...[LOCAL_PORT_N:]REMOTE_PORT_N]
    """

    # Check if local ports are already in use
    for i, port in enumerate(ports):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", int(port[0]))) == 0:
                raise click.UsageError("Port {} already in use".format(port[0]))

    # the name of the job is different for each invocation
    # it gets cleaned up when the command exists
    job_name = "port-forwarder-{}".format(uuid.uuid4())
    # the intermediate port in the proxy pod
    base_port = 4180
    # the time in seconds after which the port forwarding job gets terminated and cleaned up
    timeout = 3600

    # remove any resources we created when shutting down
    @atexit.register
    def remove_pods():
        cmdline = ("delete", "job", job_name, "--ignore-not-found")
        env.kubectl.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def signal_handler(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)

    # refresh token
    kube_config.update_token(env)

    # generate socat container specs for each port
    containers = generate_containers(target, ports, base_port, timeout)

    # template of the job to apply
    job_spec = generate_job(containers, job_name, timeout)

    # submit the job to kubernetes
    cmdline = ("apply", "-f", "-")
    env.kubectl.run(cmdline, check=True, input=bytes(yaml.dump(job_spec), "utf-8"), stdout=subprocess.PIPE)

    # get the readiness status of the proxy pod
    cmdline = (
        "get",
        "pods",
        "-l",
        "job-name={}".format(job_name),
        "-o",
        "jsonpath=\"{.items[*].status.conditions[?(@.type=='Ready')].status}\"",
    )

    # retry until the pod is up and ready
    with Action("Waiting for proxy pod to be ready..") as act:
        while True:
            pod_status = (
                env.kubectl.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                .stdout.decode("utf-8")
                .strip()
            )
            if pod_status == '"True"':
                break
            act.progress()
            time.sleep(1)

    # find the name of the created proxy pod
    cmdline = ("get", "pods", "-l", "job-name={}".format(job_name), "-o", "name")
    pod_name = (
        env.kubectl.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        .stdout.decode("utf-8")
        .strip()
    )

    info("You can now connect to {} via {} ..".format(target, address if address else "127.0.0.1"))

    # port-forward to the pod
    cmdline = ["port-forward", pod_name]
    if address:
        cmdline.append("--address={}".format(address))
    for i, port in enumerate(ports):
        local_port = port[0]
        cmdline += ["{}:{}".format(local_port, base_port + i)]

    env.kubectl.run(cmdline, check=True, stdout=subprocess.PIPE)


def latest_socat_image():
    docker_registry = "container-registry.zalando.net"
    team = "teapot"
    artifact = "socat"

    token = auth_token()

    response = requests.get(
        "https://{}/v2/{}/{}/tags/list".format(docker_registry, team, artifact),
        timeout=10,
        headers={"Authorization": "Bearer {}".format(token)},
    )
    response.raise_for_status()

    image = response.json()

    return "{}/{}/{}:{}".format(docker_registry, team, artifact, sorted(image["tags"])[-1])


def generate_containers(target, ports, base_port, timeout):
    containers = []
    socat_image = latest_socat_image()

    for i, port in enumerate(ports):
        local_port = base_port + i
        remote_port = port[-1]
        containers.append(generate_container(target, local_port, remote_port, socat_image, timeout))

    return containers


def generate_container(target, local_port, remote_port, socat_image, timeout):
    return {
        "name": "socat-{}".format(remote_port),
        "image": socat_image,
        "args": [
            "-d",
            "-d",
            "TCP-LISTEN:{},fork,bind=0.0.0.0".format(local_port),
            "TCP:{}:{}".format(target, remote_port),
        ],
        "env": [
            {
                "name": "TIMEOUT",
                "value": str(timeout),
            }
        ],
        "resources": {"limits": {"cpu": "10m", "memory": "128Mi"}},
        "securityContext": {
            "runAsNonRoot": True,
            "runAsUser": 65534,
            "readOnlyRootFilesystem": True,
            "capabilities": {"drop": ["ALL"]},
        },
    }


def generate_job(containers, name, timeout):
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": name,
            "labels": {"application": "teapot-port-forward"},
            "annotations": {"janitor/ttl": "{}s".format(timeout)},
        },
        "spec": {
            "activeDeadlineSeconds": timeout,
            "backoffLimit": 0,
            "ttlSecondsAfterFinished": 0,
            "template": {
                "metadata": {"labels": {"application": "teapot-port-forward"}},
                "spec": {"automountServiceAccountToken": False, "restartPolicy": "Never", "containers": containers},
            },
        },
    }


def print_help(ctx):
    click.secho("Zalando Kubectl {}\n".format(zalando_kubectl.APP_VERSION), bold=True)

    formatter = ctx.make_formatter()
    click_cli.format_commands(ctx, formatter)
    print(formatter.getvalue().rstrip("\n"))

    click.echo("")
    click.echo("All other commands are forwarded to kubectl:\n")
    ctx.obj.kubectl.exec("--help")


@click_cli.command("help")
@click.pass_context
def show_help(ctx):
    """Show the help message and exit"""
    print_help(ctx)
    sys.exit(0)


@click_cli.command("init")
@click.argument("directory", nargs=-1)
@click.option(
    "-t", "--template", help="Use a custom template (default: webapp)", metavar="TEMPLATE_ID", default="webapp"
)
@click.option("--from-senza", help="Convert Senza definition", type=click.File("r"), metavar="SENZA_FILE")
@click.option("--kubernetes-cluster")
@click.pass_obj
def init(env: Environment, directory, template, from_senza, kubernetes_cluster):
    """Initializes a new deploy folder with default Kubernetes manifests and
    CDP configuration.

    You can choose a different template using the '-t' option and specifying
    one of the following templates:

    webapp  - Default template with a simple public facing web application
              configured with rolling updates through CDP;

    traffic - Public facing web application configured for blue/green
              deployments, enabling traffic switching;

    senza   - Used for migrating a Senza definition file. You can use
              --from-senza directly instead.
    """
    if directory:
        path = Path(directory[0])
    else:
        path = Path(".")

    if from_senza:
        variables = read_senza_variables(from_senza)
        template = "senza"
    else:
        variables = {}

    if kubernetes_cluster:
        cluster_id = kubernetes_cluster
    else:
        info("Please select your target Kubernetes cluster")
        clusters = do_list_clusters(env.config)
        valid_cluster_names = list(chain.from_iterable((c["id"], c["alias"]) for c in clusters))
        cluster_id = ""
        while cluster_id not in valid_cluster_names:
            cluster_id = click.prompt("Kubernetes Cluster ID to use")

    variables["cluster_id"] = cluster_id

    template_path = Path(__file__).parent / "templates" / template
    variables = prepare_variables(variables)
    copy_template(template_path, path, variables)

    print()

    notes = path / "NOTES.txt"
    with notes.open() as fd:
        print(fd.read())


@click_cli.group(
    name="cluster-access",
    cls=DecoratingGroup,
    context_settings=CONTEXT_SETTINGS,
    help="Manual/emergency access related commands",
)
def cluster_access():
    pass


def cluster_access_check_environment(env: Environment):
    try:
        registry_url = get_registry_url(env.config)
        cluster_metadata = registry.get_cluster_with_params(registry_url, alias=utils.get_cluster_alias(env))
        if cluster_metadata["environment"] == "test":
            raise ClusterAccessUnsupported("Cluster access requests are not needed in test clusters")
    except ClusterAccessUnsupported:
        raise
    except Exception as e:
        # We don't want to prevent the users from using these commands if CR is down
        clickclick.warning("Unable to verify cluster environment: {}".format(e))


@cluster_access.command("request")
@click.option("--emergency", is_flag=True, help="Request emergency access to the cluster")
@click.option(
    "--okta-auth-client-id",
    help="Okta client ID to use for authentication (only use if Cluster Registry is unavailable)",
)
@click.option(
    "--account-name", help="The name of the account to request access for (only use if Cluster Registry is unavailable)"
)
@click.option("-i", "--incident", help="Opsgenie incident number or URL, [required] with --emergency", type=str)
@click.option("--wait-for-approval/--no-wait-for-approval", default=True, help="Block until access is approved")
@click.option(
    "-t",
    "--timeout",
    help="Duration, in seconds, to wait for the request to be approved",
    default=600,
    required=False,
    type=int,
)
@click.option(
    "--force-new-request/--no-force-new-request",
    default=False,
    help="Create new privileged access request even if there is already one pending/approved/expired",
)
@click.argument("reason", nargs=-1, required=True)
@click.pass_obj
def request_cluster_access(
    env: Environment,
    emergency,
    incident,
    reason,
    okta_auth_client_id,
    account_name,
    wait_for_approval,
    timeout,
    force_new_request,
):
    """Request access to the cluster"""
    cluster_access_check_environment(env)

    if emergency:
        if not incident:
            raise click.UsageError("You must specify an incident ticket [--incident] when requesting emergency access")
        if incident.startswith("https://"):
            reference_url = incident
        elif incident.startswith("INC-"):
            reference_url = "https://jira.zalando.net/browse/" + incident
        elif incident.isdigit():
            # This way we can be sort of compatible with both old and new incident processes
            reference_url = "https://jira.zalando.net/browse/INC-" + incident
        elif re.fullmatch(r"\w+-\w+-\w+-\w+-\w+", incident):
            reference_url = "https://zalando.app.opsgenie.com/incident/detail/" + incident
        elif re.fullmatch(r"\w+-\w+-\w+-\w+-\w+-\d+", incident):
            reference_url = "https://zalando.app.opsgenie.com/alert/show/" + incident
        else:
            raise click.UsageError("You must provide a valid incident number or ID, alert ID or an Opsgenie URL")
        make_emergency_access_request(
            env, reference_url, reason, okta_auth_client_id, account_name, wait_for_approval, timeout, force_new_request
        )
    else:
        make_manual_access_request(
            env, reason, okta_auth_client_id, account_name, wait_for_approval, timeout, force_new_request
        )


def make_emergency_access_request(
    env: Environment,
    reference_url,
    reason,
    okta_auth_client_id,
    account_name,
    wait_for_approval,
    timeout,
    force_new_request,
):
    access_request.create_with_okta(
        env,
        "emergency",
        reference_url,
        " ".join(reason),
        okta_auth_client_id,
        account_name,
        wait_for_approval,
        timeout,
        force_new_request,
    )


def make_manual_access_request(
    env: Environment, reason, okta_auth_client_id, account_name, wait_for_approval, timeout, force_new_request
):
    access_request.create_with_okta(
        env,
        "privileged",
        None,
        " ".join(reason),
        okta_auth_client_id,
        account_name,
        wait_for_approval,
        timeout,
        force_new_request,
    )


@cluster_access.command("approve")
@click.argument("request_key", required=True)
@click.option("--okta-auth-client-id", help="Okta client ID to use for authentication")
@click.option("--yes/--no-yes", default=False, help="Approve the given access request without prompting again.")
@click.pass_obj
def approve_access_request(env: Environment, request_key, okta_auth_client_id, yes):
    """Approve a manual access request

    REQUEST_KEY is the request_key to approve access for.
    """
    cluster_access_check_environment(env)

    access_request.approve_with_okta(env, request_key, okta_auth_client_id, yes)


@cluster_access.command("list")
@click.option("--request-key", help="The request key that identifies your privileged access request")
@click.option(
    "--okta-auth-client-id",
    help="Okta client ID to use for authentication (only use if Cluster Registry is unavailable)",
)
@click.option(
    "--account-name", help="The name of the account to list requests for (only use if Cluster Registry is unavailable)"
)
@click.option(
    "-o", "--output", type=click.Choice(["text", "json"]), default="text", help="Command output format (default: text)"
)
@click.pass_obj
def list_cluster_requests(env: Environment, request_key, okta_auth_client_id, account_name, output):
    """List all current pending/approved access requests for the cluster"""
    cluster_access_check_environment(env)

    access_request.list_with_okta(env, request_key, okta_auth_client_id, account_name, output)


@click_cli.command("restart-pods", help="Restart all pods in a deployment.")
@click.argument("target")
@click.pass_obj
def restart_pods(env: Environment, target):
    deployment = Deployment(env.kubectl, name=target)
    annotation_id = str(uuid.uuid4())
    if deployment.ss_ref():
        target_obj = deployment.get_stackset()
    else:
        target_obj = deployment

    target_obj.annotate_restart(annotation_id)
    print("Successfully patched {} for restart".format(target))


@click_cli.command(
    "delete",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
    add_help_option=False,
)
@click.option("--all", is_flag=False, flag_value="true")
@click.pass_context
def kubectl_delete(ctx, all):
    if all:
        print("delete --all is disabled", file=sys.stderr)
        sys.exit(1)

    kube_config.update_token(ctx.obj)
    ctx.obj.kubectl.exec(*sys.argv[1:])


@click_cli.command(
    "edit",
    help="Edit a resource on the server",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
    add_help_option=False,
)
@click.option("--no-diff", is_flag=True)
@click.pass_context
def kubectl_edit(ctx, no_diff):
    args, env = sys.argv[1:], os.environ.copy()

    if no_diff:
        args.remove("--no-diff")
    else:
        if "KUBE_EDITOR" in env:
            env["DIFFEDIT_EDITOR"] = env["KUBE_EDITOR"]

        print("Using zkubectl diffedit as KUBE_EDITOR, disable via --no-diff", file=sys.stderr)
        env["KUBE_EDITOR"] = "zkubectl diffedit"

    kube_config.update_token(ctx.obj)
    ctx.obj.kubectl.exec(*args, env=env)


@click_cli.command(
    "diffedit", help="Edit a file and show a diff of the changes. It is suitable for use as KUBE_EDITOR."
)
@click.argument("input_file", required=True)
def diffedit(input_file):
    # split editor to allow extra args, e.g.:
    # export EDITOR="code -w"
    editor = shlex.split(os.getenv("DIFFEDIT_EDITOR", os.getenv("EDITOR", "vi")))

    if not shutil.which("diff"):
        print("diff command not found, please install", file=sys.stderr)
        subprocess.run(editor + [input_file], check=True, env=os.environ.copy())
        return

    # reuse input file extension to enable editor syntax highlighting
    _, ext = os.path.splitext(input_file)
    copy_file = tempfile.mktemp(suffix=ext)

    shutil.copyfile(input_file, copy_file)

    subprocess.run(editor + [copy_file], check=True, env=os.environ.copy())

    diff_result = subprocess.run(["diff", "--color", "-u3", input_file, copy_file], env=os.environ.copy())
    if diff_result.returncode != 0:
        if input("Apply changes? [yes/no]: ").strip().lower() in ["yes", "y"]:
            os.rename(copy_file, input_file)


def find_cmd(cmdline):
    while len(cmdline) > 0:
        if any(cmdline[0].startswith(flag) for flag in ("-n", "--namespace", "--context")):
            if "=" in cmdline[0]:
                cmdline = cmdline[1:]
            else:
                cmdline = cmdline[2:]
            continue
        return cmdline[0]
    return None


def check_latest_zkubectl_version():
    app_dir = click.get_app_dir(zalando_kubectl.APP_NAME)
    f = os.path.join(app_dir, "last_update_check")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    if not os.path.exists(f):
        Path(f).touch()
    last_modified = datetime.datetime.fromtimestamp(os.stat(f).st_mtime)
    time_delta = datetime.datetime.now() - last_modified
    if time_delta.days < 1:
        return

    # We don't want to keep trying if a check fails, it's fine to retry tomorrow
    Path(f).touch()

    resp = requests.get("https://pypi.org/pypi/zalando-kubectl/json", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    latest_release_version = "v" + data["info"]["version"]
    if latest_release_version != zalando_kubectl.APP_VERSION:
        clickclick.warning(
            "You are not running the latest version of zkubectl (current version: {}, latest version: {})."
            " Please update zkubectl via `pipx upgrade zalando-kubectl`.".format(
                zalando_kubectl.APP_VERSION, latest_release_version
            )
        )


def debug_print_exc():
    if "ZKUBECTL_DEBUG" in os.environ:
        import traceback

        traceback.print_exc()


def main():
    def cleanup_fds():
        # Python tries to flush stdout/stderr on exit, which prints annoying stuff if we get
        # a SIGPIPE because we're piping to head/grep/etc.
        # Close the FDs explicitly and swallow BrokenPipeError to get rid of the exception.
        try:
            sys.stdout.close()
            sys.stderr.close()
        except BrokenPipeError:
            sys.exit(141)

    atexit.register(cleanup_fds)

    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            check_latest_zkubectl_version()
        # Only inform users to update zkubectl
        except Exception as e:
            clickclick.error("Unable to check for updates: {}".format(e))

    try:
        # We need a dummy context to make Click happy
        ctx = click_cli.make_context(sys.argv[0], [], resilient_parsing=True)

        cmd = find_cmd(sys.argv[1:])

        if cmd in click_cli.commands:
            click_cli()
        elif not cmd or cmd in click_cli.get_help_option_names(ctx):
            print_help(ctx)
        else:
            kube_config.update_token(ctx.obj)
            ctx.obj.kubectl.exec(*sys.argv[1:])
    except KeyboardInterrupt:
        debug_print_exc()
        pass
    except BrokenPipeError:
        debug_print_exc()
        sys.exit(141)
    except Exception as e:
        debug_print_exc()
        clickclick.error(e)
        sys.exit(1)
