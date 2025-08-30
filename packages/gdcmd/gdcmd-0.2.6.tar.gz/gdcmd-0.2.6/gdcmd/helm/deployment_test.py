import os
import urllib
from time import sleep
from urllib import parse

from gdcmd.helm.values import ValuesYaml
import requests

VERBOSE = False
ERRORS = 0


def log(msg: str):
    if VERBOSE:
        print(msg)


def log_error(msg: str):
    global ERRORS
    ERRORS += 1
    print(msg)


def deployment_test(path: str, verbose: bool = False):
    global VERBOSE
    global ERRORS
    VERBOSE = verbose
    try:
        content = open(path, 'r').read()
        log("Found values file:")
        log(f"{content}\n")

        values = ValuesYaml.from_str(content)
    except Exception as e:
        log_error(f"Error parsing values file '{path}': \n{e}")
        return

    active_services: list[str] = []

    if values.deploy.link:
        active_services.append(f"http://{values.link.app.host}:4002")
        if values.common.requireHttps:
            active_services.append(f"https://link-pod:4003")

    if values.deploy.sync:
        active_services.append(f"http://{values.sync.app.host}:4002")
        if values.common.requireHttps:
            active_services.append(f"https://{values.sync.app.host}:4003")

    if values.deploy.keycloak:
        active_services.append(f"http://{values.keycloak.host}:8080")

    for service in active_services:
        ensure_url_is_reachable(service, retries=30)

    url = values.prometheus.cloudGrafanaRemoteWrite.url
    labels = f'reseller="{values.common.reseller}",tenant="{values.common.tenant}"'
    u = values.prometheus.cloudGrafanaRemoteWrite.username
    p = os.getenv("CLOUD_GRAFANA_READ_ACCESS_KEY", None)

    if not p:
        log_error("Environment variable CLOUD_GRAFANA_READ_ACCESS_KEY is not set, cannot test metrics")
        return

    if values.deploy.prometheus:
        if values.prometheus.nodeExporter:
            ensure_query_exists(f'node_cpu_seconds_total{{{labels}}}', url, u, p)
        if values.deploy.sync:
            ensure_query_exists(f'{{{labels},app="sync",__name__=~"griddot_.*"}}', url, u, p)
            if values.deploy.db and values.prometheus.databaseExporter:
                ensure_query_exists(f'pg_up{{{labels},app="sync"}}', url, u, p)
        if values.deploy.link:
            ensure_query_exists(f'{{{labels},app="link",__name__=~"griddot_.*"}}', url, u, p)
            if values.deploy.db and values.prometheus.databaseExporter:
                ensure_query_exists(f'pg_up{{{labels},app="link"}}', url, u, p)

    if ERRORS > 0:
        log_error(f"Deployment test completed with {ERRORS} errors. Check the logs above for details.")

    # TODO: test systemd is working
    # TODO: test promtail is working
    # TODO: test normal logs in containers are working

    # TODO: For db we set memory limits, which can be more than available, test this
    # TODO: Go through the whole helm installation config and check if something is missing
    # TODO: Go through the whole values.yaml and check if something is missing


def ensure_url_is_reachable(url: str, retries: int):
    requests_session = requests.Session()
    requests_session.verify = False
    for i in range(retries):
        try:
            response = requests_session.get(url)
            if response.status_code == 200:
                log(f"URL {url} is reachable")
                return
            else:
                if i == retries - 1:
                    log_error(f"URL {url} returned status code {response.status_code}")
        except requests.RequestException as e:
            sleep(5)
            if i == retries - 1:
                log_error(f"Error connecting to URL {url}: {e}")


def ensure_query_exists(query, remote_write_url, username, password):
    url = remote_write_url.replace("api/prom/push", "api/prom/api/v1/query")
    response = requests.get(url, params={"query": query}, auth=(username, password), timeout=20)
    decoded_url = parse.unquote(response.url)

    # Check result
    response.raise_for_status()
    json = response.json()
    if not json.get("data") and not json.get("data").get("result"):
        log_error(f"No result found in the response for user {username} in {decoded_url}: {json}")
        return

    result = json.get("data", {}).get("result", [])
    if len(result) == 0:
        log_error(f"No results found in the response for user {username} in {decoded_url}: {json}")
        return

    log(f"Found {len(result)} series for query {query}")


if __name__ == "__main__":
    VERBOSE = True
    ensure_query_exists('node_cpu_seconds_total{cluster="eg"}',
                        "https://prometheus-prod-01-eu-west-0.grafana.net/api/prom/push",
                        "772948",
                        "glc_eyJvIjoiNzk0NTA1IiwibiI6InJlYWQtYWNjZXNzLWhlbG0tZGVwbG95bWVudC10ZXN0ZXIiLCJrIjoibkM3bWVnOTlhNzlCM2FJSTU5anBMcDQ2IiwibSI6eyJyIjoiZXUifX0="
                        )
