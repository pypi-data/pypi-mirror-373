import copy
import json
import os
import tempfile
import yaml

from subprocess import PIPE
from zalando_kubectl.utils import Environment, auth_token
import zalando_kubectl.access_request


KUBECONFIG = os.path.expanduser("~/.kube/config")
KUBE_USER = "zalando-token"
AUTH_API_VERSION = "client.authentication.k8s.io/v1beta1"


def update(url, alias, okta_auth_client_id, token, ca=None):
    name = alias or generate_name(url)
    config = read_config()

    username = KUBE_USER
    config_users = [{"name": KUBE_USER, "user": {"token": token}}]

    username = f"okta-{alias}"
    config_users = [
        {
            "name": username,
            "user": {
                "exec": {
                    "apiVersion": AUTH_API_VERSION,
                    "command": "zkubectl",
                    "args": ["credentials", name, "--okta-auth-client-id", okta_auth_client_id],
                }
            },
        }
    ]

    cluster = {"server": url}
    if ca is not None:
        cluster["certificate-authority-data"] = ca

    new_config = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": [{"name": name, "cluster": cluster}],
        "users": config_users,
        "contexts": [{"name": name, "context": {"cluster": name, "user": username}}],
        "current-context": name,
    }

    updated_config = merge_config(config, new_config)
    if updated_config != config:
        write_config(updated_config)

    return updated_config


def get_auth(env: Environment, okta_auth_client_id, force_refresh=False, stdout=None, stderr=None):
    oidc_issuer_url = get_okta_auth_url(env.config)
    cmd = [
        "get-token",
        f"--oidc-issuer-url={oidc_issuer_url}",
        f"--oidc-client-id={okta_auth_client_id}",
        "--oidc-extra-scope=email",
        "--oidc-extra-scope=offline_access",
    ]
    if force_refresh:
        cmd.append("--force-refresh")

    return env.kubelogin.run(cmd, stdout=stdout, stderr=stderr, forward_context=False, forward_namespace=False)


def get_okta_auth_url(config):
    try:
        return config["okta_auth"].rstrip("/")
    except KeyError:
        raise Exception("Okta auth URL missing, please reconfigure zkubectl by running `zalando-cli-bundle configure`")


def get_auth_token(env, alias, okta_auth_client_id, force_refresh=False):
    cmd = get_auth(env, okta_auth_client_id, force_refresh, stdout=PIPE, stderr=PIPE)
    stderr = cmd.stderr.decode("utf-8")
    if len(stderr) > 0 and "error" in stderr:
        if "access_denied User is not assigned to the client application." in stderr:
            stderr = f"No roles found for cluster '{alias}'. Please request a role: https://cloud.docs.zalando.net/reference/access-roles/#saviynt-access-roles"
        raise Exception(f"Error getting token: {stderr}")

    token_bytes = cmd.stdout
    return json.loads(token_bytes.decode("utf-8"))["status"]["token"]


def is_okta_user():
    config = read_config()
    try:
        for c in config["contexts"]:
            if c["name"] == config["current-context"]:
                return "okta" in c["context"]["user"]
        return False
    except KeyError:
        return False


def update_token(env):
    if is_okta_user():
        current_cluster = get_current_context()
        if zalando_kubectl.access_request._has_any_state_file(current_cluster):
            okta_auth_client_id = get_okta_auth_client_id(env, current_cluster)
            get_auth_token(env, current_cluster, okta_auth_client_id, True)
        return

    raise Exception("Not an okta user, cannot update token")


def write_config(config):
    os.makedirs(os.path.dirname(KUBECONFIG), exist_ok=True)
    new_fp, new_file = tempfile.mkstemp(prefix="config", dir=os.path.dirname(KUBECONFIG))
    try:
        with open(new_fp, mode="w", closefd=True) as f:
            yaml.safe_dump(config, f)
            f.flush()
    except Exception:
        os.unlink(new_file)
        raise
    else:
        os.rename(new_file, KUBECONFIG)


def generate_name(url):
    url = url.replace("http://", "")
    url = url.replace("https://", "")
    url = url.replace(".", "_")
    url = url.replace("/", "")
    return url


def read_config():
    try:
        with open(KUBECONFIG, "r") as fd:
            data = yaml.safe_load(fd)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def merge_config(config, new_config):
    result = copy.deepcopy(config)
    for key, item in new_config.items():
        if key in ("clusters", "users", "contexts"):
            merge_list(result, key, item)
        else:
            result[key] = item
    return result


def merge_list(config, key, items):
    if key not in config:
        config[key] = items
        return

    if config[key] is None:
        config[key] = []

    existing = {item["name"]: item for item in config[key] if "name" in item}
    for item in items:
        existing_item = existing.get(item["name"])
        if existing_item:
            merge_dict(existing_item, item)
        else:
            config[key].append(item)


def merge_dict(d1, d2):
    for key, value in d2.items():
        if key in d1:
            existing = d1[key]
            if isinstance(existing, dict) and isinstance(value, dict):
                merge_dict(existing, value)
            else:
                d1[key] = value
        else:
            d1[key] = value


def get_current_namespace():
    config = read_config()
    for context in config.get("contexts", []):
        if "current-context" in config and context["name"] == config["current-context"]:
            if "namespace" in context["context"]:
                return context["context"]["namespace"]
    return "default"


def get_current_context():
    config = read_config()
    return config.get("current-context")


def get_context(env: Environment):
    return env.kube_context or get_current_context()


def get_okta_auth_client_id(env, cluster):
    try:
        _, _, okta_auth_client_id, _ = zalando_kubectl.main.login(env.config, cluster)
        return okta_auth_client_id
    except Exception:
        return f"{zalando_kubectl.main.OKTA_AUTH_CLIENT_ID_PREFIX}{cluster}"
