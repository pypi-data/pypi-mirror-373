from __future__ import annotations

import ssl
import warnings
from pathlib import Path
from typing import (
    Any,
)

import exasol.bucketfs as bfs
import exasol.saas.client.api_access as saas_api
import ibis
import pyexasol
import sqlalchemy
from sqlalchemy.engine.url import URL

from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.ai_lab_config import StorageBackend
from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.utils import optional_str_to_bool


def _optional_encryption(conf: Secrets, key: CKey = CKey.db_encryption) -> bool | None:
    return optional_str_to_bool(conf.get(key))


def _extract_ssl_options(conf: Secrets) -> dict:
    """
    Extracts SSL parameters from the provided configuration.
    Returns a dictionary in the winsocket-client format
    (see https://websocket-client.readthedocs.io/en/latest/faq.html#what-else-can-i-do-with-sslopts)
    """
    sslopt: dict[str, object] = {}

    # Is server certificate validation required?
    certificate_validation = optional_str_to_bool(conf.get(CKey.cert_vld))
    if certificate_validation is not None:
        sslopt["cert_reqs"] = (
            ssl.CERT_REQUIRED if certificate_validation else ssl.CERT_NONE
        )

    # Is a bundle with trusted CAs provided?
    trusted_ca = conf.get(CKey.trusted_ca)
    if trusted_ca:
        trusted_ca_path = Path(trusted_ca)
        if trusted_ca_path.is_dir():
            sslopt["ca_cert_path"] = trusted_ca
        elif trusted_ca_path.is_file():
            sslopt["ca_certs"] = trusted_ca
        else:
            raise ValueError(f"Trusted CA location {trusted_ca} doesn't exist.")

    # Is client's own certificate provided?
    client_certificate = conf.get(CKey.client_cert)
    if client_certificate:
        if not Path(client_certificate).is_file():
            raise ValueError(f"Certificate file {client_certificate} doesn't exist.")
        sslopt["certfile"] = client_certificate
        private_key = conf.get(CKey.client_key)
        if private_key:
            if not Path(private_key).is_file():
                raise ValueError(f"Private key file {private_key} doesn't exist.")
            sslopt["keyfile"] = private_key

    return sslopt


def get_backend(conf: Secrets) -> StorageBackend:
    """
    Tries to find which backend was selected in the configuration. If the relevant
    configuration element is not there - which may be the case if the configuration
    has been created before the SaaS support was introduced - returns the
    StorageBackend.onprem.
    """
    storage_backend = conf.get(CKey.storage_backend, StorageBackend.onprem.name)
    return StorageBackend[storage_backend]  # type: ignore


def get_external_host(conf: Secrets) -> str:
    """Constructs the host part of a DB URL using provided configuration parameters."""
    return f"{conf.get(CKey.db_host_name)}:{conf.get(CKey.db_port)}"


def get_udf_bucket_path(conf: Secrets) -> str:
    """
    Builds the path of the BucketFS bucket specified in the configuration,
    as it's seen in the udf's file system.
    """
    bucket = open_bucketfs_bucket(conf)
    return bucket.udf_path


def get_saas_database_id(conf: Secrets) -> str:
    """
    Gets the SaaS database id using the available configuration elements.
    """
    saas_database_id = conf.get(CKey.saas_database_id)

    if saas_database_id:
        return saas_database_id

    return saas_api.get_database_id(
        host=conf[CKey.saas_url],
        account_id=conf[CKey.saas_account_id],
        pat=conf[CKey.saas_token],
        database_name=conf[CKey.saas_database_name],
    )


def _get_pyexasol_connection_params(conf: Secrets, **kwargs) -> dict[str, Any]:
    if get_backend(conf) == StorageBackend.onprem:
        conn_params: dict[str, Any] = {
            "dsn": get_external_host(conf),
            "user": conf.get(CKey.db_user),
            "password": conf.get(CKey.db_password),
        }
    else:
        conn_params = saas_api.get_connection_params(
            host=conf[CKey.saas_url],
            account_id=conf[CKey.saas_account_id],
            pat=conf[CKey.saas_token],
            database_id=conf.get(CKey.saas_database_id),
            database_name=conf.get(CKey.saas_database_name),
        )

    encryption = _optional_encryption(conf)
    if encryption is not None:
        conn_params["encryption"] = encryption
    ssopt = _extract_ssl_options(conf)
    if ssopt:
        conn_params["websocket_sslopt"] = ssopt

    conn_params.update(kwargs)
    return conn_params


