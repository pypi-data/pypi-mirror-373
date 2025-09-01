import unittest.mock
from unittest.mock import MagicMock

import pytest
import requests
from click.testing import CliRunner
from urllib.parse import urlencode

import zalando_kubectl.main
import zalando_kubectl.registry
import zalando_kubectl.utils
import zalando_kubectl.access_request
from zalando_kubectl.main import click_cli
from zalando_kubectl.utils import Environment

from subprocess import CompletedProcess


def expect_success(cli_result, output=None):
    if cli_result.exception:
        raise cli_result.exception
    assert 0 == cli_result.exit_code
    if output is not None:
        assert output == cli_result.output.strip()


def assert_cli_successful(*args, input=None):
    result = CliRunner().invoke(click_cli, args=args, input=input)
    expect_success(result)
    return result


def assert_cli_failed(*args, input=None):
    result = CliRunner().invoke(click_cli, args, input=input)
    assert result.exit_code != 0
    return result


def test_fix_url():
    assert zalando_kubectl.main.fix_url(" api.example.org ") == "https://api.example.org"


def expect_exit_status(monkeypatch, exit_status):
    def mock_exit(status):
        assert status == exit_status

    monkeypatch.setattr("sys.exit", mock_exit)


def test_main(monkeypatch):
    monkeypatch.setattr("zalando_kubectl.utils.ExternalBinary.download", MagicMock())
    monkeypatch.setattr("zalando_kubectl.main.login", MagicMock())
    monkeypatch.setattr("subprocess.call", lambda args: 11)
    monkeypatch.setattr("zalando_kubectl.utils.get_api_server_url", lambda config: "foo,example.org")
    monkeypatch.setattr("zign.api.get_token", MagicMock(return_value="mytok"))
    monkeypatch.setattr("zalando_kubectl.kube_config.update", MagicMock(return_value={}))
    expect_exit_status(monkeypatch, 11)
    assert_cli_failed("get", "pods")


def test_main_completion(monkeypatch):
    mock_download = MagicMock()
    mock_download.return_value = "/path/to/kubectl"
    monkeypatch.setattr("zalando_kubectl.utils.ExternalBinary.download", mock_download)
    monkeypatch.setattr("zalando_kubectl.utils.ExternalBinary.exists", lambda self: True)
    mock_run = MagicMock()
    mock_run.return_value.stdout = b"kubectl is sort of okay"
    mock_run.return_value.wait.return_value = 0
    monkeypatch.setattr("subprocess.run", mock_run)

    result = assert_cli_successful("completion", "bash")
    expect_success(result, "zkubectl is sort of okay")


def test_login(monkeypatch):
    cluster_registry = "https://cluster-registry.example.org"
    config = {"cluster_registry": cluster_registry}

    store_config = MagicMock()
    monkeypatch.setattr("stups_cli.config.load_config", lambda x: config)
    monkeypatch.setattr("stups_cli.config.store_config", store_config)

    api_url = "https://my-cluster.example.org"

    mock_cluster = {"api_server_url": api_url, "alias": "my-alias", "provider": "zalando-aws"}

    def get_cluster_with_id(cluster_registry_url, cluster_id, verbose=False):
        assert cluster_registry_url == cluster_registry
        assert cluster_id == "aws:123:eu-west-1:my-kube-1"
        assert not verbose
        return mock_cluster

    def get_cluster_with_params(cluster_registry_url, verbose=False, **params):
        assert cluster_registry_url == cluster_registry
        assert params == {"alias": "my-alias"}
        assert not verbose
        return mock_cluster

    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_id", get_cluster_with_id)
    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_params", get_cluster_with_params)
    monkeypatch.setattr("zalando_kubectl.main.configure_zdeploy", lambda cluster: None)

    url, alias, okta_auth_client_id, ca = zalando_kubectl.main.login(config, "aws:123:eu-west-1:my-kube-1")
    assert api_url == url
    assert alias == "my-alias"
    assert okta_auth_client_id == "kubernetes.cluster.my-alias"
    assert ca is None

    url, alias, okta_auth_client_id, ca = zalando_kubectl.main.login(config, "my-alias.example.org")
    assert "https://my-alias.example.org" == url
    assert alias is None
    assert okta_auth_client_id == "kubernetes.cluster.None"
    assert ca is None

    url, alias, okta_auth_client_id, ca = zalando_kubectl.main.login(config, "my-alias")
    assert api_url == url
    assert alias == "my-alias"
    assert okta_auth_client_id == "kubernetes.cluster.my-alias"
    assert ca is None

    url, alias, okta_auth_client_id, ca = zalando_kubectl.main.login(config, "https://my-alias.example.org")
    assert "https://my-alias.example.org" == url
    assert alias is None
    assert okta_auth_client_id == "kubernetes.cluster.None"
    assert ca is None


