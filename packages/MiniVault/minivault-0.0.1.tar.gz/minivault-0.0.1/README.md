![MiniVault Logo](https://mauricelambert.github.io/info/python/code/MiniVault_small.png "MiniVault logo")

# MiniVault

## Description

A simple, lightweight vault implemented in pure Python, using RC6, for
securely storing and retrieving secrets in light-duty applications.

## Requirements

This package require:

 - python3
 - python3 Standard Library
 - RC6Encryption

## Installation

### Pip

```bash
python3 -m pip install MiniVault
```

### Git

```bash
git clone "https://github.com/mauricelambert/MiniVault.git"
cd "MiniVault"
python3 -m pip install .
```

### Wget

```bash
wget https://github.com/mauricelambert/MiniVault/archive/refs/heads/main.zip
unzip main.zip
cd MiniVault-main
python3 -m pip install .
```

### cURL

```bash
curl -O https://github.com/mauricelambert/MiniVault/archive/refs/heads/main.zip
unzip main.zip
cd MiniVault-main
python3 -m pip install .
```

## Usages

### Python script

```python
from MiniVault import *
from getpass import getpass

category = "finance"
role = "db-admin"
username = "alice"
password = "S3cureP@ss!"
master_password = getpass()

vault = PasswordVault.start(
    master_password=master_password, root_dir="my_vault"
)                                                           # master password required to open vault
vault.create_new_category("finance", master_password)       # master password required to create new category
vault.put_credentials(category, role, username, password)   # master password not required to add new password
vault.put_credentials(category, "db-system", username, password)

creds = vault.get_credentials(category, role)
print("Username:", creds["username"] + ",", "Password:", creds["password"])
assert creds["username"] == username, "Invalid username"
assert creds["password"] == password, "Invalid password"
```

## Links

 - [Pypi](https://pypi.org/project/MiniVault)
 - [Github](https://github.com/mauricelambert/MiniVault)
 - [Documentation](https://mauricelambert.github.io/info/python/code/MiniVault.html)

## License

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
