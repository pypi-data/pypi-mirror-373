import yaml

cvmfs_path = "/cvmfs/ctao.dpps.test"
apptainer_options = []

def translate(cwl):
    if cwl["class"] != "CommandLineTool":
        return cwl

    if (requirement := cwl.get("requirements", {}).pop("DockerRequirement", None)) is not None:

        image = requirement["dockerPull"]
        cmd = ["apptainer", "run", *apptainer_options, f"{cvmfs_path}/{image}"] + cwl["baseCommand"]
        cwl["baseCommand"] = cmd

    return cwl


if __name__ == "__main__":
    with open("./test.cwl") as f:
        cwl = yaml.safe_load(f)

    print(yaml.dump(translate(cwl)))
