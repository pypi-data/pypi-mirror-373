from importlib.metadata import version

from exasol_transformers_extension.deployment.scripts_deployer import ScriptsDeployer
from exasol_transformers_extension.deployment.te_language_container_deployer import (
    TeLanguageContainerDeployer,
)

from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.bfs_connection import ensure_bfs_connection
from exasol.nb_connector.connections import open_pyexasol_connection
from exasol.nb_connector.extension_wrapper_common import (
    PATH_IN_BUCKET_FOR_SLC,
    deploy_language_container,
    encapsulate_huggingface_token,
)
from exasol.nb_connector.language_container_activation import (
    ACTIVATION_KEY_PREFIX,
    get_activation_sql,
)
from exasol.nb_connector.model_installation import ensure_model_subdir_config_value
from exasol.nb_connector.secret_store import Secrets

LANGUAGE_ALIAS = "PYTHON3_TE"

LATEST_KNOWN_VERSION = version("exasol_transformers_extension")

# Activation SQL for the Transformers Extension will be saved in the secret
# store with this key.
ACTIVATION_KEY = ACTIVATION_KEY_PREFIX + "te"

# The name of the connection object with BucketFS location and credentials
# will be prefixed with this string.
BFS_CONNECTION_PREFIX = "TE_BFS"

# The name of the connection object with a Huggingface token will be prefixed
# with this string.
HF_CONNECTION_PREFIX = "TE_HF"

# Models downloaded from the Huggingface archive to a local drive will be
# cached in this directory.
MODELS_CACHE_DIR = "models_cache"


def deploy_scripts(conf: Secrets, language_alias: str) -> None:
    """
    Deploys all the extension's scripts to the database.

    Parameters:
        conf:
            The secret store. The store should contain the language activation
            SQL command. This command should be created during the language
            container deployment. The store should also have the DB schema.
        language_alias:
            The language alias of the extension's language container.
    """

    with open_pyexasol_connection(conf, compression=True) as conn:
        # First need to activate the language container at the session level, otherwise the script creation fails.
        activation_sql = get_activation_sql(conf)
        conn.execute(activation_sql)

        scripts_deployer = ScriptsDeployer(
            language_alias, conf.get(CKey.db_schema), conn, install_all_scripts=True
        )
        scripts_deployer.deploy_scripts()


def initialize_te_extension(
    conf: Secrets,
    version: str = LATEST_KNOWN_VERSION,
    language_alias: str = LANGUAGE_ALIAS,
    run_deploy_container: bool = True,
    run_deploy_scripts: bool = True,
    run_encapsulate_bfs_credentials: bool = True,
    run_encapsulate_hf_token: bool = True,
    allow_override: bool = True,
) -> None:
    """
    Performs all necessary operations to get the Transformers Extension
    up and running. See the "Getting Started" and "Setup" sections of the
    extension's User Guide for details.

    Parameters:
        conf:
            The secret store. The store should contain all the required
            parameters for accessing the database and BucketFS.
        version:
            Transformers Extension version. If not specified the hardcoded
            latest known version will be used.
        language_alias:
            The language alias of the extension's language container. Normally
            this parameter would only be used for testing.
        run_deploy_container:
            If set to False will skip the language container deployment.
        run_deploy_scripts:
            If set to False will skip the deployment of the UDF scripts.
        run_encapsulate_bfs_credentials:
            If set to False will skip the creation of the database connection
            object encapsulating the BucketFS credentials.
        run_encapsulate_hf_token:
            If set to False will skip the creation of the database connection
            object encapsulating the Huggingface token.
        allow_override:
            If True allows overriding the language definition. Otherwise, if
            the database already has a language definition for the specified
            language alias, an attempt to deploy the container will result
            in a RuntimeError.
    """

    # Make the connection object names
    db_user = str(conf.get(CKey.db_user))
    token = conf.get(CKey.huggingface_token)
    hf_conn_name = "_".join([HF_CONNECTION_PREFIX, db_user]) if token else ""

    if run_deploy_container:
        container_url = TeLanguageContainerDeployer.SLC_URL_FORMATTER.format(
            version=version
        )
        deploy_language_container(
            conf,
            container_url=container_url,
            container_name=TeLanguageContainerDeployer.SLC_NAME,
            language_alias=language_alias,
            activation_key=ACTIVATION_KEY,
            path_in_bucket=PATH_IN_BUCKET_FOR_SLC,
            allow_override=allow_override,
        )

    ensure_bfs_connection(conf)
    ensure_model_subdir_config_value(conf)

    # Create the required objects in the database
    if run_deploy_scripts:
        deploy_scripts(conf, language_alias)
    if token and run_encapsulate_hf_token:
        encapsulate_huggingface_token(conf, hf_conn_name)

    # Save the connection object name in the secret store.
    conf.save(CKey.te_hf_connection, hf_conn_name)
    # Save the directory names in the secret store
    conf.save(CKey.te_models_cache_dir, MODELS_CACHE_DIR)


def upload_model_from_cache(conf: Secrets, model_name: str, cache_dir: str) -> None:
    """
    Uploads model previously downloaded and cached on a local drive. This,
    for instance, could have been done with the following code.

    from transformers import AutoTokenizer, AutoModel
    AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    AutoModel.from_pretrained(model_name, cache_dir=cache_dir)

    Parameters:
        conf:
            The secret store.
        model_name:
            Name of the model at the Huggingface archive.
        cache_dir:
            Directory on the local drive where the model was cached. Each model
            should have its own cache directory.
    """

    raise NotImplementedError(
        "Uploading the model is temporarily unavailable. "
        "Awaiting changes in the Transformers Extension module."
    )


def upload_model(conf: Secrets, model_name: str, cache_dir: str, **kwargs) -> None:
    """
    Uploads model from the Huggingface hub or from the local cache in case it
    has already been downloaded from the hub. The user token, if found in the
    secret store will be passed to the Huggingface interface.

    Parameters:
        conf:
            The secret store.
        model_name:
            Name of the model at the Huggingface archive.
        cache_dir:
            Directory on the local drive where the model is to be cached.
            Each model should have its own cache directory.
        kwargs:
            Additional parameters to be passed to the `from_pretrained`
            methods of the AutoTokenizer and AutoModel. The user token, if specified
            here, will be used instead of the one in the secret store.
    """
    from transformers import (
        AutoModel,
        AutoTokenizer,
    )

    if "token" not in kwargs:
        token = conf.get(CKey.huggingface_token)
        if token:
            kwargs["token"] = token

    AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir, **kwargs)
    AutoModel.from_pretrained(model_name, cache_dir=cache_dir, **kwargs)

    upload_model_from_cache(conf, model_name, cache_dir)