def test_login_eks(monkeypatch):
    cluster_registry = "https://cluster-registry.example.org"
    config = {"cluster_registry": cluster_registry}

    store_config = MagicMock()
    monkeypatch.setattr("stups_cli.config.load_config", lambda x: config)
    monkeypatch.setattr("stups_cli.config.store_config", store_config)

    api_url = "https://my-cluster.example.org"
    eks_url = "https://my-eks-cluster.example.org"
    eks_ca = "my-eks-ca"

    mock_cluster = {
        "api_server_url": api_url,
        "alias": "my-eks-alias",
        "provider": "zalando-eks",
        "config_items": {
            "eks_endpoint": eks_url,
            "eks_certificate_authority_data": eks_ca,
        },
    }

    def get_cluster_with_id(cluster_registry_url, cluster_id, verbose=False):
        assert cluster_registry_url == cluster_registry
        assert cluster_id == "aws:123:eu-west-1:my-kube-eks-1"
        return mock_cluster

    def get_cluster_with_params(cluster_registry_url, verbose=False, **params):
        assert cluster_registry_url == cluster_registry
        assert params == {"alias": "my-eks-alias"}
        return mock_cluster

    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_id", get_cluster_with_id)
    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_params", get_cluster_with_params)
    monkeypatch.setattr("zalando_kubectl.main.configure_zdeploy", lambda cluster: None)

    url, alias, okta_auth_client_id, ca = zalando_kubectl.main.login(config, "aws:123:eu-west-1:my-kube-eks-1")
    assert eks_url == url
    assert alias == "my-eks-alias"
    assert okta_auth_client_id == "kubernetes.cluster.my-eks-alias"
    assert ca == eks_ca

    with pytest.raises(zalando_kubectl.main.ClusterAccessUnsupported):
        zalando_kubectl.main.login(config, "my-eks-alias.example.org")

    url, alias, okta_auth_client_id, ca = zalando_kubectl.main.login(config, "my-eks-alias")
    assert eks_url == url
    assert alias == "my-eks-alias"
    assert okta_auth_client_id == "kubernetes.cluster.my-eks-alias"
    assert ca == eks_ca

    with pytest.raises(zalando_kubectl.main.ClusterAccessUnsupported):
        zalando_kubectl.main.login(config, "my-eks-alias.example.org")


def test_login_eks_with_custom_oidc_client_id(monkeypatch):
    cluster_registry = "https://cluster-registry.example.org"
    config = {"cluster_registry": cluster_registry}

    store_config = MagicMock()
    monkeypatch.setattr("stups_cli.config.load_config", lambda x: config)
    monkeypatch.setattr("stups_cli.config.store_config", store_config)

    api_url = "https://my-cluster.example.org"
    eks_url = "https://my-eks-cluster.example.org"
    eks_ca = "my-eks-ca"

    mock_cluster = {
        "api_server_url": api_url,
        "alias": "my-eks-alias",
        "provider": "zalando-eks",
        "config_items": {
            "eks_endpoint": eks_url,
            "eks_certificate_authority_data": eks_ca,
            "okta_auth_client_id": "kubernetes.cluster.bar",
        },
    }

    def get_cluster_with_id(cluster_registry_url, cluster_id, verbose=False):
        assert cluster_registry_url == cluster_registry
        assert cluster_id == "aws:123:eu-west-1:my-kube-eks-1"
        return mock_cluster

    def get_cluster_with_params(cluster_registry_url, verbose=False, **params):
        assert cluster_registry_url == cluster_registry
        assert params == {"alias": "my-eks-alias"}
        return mock_cluster

    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_id", get_cluster_with_id)
    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_params", get_cluster_with_params)
    monkeypatch.setattr("zalando_kubectl.main.configure_zdeploy", lambda cluster: None)

    url, alias, okta_auth_client_id, ca = zalando_kubectl.main.login(config, "aws:123:eu-west-1:my-kube-eks-1")
    assert eks_url == url
    assert alias == "my-eks-alias"
    assert okta_auth_client_id == "kubernetes.cluster.bar"
    assert ca == eks_ca

    with pytest.raises(zalando_kubectl.main.ClusterAccessUnsupported):
        zalando_kubectl.main.login(config, "my-eks-alias.example.org")

    url, alias, okta_auth_client_id, ca = zalando_kubectl.main.login(config, "my-eks-alias")
    assert eks_url == url
    assert alias == "my-eks-alias"
    assert okta_auth_client_id == "kubernetes.cluster.bar"
    assert ca == eks_ca

    with pytest.raises(zalando_kubectl.main.ClusterAccessUnsupported):
        zalando_kubectl.main.login(config, "my-eks-alias.example.org")


