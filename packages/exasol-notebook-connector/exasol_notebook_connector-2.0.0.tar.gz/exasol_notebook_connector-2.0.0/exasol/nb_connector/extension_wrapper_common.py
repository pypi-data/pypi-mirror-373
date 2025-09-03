from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import exasol.bucketfs as bfs
from exasol.python_extension_common.deployment.extract_validator import ExtractValidator
from exasol.python_extension_common.deployment.language_container_deployer import (
    LanguageContainerDeployer,
)

from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.ai_lab_config import StorageBackend
from exasol.nb_connector.connections import (
    get_backend,
    get_external_host,
    get_saas_database_id,
    open_bucketfs_location,
    open_pyexasol_connection,
)
from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.utils import optional_str_to_bool

PATH_IN_BUCKET_FOR_SLC = "ai-lab/slc"
"""
Location to deploy Script-Language-Contains relatively to bucket in BucketFS.
"""


def str_to_bool(conf: Secrets, key: CKey, default_value: bool) -> bool:
    """
    Tries to read a binary (i.e. yes/no) value from the secret store. If found
    returns the correspondent boolean. Otherwise, returns the provided default
    value.

    Parameters:
        conf:
            The secret store.
        key:
            The binary value key in the secret store.
        default_value:
            Default value if the key is not in the secret store.
    """
    prop_value = optional_str_to_bool(conf.get(key))
    return default_value if prop_value is None else prop_value


def _get_optional_external_host(conf: Secrets) -> str | None:
    """
    Get the host part of an onprem database URL if the data can be found
    in the configuration, otherwise None.
    """
    if conf.get(CKey.db_host_name) and conf.get(CKey.db_port):
        return get_external_host(conf)
    return None


def _get_optional_bfs_port(conf: Secrets) -> int | None:
    """
    Return the BucketFS service port number if it can be found in the
    configuration, otherwise None.
    """
    port_str = conf.get(CKey.bfs_port)
    if port_str:
        return int(port_str)
    return None


def deploy_language_container(
    conf: Secrets,
    path_in_bucket: str,
    language_alias: str,
    activation_key: str,
    container_url: str | None = None,
    container_file: Path | None = None,
    container_name: str | None = None,
    allow_override: bool = True,
    timeout: timedelta = timedelta(minutes=10),
) -> None:
    """
    Downloads language container from the specified location and uploads it to the
    BucketFS.

    This function doesn't activate the language container. Instead, it generates the
    activation SQL command and writes it to the secret store using the provided key.

    Parameters:
        conf:
            The secret store. The store must contain the DB connection parameters
            and the parameters of the BucketFS service.
        path_in_bucket:
            Path in the BucketFS where the container should be saved.
        language_alias:
            The language alias of the extension's language container.
        activation_key:
            A secret store key for saving the activation SQL.
        container_url:
            An optional URL to download the language container from.
            Either the `container_url` or `container_file` must be provided,
            otherwise a ValueError will be raised.
        container_file:
            An optional path of the container file (*.tar.gz) in a local file system.
            Either the `container_url` or `container_file` must be provided,
            otherwise a ValueError will be raised.
        container_name:
            If provided, the language container will be saved in given bucket of
            BucketFS with this filename. Otherwise, the name of the container file
            will be used.
        allow_override:
            If True allows overriding the language definition.
        timeout:
            Maximum time allowed for saving the container in the BucketFS.
            This includes the time required to unpack the container.
            The downloading time is not included.
    """

    with open_pyexasol_connection(conf, compression=True) as conn:
        validator = ExtractValidator(conn, timeout)
        bucketfs_location = open_bucketfs_location(conf) / path_in_bucket
        deployer = LanguageContainerDeployer(
            pyexasol_connection=conn,
            language_alias=language_alias,
            bucketfs_path=bucketfs_location,
            extract_validator=validator,
        )

        if container_file:
            deployer.run(
                container_file,
                container_name,
                alter_system=False,
                allow_override=allow_override,
                wait_for_completion=True,
            )
        elif container_url:
            deployer.download_and_run(
                container_url,
                container_name,
                alter_system=False,
                allow_override=allow_override,
                wait_for_completion=True,
            )
        else:
            raise ValueError("Either container URL or container file must be provided")

        # Install the language container.
        # Save the activation SQL in the secret store.
        language_def = deployer.get_language_definition(container_name)
        conf.save(activation_key, language_def)


