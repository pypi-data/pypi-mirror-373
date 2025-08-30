import json
import sys
import time
import requests
import urllib3

# Disable warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ADMIN_USERNAME = "temp-admin"
DEFAULT_URL = "https://localhost:8443"


def import_realm(
        url: str,
        admin_username: str,
        admin_password: str,
        realm_json_path: str,
        email_provider_password: str | None,
        send_emails: bool
):
    print(f'Provisioning Keycloak at {url}')
    wait_for_keycloak_to_start(url)
    token = get_access_token(url, admin_username, admin_password)

    realm = json.load(open(realm_json_path, "r", encoding="utf-8"))

    if email_provider_password:
        if "smtpServer" in realm:
            realm["smtpServer"]["password"] = email_provider_password

    create_realm(url, realm, token)
    send_emails_to_users(url, realm["realm"], token, realm.get("users", []), send_emails=send_emails)


def get_user_uuid_by_username(url, realm, token, username):
    all_users = get_users(url, realm, token)
    for user in all_users:
        if user["username"] == username:
            return user["id"]

    raise Exception(f"User {username} not found in realm {realm}")


def wait_for_keycloak_to_start(url):
    max_retries = 60
    retries = max_retries
    while retries > 0:
        try:
            response = requests.get(url, verify=False)
            print()
            if response.status_code == 200:
                print("Keycloak is up and running.", flush=True)
                break
            else:
                print(f"Keycloak is not ready yet. Status code: {response.status_code}")
        except requests.exceptions.RequestException:
            if retries == max_retries:
                print(f"Keycloak is not ready yet .", end="", flush=True)
            else:
                print(".", end="", flush=True)
        time.sleep(1)
        retries -= 1
    else:
        print("Keycloak did not start in time.", flush=True)
        sys.exit(1)


def get_access_token(url, username, password):
    token_url = f"{url}/realms/master/protocol/openid-connect/token"
    data = {
        "client_id": "admin-cli",
        "username": username,
        "password": password,
        "grant_type": "password"
    }
    response = requests.post(token_url, data=data, verify=False)
    if response.status_code != 200:
        print("Failed to get access token:", response.text)
        sys.exit(1)
    return response.json()["access_token"]


def send_emails_to_users(url, realm, token, users, send_emails):
    for user in users:
        user_uuid = get_user_uuid_by_username(url, realm, token, user["username"])
        credentials_url = f"{url}/admin/realms/{realm}/users/{user_uuid}/credentials"
        credentials_response = requests.get(credentials_url, headers=get_token_header(token), verify=False)

        has_user_password = False
        if credentials_response.status_code == 200:
            has_user_password = len(credentials_response.json()) > 0

        if not has_user_password:
            if send_emails:
                print(f"Sent email to {user['username']} for password setup.")
                send_email_for_password_setup(url, realm, token, user_uuid)
            else:
                print(f"Dry run: Would send email to {user['username']} for password setup.")


def delete_user(url, realm, token, user_id):
    delete_url = f"{url}/admin/realms/{realm}/users/{user_id}"
    response = requests.delete(
        delete_url,
        headers=get_token_header(token),
        verify=False
    )
    response.raise_for_status()


def get_users(url, realm, token):
    users_url = f"{url}/admin/realms/{realm}/users"
    response = requests.get(users_url, headers=get_token_header(token), verify=False)
    response.raise_for_status()
    return response.json()