def test_login_okta_missing_access(monkeypatch):
    mock_config(monkeypatch)
    mock_get_cluster(
        monkeypatch,
        {
            "environment": "production",
            "api_server_url": "https://kube-1.cluster-x.example.com",
            "alias": "cluster-x",
            "provider": "zalando-aws",
        },
        expected_id="cluster-x",
    )
    monkeypatch.setattr(
        "zalando_kubectl.kube_config.get_auth",
        lambda env, okta_auth_client_id, force_refresh=False, stdout=None, stderr=None: CompletedProcess(
            args=[],
            returncode=1,
            stdout=None,
            stderr="error: get-token: authentication error: authcode-browser error: authentication error: authorization code flow error: oauth2 error: authorization error: authorization error from server: access_denied User is not assigned to the client application.".encode(
                "utf-8"
            ),
        ),
    )

    result = assert_cli_failed("login", "cluster-x")
    assert (
        str(result.exception)
        == "Error getting token: No roles found for cluster 'cluster-x'. Please request a role: https://cloud.docs.zalando.net/reference/access-roles/#saviynt-access-roles"
    )


def test_get_cluster_with_id(monkeypatch):
    mock_cluster = {"api_server_url": "https://my-cluster.example.org"}

    get = MagicMock()
    get.return_value.json.return_value = mock_cluster

    monkeypatch.setattr("zign.api.get_token", lambda x, y: "mytok")
    monkeypatch.setattr("requests.get", get)

    result = zalando_kubectl.registry.get_cluster_with_id("https://cluster-registry.example.org", "my-id")
    assert result == mock_cluster


def test_get_cluster_with_params(monkeypatch):
    mock_cluster = {"api_server_url": "https://my-cluster.example.org"}

    get = MagicMock()
    get.return_value.json.return_value = {"items": [mock_cluster]}

    monkeypatch.setattr("zign.api.get_token", lambda x, y: "mytok")
    monkeypatch.setattr("requests.get", get)

    result = zalando_kubectl.registry.get_cluster_with_params("https://cluster-registry.example.org", alias="my-alias")
    assert result == mock_cluster


def mock_http_post(monkeypatch, expected_url, expected_json, response):
    def mock_fn(url, json=None, **_kwargs):
        assert url == expected_url
        if expected_json:
            assert json == expected_json

        if isinstance(response, Exception):
            raise response
        else:
            result_mock = MagicMock()
            result_mock.raise_for_status.return_value = None
            result_mock.json.return_value = response
            return result_mock

    monkeypatch.setattr("requests.post", mock_fn)


def mock_http_get(monkeypatch, expected_url, expected_json, response):
    def mock_fn(url, json=None, **_kwargs):
        if "params" in _kwargs:
            url = url + "?" + urlencode(_kwargs["params"])
        assert url == expected_url
        if expected_json:
            assert json == expected_json

        if isinstance(response, Exception):
            raise response
        else:
            result_mock = MagicMock()
            result_mock.raise_for_status.return_value = None
            result_mock.json.return_value = response
            return result_mock

    monkeypatch.setattr("requests.get", mock_fn)


def mock_get_username(monkeypatch, _username):
    monkeypatch.setattr("zalando_kubectl.utils.current_user", lambda: _username)
    # replace imported copy as well
    monkeypatch.setattr("zalando_kubectl.main.current_user", lambda: _username)


def test_request_manual_access_no_message(monkeypatch):
    mock_get_cluster(monkeypatch, {"environment": "production"})
    assert_cli_failed("cluster-access", "request")


def mock_get_auth_token(monkeypatch):
    monkeypatch.setattr(
        "zalando_kubectl.kube_config.get_auth_token",
        lambda env, cluster, okta_auth_client_id, force_refresh=False: "YXV0aHRva2VuCg==",
    )


def mock_get_current_context(monkeypatch, context_name):
    monkeypatch.setattr("zalando_kubectl.kube_config.get_current_context", lambda: context_name)


