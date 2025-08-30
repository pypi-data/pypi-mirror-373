import subprocess
import pytest
from click.testing import CliRunner

from gdcmd.cli import cli
from gdcmd.keycloak import get_access_token, wait_for_keycloak_to_start, import_realm, get_realms, \
    import_users, get_client_roles, get_user_uuid_by_username, get_client_roles_for_user, import_client_roles, \
    import_client, create_realm

USERNAME = "temp-admin"
PASSWORD = "temp-admin"
EMAIL_PASSWORD = "ppgb ddgj sjki xbya"


@pytest.fixture(scope="module", autouse=True)
def setup_once_for_module():
    # This runs once before any tests in this module
    setup_keycloak(False, False)
    yield
    # This runs once after all tests in this module


def setup_keycloak(clean, build_images):
    if build_images:
        build_keycloak_images()

    if clean:
        run_keycloak()


def run_keycloak():
    cwd = "../../containers/keycloak"
    print("Deleting existing Keycloak resources...")
    subprocess.run(f"podman kube play --down --force dev.yaml", check=False, shell=True, cwd=cwd)
    print("Starting Keycloak...")
    subprocess.run(f"podman kube play --replace dev.yaml", check=True, shell=True, cwd=cwd)


def build_keycloak_images():
    print("Building Keycloak images...")
    subprocess.run("python3 build_images.py", check=True, shell=True, cwd="../../containers")


def wait_for_keycloak_and_get_token(url="https://localhost:8443"):
    wait_for_keycloak_to_start(url)
    token = get_access_token(url, USERNAME, PASSWORD)
    return url, token


def test_import_realm():
    url = "https://localhost:8443"
    master_realm = "../../containers/keycloak/realms/master-realm.json"
    import_realm(url, USERNAME, PASSWORD, master_realm, EMAIL_PASSWORD, False)

    platform_realm = "../../containers/keycloak/realms/platform-realm.json"
    import_realm(url, USERNAME, PASSWORD, platform_realm, EMAIL_PASSWORD, False)
    import_realm(url, USERNAME, PASSWORD, platform_realm, EMAIL_PASSWORD, False)  # idempotency test

    token = get_access_token(url, USERNAME, PASSWORD)
    realms = get_realms(url, token)
    realms_names = [realm["realm"] for realm in realms]
    assert "master" in realms_names, "Master realm not found"
    assert "platform" in realms_names, "Platform realm not found"


def test_cli():
    url, _ = wait_for_keycloak_and_get_token()

    runner = CliRunner()
    result = runner.invoke(cli, [
        'provision-keycloak',
        '--url', "https://localhost:8443",
        '--username', USERNAME,
        '--password', PASSWORD,
        '--realms-dir', '../../containers/keycloak/realms',
        '--delete-user-when-provisioned', 'Yes',
        '--email-password', EMAIL_PASSWORD
    ])

    assert result.exit_code == 0, result.output


def test_creating_realm():
    url, token = wait_for_keycloak_and_get_token()
    realm = {
        "realm": "test-realm",
        "enabled": True,
    }
    create_realm(url, realm, token)

    all_realms = get_realms(url, token)
    assert any(realm["realm"] == "test-realm" for realm in all_realms), "test-realm should be created"

    # ensure creating the realm is idempotent
    create_realm(url, realm, token)


def configure_email_provider(url, realm_name, token, email_config):
    pass


def test_import_users():
    url, token = wait_for_keycloak_and_get_token()

    realm_name = "import-users-realm"
    realm = {
        "realm": realm_name,
        "enabled": True,
    }

    create_realm(url, realm, token)
    create_realm(url, realm, token)

    client = {
        "clientId": "my-client",
        "name": "My Admin Client",
        "enabled": True,
        "protocol": "openid-connect",
    }

    client_uuid = import_client(url, realm_name, token, client)
    client_uuid2 = import_client(url, realm_name, token, client)  # idempotency check
    assert client_uuid == client_uuid2, "Client ID should be the same on idempotent import"

    roles = [
        {
            "name": "my-admin",
            "description": "My admin role",
            "clientRole": True,
        },
        {
            "name": "myy-user",
            "description": "My user role",
            "clientRole": True,
        },
    ]
    import_client_roles(url, realm_name, token, client_uuid, roles)
    import_client_roles(url, realm_name, token, client_uuid, roles)  # idempotency check

    users_to_import = [
        {
            "username": "ali",
            "email": "ali@example.com",
            "enabled": True,
            "credentials": [{"type": "password", "value": "test"}],
            "clientRoles": {
                "my-client": ["my-admin"],
            }
        },
        {
            "username": "bob",
            "email": "bob@example.com",
            "enabled": True,
            "credentials": [{"type": "password", "value": "test"}],
            "clientRoles": {
                "my-client": ["myy-user"],
            },
        },
    ]

    import_users(url, realm_name, token, users_to_import)
    import_users(url, realm_name, token, users_to_import)  # idempotency check

    client_roles = {role["name"] for role in get_client_roles(url, realm_name, token, client_uuid)}
    assert "my-admin" in client_roles, "my-admin role should have been created"
    assert "myy-user" in client_roles, "myy-user role should have been created"

    for user_spec in users_to_import:
        uuid = get_user_uuid_by_username(url, realm_name, token, user_spec["username"])
        user_roles = get_client_roles_for_user(url, realm_name, token, uuid, client_uuid)
        user_roles_names = {role["name"] for role in user_roles}
        for role in user_spec["clientRoles"]["my-client"]:
            assert role in user_roles_names, f"Role {role} should be assigned to user {user_spec['username']}"
