from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.extension_wrapper_common import (
    encapsulate_bucketfs_credentials,
)
from exasol.nb_connector.secret_store import Secrets

DEF_BFS_CONNECTION_NAME = "bfs_ai_lab_connection"

PATH_IN_BUCKET = "ai-lab"
""" Location in BucketFS bucket to upload data for Extensions, e.g. its language container. """


def ensure_bfs_connection_name(conf: Secrets) -> str:
    connection_name = conf.get(CKey.bfs_connection_name)
    if connection_name is None:
        conf.save(CKey.bfs_connection_name, DEF_BFS_CONNECTION_NAME)
        connection_name = DEF_BFS_CONNECTION_NAME
    return connection_name


def ensure_bfs_connection(conf: Secrets) -> None:
    """
    Creates a connection object in the database encapsulating
    a location in the BucketFS and BucketFS access credentials, if no connection was created yet.
    The path in the bucket is the hard-coded value for models.
    The connection name will be used from Secret-Store (Key='bfs_connection_name') if exists, otherwise
    "DEF_BFS_CONNECTION_NAME" will be used.
    Parameters:
         conf:
            The secret store.
    """
    encapsulate_bucketfs_credentials(
        conf,
        path_in_bucket=PATH_IN_BUCKET,
        connection_name=ensure_bfs_connection_name(conf),
    )
