import json
from zalando_kubectl.models.bluegreen import BlueGreen


class StackSet(BlueGreen):
    def __init__(self, definition):
        super().__init__(definition)

        if "traffic" in self.definition["spec"]:
            for stack in self.definition["spec"]["traffic"]:
                self.stacks[stack["stackName"]] = stack

        if "traffic" in self.definition["status"]:
            for stack in self.definition["status"]["traffic"]:
                self.stacks_status[stack["stackName"]] = stack["weight"]

    def get_traffic(self):
        traffic = super().get_traffic()
        for stack in traffic:
            stack["desired"] = self.stacks[stack["name"]]["weight"]

        stacks_present = [stack["name"] for stack in traffic]
        for name, weight in self.stacks_status.items():
            if name not in stacks_present:
                traffic.append({"name": name, "actual": weight, "desired": 0.0})

        return traffic

    def get_traffic_cmd(self):
        patch = json.dumps({"spec": {"traffic": self.definition["spec"]["traffic"]}})
        return ("patch", "StackSet", self.get_name(), "--type=merge", "--patch", patch)

    def get_stacks_to_update(self):
        stacks = super().get_stacks_to_update()
        return {stack: stacks[stack]["weight"] for stack in stacks}

    def update_stacks(self, new_weights):
        if new_weights:
            for name, new_weight in new_weights.items():
                if name in self.stacks:
                    self.stacks[name]["weight"] = new_weight
                else:
                    self.stacks[name] = {"stackName": name, "weight": new_weight}
                    if "traffic" in self.definition["spec"]:
                        self.definition["spec"]["traffic"].append(self.stacks[name])
                    else:
                        self.definition["spec"]["traffic"] = [self.stacks[name]]
