import base64
import subprocess
from zalando_kubectl.utils import auth_token, Environment, ExternalBinary

_ENCRYPT_ROLES = ("ReadOnly", "Deployer", "Manual", "Emergency", "Administrator", "PowerUser")
_DECRYPT_ROLES = ("Manual", "Emergency", "Administrator", "PowerUser")


def zalando_aws_cli_run(zalando_aws_cli: ExternalBinary, *cmd):
    return zalando_aws_cli.run(
        cmd, check=True, stdout=subprocess.PIPE, forward_context=False, forward_namespace=False
    ).stdout


def find_aws_role(token, account_id, roles):
    """Returns the best matching AWS role for the provided account"""
    user_roles = zalando_aws_cli.api.get_roles(token)
    matching_roles = [role for role in user_roles if role.account_id == account_id and role.role_name in roles]

    # Order the roles in the order of preference
    matching_roles.sort(key=lambda role: roles.index(role.role_name))

    if matching_roles:
        return matching_roles[0]
    else:
        return None


def encrypt_with_okta(env: Environment, account_metadata, kms_keyid, role, strip, plain_text):
    cmdline = [
        "--target-account={}".format(account_metadata["name"]),
        "encrypt",
    ]
    if not strip:
        cmdline.append("--strip=false")
    if kms_keyid:
        cmdline.append("--kms-keyid={}".format(kms_keyid))
    if role:
        cmdline.append("--roles={}".format(role))
    cmdline.extend(
        [
            "--",
            plain_text,
        ]
    )

    return zalando_aws_cli_run(env.zalando_aws_cli, *cmdline)


def decrypt_with_okta(env: Environment, role, encrypted_value):
    cmdline = [
        "decrypt",
    ]
    if role:
        cmdline.append("--roles={}".format(role))
    cmdline.extend(
        [
            "--",
            encrypted_value,
        ]
    )

    return zalando_aws_cli_run(env.zalando_aws_cli, *cmdline)