def open_pyexasol_connection(conf: Secrets, **kwargs) -> pyexasol.ExaConnection:
    """
    Opens a pyexasol connection using provided configuration parameters.
    Supports both On-Prem and Saas backends.
    Does NOT set the default schema, even if it is defined in the configuration.

    Any additional parameters can be passed to pyexasol via the kwargs.
    Parameters in kwargs override the correspondent values in the configuration.

    The configuration should provide the following parameters:
    On-Prem:
        - Server address and port (db_host_name, db_port),
        - Client security credentials (db_user, db_password).
    Saas:
        - SaaS service url (saas_url),
        - SaaS account id (saas_account_id),
        - Database id or name (saas_database_id or saas_database_name),
        - Client security credentials (saas_token).
    Optional parameters include:
    - Secured comm flag (db_encryption),
    - Some of the SSL options (cert_vld, trusted_ca, client_cert).

    If the schema is not provided then it should be set explicitly in every SQL statement.
    For other optional parameters the default settings are as per the pyexasol interface.
    """

    conn_params = _get_pyexasol_connection_params(conf, **kwargs)
    return pyexasol.connect(**conn_params)


def open_sqlalchemy_connection(conf: Secrets):
    """
    Creates an Exasol SQLAlchemy websocket engine using provided configuration parameters.
    Supports both On-Prem and Saas backends.
    Sets the default schema if it is defined in the configuration.

    The configuration should provide the following parameters:
    On-Prem:
        - Server address and port (db_host_name, db_port),
        - Client security credentials (db_user, db_password).
    Saas:
        - SaaS service url (saas_url),
        - SaaS account id (saas_account_id),
        - Database id or name (saas_database_id or saas_database_name),
        - Client security credentials (saas_token).
    Optional parameters include:
    - Secured comm flag (db_encryption).
    - Validation of the server's TLS/SSL certificate by the client (cert_vld).

    If the schema is not provided then it should be set explicitly in every SQL statement.
    For other optional parameters the default settings are as per the Exasol SQLAlchemy interface.
    Currently, it's not possible to use a bundle of trusted CAs other than the default. Neither
    it is possible to set the client TLS/SSL certificate.
    """

    query_params = {}
    encryption = _optional_encryption(conf)
    if encryption is not None:
        query_params["ENCRYPTION"] = "Yes" if encryption else "No"
    certificate_validation = _extract_ssl_options(conf).get("cert_reqs")
    if (certificate_validation is not None) and (not certificate_validation):
        query_params["SSLCertificate"] = "SSL_VERIFY_NONE"

    if get_backend(conf) == StorageBackend.onprem:
        conn_params: dict[str, Any] = {
            "host": conf.get(CKey.db_host_name),
            "port": int(conf.get(CKey.db_port)),  # type: ignore
            "username": conf.get(CKey.db_user),
            "password": conf.get(CKey.db_password),
        }
    else:
        conn_params = saas_api.get_connection_params(
            host=conf[CKey.saas_url],
            account_id=conf[CKey.saas_account_id],
            pat=conf[CKey.saas_token],
            database_id=conf.get(CKey.saas_database_id),
            database_name=conf.get(CKey.saas_database_name),
        )
        host, port = str(conn_params["dsn"]).split(":")
        conn_params = {
            "host": host,
            "port": int(port),
            "username": conn_params["user"],
            "password": conn_params["password"],
        }

    websocket_url = URL.create(
        "exa+websocket",
        **conn_params,
        database=conf.get(CKey.db_schema),
        query=query_params,
    )

    return sqlalchemy.create_engine(websocket_url)


def _get_onprem_bucketfs_url(conf: Secrets) -> str:
    bucketfs_url_prefix = (
        "https" if _optional_encryption(conf, CKey.bfs_encryption) else "http"
    )
    bucketfs_host = conf.get(CKey.bfs_host_name, conf.get(CKey.db_host_name))
    return f"{bucketfs_url_prefix}://{bucketfs_host}:{conf.get(CKey.bfs_port)}"