def test_request_manual_access_with_okta_approved(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
        "infrastructure_account": "aws:1234",
    }
    mock_account = {
        "id": "aws:1234",
        "name": "production_account",
    }
    mock_get_cluster(monkeypatch, mock_cluster, expected_id="production_cluster")
    mock_get_account(monkeypatch, mock_account, expected_id="aws:1234")
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")
    zalando_kubectl.access_request._remove_state_file("privileged", "production_cluster")

    expected_json = {
        "access_role": "default",
        "account_name": "production_account",
        "business_justification": "foo bar",
    }
    response = {
        "result": {
            "request_key": "85625",
            "_links": {
                "request_status": {
                    "href": "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625"
                },
                "approval_ui": {"href": "https://zalando-dev.saviyntcloud.com/ECMv6/review/requestApproval/6030927"},
            },
        }
    }
    mock_http_post(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/privileged/cloud-infrastructure/aws/account",
        expected_json,
        response,
    )

    response2 = [
        {
            "request_status": "PROVISIONED",
        }
    ]
    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625",
        None,
        response2,
    )

    assert_cli_successful("cluster-access", "request", "foo", "bar")
    assert not zalando_kubectl.access_request._has_state_file("privileged", "production_cluster")


def test_request_manual_access_with_okta_pending(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
        "infrastructure_account": "aws:1234",
    }
    mock_account = {
        "id": "aws:1234",
        "name": "production_account",
    }
    mock_get_cluster(monkeypatch, mock_cluster, expected_id="production_cluster")
    mock_get_account(monkeypatch, mock_account, expected_id="aws:1234")
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")
    zalando_kubectl.access_request._remove_state_file("privileged", "production_cluster")

    expected_json = {
        "access_role": "default",
        "account_name": "production_account",
        "business_justification": "foo bar",
    }
    response = {
        "result": {
            "request_key": "85625",
            "_links": {
                "request_status": {
                    "href": "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625"
                },
                "approval_ui": {"href": "https://zalando-dev.saviyntcloud.com/ECMv6/review/requestApproval/6030927"},
            },
        }
    }
    mock_http_post(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/privileged/cloud-infrastructure/aws/account",
        expected_json,
        response,
    )

    response2 = [
        {
            "request_status": "PENDING",
        }
    ]
    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625",
        None,
        response2,
    )

    assert_cli_successful("cluster-access", "request", "--timeout", "15", "foo", "bar")
    assert zalando_kubectl.access_request._has_state_file("privileged", "production_cluster")


def test_request_manual_access_with_okta_pending_no_wait_for_approval(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
        "infrastructure_account": "aws:1234",
    }
    mock_account = {
        "id": "aws:1234",
        "name": "production_account",
    }
    mock_get_cluster(monkeypatch, mock_cluster, expected_id="production_cluster")
    mock_get_account(monkeypatch, mock_account, expected_id="aws:1234")
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")
    zalando_kubectl.access_request._remove_state_file("privileged", "production_cluster")

    expected_json = {
        "access_role": "default",
        "account_name": "production_account",
        "business_justification": "foo bar",
    }
    response = {
        "result": {
            "request_key": "85625",
            "_links": {
                "request_status": {
                    "href": "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625"
                },
                "approval_ui": {"href": "https://zalando-dev.saviyntcloud.com/ECMv6/review/requestApproval/6030927"},
            },
        }
    }
    mock_http_post(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/privileged/cloud-infrastructure/aws/account",
        expected_json,
        response,
    )

    response2 = [
        {
            "request_status": "PENDING",
        }
    ]
    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625",
        None,
        response2,
    )

    assert_cli_successful("cluster-access", "request", "--no-wait-for-approval", "foo", "bar")
    assert zalando_kubectl.access_request._has_state_file("privileged", "production_cluster")


def test_list_access_requests_with_okta(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
        "infrastructure_account": "aws:1234",
    }
    mock_account = {
        "id": "aws:1234",
        "name": "production_account",
    }
    mock_get_cluster(monkeypatch, mock_cluster, expected_id="production_cluster")
    mock_get_account(monkeypatch, mock_account, expected_id="aws:1234")
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")

    response = [
        {
            "request_status": "PENDING",
        }
    ]
    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?account_name=production_account",
        None,
        response,
    )
    assert_cli_successful("cluster-access", "list")

    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?account_name=production_account&request_key=85625",
        None,
        response,
    )
    assert_cli_successful("cluster-access", "list", "--request-key", "85625")


def test_approve_manual_access_with_okta(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
    }
    mock_get_cluster(monkeypatch, mock_cluster)
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")

    response = [
        {
            "requestor": "team-velma+privileged-access-pen-test-requestor@zalando.de",
            "account_name": "production_account",
            "business_justification": "foo bar",
            "request_status": "PENDING",
        }
    ]
    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625",
        None,
        response,
    )

    expected_json = {
        "account_name": "production_account",
        "business_justification": "foo bar",
        "access_role": "default",
        "approver_comment": "",
        "decision": "APPROVED",
        "request_key": "85625",
        "requestor": "team-velma+privileged-access-pen-test-requestor@zalando.de",
    }
    mock_http_post(
        monkeypatch,
        "http://access.zalan.do/v1/approve/tech/privileged/cloud-infrastructure/aws/account",
        expected_json,
        None,
    )

    assert_cli_successful("cluster-access", "approve", "--yes", "85625")


