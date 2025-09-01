import io
import hashlib
import os
import random
import string
import subprocess
import sys
import tarfile
from pathlib import Path
from zipfile import ZipFile

import click
import jwt
import requests
import stups_cli
import stups_cli.config
import zign.api
from clickclick import Action, AliasedGroup
from subprocess import check_output

from . import (
    APP_NAME,
    APP_VERSION,
    KUBECTL_VERSION,
    KUBECTL_SHA512,
    KUBELOGIN_VERSION,
    KUBELOGIN_SHA256,
    ZALANDO_AWS_CLI_VERSION,
    ZALANDO_AWS_CLI_SHA256,
    STERN_VERSION,
    STERN_SHA256,
)


def auth_token():
    return zign.api.get_token("kubectl", ["uid"])


def _token_username():
    decoded_token = jwt.decode(auth_token(), options={"verify_signature": False})
    if decoded_token.get("https://identity.zalando.com/realm") == "users":
        return decoded_token.get("https://identity.zalando.com/managed-id")


def current_user():
    return zign.api.get_config().get("user") or _token_username()


def auth_headers():
    return {"Authorization": "Bearer {}".format(auth_token())}


def extract_none(archive):
    return archive


def extract_tgz(filepath):
    def extract(archive):
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tf:
            return tf.extractfile(filepath).read()

    return extract


def extract_zip(filepath):
    def extract(archive):
        with ZipFile(io.BytesIO(archive), "r") as zf:
            with zf.open(zf.infolist()[0].filename) as file:
                return file.read()

    return extract


class ExternalBinary:
    def __init__(self, env, name, url_template, version, checksum_algo, checksum, extract, exec_name=None):
        self.env = env
        self.name = name
        self.url_template = url_template
        self.version = version
        self.checksum_algo = checksum_algo
        self.checksum = checksum
        self.extract = extract
        self.exec_name = exec_name

    def _binary(self):
        path = Path(os.getenv("KUBECTL_DOWNLOAD_DIR") or click.get_app_dir(APP_NAME))
        return path / "{}-{}".format(self.name, self.version)

    def exists(self):
        return self._binary().exists()

    def download(self):
        binary = self._binary()

        if not binary.exists():
            try:
                binary.parent.mkdir(parents=True)
            except FileExistsError:
                # support Python 3.4
                # "exist_ok" was introduced with 3.5
                pass

            platform = sys.platform  # linux or darwin
            arch = "amd64"  # FIXME: hardcoded value
            url = self.url_template.format(version=self.version, os=platform, arch=arch)
            with Action("Downloading {} {}...".format(self.name, self.version)) as act:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                data = response.content
                m = self.checksum_algo()
                m.update(data)
                if m.hexdigest() != self.checksum[platform]:
                    act.fatal_error("CHECKSUM MISMATCH")

                self.create_binary(binary, self.extract(data))

        return str(binary)

    def create_binary(self, binary, data):
        # add random suffix so we can do an atomic write and rename
        random_suffix = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        local_file = binary.with_name("{}.download-{}".format(binary.name, random_suffix))
        with local_file.open("wb") as fd:
            fd.write(data)
            fd.flush()
        local_file.chmod(0o755)
        local_file.rename(binary)

    def run(
        self,
        args,
        input=None,
        stdout=None,
        stderr=None,
        check=False,
        forward_context=True,
        forward_namespace=True,
        env=None,
    ):
        if self.exec_name is not None:
            exec_name = self.exec_name
        else:
            exec_name = self.name

        cmdline = [exec_name]
        if forward_namespace and self.env.namespace:
            cmdline += ["-n", self.env.namespace]
        if forward_context and self.env.kube_context:
            cmdline += ["--context", self.env.kube_context]
        cmdline.extend(args)

        return subprocess.run(
            cmdline,
            input=input,
            stdout=stdout,
            stderr=stderr,
            check=check,
            executable=self.download(),
            env=env,
        )

    def exec(self, *args, env=None):
        sys.exit(self.run(args, env=env).returncode)


