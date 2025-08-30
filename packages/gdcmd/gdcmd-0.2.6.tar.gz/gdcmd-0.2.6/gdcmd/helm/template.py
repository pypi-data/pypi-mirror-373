import subprocess

def template(deployment: str, values: tuple[str] = None):
    """
    Create a Kubernetes deployment using helm, from the possible deployments in list_helm_charts.
    """
    cmd = "podman"
    try:
        subprocess.run("podman --version", shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        cmd = "docker"
    container_cmd = cmd

    if len(values) > 0:
        values_mount = " ".join([f"-v ./{value}:/{value.split('/')[-1]}" for value in values])
        values_option = "".join([f"-f /{value.split('/')[-1]} " for value in values])
    else:
        values_option = ""
        values_mount = ""

    result = subprocess.run(
        f"{container_cmd} run --rm {values_mount} registry.gitlab.com/griddot/packages/helm:latest helm template {deployment} {values_option}",
        shell=True, check=True, capture_output=True
    )

    return result.stdout.decode('utf-8')
