from unittest.mock import MagicMock

import pytest

from zalando_kubectl import kube_config
from zalando_kubectl.utils import Environment


def _update_config(monkeypatch, current_config, url, alias):
    monkeypatch.setattr("zalando_kubectl.kube_config.write_config", MagicMock())
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=current_config))
    monkeypatch.setattr("zign.api.get_token", MagicMock(return_value="mytok"))
    return kube_config.update(url, alias, f"kubernetes.cluster.{alias}", "mytok")


def test_kube_config_update(monkeypatch):
    updated = _update_config(monkeypatch, {}, "https://zalan.k8s.do", "foo")
    assert updated == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "foo",
        "clusters": [{"cluster": {"server": "https://zalan.k8s.do"}, "name": "foo"}],
        "contexts": [{"context": {"cluster": "foo", "user": "okta-foo"}, "name": "foo"}],
        "users": [
            {
                "name": "okta-foo",
                "user": {
                    "exec": {
                        "apiVersion": "client.authentication.k8s.io/v1beta1",
                        "args": ["credentials", "foo", "--okta-auth-client-id", "kubernetes.cluster.foo"],
                        "command": "zkubectl",
                    }
                },
            }
        ],
    }


def test_kube_config_update_url(monkeypatch):
    updated = _update_config(monkeypatch, {}, "https://zalan.k8s.do", None)
    assert updated == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "zalan_k8s_do",
        "clusters": [{"cluster": {"server": "https://zalan.k8s.do"}, "name": "zalan_k8s_do"}],
        "contexts": [{"context": {"cluster": "zalan_k8s_do", "user": "okta-None"}, "name": "zalan_k8s_do"}],
        "users": [
            {
                "name": "okta-None",
                "user": {
                    "exec": {
                        "apiVersion": "client.authentication.k8s.io/v1beta1",
                        "args": ["credentials", "zalan_k8s_do", "--okta-auth-client-id", "kubernetes.cluster.None"],
                        "command": "zkubectl",
                    }
                },
            }
        ],
    }


def test_kube_config_update_merge(monkeypatch):
    existing = {
        "apiVersion": "v0",
        "kind": "Unknown",
        "current-context": "another",
        "clusters": [
            {"cluster": {"server": "https://zalan.k8s.do"}, "name": "zalan_k8s_do"},
            {"cluster": {"server": "https://zalan.k8s.do", "custom": "setting"}, "name": "foo"},
        ],
        "contexts": [
            {"context": {"cluster": "zalan_k8s_do", "user": "zalando-token"}, "name": "zalan_k8s_do"},
            {"context": {"cluster": "foo", "user": "zalando-token2", "custom": "setting"}, "name": "foo"},
        ],
        "users": [
            {"user": {"token": "mytok"}, "name": "another-token"},
            {"user": {"token": "mytok", "custom": "setting"}, "name": "zalando-token"},
        ],
    }
    updated = _update_config(monkeypatch, existing, "https://zalan2.k8s.do", "foo")
    assert updated == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "foo",
        "clusters": [
            {"cluster": {"server": "https://zalan.k8s.do"}, "name": "zalan_k8s_do"},
            {"cluster": {"server": "https://zalan2.k8s.do", "custom": "setting"}, "name": "foo"},
        ],
        "contexts": [
            {"context": {"cluster": "zalan_k8s_do", "user": "zalando-token"}, "name": "zalan_k8s_do"},
            {"context": {"cluster": "foo", "custom": "setting", "user": "okta-foo"}, "name": "foo"},
        ],
        "users": [
            {"name": "another-token", "user": {"token": "mytok"}},
            {"user": {"token": "mytok", "custom": "setting"}, "name": "zalando-token"},
            {
                "name": "okta-foo",
                "user": {
                    "exec": {
                        "apiVersion": "client.authentication.k8s.io/v1beta1",
                        "args": ["credentials", "foo", "--okta-auth-client-id", "kubernetes.cluster.foo"],
                        "command": "zkubectl",
                    },
                },
            },
        ],
    }

    updated2 = _update_config(monkeypatch, updated, "https://zalan3.k8s.do", "bar")
    assert updated2 == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "bar",
        "clusters": [
            {"cluster": {"server": "https://zalan.k8s.do"}, "name": "zalan_k8s_do"},
            {"cluster": {"server": "https://zalan2.k8s.do", "custom": "setting"}, "name": "foo"},
            {"cluster": {"server": "https://zalan3.k8s.do"}, "name": "bar"},
        ],
        "contexts": [
            {"context": {"cluster": "zalan_k8s_do", "user": "zalando-token"}, "name": "zalan_k8s_do"},
            {"context": {"cluster": "foo", "custom": "setting", "user": "okta-foo"}, "name": "foo"},
            {"context": {"cluster": "bar", "user": "okta-bar"}, "name": "bar"},
        ],
        "users": [
            {"name": "another-token", "user": {"token": "mytok"}},
            {"user": {"token": "mytok", "custom": "setting"}, "name": "zalando-token"},
            {
                "name": "okta-foo",
                "user": {
                    "exec": {
                        "apiVersion": "client.authentication.k8s.io/v1beta1",
                        "args": ["credentials", "foo", "--okta-auth-client-id", "kubernetes.cluster.foo"],
                        "command": "zkubectl",
                    },
                },
            },
            {
                "name": "okta-bar",
                "user": {
                    "exec": {
                        "apiVersion": "client.authentication.k8s.io/v1beta1",
                        "args": ["credentials", "bar", "--okta-auth-client-id", "kubernetes.cluster.bar"],
                        "command": "zkubectl",
                    },
                },
            },
        ],
    }