class Environment:
    def __init__(self):
        self.namespace = None
        self.kube_context = None
        self.config = stups_cli.config.load_config(APP_NAME)

        kubectl_template = "https://dl.k8s.io/{version}/kubernetes-client-{os}-{arch}.tar.gz"
        self.kubectl = ExternalBinary(
            self,
            "kubectl",
            kubectl_template,
            KUBECTL_VERSION,
            hashlib.sha512,
            KUBECTL_SHA512,
            extract_tgz("kubernetes/client/bin/kubectl"),
            exec_name="zkubectl-{}".format(APP_VERSION),
        )

        stern_template = (
            "https://github.com/stern/stern/releases/download/v{version}/stern_{version}_{os}_{arch}.tar.gz"
        )
        self.stern = ExternalBinary(
            self,
            "stern",
            stern_template,
            STERN_VERSION,
            hashlib.sha256,
            STERN_SHA256,
            extract_tgz("stern"),
        )

        kubelogin_template = "https://github.com/int128/kubelogin/releases/download/{version}/kubelogin_{os}_{arch}.zip"
        self.kubelogin = ExternalBinary(
            self,
            "kubelogin",
            kubelogin_template,
            KUBELOGIN_VERSION,
            hashlib.sha256,
            KUBELOGIN_SHA256,
            extract_zip(
                "kubelogin_{version}_{os}_{arch}/kubelogin".format(
                    version=KUBELOGIN_VERSION, os=sys.platform, arch="amd64"
                )
            ),
        )

        zalando_aws_cli_template = "https://cloud-utils.s3.eu-central-1.amazonaws.com/zalando-aws-cli/zalando-aws-cli-{version}-{os}-{arch}.tar.gz"
        self.zalando_aws_cli = ExternalBinary(
            self,
            "zalando-aws-cli",
            zalando_aws_cli_template,
            ZALANDO_AWS_CLI_VERSION,
            hashlib.sha256,
            ZALANDO_AWS_CLI_SHA256,
            extract_tgz("zalando-aws-cli"),
        )

    def store_config(self):
        stups_cli.config.store_config(self.config, APP_NAME)

    def set_namespace(self, namespace):
        self.namespace = namespace

    def set_kube_context(self, kube_context):
        self.kube_context = kube_context


class DecoratingGroup(AliasedGroup):
    """An AliasedGroup that decorates all commands added to the group with a given decorator. If the command is also
    a DecoratingGroup, the decorator is propagated as well."""

    def __init__(self, name=None, commands=None, **attrs):
        super(DecoratingGroup, self).__init__(name=name, commands=commands, **attrs)
        self.decorator = None

    def add_command(self, cmd, name=None):
        if self.decorator:
            cmd = self.decorator(cmd)
        if isinstance(cmd, DecoratingGroup):
            cmd.decorator = self.decorator
        super(DecoratingGroup, self).add_command(cmd, name=name)


class PortMappingParamType(click.ParamType):
    name = "port_mapping"

    def convert(self, value, param, ctx):
        parts = value.split(":")
        if len(parts) > 2:
            self.fail("{} has too many colons".format(value), param, ctx)
        for p in parts:
            if not p.isdigit():
                self.fail("{} is not a number".format(p), param, ctx)
            if int(p) < 0 or int(p) > 65535:
                self.fail("{} is not a valid port number".format(p), param, ctx)
        return parts[0], parts[-1]


def get_api_server_url(env: Environment) -> str:
    try:
        # --minify returns the information about the current context only, which works nicely with --context
        args = ["config", "view", "--minify", "-o", "jsonpath={.clusters[].cluster.server}"]
        return env.kubectl.run(args, stdout=subprocess.PIPE).stdout.decode("utf-8")
    except Exception:
        raise Exception("Unable to determine API server URL, please run zkubectl login")


def get_cluster_alias(env: Environment) -> str:
    try:
        # --minify returns the information about the current context only, which works nicely with --context
        args = ["config", "view", "--minify", "-o", "jsonpath={.clusters[].name}"]
        return env.kubectl.run(args, stdout=subprocess.PIPE).stdout.decode("utf-8")
    except Exception:
        raise Exception("Unable to determine cluster alias, please run zkubectl login")
