from zalando_kubectl.models.bluegreen import BlueGreen
from zalando_kubectl.models.bluegreen import BACKEND_WEIGHTS

import json

STACK_TRAFFIC_WEIGHTS = "zalando.org/stack-traffic-weights"


class StackSetIngressAuthoritative(BlueGreen):
    def __init__(self, ingress_def, stacks_def):
        super().__init__(ingress_def)

        self.weights_annotation = STACK_TRAFFIC_WEIGHTS
        self.stacks_desired = dict()

        if "annotations" in self.definition["metadata"]:
            stack_traffic_weights = self.definition["metadata"]["annotations"].get(self.weights_annotation)
            if stack_traffic_weights:
                self.stacks_desired = json.loads(stack_traffic_weights)

        for stack in stacks_def.get("items", []):
            self.stacks[stack["metadata"]["name"]] = self.stacks_desired.get(stack["metadata"]["name"], 0)
            if stack["metadata"]["name"] not in self.stacks_status:
                self.stacks_status[stack["metadata"]["name"]] = 0

    def force_traffic_weight(self):
        self.to_annotate[BACKEND_WEIGHTS] = self.definition["metadata"]["annotations"].get(self.weights_annotation)
        self.definition["metadata"]["annotations"][BACKEND_WEIGHTS] = self.to_annotate[BACKEND_WEIGHTS]