@pytest.mark.parametrize(
    "existing, expected",
    [
        # Add new okta entry
        (
            {},
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [{"name": "foo", "cluster": {"server": "https://zalan.k8s.do"}}],
                "contexts": [{"name": "foo", "context": {"cluster": "foo", "user": "okta-foo"}}],
                "current-context": "foo",
                "users": [
                    {
                        "name": "okta-foo",
                        "user": {
                            "exec": {
                                "apiVersion": "client.authentication.k8s.io/v1beta1",
                                "args": ["credentials", "foo", "--okta-auth-client-id", "kubernetes.cluster.foo"],
                                "command": "zkubectl",
                            }
                        },
                    },
                ],
            },
        ),
        # Switch to Okta from an existing Zalando OAuth setup
        (
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [{"name": "foo", "cluster": {"server": "https://zalan.k8s.do"}}],
                "contexts": [{"name": "foo", "context": {"cluster": "foo", "user": "zalando-token"}}],
                "current-context": "foo",
                "users": [
                    {"name": "zalando-token", "user": {"token": "mytok"}},
                ],
            },
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [{"name": "foo", "cluster": {"server": "https://zalan.k8s.do"}}],
                "contexts": [{"name": "foo", "context": {"cluster": "foo", "user": "okta-foo"}}],
                "current-context": "foo",
                "users": [
                    {"name": "zalando-token", "user": {"token": "mytok"}},
                    {
                        "name": "okta-foo",
                        "user": {
                            "exec": {
                                "apiVersion": "client.authentication.k8s.io/v1beta1",
                                "args": ["credentials", "foo", "--okta-auth-client-id", "kubernetes.cluster.foo"],
                                "command": "zkubectl",
                            }
                        },
                    },
                ],
            },
        ),
    ],
)
def test_kube_config_update_okta(monkeypatch, existing, expected):
    updated = _update_config(monkeypatch, existing, "https://zalan.k8s.do", "foo")
    assert updated == expected


def test_kube_config_update_broken(monkeypatch):
    existing = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": None,
        "contexts": None,
        "current-context": "",
        "users": None,
    }
    updated = _update_config(monkeypatch, existing, "https://zalan.k8s.do", "foo")
    assert updated == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "foo",
        "clusters": [{"cluster": {"server": "https://zalan.k8s.do"}, "name": "foo"}],
        "contexts": [{"context": {"cluster": "foo", "user": "okta-foo"}, "name": "foo"}],
        "users": [
            {
                "name": "okta-foo",
                "user": {
                    "exec": {
                        "apiVersion": "client.authentication.k8s.io/v1beta1",
                        "args": ["credentials", "foo", "--okta-auth-client-id", "kubernetes.cluster.foo"],
                        "command": "zkubectl",
                    }
                },
            },
        ],
    }


def test_kube_config_get_namespace(monkeypatch):
    ns_config = {"contexts": [{"name": "none", "context": {"namespace": "some"}}]}
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=ns_config))
    assert kube_config.get_current_namespace() == "default"
    ns_config["current-context"] = "none"
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=ns_config))
    assert kube_config.get_current_namespace() == "some"
    ns_config["contexts"][0]["context"] = {}
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=ns_config))
    assert kube_config.get_current_namespace() == "default"