def test_approve_manual_access_with_okta_already_approved(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
    }
    mock_get_cluster(monkeypatch, mock_cluster)
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")

    response = [
        {
            "requestor": "team-velma+privileged-access-pen-test-requestor@zalando.de",
            "account_name": "production_account",
            "business_justification": "foo bar",
            "request_status": "PROVISIONED",
        }
    ]
    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625",
        None,
        response,
    )

    expected_json = {
        "account_name": "production_account",
        "business_justification": "foo bar",
        "access_role": "default",
        "approver_comment": "",
        "decision": "APPROVED",
        "request_key": "85625",
        "requestor": "team-velma+privileged-access-pen-test-requestor@zalando.de",
    }
    mock_http_post(
        monkeypatch,
        "http://access.zalan.do/v1/approve/tech/privileged/cloud-infrastructure/aws/account",
        expected_json,
        requests.exceptions.HTTPError(412),
    )

    assert_cli_successful("cluster-access", "approve", "--yes", "85625")


def test_request_manual_access_with_okta_test_cluster(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_get_cluster(monkeypatch, {"environment": "test"})
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "test_cluster")

    assert_cli_failed("cluster-access", "request", "foo", "bar")


def test_request_emergency_access_invalid_incident(monkeypatch):
    mock_get_username(monkeypatch, "username")
    mock_get_cluster(monkeypatch, {"environment": "production"})

    assert_cli_failed("cluster-access", "request", "--emergency", "-i", "FOO")


def test_request_emergency_access_no_message(monkeypatch):
    mock_get_username(monkeypatch, "username")
    mock_get_cluster(monkeypatch, {"environment": "production"})

    assert_cli_failed("cluster-access", "request", "--emergency", "-i", "1234")


def test_request_emergency_access_no_incident(monkeypatch):
    mock_get_username(monkeypatch, "username")
    mock_get_api_server_url(monkeypatch)
    mock_get_cluster(monkeypatch, {"environment": "production"})

    assert_cli_failed("cluster-access", "request", "--emergency", "foo", "bar")


def test_request_emergency_access_with_okta_approved(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
        "infrastructure_account": "aws:1234",
    }
    mock_account = {
        "id": "aws:1234",
        "name": "production_account",
    }
    mock_get_cluster(monkeypatch, mock_cluster, expected_id="production_cluster")
    mock_get_account(monkeypatch, mock_account, expected_id="aws:1234")
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")
    reference_url = "https://zalando.app.opsgenie.com/alert/detail/a6f295c8-9518-4427-a4ff-000000000-000000000/details"
    zalando_kubectl.access_request._remove_state_file("emergency", "production_cluster")

    expected_json = {
        "access_role": "default",
        "account_name": "production_account",
        "business_justification": "foo bar",
        "reference_url": reference_url,
    }
    response = {
        "result": {
            "request_key": "85625",
            "_links": {
                "request_status": {
                    "href": "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625"
                },
            },
        }
    }
    mock_http_post(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/emergency/cloud-infrastructure/aws/account",
        expected_json,
        response,
    )

    response2 = [
        {
            "request_status": "PROVISIONED",
        }
    ]
    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625",
        None,
        response2,
    )

    assert_cli_successful("cluster-access", "request", "--emergency", "-i", reference_url, "foo", "bar")
    assert not zalando_kubectl.access_request._has_state_file("emergency", "production_cluster")


def test_request_emergency_access_with_okta_pending(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
        "infrastructure_account": "aws:1234",
    }
    mock_account = {
        "id": "aws:1234",
        "name": "production_account",
    }
    mock_get_cluster(monkeypatch, mock_cluster, expected_id="production_cluster")
    mock_get_account(monkeypatch, mock_account, expected_id="aws:1234")
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")
    reference_url = "https://zalando.app.opsgenie.com/alert/detail/a6f295c8-9518-4427-a4ff-000000000-000000000/details"
    zalando_kubectl.access_request._remove_state_file("emergency", "production_cluster")

    expected_json = {
        "access_role": "default",
        "account_name": "production_account",
        "business_justification": "foo bar",
        "reference_url": reference_url,
    }
    response = {
        "result": {
            "request_key": "85625",
            "_links": {
                "request_status": {
                    "href": "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625"
                },
            },
        }
    }
    mock_http_post(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/emergency/cloud-infrastructure/aws/account",
        expected_json,
        response,
    )

    response2 = [
        {
            "request_status": "PENDING",
        }
    ]
    mock_http_get(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/cloud-infrastructure/aws/account?request_key=85625",
        None,
        response2,
    )

    assert_cli_successful(
        "cluster-access", "request", "--emergency", "-i", reference_url, "--timeout", "15", "foo", "bar"
    )
    assert zalando_kubectl.access_request._has_state_file("emergency", "production_cluster")


