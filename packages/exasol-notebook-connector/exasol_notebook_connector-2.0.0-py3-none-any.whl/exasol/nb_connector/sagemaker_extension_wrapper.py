from importlib.metadata import version

from exasol_sagemaker_extension.deployment.deploy_create_statements import (
    DeployCreateStatements,
)
from exasol_sagemaker_extension.deployment.sme_language_container_deployer import (
    SmeLanguageContainerDeployer,
)

from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.connections import open_pyexasol_connection
from exasol.nb_connector.extension_wrapper_common import (
    deploy_language_container,
    encapsulate_aws_credentials,
)
from exasol.nb_connector.language_container_activation import (
    ACTIVATION_KEY_PREFIX,
    get_activation_sql,
)
from exasol.nb_connector.secret_store import Secrets

# Root directory in a BucketFS bucket where all stuff of the Sagemaker
# Extension, including its language container, will be uploaded.
PATH_IN_BUCKET = "SME"

LANGUAGE_ALIAS = "PYTHON3_SME"

LATEST_KNOWN_VERSION = version("exasol_sagemaker_extension")

# Activation SQL for the Sagemaker Extension will be saved in the secret
# store with this key.
ACTIVATION_KEY = ACTIVATION_KEY_PREFIX + "sme"

# Name of the connection object with AWS credentials and S3 location
# will be prefixed with this string.
AWS_CONNECTION_PREFIX = "SME_AWS"


def deploy_scripts(conf: Secrets) -> None:
    """
    Deploys all the extension's scripts to the database.

    Parameters:
        conf:
            The secret store. The store should contain the language activation
            SQL command. This command should be created during the language
            container deployment. The store should also have the DB schema.
    """

    with open_pyexasol_connection(conf, compression=True) as conn:
        # First need to activate the language container at the session level.
        activation_sql = get_activation_sql(conf)
        conn.execute(activation_sql)

        scripts_deployer = DeployCreateStatements(
            exasol_conn=conn,
            schema=conf.get(CKey.db_schema),
            to_print=False,
            develop=False,
        )
        scripts_deployer.run()


def initialize_sme_extension(
    conf: Secrets,
    version: str = LATEST_KNOWN_VERSION,
    language_alias: str = LANGUAGE_ALIAS,
    run_deploy_container: bool = True,
    run_deploy_scripts: bool = True,
    run_encapsulate_aws_credentials: bool = True,
    allow_override: bool = True,
) -> None:
    """
    Performs all necessary operations to get the Sagemaker Extension
    up and running. See the "Getting Started" and "Setup" sections of the
    extension's User Guide for details.

    Parameters:
        conf:
            The secret store. The store should contain all the required
            parameters for accessing the database, BucketFS and AWS.
        version:
            Sagemaker Extension version. If not specified the hardcoded
            latest known version will be used.
        language_alias:
            The language alias of the extension's language container. Normally
            this parameter would only be used for testing.
        run_deploy_container:
            If set to False will skip the language container deployment.
        run_deploy_scripts:
            If set to False will skip the deployment of the scripts.
        run_encapsulate_aws_credentials:
            If set to False will skip the creation of the database connection
            object encapsulating the AWS credentials.
        allow_override:
            If True allows overriding the language definition. Otherwise, if
            the database already has a language definition for the specified
            language alias, an attempt to deploy the container will result
            in a RuntimeError.
    """

    # Make the connection object name
    aws_conn_name = "_".join([AWS_CONNECTION_PREFIX, str(conf.get(CKey.db_user))])

    if run_deploy_container:
        container_url = SmeLanguageContainerDeployer.SLC_URL_FORMATTER.format(
            version=version
        )
        deploy_language_container(
            conf,
            container_url=container_url,
            container_name=SmeLanguageContainerDeployer.SLC_NAME,
            language_alias=language_alias,
            activation_key=ACTIVATION_KEY,
            path_in_bucket=PATH_IN_BUCKET,
            allow_override=allow_override,
        )

    # Create the required objects in the database
    if run_deploy_scripts:
        deploy_scripts(conf)
    if run_encapsulate_aws_credentials:
        encapsulate_aws_credentials(conf, aws_conn_name, CKey.sme_aws_bucket)

    # Save the connection object name in the secret store.
    conf.save(CKey.sme_aws_connection, aws_conn_name)
