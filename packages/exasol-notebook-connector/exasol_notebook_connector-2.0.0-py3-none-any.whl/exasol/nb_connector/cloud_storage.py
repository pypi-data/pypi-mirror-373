import pyexasol

_SETUP_SQL = [
    "OPEN SCHEMA {schema!i}",
    """
--/
            CREATE OR REPLACE JAVA SET SCRIPT IMPORT_PATH(...) EMITS (...) AS
              %scriptclass com.exasol.cloudetl.scriptclasses.FilesImportQueryGenerator;
              %jar {jar_path!r};
/
        """,
    """
--/
        CREATE OR REPLACE JAVA SCALAR SCRIPT IMPORT_METADATA(...) 
          EMITS (
                filename VARCHAR(2000), 
                partition_index VARCHAR(100), 
                start_index DECIMAL(36, 0), 
                end_index DECIMAL(36, 0)
          ) AS
          %scriptclass com.exasol.cloudetl.scriptclasses.FilesMetadataReader;
          %jar {jar_path!r};
/
        """,
    """
--/
        CREATE OR REPLACE JAVA SET SCRIPT IMPORT_FILES(...) EMITS (...) AS
          %scriptclass com.exasol.cloudetl.scriptclasses.FilesDataImporter;
          %jar {jar_path!r};
/
        """,
]


def setup_scripts(
    db_connection: pyexasol.ExaConnection, schema_name: str, bucketfs_jar_path: str
):
    """
    Perform initialization of scripts for could-storage-extension.
    :param db_connection: DB connection
    :param schema_name: name of the schema to be used.
    :param bucketfs_jar_path: path to cloud-storage-extension jar in BucketFS
    :return:
    """
    for sql in _SETUP_SQL:
        db_connection.execute(
            sql,
            query_params={
                "schema": schema_name,
                "jar_path": bucketfs_jar_path,
            },
        )
