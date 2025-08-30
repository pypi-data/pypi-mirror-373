import subprocess

from gdcmd.keycloak import get_realms
from tests.manual.keycloak_test import build_keycloak_images, run_keycloak, wait_for_keycloak_and_get_token


def setup_keycloak_with_provisioner(clean, build_images):
    if build_images:
        build_keycloak_images()

    if clean:
        run_keycloak()

    cwd = "../../containers/keycloak-provisioner"
    subprocess.run(f"podman kube play --replace provisioner.yaml", check=True, shell=True, cwd=cwd)


def test_provisioner():
    setup_keycloak_with_provisioner(True, False)
    url, token = wait_for_keycloak_and_get_token()

    realms = get_realms(url, token)
    realms_names = [realm["realm"] for realm in realms]
    assert "master" in realms_names, "Master realm not found"
    assert "platform" in realms_names, "Platform realm not found"
