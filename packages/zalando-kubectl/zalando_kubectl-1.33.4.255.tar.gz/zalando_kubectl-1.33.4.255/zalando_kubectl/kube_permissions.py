import base64
import requests
import tempfile

_NO_ROLES_FOUND_ERROR = """No roles found for cluster "{}", please request a role for the cluster's product community (see https://cloud.docs.zalando.net/howtos/product-clusters/ for details).
If you already have the community role, please try requesting it again. It can fail to be provisioned correctly due to a bug in ZACK.
If requesting the role again doesn't work, please contact support at https://sunrise.zalando.net/support/setup/zack"""


def check_cluster_permissions(cluster_url, cluster_alias, token, ca=None):
    """Checks the cluster permissions of a user"""

    verify = True
    if ca is not None:
        ca_cert = tempfile.NamedTemporaryFile()
        ca_cert.write(base64.b64decode(ca))
        ca_cert.flush()
        verify = ca_cert.name

    response = requests.post(
        "{}/apis/authorization.k8s.io/v1/selfsubjectaccessreviews".format(cluster_url),
        json={
            "kind": "SelfSubjectAccessReview",
            "apiVersion": "authorization.k8s.io/v1",
            "spec": {"resourceAttributes": {"namespace": "default", "verb": "get", "resource": "pods"}},
        },
        headers={"Authorization": "Bearer {}".format(token)},
        verify=verify,
        timeout=20,
    )

    if ca is not None:
        ca_cert.close()

    response.raise_for_status()
    data = response.json()
    if not data["status"]["allowed"]:
        raise ValueError(_NO_ROLES_FOUND_ERROR.format(cluster_alias))