def create_realm(url, realm, token):
    realm_name = realm.get("realm")
    if not realm_name:
        raise Exception("The 'realm' dictionary must contain a 'realm' key.")

    th = get_token_header(token)

    # Check if the realm already exists
    check_url = f"{url}/admin/realms/{realm_name}"
    response = requests.get(check_url, headers=th, verify=False)

    # Update realm if it already exists
    if response.status_code == 200:
        update_url = f"{url}/admin/realms/{realm_name}"
        update_response = requests.put(update_url, headers=th, data=json.dumps(realm), verify=False)
        update_response.raise_for_status()

        # When updating a realm, users, roles, and clients are not updated automatically
        if "users" in realm:
            import_users(url, realm_name, token, realm["users"])
        if "roles" in realm:
            if "realmRoles" in realm["roles"]:
                raise Exception("Realm roles are not supported yet ...")
            if "clientRoles" in realm["roles"]:
                for client_id, roles in realm["roles"]["clientRoles"].items():
                    client_uuid = get_client_uuid_by_client_id(url, realm_name, token, client_id)
                    import_client_roles(url, realm_name, token, client_uuid, roles)
        if "clients" in realm:
            for client in realm["clients"]:
                import_client(url, realm_name, token, client)

        print(f"Realm {realm_name} updated successfully.")
        return

    realm_url = f"{url}/admin/realms"
    response = requests.post(realm_url, headers=th, data=json.dumps(realm), verify=False)
    response.raise_for_status()
    print(f"Realm {realm_name} created successfully.")


def send_email_for_password_setup(url, realm, token, user_id):
    send_email_url = f"{url}/admin/realms/{realm}/users/{user_id}/execute-actions-email"
    send_email_response = requests.put(send_email_url,
                                       headers=get_token_header(token),
                                       params={
                                           "lifespan": 3600 * 24 * 7,
                                           "client_id": "account-console",
                                       },
                                       data=json.dumps(["UPDATE_PASSWORD"]),
                                       verify=False)
    send_email_response.raise_for_status()


