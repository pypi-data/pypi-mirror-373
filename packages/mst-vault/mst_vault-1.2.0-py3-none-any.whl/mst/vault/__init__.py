import logging
import os
from typing import Optional
from pathlib import Path
import hvac
from mst.core import LogAPIUsage


log = logging.getLogger(__name__)


class MSTVault:
    """Allows retrieving secrets from the vault server.

    Depending on constructor params, may authenticate to vault server using one of the following
    mechanisms:

    * use pre-existing authentication
    * use "approle" login
    * use token read from environment variable
    * use token read from file

    For reading token from file, requires a token in either ``/vault/secrets/token`` or
    ``/run/secrets/kubernetes.io/serviceaccount/token`` to initialize, prioritizing the former.

    :param role_id: Optional role ID to use for "approle" login.

    :param secret_id: Optional secret ID to use for "approle" login.

    :param force: Set to ``True`` to force authentication to happen
       here, and *ignore* any pre-existing authentication.  This is
       ``False`` by default, which means pre-existing authentication
       will be used if available.

    :raises RuntimeError: if authentication is unsuccessful.
    """

    def __init__(self, role_id=None, secret_id=None, force=False):
        self.vault_addr = os.getenv("VAULT_ADDR", "https://vault.mst.edu")
        self.app_user = os.getenv("APP_USER")

        # try to use pre-existing auth unless user "forces" new auth
        if not force:
            client = hvac.Client(url=self.vault_addr)
            if client.is_authenticated():
                log.debug("already authenticated to vault with filesystem token")
                self.client = client
                return

        # try to use 'approle' login
        if role_id and secret_id:
            client = hvac.Client(url=self.vault_addr)
            login_info = client.auth.approle.login(role_id=role_id, secret_id=secret_id)
            if client.is_authenticated():
                log.debug("authenticated to vault with role_id and secret_id")
                self.client = client
                self.ephemeral_token = login_info["auth"]["client_token"]
                self.login_info = login_info
                return
            raise RuntimeError("vault client could not authenticate (via approle login)")

        # try to use token from environment variable
        token = os.getenv("VAULT_TOKEN")
        if token:
            client = hvac.Client(url=self.vault_addr, token=token)
            if client.is_authenticated():
                log.debug("authenticated to vault with VAULT_TOKEN in env")
                self.client = client
                return
            raise RuntimeError("vault client could not authenticate (via VAULT_TOKEN env var)")

        t = Path("/vault/secrets/token")
        f = Path("/run/secrets/kubernetes.io/serviceaccount/token")

        if t.is_file():
            token = t.read_text(encoding="utf8").strip()
            client = hvac.Client(url=self.vault_addr, token=token)
            try:
                if client.is_authenticated():
                    self.client = client
            except Exception as err:
                raise RuntimeError("vault client could not authenticate")
        elif f.is_file() and self.app_user:
            k8s_jwt = f.read_text(encoding="utf8")
            client = hvac.Client(url=self.vault_addr)

            mounts = []
            if os.getenv("VAULT_K8S_MOUNT"):
                mounts.append("VAULT_K8S_MOUNT")
            else:
                if not os.getenv("LOCAL_ENV") or "dev" in os.getenv("LOCAL_ENV"):
                    mounts.append("rke-apps-d")
                if not os.getenv("LOCAL_ENV") or "test" in os.getenv("LOCAL_ENV"):
                    mounts.append("rke-apps-t")
                if not os.getenv("LOCAL_ENV") or "prod" in os.getenv("LOCAL_ENV"):
                    mounts.append("rke-apps-p")

                for mount in mounts:
                    res = client.auth.jwt.jwt_login(role=f"app-{self.app_user}", jwt=k8s_jwt, path=mount)
                    if res and res["auth"]["client_token"]:
                        client = hvac.Client(url=self.vault_addr, token=res["auth"]["client_token"])
                        try:
                            if client.is_authenticated():
                                self.client = client
                                break
                        except Exception as err:
                            raise RuntimeError("vault client could not authenticate")

        else:
            raise RuntimeError("Vault Client not configured or is missing!")

    def read_secret(self, path: str) -> Optional[str]:
        """Reads a secret value from the given path

        Args:
            path (str): the path on vault to the secret

        Returns:
            Optional[str]: The value of the secret or none if it does not exist
        """
        LogAPIUsage()
        secrets = self.client.secrets.kv.v1.read_secret(mount_point="secret", path=f"data/{path}")
        return secrets["data"]["data"]