def test_request_emergency_access_with_okta_already_approved(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_cluster = {
        "api_server_url": "https://my-cluster.example.org",
        "alias": "my-alias",
        "provider": "zalando-aws",
        "environment": "production",
        "infrastructure_account": "aws:1234",
    }
    mock_account = {
        "id": "aws:1234",
        "name": "production_account",
    }
    mock_get_cluster(monkeypatch, mock_cluster, expected_id="production_cluster")
    mock_get_account(monkeypatch, mock_account, expected_id="aws:1234")
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")
    reference_url = "https://zalando.app.opsgenie.com/alert/detail/a6f295c8-9518-4427-a4ff-000000000-000000000/details"
    zalando_kubectl.access_request._remove_state_file("emergency", "production_cluster")

    expected_json = {
        "access_role": "default",
        "account_name": "production_account",
        "business_justification": "foo bar",
        "reference_url": reference_url,
    }
    response = {
        "result": {
            "account_name": "production_account",
            "business_justification": "foo bar",
            "request_status": "PROVISIONED",
        }
    }
    mock_http_post(
        monkeypatch,
        "http://access.zalan.do/v1/requests/tech/emergency/cloud-infrastructure/aws/account",
        expected_json,
        response,
    )

    assert_cli_successful(
        "cluster-access", "request", "--emergency", "-i", reference_url, "--timeout", "15", "foo", "bar"
    )
    assert not zalando_kubectl.access_request._has_state_file("emergency", "production_cluster")


def test_request_emergency_access_with_okta_invalid_incident(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)
    mock_get_cluster(monkeypatch, {"environment": "production"})
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")

    assert_cli_failed("cluster-access", "request", "--emergency", "-i", "WRONG_LINK", "foo", "bar")


def test_request_emergency_access_with_okta_no_message(monkeypatch):
    mock_config(monkeypatch)
    mock_get_cluster(monkeypatch, {"environment": "production"})
    mock_get_auth_token(monkeypatch)
    mock_get_current_context(monkeypatch, "production_cluster")
    reference_url = "https://zalando.app.opsgenie.com/alert/detail/a6f295c8-9518-4427-a4ff-000000000-000000000/details"

    assert_cli_failed("cluster-access", "request", "--emergency", "-i", reference_url)


def test_configure(monkeypatch):
    config = {}
    monkeypatch.setattr("stups_cli.config.load_config", lambda app: config)

    def store_config(conf, _):
        config.update(**conf)

    monkeypatch.setattr("stups_cli.config.store_config", store_config)

    assert_cli_successful("configure", "--cluster-registry=123")
    assert {"cluster_registry": "123"} == config


def test_looks_like_url():
    assert not zalando_kubectl.main.looks_like_url("")
    assert not zalando_kubectl.main.looks_like_url("foo")
    assert not zalando_kubectl.main.looks_like_url("foo.example")
    assert zalando_kubectl.main.looks_like_url("https://localhost")
    assert zalando_kubectl.main.looks_like_url("http://localhost")
    assert zalando_kubectl.main.looks_like_url("foo.example.org")


def test_print_help():
    for arg in ["-h", "--help", "help"]:
        assert_cli_successful(arg)


def test_stern(monkeypatch):
    monkeypatch.setattr("zalando_kubectl.kube_config.update_token", MagicMock(return_value={}))
    assert_cli_successful("logtail", "--help")


def mock_config(monkeypatch):
    monkeypatch.setattr("zign.api.get_token", lambda _x, _y: "mytok")
    monkeypatch.setattr(
        "stups_cli.config.load_config",
        lambda x: {
            "cluster_registry": "http://registry.zalan.do",
            "okta_auth": "http://okta.zalan.do",
            "privileged_access_api": "http://access.zalan.do",
        },
    )


def mock_get_api_server_url(monkeypatch):
    monkeypatch.setattr("zalando_kubectl.utils.get_api_server_url", lambda env: "https://kube-1.testing.zalan.do")


def mock_get_cluster_alias(monkeypatch):
    monkeypatch.setattr("zalando_kubectl.utils.get_cluster_alias", lambda env: "testing")


def mock_get_cluster_error(monkeypatch):
    def fail(*args, **kwargs):
        raise Exception("Failed")

    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_by_id_or_alias", fail)
    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_params", fail)


def mock_get_account(monkeypatch, account_definition, expected_id=None):
    def get_account_with_id(_registry_url, account_id):
        if expected_id is not None:
            assert account_id == expected_id
        return account_definition

    monkeypatch.setattr("zalando_kubectl.registry.get_account_with_id", get_account_with_id)


def mock_get_cluster(monkeypatch, cluster_definition, expected_id=None, expected_params=None):
    def mock_get_cluster_by_id_or_alias(_config, cluster, verbose=False):
        if expected_id is not None:
            assert cluster == expected_id
        assert not verbose
        return cluster_definition

    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_by_id_or_alias", mock_get_cluster_by_id_or_alias)

    def mock_get_cluster(_registry, **params):
        if expected_params is not None:
            assert params == expected_params
        return cluster_definition

    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_params", mock_get_cluster)


def mock_update_config_item(monkeypatch, expected_cluster_id, expected_config_item, expected_value):
    def mock_fn(_registry_url, cluster_id, config_item, value):
        assert cluster_id == expected_cluster_id
        assert config_item == expected_config_item
        assert value == expected_value
        return None

    monkeypatch.setattr("zalando_kubectl.registry.update_config_item", mock_fn)


def mock_delete_config_item(monkeypatch, expected_cluster_id, expected_config_item):
    def mock_fn(_registry_url, cluster_id, config_item):
        assert cluster_id == expected_cluster_id
        assert config_item == expected_config_item
        return None

    monkeypatch.setattr("zalando_kubectl.registry.delete_config_item", mock_fn)


@pytest.mark.parametrize("status", [None, {"current_version": "foo"}, {"current_version": "foo", "next_version": ""}])
def test_cluster_update_status_normal(monkeypatch, status):
    mock_config(monkeypatch)
    mock_get_cluster_alias(monkeypatch)

    cluster = {"id": "aws:1234:eu-central-1:mycluster", "alias": "testing"}
    if status:
        cluster["status"] = status

    mock_get_cluster(monkeypatch, cluster, expected_params={"alias": "testing", "verbose": True})
    result = assert_cli_successful("cluster-update", "status")
    assert result.output == "Cluster testing is up-to-date\n"


def test_cluster_update_status_updating(monkeypatch):
    mock_config(monkeypatch)
    mock_get_cluster_alias(monkeypatch)

    mock_get_cluster(
        monkeypatch,
        {
            "id": "aws:1234:eu-central-1:mycluster",
            "alias": "testing",
            "status": {"current_version": "foo", "next_version": "bar"},
        },
        expected_params={"alias": "testing", "verbose": True},
    )
    result = assert_cli_successful("cluster-update", "status")
    assert result.output == "Cluster testing is being updated\n"


@pytest.mark.parametrize("status", [None, {"current_version": "foo", "next_version": "bar"}])
@pytest.mark.parametrize("reason", ["", "example reason"])
def test_cluster_update_status_update_blocked(monkeypatch, status, reason):
    mock_config(monkeypatch)
    mock_get_cluster_alias(monkeypatch)

    cluster = {
        "id": "aws:1234:eu-central-1:mycluster",
        "alias": "testing",
        "config_items": {"cluster_update_block": reason},
    }
    if status:
        cluster["status"] = status

    mock_get_cluster(monkeypatch, cluster, expected_params={"alias": "testing", "verbose": True})
    result = assert_cli_successful("cluster-update", "status")
    assert result.output == "Cluster updates for testing are blocked: {}\n".format(reason)


def test_cluster_update_unblock_not_blocked(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)

    cluster = {"id": "aws:1234:eu-central-1:mycluster", "alias": "test"}
    mock_get_cluster(monkeypatch, cluster)

    result = assert_cli_successful("cluster-update", "unblock")
    assert result.output == "Cluster updates aren't blocked\n"


def test_cluster_update_unblock_blocked(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)

    cluster = {
        "id": "aws:1234:eu-central-1:mycluster",
        "alias": "test",
        "config_items": {"cluster_update_block": "foo"},
    }
    mock_get_cluster(monkeypatch, cluster)
    mock_delete_config_item(monkeypatch, cluster["id"], "cluster_update_block")
    result = assert_cli_successful("cluster-update", "unblock", input="y")
    assert result.output.endswith("Cluster updates unblocked\n")


def test_cluster_update_block_normal(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)

    cluster = {"id": "aws:1234:eu-central-1:mycluster", "alias": "test"}
    mock_get_cluster(monkeypatch, cluster)
    mock_get_username(monkeypatch, "username")
    mock_update_config_item(monkeypatch, cluster["id"], "cluster_update_block", "example reason (username)")

    result = assert_cli_successful("cluster-update", "block", input="example reason")
    assert result.output.endswith("Cluster updates blocked\n")


def test_cluster_update_block_overwrite(monkeypatch):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)

    cluster = {
        "id": "aws:1234:eu-central-1:mycluster",
        "alias": "test",
        "config_items": {"cluster_update_block": "foo"},
    }
    mock_get_cluster(monkeypatch, cluster)
    mock_get_username(monkeypatch, "username")
    mock_update_config_item(monkeypatch, cluster["id"], "cluster_update_block", "example reason (username)")

    result = assert_cli_successful("cluster-update", "block", input="y\nexample reason")
    assert result.output.endswith("Cluster updates blocked\n")


