import json
import subprocess

from zalando_kubectl.models.stack import Stack
from zalando_kubectl.utils import ExternalBinary


class DeploymentUpdateError(Exception):
    pass


class Deployment:
    def __init__(self, kubectl: ExternalBinary, name: str):
        self.kubectl = kubectl
        self.name = name

    def _spec(self):
        command = ("get", "deployment", self.name, "-o", "json")
        output = self.kubectl.run(command, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, check=True).stdout
        return json.loads(output.decode("utf-8"))

    def ss_ref(self):
        try:
            deployment = self._spec()
        except subprocess.CalledProcessError:
            raise RuntimeError("Failed to get deployment spec {}".format(self.name))
        if "ownerReferences" not in deployment["metadata"]:
            return None
        for r in deployment["metadata"]["ownerReferences"]:
            if r["kind"] == "Stack":
                return r
        return None

    def get_stackset(self):
        ref = self.ss_ref()
        return Stack(self.kubectl, ref["name"])

    def annotate_restart(self, restart_id):
        patch = {"spec": {"template": {"metadata": {"annotations": {"restart": restart_id}}}}}
        command = ("patch", "deployment", self.name, "--type=merge", "--patch", json.dumps(patch))
        try:
            self.kubectl.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            raise DeploymentUpdateError("Failed to annotate deployment: {}".format(e.stderr.decode("utf-8")))
