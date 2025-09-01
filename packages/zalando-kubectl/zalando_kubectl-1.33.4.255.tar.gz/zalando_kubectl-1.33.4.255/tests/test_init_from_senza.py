import pytest
from pathlib import Path
from unittest.mock import MagicMock

from click.testing import CliRunner
from zalando_kubectl.main import click_cli


@pytest.fixture
def mock_config(monkeypatch):
    config = {
        "kubernetes_api_server": "https://example.org",
        "kubernetes_cluster": "mycluster",
        "kubernetes_namespace": "mynamespace",
        "deploy_api": "https://deploy.example.org",
    }
    load_config = MagicMock(return_value=config)
    monkeypatch.setattr("stups_cli.config.load_config", load_config)
    return load_config


def test_init_from_senza():
    runner = CliRunner()

    senza_file = Path(__file__).parent / "fixtures" / "senza-helloworld.yaml"

    with runner.isolated_filesystem():
        result = runner.invoke(
            click_cli, ["init", "--from-senza={}".format(senza_file), "--kubernetes-cluster=aws:123:my-region:my-kube"]
        )

        for path in Path(".").iterdir():
            print(path)
    print(result.output)