def test_zalando_aws_cli_download():
    Environment().zalando_aws_cli.download()


@pytest.mark.parametrize("cluster", [(None, []), ("foo", ["--cluster", "foo"])])
@pytest.mark.parametrize("strip", [("foo", []), ("foo", ["--strip"]), ("foo\n", ["--no-strip"])])
@pytest.mark.parametrize(
    "key_id", [("alias/mycluster-deployment-secret", []), ("custom-key", ["--kms-keyid", "custom-key"])]
)
def test_encrypt(monkeypatch, cluster, key_id, strip):
    mock_config(monkeypatch)
    mock_get_cluster_alias(monkeypatch)

    test_region = "ap-east-1"
    test_cluster = {
        "id": "aws:1234:{}:mycluster".format(test_region),
        "infrastructure_account": "aws:1234",
        "alias": "test",
        "region": test_region,
    }
    test_account = {
        "id": "aws:1234",
        "name": "testing",
    }

    expected_cluster, cluster_args = cluster
    expected_key, key_id_args = key_id
    plaintext, strip_args = strip

    if expected_cluster:
        mock_get_cluster(monkeypatch, test_cluster, expected_id=expected_cluster)
    else:
        mock_get_cluster(monkeypatch, test_cluster, expected_params={"alias": "testing"})

    mock_get_account(monkeypatch, test_account, expected_id="aws:1234")

    mock_boto = MagicMock()
    client = mock_boto.client.return_value
    client.encrypt.return_value = {"CiphertextBlob": b"test"}

    mock_run = MagicMock()
    mock_run.return_value.stdout = b"deployment-secret:2:test:dGVzdA=="
    mock_run.return_value.wait.return_value = 0
    monkeypatch.setattr("subprocess.run", mock_run)

    cmdline = ["encrypt"]
    cmdline.extend(key_id_args)
    cmdline.extend(strip_args)
    cmdline.extend(cluster_args)

    result = CliRunner().invoke(click_cli, cmdline, input="foo\n")

    expect_success(result, "deployment-secret:2:test:dGVzdA==")

    mock_kms = unittest.mock.call.client("kms", test_region)
    expected_calls = []
    assert mock_boto.mock_calls == expected_calls