def _get_ca_cert_verification(conf: Secrets) -> Any:
    sslopt = _extract_ssl_options(conf)
    verify = sslopt.get("cert_reqs") == ssl.CERT_REQUIRED
    return sslopt.get("ca_certs") or sslopt.get("ca_cert_path") or verify


def open_bucketfs_connection(conf: Secrets) -> bfs.BucketLike:
    """
    This function is deprecated, please use open_bucketfs_bucket(conf) instead.
    """

    warnings.warn(
        "open_bucketfs_connection is deprecated. Use open_bucketfs_bucket instead.",
        DeprecationWarning,
    )
    return open_bucketfs_bucket(conf)


def open_bucketfs_bucket(conf: Secrets) -> bfs.BucketLike:
    """
    Connects to a BucketFS service using provided configuration parameters.
    Returns the BucketLike object for the bucket selected in the configuration.
    Supports both On-Prem and Saas backends.

    The configuration should provide the following parameters;
    On-Prem:
        - Host name and port of the BucketFS service (bfs_host_name or db_host_name, bfs_port),
        - Client security credentials (bfs_user, bfs_password).
        - Bucket name (bfs_bucket)
        Optional parameters include:
        - Secured comm flag (bfs_encryption), defaults to False.
        - Some of the SSL options (cert_vld, trusted_ca).
    Saas:
        - SaaS service url (saas_url),
        - SaaS account id (saas_account_id),
        - Database id or name (saas_database_id or saas_database_name),
        - Client security credentials (saas_token).
    """

    if get_backend(conf) == StorageBackend.onprem:
        bucketfs_url = _get_onprem_bucketfs_url(conf)
        verify = _get_ca_cert_verification(conf)
        bucketfs_credentials = {
            conf.get(CKey.bfs_bucket): {
                "username": conf.get(CKey.bfs_user),
                "password": conf.get(CKey.bfs_password),
            }
        }

        # Connect to the BucketFS service and navigate to the bucket of choice.
        bucketfs = bfs.Service(
            bucketfs_url,
            bucketfs_credentials,  # type: ignore
            verify,  # type: ignore
            conf.get(CKey.bfs_service),
        )
        return bucketfs[conf.get(CKey.bfs_bucket)]  # type: ignore

    else:
        saas_url, saas_token, saas_account_id = (
            conf.get(key)
            for key in [CKey.saas_url, CKey.saas_token, CKey.saas_account_id]
        )
        saas_database_id = get_saas_database_id(conf)
        return bfs.SaaSBucket(
            url=saas_url,  # type: ignore
            account_id=saas_account_id,  # type: ignore
            database_id=saas_database_id,  # type: ignore
            pat=saas_token,  # type: ignore
        )


def open_bucketfs_location(conf: Secrets) -> bfs.path.PathLike:
    """
    Similar to `open_buckets_connection`, but returns a PathLike interface.
    """
    if get_backend(conf) == StorageBackend.onprem:
        return bfs.path.build_path(
            backend=bfs.path.StorageBackend.onprem,
            url=_get_onprem_bucketfs_url(conf),
            username=conf.get(CKey.bfs_user),
            password=conf.get(CKey.bfs_password),
            verify=_get_ca_cert_verification(conf),
            bucket_name=conf.get(CKey.bfs_bucket),
            service_name=conf.get(CKey.bfs_service),
        )
    else:
        return bfs.path.build_path(
            backend=bfs.path.StorageBackend.saas,
            url=conf.get(CKey.saas_url),
            account_id=conf.get(CKey.saas_account_id),
            database_id=get_saas_database_id(conf),
            pat=conf.get(CKey.saas_token),
        )


def open_ibis_connection(conf: Secrets, **kwargs):
    """
    Creates a connection to Ibis with Exasol backend.

    The parameters are similar to those of open_pyexasol_connection function.
    The downstream call signature is also similar to pyexasol, except that the dsn is
    provided in two separate parts - host and port.

    Unlike open_pyexasol_connection, this function sets the default schema if it's
    defined in the configuration.
    """

    conn_params = _get_pyexasol_connection_params(conf, **kwargs)

    dsn = conn_params.pop("dsn")
    host_port = dsn.split(":")
    conn_params["host"] = host_port[0]
    if len(host_port) > 1:
        conn_params["port"] = int(host_port[1])

    schema = conf.get(CKey.db_schema)
    if schema:
        conn_params["schema"] = schema

    return ibis.exasol.connect(**conn_params)
