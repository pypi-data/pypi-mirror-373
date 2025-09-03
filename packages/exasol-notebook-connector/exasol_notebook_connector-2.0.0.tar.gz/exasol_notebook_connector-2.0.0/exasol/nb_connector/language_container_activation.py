import pyexasol

from exasol.nb_connector.connections import open_pyexasol_connection
from exasol.nb_connector.secret_store import Secrets

# All secret store entries with language container activation commands
# will have this common prefix in their keys.
ACTIVATION_KEY_PREFIX = "language_container_activation_"


def get_registered_languages_string(conf: Secrets) -> str:
    """
    Gets the session level language definitions from the database. Returns a string
    in a format of a space separated list: "<alias1>=<url1> <alias2=<url2> ..."
    """

    with open_pyexasol_connection(conf) as pyexasol_conn:
        query_result = pyexasol_conn.execute(
            "SELECT SESSION_VALUE FROM SYS.EXA_PARAMETERS WHERE PARAMETER_NAME='SCRIPT_LANGUAGES'"
        ).fetchall()
        return query_result[0][0]


def get_registered_languages(conf: Secrets) -> dict[str, str]:
    """
    Collects the existing, session level, language definitions from the database.
    Returns them as a dictionary {alias: language_url}
    """

    lang_definitions_str = get_registered_languages_string(conf)
    result: dict[str, str] = {}
    for lang_definition in lang_definitions_str.split():
        alias, lang_url = lang_definition.split("=", maxsplit=1)
        result[alias] = lang_url
    return result


def get_requested_languages(conf: Secrets) -> dict[str, str]:
    """
    Collects language definitions from the secret store. Returns them as a
    dictionary {alias: language_url}.

    Raises a RuntimeError if tt finds two entries with the same alias but
    different language definitions (i.e. URLs).
    """

    result: dict[str, str] = {}
    # Iterate over all entries that look like language definitions.
    for key, value in conf.items():
        if key.startswith(ACTIVATION_KEY_PREFIX):
            alias, lang_url = value.split("=", maxsplit=1)
            alias = alias.upper()
            if alias in result:
                if result[alias] != lang_url:
                    error = (
                        "Unable to merge multiple language definitions. "
                        f"Found incompatible definitions for the language alias {alias}."
                    )
                    raise RuntimeError(error)
            else:
                result[alias] = lang_url
    return result


def get_activation_sql(conf: Secrets) -> str:
    """
    Merges multiple language definitions (i.e. URLs) found in the secret store with
    language definitions currently registered in the database at the SESSION level.
    Returns a language activation command which combines all that language definitions.

    For details on how an activation command may look like please refer to
    https://docs.exasol.com/db/latest/database_concepts/udf_scripts/adding_new_packages_script_languages.htm

    The secret store entries containing language definitions should have keys with a
    common prefix. This prefix is defined in the ACTIVATION_KEY_PREFIX.

    Multiple language definitions in the secret store would normally have unique
    aliases. In case there are more than one entry with the same alias, their
    definitions should match. Otherwise, a RuntimeError will be raised. If a language
    with the same aliases is already present in the database, its definition will be
    overwritten, no exception raised.
    """

    # Collect language definitions, either already registered in the database or
    # recorded in the secret store.
    lang_definitions = get_registered_languages(conf)
    lang_definitions.update(get_requested_languages(conf))

    # Build and return an SQL command for the language container activation.
    merged_langs_str = " ".join(
        f"{key}={value}" for key, value in lang_definitions.items()
    )
    return f"ALTER SESSION SET SCRIPT_LANGUAGES='{merged_langs_str}';"


def open_pyexasol_connection_with_lang_definitions(
    conf: Secrets, **kwargs
) -> pyexasol.ExaConnection:
    """
    Opens a `pyexasol` connection and applies the `ALTER SESSION` command using all registered languages.
    """
    conn = open_pyexasol_connection(conf, **kwargs)
    conn.execute(get_activation_sql(conf))
    return conn
