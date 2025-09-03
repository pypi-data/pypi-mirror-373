from enum import (
    Enum,
    auto,
)


class AILabConfig(Enum):
    use_itde = auto()
    db_host_name = auto()
    db_port = auto()
    db_schema = auto()
    db_user = auto()
    db_password = auto()
    db_encryption = auto()
    cert_vld = auto()
    trusted_ca = auto()
    client_cert = auto()
    client_key = auto()
    bfs_host_name = auto()
    bfs_port = auto()
    bfs_internal_host_name = auto()
    bfs_internal_port = auto()
    bfs_service = auto()
    bfs_bucket = auto()
    bfs_user = auto()
    bfs_password = auto()
    bfs_encryption = auto()
    mem_size = auto()
    disk_size = auto()
    huggingface_token = auto()
    aws_region = auto()
    aws_access_key_id = auto()
    aws_secret_access_key = auto()
    itde_container = auto()
    itde_volume = auto()
    itde_network = auto()
    te_hf_connection = auto()
    te_models_cache_dir = auto()
    txaie_models_cache_dir = auto()
    sme_aws_bucket = auto()
    sme_aws_role = auto()
    sme_aws_connection = auto()
    saas_url = auto()
    saas_token = auto()
    saas_account_id = auto()
    saas_database_id = auto()
    saas_database_name = auto()
    storage_backend = auto()
    accelerator = auto()
    bfs_model_subdir = auto()
    bfs_connection_name = auto()


class StorageBackend(Enum):
    onprem = auto()
    saas = auto()


class Accelerator(Enum):
    none = "none"
    nvidia = "nvidia"
