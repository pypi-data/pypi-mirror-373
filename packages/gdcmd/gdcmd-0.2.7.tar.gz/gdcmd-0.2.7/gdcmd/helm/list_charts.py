import requests
from requests.auth import HTTPBasicAuth
import yaml


def list_charts():
    encoded_project = requests.utils.quote("griddot/packages", safe="")
    url = f"https://gitlab.com/api/v4/projects/{encoded_project}/packages/helm/stable/index.yaml"

    # GitLab expects: username = anything (often 'gitlab-ci-token'), password = the token
    auth = HTTPBasicAuth("helm-user", "glpat-mKckaB2sg2vC74xzFWWB")  # or "gitlab-ci-token", token

    response = requests.get(url, auth=auth)
    response.raise_for_status()

    index = yaml.safe_load(response.text)
    charts = list(index.get("entries", {}).keys())
    charts = [f"griddot/{chart}" for chart in charts]
    return charts
