from __future__ import annotations

from exasol.slc.models.compression_strategy import CompressionStrategy

from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.slc.slc_error import SlcError


class SlcCompressionStrategy:
    def __init__(self, slc_name):
        self.slc_name = slc_name

    @property
    def key(self):
        return f"SLC_COMPRESSION_STRATEGY_{self.slc_name.upper()}"

    def save(self, secrets: Secrets, compression_strategy: CompressionStrategy) -> None:
        secrets.save(self.key, compression_strategy.value)

    def exists(self, secrets: Secrets) -> bool:
        return True if secrets.get(self.key) else False

    def verify(self, secrets: Secrets) -> CompressionStrategy:
        try:
            value = secrets[self.key]
            return CompressionStrategy(value)
        except AttributeError as ex:
            raise SlcError(
                "Secure Configuration Storage does not contain a"
                f" compression strategy for SLC {self.slc_name}."
            ) from ex