@pytest.mark.parametrize("secret_args", [["deployment-secret:test:dGVzdA=="], ["deployment-secret:2:test:dGVzdA=="]])
def test_decrypt(monkeypatch, secret_args):
    mock_config(monkeypatch)
    mock_get_api_server_url(monkeypatch)

    test_region = "ap-east-1"
    test_cluster = {
        "id": "aws:1234:{}:mycluster".format(test_region),
        "infrastructure_account": "aws:1234",
        "alias": "test",
        "region": test_region,
    }

    def mock_get_cluster_with_params(_config, **params):
        assert params == {"alias": "test"}
        return test_cluster

    monkeypatch.setattr("zalando_kubectl.registry.get_cluster_with_params", mock_get_cluster_with_params)

    mock_boto = MagicMock()
    client = mock_boto.client.return_value
    client.decrypt.return_value = {"Plaintext": b"foo"}

    mock_run = MagicMock()
    mock_run.return_value.stdout = b"foo\r\n"
    mock_run.return_value.wait.return_value = 0
    monkeypatch.setattr("subprocess.run", mock_run)

    cmdline = ["decrypt"]
    cmdline.extend(secret_args)

    result = CliRunner().invoke(click_cli, cmdline)

    expect_success(result, "foo")

    mock_kms = unittest.mock.call.client("kms", test_region)
    expected_calls = []
    assert mock_boto.mock_calls == expected_calls


def test_delete_all_is_forbidden(monkeypatch):
    mock_get_cluster(monkeypatch, {"environment": "production"})

    assert_cli_failed("delete", "--all", "namespaces")
    assert_cli_failed("delete", "--all=true", "namespaces")
    assert_cli_failed("delete", "--all=false", "namespaces")
