from __future__ import annotations

from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.slc.slc_error import SlcError


class SlcFlavor:
    def __init__(self, slc_name: str):
        self.slc_name = slc_name

    @property
    def key(self):
        return f"SLC_FLAVOR_{self.slc_name.upper()}"

    def save(self, secrets: Secrets, flavor: str) -> None:
        secrets.save(self.key, flavor)

    def exists(self, secrets: Secrets) -> bool:
        return True if secrets.get(self.key) else False

    def verify(self, secrets: Secrets) -> str:
        try:
            return secrets[self.key]
        except AttributeError as ex:
            raise SlcError(
                "Secure Configuration Storage does not contain a"
                f" flavor for SLC {self.slc_name}."
            ) from ex
