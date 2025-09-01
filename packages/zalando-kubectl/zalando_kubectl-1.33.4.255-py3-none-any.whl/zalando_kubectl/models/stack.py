import json
import subprocess

from zalando_kubectl.utils import ExternalBinary


class StackUpdateError(Exception):
    pass


class Stack:
    def __init__(self, kubectl: ExternalBinary, name: str):
        self.kubectl = kubectl
        self.name = name

    def annotate_restart(self, restart_id):
        patch = {"spec": {"podTemplate": {"metadata": {"annotations": {"restart": restart_id}}}}}
        command = ("patch", "stack", self.name, "--type=merge", "--patch", json.dumps(patch))
        try:
            self.kubectl.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            raise StackUpdateError("Failed to add annotations to pod template: {}".format(e.stderr.decode("utf-8")))
