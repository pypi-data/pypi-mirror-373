import shutil

import requests


def requests_get(href: str, dst: str, headers: dict):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(href, headers=headers, stream=True, verify=False)  # NOSONAR

    with open(dst, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)


def requests_head(href: str, headers: dict) -> requests.Response:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    r = requests.head(href, headers=headers, verify=False)  # NOSONAR
    return r


def requests_exists(href: str, headers: dict) -> bool:
    r = requests_head(href, headers)
    return r.status_code >= 200 and r.status_code < 300
