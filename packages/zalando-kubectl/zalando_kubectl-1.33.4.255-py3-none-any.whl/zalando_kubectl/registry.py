import json
import requests
from zalando_kubectl.utils import auth_headers


def get_account_with_id(cluster_registry_url: str, account_id: str):
    """Return the full definition of the account with the provided ID. Throw exception if no accounts are found."""
    response = requests.get(
        "{}/infrastructure-accounts/{}".format(cluster_registry_url, account_id),
        headers=auth_headers(),
        timeout=10,
    )
    if response.status_code == 404:
        raise Exception(
            "Infrastructure account {} not found in Cluster Registry. Is the id correct?".format(account_id)
        )
    response.raise_for_status()
    return response.json()


def get_cluster_with_id(cluster_registry_url: str, cluster_id: str, verbose=False):
    """Return the full definition of the cluster with the provided ID. Throw exception if no clusters are found."""
    response = requests.get(
        "{}/kubernetes-clusters/{}".format(cluster_registry_url, cluster_id),
        params={"verbose": json.dumps(verbose)},
        headers=auth_headers(),
        timeout=10,
    )
    if response.status_code == 404:
        raise Exception("Kubernetes cluster {} not found in Cluster Registry. Is the id correct?".format(cluster_id))
    response.raise_for_status()
    return response.json()


def get_cluster_with_params(cluster_registry_url: str, verbose=False, **params: str):
    """Return the full definition of a cluster with arbitrary parameters. Throw if no clusters are found."""
    full_params = dict(**params)
    full_params.update(verbose=json.dumps(verbose))
    response = requests.get(
        "{}/kubernetes-clusters".format(cluster_registry_url), params=full_params, headers=auth_headers(), timeout=10
    )
    response.raise_for_status()
    data = response.json()

    if not data["items"]:
        params_desc = ", ".join(params.values())
        raise Exception("Kubernetes cluster {} not found in Cluster Registry. Is the name correct?".format(params_desc))

    return data["items"][0]


def get_cluster_by_id_or_alias(cluster_registry_url: str, id_or_alias: str, verbose=False):
    if len(id_or_alias.split(":")) >= 3:
        # looks like a Cluster ID (aws:123456789012:eu-central-1:kube-1)
        return get_cluster_with_id(cluster_registry_url, id_or_alias, verbose=verbose)
    else:
        return get_cluster_with_params(cluster_registry_url, alias=id_or_alias, verbose=verbose)


def _check_response_status(response):
    if response.status_code == 403:
        raise Exception("Access denied, please request the Production Deployer role in ZACK")
    response.raise_for_status()


def update_config_item(registry_url, cluster_id, config_item, value):
    """Set the value of a config item"""
    url = "{}/kubernetes-clusters/{}/config-items/{}".format(registry_url, cluster_id, config_item)
    response = requests.put(url, json={"value": value}, headers=auth_headers(), timeout=10)
    _check_response_status(response)


def delete_config_item(registry_url, cluster_id, config_item):
    """Delete a config item"""
    url = "{}/kubernetes-clusters/{}/config-items/{}".format(registry_url, cluster_id, config_item)
    response = requests.delete(url, headers=auth_headers(), timeout=10)
    _check_response_status(response)
