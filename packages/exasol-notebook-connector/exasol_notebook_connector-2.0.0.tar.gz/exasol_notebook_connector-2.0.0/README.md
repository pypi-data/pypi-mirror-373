# Exasol Notebook Connector

Connection configuration management and additional tools for Jupyter notebook applications provided by Exasol company.

[![PyPI Version](https://img.shields.io/pypi/v/exasol-notebook-connector)](https://pypi.org/project/exasol-notebook-connector/)
[![License](https://img.shields.io/pypi/l/exasol-notebook-connector)](https://opensource.org/licenses/MIT)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/exasol-notebook-connector)](https://pypi.org/project/exasol-notebook-connector)
[![Last Commit](https://img.shields.io/github/last-commit/exasol/notebook-connector)](https://pypi.org/project/exasol-notebook-connector/)

## Features

Exasol Notebook Connector (ENC) currently contains a **Secure Configuration Storage** that can be used in Jupyter notebook applications to store arbitrary credentials and configuration items, such as user names, passwords, URLs, etc.

By that users of such notebook applications
* need to enter their credentials and configuration items only once
* can store them in a secure, encrypted, and persistent file based on SQLite and [coleifer/sqlcipher3](https://github.com/coleifer/sqlcipher3)
* can use these credentials and configuration items in their notebook applications

## Usage

```python
from pathlib import Path
from exasol.nb_connector.secret_store import Secrets

file = "password_db.sqlite"
secrets = Secrets(Path(file), "my secret password")
key = "my key"
secrets.save(key, "my value")
value = secrets.get(key)
```

#### Constraints and Special Situations

* If file does not exist then class `Secrets` will create it.
* If password is wrong then `Secrets` will throw an exception.
* If file contains key from a session in the past then method `secrets.save()` will overwrite the value for this key.
* If key is not contained in file then method `get()` returns `None`.
* Saving multiple keys can be chained: `secrets.save("key-1", "A").save("key-2", "B")`

## Additional Information

* [User Guide](doc/user_guide/user-guide.md)
* [Developer Guide](doc/developer_guide/developer-guide.md)
