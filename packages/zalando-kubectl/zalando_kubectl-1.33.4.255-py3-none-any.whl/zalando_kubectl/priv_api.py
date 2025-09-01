from dataclasses import asdict, dataclass
from typing import Any

import requests


@dataclass
class PrivRequest:
    account_name: str
    business_justification: str
    access_type: str
    reference_url: str


@dataclass
class ListRequests:
    requestor: str
    account_name: str
    request_key: str


@dataclass
class PrivApprove:
    request_key: str
    requestor: str
    account_name: str
    business_justification: str
    decision: str
    approver_comment: str


def post_request(priv_api_url, auth_header, request: PrivRequest) -> requests.Response:
    """Posts access request to privileged access api"""

    priv_endpoint = f"{priv_api_url}/v1/requests/tech/{request.access_type}/cloud-infrastructure/aws/account"

    payload = {
        "account_name": request.account_name,
        "business_justification": request.business_justification,
        "access_role": "default",
    }

    if request.access_type == "emergency":
        payload["reference_url"] = request.reference_url

    response = requests.post(
        priv_endpoint,
        json=payload,
        headers=auth_header,
    )

    return response


def list_requests(priv_api_url, auth_header, request: ListRequests) -> requests.Response:
    """Lists access requests based on provided filters"""

    priv_endpoint = f"{priv_api_url}/v1/requests/tech/cloud-infrastructure/aws/account"

    request_dict = asdict(request)

    params = {}
    for i in ["requestor", "account_name", "request_key"]:
        if request_dict[i]:
            params[i] = request_dict[i]

    response = requests.get(
        priv_endpoint,
        params=params,
        headers=auth_header,
    )

    return response


def post_approve(priv_api_url, auth_header, request: PrivApprove) -> requests.Response:
    """Post approve request to privileged access api"""

    priv_endpoint = f"{priv_api_url}/v1/approve/tech/privileged/cloud-infrastructure/aws/account"

    payload = {
        "requestor": request.requestor,
        "account_name": request.account_name,
        "business_justification": request.business_justification,
        "access_role": "default",
        "request_key": request.request_key,
        "decision": request.decision,
        "approver_comment": request.approver_comment,
    }

    response = requests.post(
        priv_endpoint,
        json=payload,
        headers=auth_header,
    )

    return response