def encapsulate_bucketfs_credentials(
    conf: Secrets, path_in_bucket: str, connection_name: str
) -> None:
    """
    Creates a connection object in the database encapsulating
    a location in the BucketFS and BucketFS access credentials.

    Parameters:
        conf:
            The secret store.
            For an On-Prem database the store must hold the BucketFS service
            parameters (bfs_host_name or db_host_name, bfs_port,
            bfs_service), the access credentials (bfs_user,
            bfs_password), and the bucket name (bfs_bucket), as well
            as the DB connection parameters.
            For a SaaS database the store must hold the SaaS connection
            parameters (saas_url, saas_account_id, saas_database_id or
            saas_database_name, saas_token).
        path_in_bucket:
            Path identifying a location in the bucket.
        connection_name:
            Name for the connection object to be created.

    The parameters will be stored in json strings. The distribution
    of the parameters among the connection entities will be as following.
    On-Prem:
        TO: backend, url, service_name, bucket_name, verify, path
        USER: username
        IDENTIFIED BY: password
    SaaS:
        TO: backend, url, account_id, path
        USER: database_id
        IDENTIFIED BY: pat

    Note that the parameter names correspond to the arguments of the build_path
    function. provided by the bucketfs-python. Hence, the most convenient way to
    handle this lot is to combine json structures from all three entities and
    pass them as kwargs to the build_path. The code below gives a usage example.

    bfs_params = json.loads(conn_obj.address)
    bfs_params.update(json.loads(conn_obj.user))
    bfs_params.update(json.loads(conn_obj.password))
    bfs_path = build_path(**bfs_params)

    A note about handling the TLS certificate verification settings.
    If the server certificate verification is turned on, either through
    reliance of the default https request settings or by setting the cert_vld
    configuration parameter to True, this intention will be passed to
    the connection object. However, if the user specifies a custom CA list
    file or directory, which also implies the certificate verification,
    the connection object will instead turn the verification off. This is
    because there is no guarantee that the consumer of the connection object,
    i.e. a UDF, would have this custom CA list, and even if it would, its location
    is unknown. This is only applicable for an On-Prem backend.
    """

    def to_json_str(**kwargs) -> str:
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return json.dumps(filtered_kwargs)

    backend = get_backend(conf)
    if backend == StorageBackend.onprem:
        # Here we are using the internal bucket-fs host and port, falling back
        # to the external parameters if the former are not specified.
        host = conf.get(
            CKey.bfs_internal_host_name,
            conf.get(CKey.bfs_host_name, conf.get(CKey.db_host_name)),
        )
        port = conf.get(CKey.bfs_internal_port, conf.get(CKey.bfs_port))
        protocol = "https" if str_to_bool(conf, CKey.bfs_encryption, True) else "http"
        url = f"{protocol}://{host}:{port}"
        verify: bool | None = (
            False
            if conf.get(CKey.trusted_ca)
            else optional_str_to_bool(conf.get(CKey.cert_vld))
        )
        conn_to = to_json_str(
            backend=bfs.path.StorageBackend.onprem.name,
            url=url,
            service_name=conf.get(CKey.bfs_service),
            bucket_name=conf.get(CKey.bfs_bucket),
            path=path_in_bucket,
            verify=verify,
        )
        conn_user = to_json_str(username=conf.get(CKey.bfs_user))
        conn_password = to_json_str(password=conf.get(CKey.bfs_password))
    else:
        database_id = get_saas_database_id(conf)
        conn_to = to_json_str(
            backend=bfs.path.StorageBackend.saas.name,
            url=conf.get(CKey.saas_url),
            account_id=conf.get(CKey.saas_account_id),
            path=path_in_bucket,
        )
        conn_user = to_json_str(database_id=database_id)
        conn_password = to_json_str(pat=conf.get(CKey.saas_token))

    sql = f"""
    CREATE OR REPLACE CONNECTION [{connection_name}]
        TO {{BUCKETFS_ADDRESS!s}}
        USER {{BUCKETFS_USER!s}}
        IDENTIFIED BY {{BUCKETFS_PASSWORD!s}}
    """
    query_params = {
        "BUCKETFS_ADDRESS": conn_to,
        "BUCKETFS_USER": conn_user,
        "BUCKETFS_PASSWORD": conn_password,
    }
    with open_pyexasol_connection(conf, compression=True) as conn:
        conn.execute(query=sql, query_params=query_params)


def encapsulate_huggingface_token(conf: Secrets, connection_name: str) -> None:
    """
    Creates a connection object in the database encapsulating a Huggingface token.

    Parameters:
        conf:
            The secret store. The store must hold the Huggingface token (huggingface_token),
             as well as the DB connection parameters.
        connection_name:
            Name for the connection object to be created.
    """

    sql = f"""
    CREATE OR REPLACE CONNECTION [{connection_name}]
        TO ''
        IDENTIFIED BY {{TOKEN!s}}
    """
    query_params = {"TOKEN": conf.get(CKey.huggingface_token)}
    with open_pyexasol_connection(conf, compression=True) as conn:
        conn.execute(query=sql, query_params=query_params)


def encapsulate_aws_credentials(
    conf: Secrets, connection_name: str, s3_bucket_key: CKey
) -> None:
    """
    Creates a connection object in the database encapsulating the address of
    an AWS S3 bucket and AWS access credentials.

    Parameters:
        conf:
            The secret store. The store must hold the S3 bucket parameters
            (aws_bucket, aws_region) and AWS access credentials (aws_access_key_id,
            aws_secret_access_key), as well as the DB connection parameters.
        connection_name:
            Name for the connection object to be created.
        s3_bucket_key:
            The secret store key of the AWS S3 bucket name.
    """

    sql = f"""
    CREATE OR REPLACE  CONNECTION [{connection_name}]
        TO 'https://{conf.get(s3_bucket_key)}.s3.{conf.get(CKey.aws_region)}.amazonaws.com/'
        USER {{ACCESS_ID!s}}
        IDENTIFIED BY {{SECRET_KEY!s}}
    """
    query_params = {
        "ACCESS_ID": conf.get(CKey.aws_access_key_id),
        "SECRET_KEY": conf.get(CKey.aws_secret_access_key),
    }
    with open_pyexasol_connection(conf, compression=True) as conn:
        conn.execute(query=sql, query_params=query_params)