def get_token_header(token):
    return {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json"}


def get_realms(url, token):
    realms_url = f"{url}/admin/realms"
    response = requests.get(realms_url, headers=get_token_header(token), verify=False)
    response.raise_for_status()
    return response.json()


def import_users(url, realm, token, users):
    users_url = f"{url}/admin/realms/{realm}/users"
    credentials_url = lambda username: f"{url}/admin/realms/{realm}/users/{username}/credentials"
    th = get_token_header(token)

    for user in users:
        # Check if the user already exists
        response = requests.get(users_url, headers=th, params={"username": user["username"]}, verify=False)
        payload = response.json()
        user_uuid = payload[0]["id"] if len(payload) > 0 else None

        # Update user if it already exists
        if response.status_code == 200 and user_uuid:
            update_url = f"{users_url}/{user_uuid}"
            update_response = requests.put(update_url, headers=th, data=json.dumps(user), verify=False)
            update_response.raise_for_status()
            print(f"User {user['username']} updated successfully.")

        # Create a new user if it does not exist
        else:
            create_response = requests.post(users_url, headers=th, data=json.dumps(user), verify=False)
            create_response.raise_for_status()
            user_uuid = create_response.headers.get("Location").split("/")[-1]
            print(f"User {user['username']} created successfully.")

        credentials_response = requests.get(credentials_url(user_uuid), headers=th, verify=False)
        has_user_password = len(credentials_response.json()) > 0
        if not has_user_password:
            send_email_for_password_setup(url, realm, token, user_uuid)
        else:
            print(f"User {user['username']} already has a password. Skipping sending an email.")

        # Assign client roles
        if "clientRoles" in user:
            for client_id, roles_names in user["clientRoles"].items():
                client_uuid = get_client_uuid_by_client_id(url, realm, token, client_id)

                roles = []
                for role_name in roles_names:
                    role = get_client_role_by_role_name(url, realm, token, client_uuid, role_name)
                    roles.append(role)

                assign_roles_url = f"{url}/admin/realms/{realm}/users/{user_uuid}/role-mappings/clients/{client_uuid}"
                assign_response = requests.post(assign_roles_url, headers=th, data=json.dumps(roles), verify=False)
                assign_response.raise_for_status()
                print(f"Assigned roles {roles_names} to user {user['username']} for client {client_id}.")


def import_client(url, realm, token, client) -> str:
    """client: https://www.keycloak.org/docs-api/latest/rest-api/index.html?utm_source=chatgpt.com#ClientRepresentation"""
    clients_url = f"{url}/admin/realms/{realm}/clients"
    th = get_token_header(token)

    # Check if the client already exists
    response = requests.get(clients_url,
                            headers=th,
                            params={"clientId": client["clientId"]},
                            verify=False)

    # Update client if it already exists
    if response.status_code == 200 and len(response.json()) > 0:
        client_uuid = response.json()[0]["id"]
        update_url = f"{clients_url}/{client_uuid}"
        update_response = requests.put(update_url, headers=th, data=json.dumps(client), verify=False)
        update_response.raise_for_status()
        print(f"Client {client['clientId']} ({client_uuid}) updated successfully.")
        return client_uuid

    # Create a new client if it does not exist
    response = requests.post(clients_url, headers=th, data=json.dumps(client), verify=False)
    response.raise_for_status()
    location = response.headers["Location"]
    client_uuid = location.split("/")[-1]
    print(f"Client {client['clientId']} ({client_uuid}) created successfully.")
    return client_uuid


def import_client_roles(url, realm, token, client_uuid, roles):
    """role: https://www.keycloak.org/docs-api/latest/rest-api/index.html?utm_source=chatgpt.com#RoleRepresentation"""
    roles_url = f"{url}/admin/realms/{realm}/clients/{client_uuid}/roles"
    th = get_token_header(token)
    for role in roles:
        role_name = role.get("name")
        if not role_name:
            raise Exception(f"Role name not found in {role}")

        # Check if the role already exists
        response = requests.get(roles_url, headers=th, params={"search": role_name}, verify=False)

        # Update role if it already exists
        if response.status_code == 200 and len(response.json()) > 0:
            existing_role = response.json()[0]
            existing_role_name = existing_role.get("name")
            if existing_role_name == role_name:
                update_role_url = f"{roles_url}/{existing_role_name}"
                update_response = requests.put(update_role_url, data=json.dumps(role), headers=th, verify=False)
                update_response.raise_for_status()
                print(f"Role {role_name} updated successfully for client {client_uuid}.")
                continue
            else:
                raise Exception(f"Role name mismatch: expected {role_name}, found '{existing_role_name}'.")

        # Create a new role if it does not exist
        create_response = requests.post(roles_url, headers=th, data=json.dumps(role), verify=False)
        create_response.raise_for_status()
        print(f"Role {role_name} created successfully for client {client_uuid}.")


def get_client_roles(url, realm, token, client_uuid):
    roles_url = f"{url}/admin/realms/{realm}/clients/{client_uuid}/roles"
    response = requests.get(roles_url, headers=get_token_header(token), verify=False)
    response.raise_for_status()
    return response.json()


def get_client_roles_for_user(url, realm, token, user_id, client_uuid):
    roles_url = f"{url}/admin/realms/{realm}/users/{user_id}/role-mappings/clients/{client_uuid}"
    response = requests.get(roles_url, headers=get_token_header(token), verify=False)
    response.raise_for_status()
    return response.json()


def get_realm_roles(url, realm, token):
    roles_url = f"{url}/admin/realms/{realm}/roles"
    response = requests.get(roles_url, headers=get_token_header(token), verify=False)
    response.raise_for_status()
    return response.json()


def get_roles_for_user(url, realm, token, user_uuid):
    roles_url = f"{url}/admin/realms/{realm}/users/{user_uuid}/role-mappings/realm"
    response = requests.get(roles_url, headers=get_token_header(token), verify=False)
    response.raise_for_status()
    return response.json()


def get_client_uuid_by_client_id(url, realm, token, client_id):
    clients_url = f"{url}/admin/realms/{realm}/clients"
    response = requests.get(clients_url, headers=get_token_header(token), params={"clientId": client_id}, verify=False)
    response.raise_for_status()
    clients = response.json()
    if not clients:
        raise Exception(f"Client {client_id} not found in realm {realm}")
    return clients[0]["id"]


def get_client_role_by_role_name(url, realm, token, client_uuid, role_name):
    roles_url = f"{url}/admin/realms/{realm}/clients/{client_uuid}/roles"
    response = requests.get(roles_url, headers=get_token_header(token), params={"search": role_name}, verify=False)
    response.raise_for_status()
    roles = response.json()
    if not roles:
        raise Exception(f"Role {role_name} not found for client {client_uuid} in realm {realm}")
    return roles[0]
