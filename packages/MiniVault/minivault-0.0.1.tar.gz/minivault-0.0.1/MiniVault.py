#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    A simple, lightweight vault implemented in pure Python for securely
#    storing and retrieving secrets in light-duty applications.
#    Copyright (C) 2025  MiniVault

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
A simple, lightweight vault implemented in pure Python, using RC6, for
securely storing and retrieving secrets in light-duty applications.

Features
--------
- One file per category; each file stores:
  - A per-category *data key* (random) encrypted under a master key derived from the
    provided master password (via `scrypt`).
  - A list of credentials where **only the password** field is encrypted with RC6-CBC
    using the category *data key*, and then Base64-encoded. Other fields remain plaintext.
- Start the vault with `PasswordVault.start(master_password, root_dir)`; this derives
  the master key, decrypts all category data keys into memory.
- Request a password with `vault.get_credentials(category, role)`; the function reads
  the category file, locates the credential by role, decrypts the password, and
  returns the full credential.
- Add or update credentials with `vault.put_credentials(...)`.
- Secure coding practices: scrypt KDF, IV per encryption, HMAC-SHA512 over critical
  sections, atomic file writes, strict file permissions, input validation, type hints,
  docstrings, and doctests for the RC6 library usage.

Requirements
------------
- Python 3.10+
- The `RC6Encryption` module with ECB/CBC block operations.
  The vault itself uses CBC mode for password encryption.

File Format (per category JSON)
-------------------------------
{
  "version": 1,
  "kdf": {"salt": "<b64>", "n": 2**14, "r": 8, "p": 1},
  "encrypted_data_key": {"iv": "<b64>", "ciphertext": "<b64>", "hmac": "<b64>"},
  "credentials": [
     {"role": "app-admin", "username": "alice", "password_b64": "<b64 RC6-CBC>", "notes": "..."},
     ...
  ]
}
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
A simple, lightweight vault implemented in pure Python for securely
storing and retrieving secrets in light-duty applications.
"""
__url__ = "https://github.com/mauricelambert/MiniVault"

# __all__ = []

__license__ = "GPL-3.0 License"
__copyright__ = """
MiniVault  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)

from os import (
    environ,
    PathLike,
    replace,
    fdopen,
    open as os_open,
    O_WRONLY,
    O_CREAT,
    O_TRUNC,
)
from typing import Dict, List, Optional, Tuple, Any, TypedDict, TypeVar
from base64 import b64encode, b64decode
from hmac import new, compare_digest
from hashlib import scrypt, sha512
from dataclasses import dataclass
from secrets import token_bytes
from json import load, dumps
from pathlib import Path

try:
    from RC6Encryption import RC6Encryption
except Exception as exc:
    raise ImportError(
        "RC6Encryption library not found. Ensure 'RC6Encryption' is importable."
    ) from exc

BLOCK_SIZE = 16

PasswordVault = TypeVar("PasswordVault")


def pkcs5_7padding(data: bytes) -> bytes:
    """
    Apply PKCS#5/PKCS#7 padding to *data* to a multiple of 16 bytes.

    Parameters
    ----------
    data : bytes
        Input data.

    Returns
    -------
    bytes
        Padded data.
    """

    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len


def remove_pkcs_padding(data: bytes) -> bytes:
    """
    Remove PKCS#5/PKCS#7 padding from *data*.

    Raises ``ValueError`` if padding is malformed.
    """

    if not data:
        raise ValueError("Empty data")

    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding length")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding bytes")

    return data[:-pad_len]


class CredentialRecord(TypedDict, total=False):
    """
    A single credential entry stored in a category file.

    Fields
    ------
    role: str
        Logical identifier of the credential (e.g., "db-admin", "webapp-user").
        Used as the lookup key when retrieving credentials.
    username: str
        The username associated with this credential.
    password_b64: str
        The encrypted password, stored as Base64 text. The raw value is
        RC6-CBC encrypted (with PKCS#7 padding) using the per-category
        data key. It must be decoded and decrypted at runtime before use.
    notes: str, optional
        Human-readable notes or metadata about this credential.
        Not used in cryptographic operations, purely informational.

    Notes
    -----
    - Only ``password_b64`` is encrypted at rest. All other fields are
      plaintext in the JSON file.
    - This TypedDict is marked ``total=False``, which means all fields
      are optional from the type checker’s perspective. However, in
      practice ``role``, ``username`` and ``password_b64`` are always
      expected to be present in persisted files.
    """

    role: str
    username: str
    password_b64: str
    notes: str


@dataclass
class CategoryState:
    """
    Holds in-memory decrypted data key for a category.
    """

    data_key: bytes


class PasswordVault:
    """
    A small password vault that encrypts only the password fields using RC6.

    Use :meth:`PasswordVault.start` to initialize from a root directory, passing a
    master password. The constructor is not public because we want to constrain
    initialization through the key-derivation step.

    All persistent data lives in files under *root_dir*, one JSON file per category.

    Notes on Security
    -----------------
    - Passwords are encrypted with RC6 in CBC mode with PKCS#7 padding.
    - Per-category data keys are protected using a key derived from the master password
      by scrypt (N=2**14, r=8, p=1). The encrypted data key (encrypted_data_key) is integrity-protected
      with HMAC-SHA512.
    """

    _root: Path
    _master_key: Optional[bytes]
    _categories: Dict[str, CategoryState]

    def __init__(self, root_dir: Path):
        self._root = root_dir
        self._master_key = None
        self._categories = {}

    @classmethod
    def start(
        cls, master_password: str, root_dir: str | PathLike[str]
    ) -> PasswordVault:
        """
        Start the vault by deriving the master key, decrypting category data keys,
        and erasing the master password from memory.

        Parameters
        ----------
        master_password : str
            The user-provided master password.
        root_dir : str | PathLike
            Directory containing category files.
        """

        vault = cls(Path(root_dir))
        vault._root.mkdir(parents=True, exist_ok=True)

        vault._load_all_category_keys(master_password)
        return vault

    def put_credentials(
        self,
        category: str,
        role: str,
        username: str,
        password: str,
        notes: str | None = None,
    ) -> None:
        """
        Create or update a credential entry in *category*.

        Only the *password* is RC6-encrypted and Base64-encoded at rest.
        """

        category_file, content = self._load_category_file(
            category, create_if_missing=False
        )
        data_key = self._ensure_category_key(category, content)
        encrypted_password = self._rc6_cbc_encrypt_b64(
            data_key, password.encode("utf-8")
        )

        updated = False
        for record in content.get("credentials", []):
            if record.get("role") == role:
                record["username"] = username
                record["password_b64"] = encrypted_password
                if notes is not None:
                    record["notes"] = notes
                updated = True
                break

        if not updated:
            new_record: CredentialRecord = {
                "role": role,
                "username": username,
                "password_b64": encrypted_password,
            }
            if notes:
                new_record["notes"] = notes
            content.setdefault("credentials", []).append(new_record)

        self._atomic_write_json(category_file, content)

    def get_credentials(self, category: str, role: str) -> CredentialRecord:
        """
        Return the credential for (*category*, *role*), decrypting the password.

        Raises ``FileNotFoundError`` if the category file does not exist, or ``KeyError``
        if the role cannot be found.
        """

        category_file, content = self._load_category_file(
            category, create_if_missing=False
        )
        data_key = self._ensure_category_key(category, content)

        for record in content.get("credentials", []):
            if record.get("role") == role:
                encrypted_password = record.get("password_b64", "")
                decrypted_password = self._rc6_cbc_decrypt_b64(
                    data_key, encrypted_password
                )

                out: CredentialRecord = {
                    "role": record.get("role", ""),
                    "username": record.get("username", ""),
                    "password": decrypted_password.decode("utf-8"),
                }

                if "notes" in record:
                    out["notes"] = record["notes"]

                return out
        raise KeyError(f"Role {role!r} not found in category {category!r}.")

    def create_new_category(self, category: str, master_password: str) -> None:
        """
        This method creates a new category using master password.
        """

        category_file, content = self._load_category_file(
            category, create_if_missing=True
        )
        self._ensure_category_key(category, content, master_password)
        self._atomic_write_json(category_file, content)

    def _load_all_category_keys(self, master_password: str) -> None:
        """
        Load (and if necessary initialize) all category *data keys* into memory.

        For existing files, derive the master key using the file's salt and decrypt
        the encrypted data key. For new categories created later, `_ensure_category_key`
        performs the same process lazily.
        """

        for entry in sorted(self._root.glob("*.json")):
            with entry.open("r", encoding="utf-8") as fh:
                content = load(fh)
            self._decrypt_and_cache_data_key(
                entry.stem, content, master_password
            )

    def _ensure_category_key(
        self,
        category: str,
        content: Dict[str, Any],
        master_password: str = None,
    ) -> bytes:
        """
        Ensure that a symmetric data-encryption key is available for the given category.

        This method serves two roles depending on whether the category has already
        been initialized:

        1. **Cached case**:
           - If the category has already been loaded into memory, return its cached
             data key immediately.

        2. **New category (no encrypted_data_key present)**:
           - If the category document does not contain an Encrypted Data Key (encrypted_data_key),
             this method initializes the category by:
               * Generating a new random data key.
               * Deriving a one-time master key from the bootstrap master password
                 and fresh KDF parameters (salt, cost factors).
               * Encrypting (wrapping) the new data key under the derived master key
                 using RC6-CBC.
               * Computing and storing an HMAC for integrity.
               * Updating the category document with version, KDF parameters, encrypted_data_key,
                 and an empty credentials list.
               * Caching the plaintext data key in memory for subsequent use.

        3. **Existing category (encrypted_data_key present)**:
           - If the document already has an encrypted_data_key, the data key is decrypted using
             the bootstrap master password (retrieved only at vault startup).
             The decrypted key is then cached in memory and returned.

        Parameters
        ----------
        category : str
            The logical category name (derived from the filename stem).
        content : Dict[str, Any]
            Parsed JSON document for the category, possibly containing KDF
            parameters and an encrypted_data_key.

        Returns
        -------
        bytes
            The plaintext symmetric data key for the category.

        Raises
        ------
        RuntimeError
            If the vault was not started with a master password and one is required
            for key derivation or encrypted_data_key decryption.

        Notes
        -----
        - This method is internal and should not be called directly by users of the
          vault API.
        - The master password is only used transiently to bootstrap or decrypt
          category keys; only the per-category data keys are kept cached in memory
          afterwards.
        - The presence of ``PV_BOOTSTRAP_MP`` in the environment is a legacy detail
          and will be removed in future revisions; secure handling should avoid
          environment variables entirely.
        """

        if category in self._categories:
            return self._categories[category].data_key

        if "encrypted_data_key" not in content:
            salt = token_bytes(16)
            kdf_parameters = {
                "salt": b64encode(salt).decode(),
                "n": 2**14,
                "r": 8,
                "p": 1,
            }
            data_key = token_bytes(BLOCK_SIZE)
            iv = token_bytes(BLOCK_SIZE)

            master_password = master_password or environ.get("PV_BOOTSTRAP_MP")
            if not master_password:
                raise RuntimeError(
                    "Vault not started with a master password; call PasswordVault.start() first."
                )
            master_key = self._derive_master_key(
                master_password.encode("utf-8"), salt, kdf_parameters
            )
            ciphertext = self._rc6_cbc_encrypt(master_key, data_key, iv)
            hmac = self._hmac(master_key, iv + ciphertext)
            content["version"] = 1
            content["kdf"] = {
                "salt": kdf_parameters["salt"],
                "n": kdf_parameters["n"],
                "r": kdf_parameters["r"],
                "p": kdf_parameters["p"],
            }
            content["encrypted_data_key"] = {
                "iv": b64encode(iv).decode(),
                "ciphertext": b64encode(ciphertext).decode(),
                "hmac": b64encode(hmac).decode(),
            }
            content.setdefault("credentials", [])

            self._categories[category] = CategoryState(data_key=data_key)
            return data_key

        master_password = master_password or environ.get("PV_BOOTSTRAP_MP")
        if not master_password:
            raise RuntimeError(
                "Vault not started with a master password; call PasswordVault.start() first."
            )
        return self._decrypt_and_cache_data_key(
            category, content, master_password
        )

    def _decrypt_and_cache_data_key(
        self, category: str, content: Dict[str, Any], master_password: str
    ) -> bytes:
        """
        Decrypt and cache the symmetric data-encryption key for a given category.

        This method is used when a category document already contains an
        Encrypted Data Key (EDK). The EDK is unwrapped by deriving the master
        key from the user-provided master password and the stored KDF parameters.
        After decryption, the plaintext data key is cached in memory for use in
        encrypting and decrypting credential passwords within that category.

        Workflow
        --------
        1. Read KDF parameters (salt, cost factors) from the category document.
        2. Derive a master key from the supplied ``master_password`` using the KDF.
        3. Extract the IV, ciphertext, and HMAC from the ``encrypted_data_key``.
        4. Verify the integrity of the ciphertext using the HMAC.
        5. Decrypt the ciphertext (RC6-CBC) to recover the category data key.
        6. Validate the key length and cache it in ``self._categories``.

        Parameters
        ----------
        category : str
            Logical name of the category (usually derived from the file stem).
        content : Dict[str, Any]
            The parsed category JSON document, expected to contain both
            ``kdf`` and ``encrypted_data_key`` entries.
        master_password : str
            The plaintext master password provided at vault startup, used to
            derive the master key.

        Returns
        -------
        bytes
            The plaintext symmetric data key for this category, exactly
            ``BLOCK_SIZE`` bytes in length.

        Raises
        ------
        ValueError
            If the category file is malformed, missing required fields,
            if the integrity check fails, or if the decrypted data key has
            an unexpected length.

        Notes
        -----
        - This method is internal and should only be called from
          :meth:`_ensure_category_key`.
        - Integrity is verified using HMAC before decryption to prevent
          tampering or corrupted ciphertext.
        - The decrypted key is cached in memory and never written back to disk.
        """

        kdf = content.get("kdf", {})
        encrypted_data_key = content.get("encrypted_data_key", {})

        salt = kdf.get("salt")
        iv = encrypted_data_key.get("iv")
        ciphertext = encrypted_data_key.get("ciphertext")
        hmac = encrypted_data_key.get("hmac")
        if salt is None or iv is None or ciphertext is None or hmac is None:
            raise ValueError("Malformed category file")

        salt = b64decode(salt.encode())
        parameters = {
            "n": int(kdf.get("n", 2**14)),
            "r": int(kdf.get("r", 8)),
            "p": int(kdf.get("p", 1)),
        }
        master_key = self._derive_master_key(
            master_password.encode("utf-8"), salt, parameters
        )
        iv = b64decode(iv.encode())
        ciphertext = b64decode(ciphertext.encode())
        tag = b64decode(hmac.encode())

        if not compare_digest(tag, self._hmac(master_key, iv + ciphertext)):
            raise ValueError("Integrity check failed for category data key")

        data_key = self._rc6_cbc_decrypt(master_key, ciphertext, iv)
        if len(data_key) != BLOCK_SIZE:
            raise ValueError("Unexpected data key length")

        self._categories[category] = CategoryState(data_key=data_key)
        return data_key

    @staticmethod
    def _derive_master_key(
        password: bytes, salt: bytes, parameters: Dict[str, int]
    ) -> bytes:
        """
        Derive a fixed-length master key from a password using scrypt.
        """

        return scrypt(
            password,
            salt=salt,
            n=parameters["n"],
            r=parameters["r"],
            p=parameters["p"],
            dklen=BLOCK_SIZE,
        )

    @staticmethod
    def _hmac(key: bytes, data: bytes) -> bytes:
        """
        Compute HMAC-SHA512 of the given data using the provided key.
        """

        return new(key, data, sha512).digest()

    @staticmethod
    def _rc6_cbc_encrypt(
        key: bytes, plaintext: bytes, iv: Optional[bytes] = None
    ) -> bytes:
        """
        Encrypt data using RC6 in CBC mode with an optional IV.
        """

        if iv is None:
            iv = token_bytes(BLOCK_SIZE)
        rc6 = RC6Encryption(key)
        iv_used, ciphertext = rc6.data_encryption_CBC(plaintext, iv)
        assert iv_used == iv
        return ciphertext

    @staticmethod
    def _rc6_cbc_decrypt(key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
        """
        Decrypt RC6-CBC ciphertext using the given key and IV.
        """

        rc6 = RC6Encryption(key)
        return rc6.data_decryption_CBC(ciphertext, iv)

    @staticmethod
    def _rc6_cbc_encrypt_b64(data_key: bytes, plaintext: bytes) -> str:
        """
        Encrypt and base64-encode plaintext using RC6-CBC.
        """

        iv = token_bytes(BLOCK_SIZE)
        ciphertext = PasswordVault._rc6_cbc_encrypt(
            data_key, pkcs5_7padding(plaintext), iv
        )
        return b64encode(iv + ciphertext).decode("ascii")

    @staticmethod
    def _rc6_cbc_decrypt_b64(data_key: bytes, blob_b64: str) -> bytes:
        """
        Base64-decode and decrypt RC6-CBC encrypted data.
        """

        raw = b64decode(blob_b64)
        if len(raw) < BLOCK_SIZE:
            raise ValueError("Invalid encrypted blob")
        iv, ciphertext = raw[:BLOCK_SIZE], raw[BLOCK_SIZE:]
        plaintext = PasswordVault._rc6_cbc_decrypt(data_key, ciphertext, iv)
        return remove_pkcs_padding(plaintext)

    def _category_path(self, category: str) -> Path:
        """
        Return the safe filesystem path for a given category name.
        """

        safe = category.strip().replace("/", "_").replace("\\", "_")
        return (self._root / f"{safe}.json").resolve()

    def _load_category_file(
        self, category: str, create_if_missing: bool
    ) -> Tuple[Path, Dict[str, Any]]:
        """
        Load the JSON document for a given category.

        If the category file exists, it is opened and parsed. If it does not exist
        and ``create_if_missing`` is True, an empty document is returned along with
        the expected file path. Otherwise, a FileNotFoundError is raised.

        Parameters
        ----------
        category : str
            The category name (used to resolve the file path).
        create_if_missing : bool
            Whether to allow returning an empty document if the file does not exist.

        Returns
        -------
        Tuple[Path, Dict[str, Any]]
            A tuple of the resolved file path and the parsed JSON content
            (or an empty dict if the file was missing and creation is allowed).

        Raises
        ------
        FileNotFoundError
            If the file does not exist and ``create_if_missing`` is False.
        """

        path = self._category_path(category)

        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                return path, load(fh)

        if not create_if_missing:
            raise FileNotFoundError(f"Category {category!r} not found")

        return path, {}

    def _atomic_write_json(self, path: Path, obj: Dict[str, Any]) -> None:
        """
        Atomically write a dictionary as a JSON file.

        The data is first written to a temporary file with restricted permissions,
        then atomically renamed to the target path to ensure consistency and prevent
        partial writes.

        Parameters
        ----------
        path : Path
            The destination file path.
        obj : Dict[str, Any]
            The dictionary to serialize as JSON.
        """

        tmp = path.with_suffix(".tmp")
        data = dumps(obj, ensure_ascii=False, separators=(",", ":"))
        with fdopen(
            os_open(tmp, O_WRONLY | O_CREAT | O_TRUNC, 0o600),
            "w",
            encoding="utf-8",
        ) as fh:
            fh.write(data)
        replace(tmp, path)


def test():
    category = "finance"
    role = "db-admin"
    username = "alice"
    password = "S3cureP@ss!"
    master_password = "correct horse battery staple"

    vault = PasswordVault.start(
        master_password=master_password, root_dir=".\\vault_data"
    )
    vault.create_new_category("finance", master_password)
    vault.put_credentials(category, role, username, password)
    vault.put_credentials(category, "db-system", username, password)
    creds = vault.get_credentials(category, role)

    print("Username:", creds["username"] + ",", "Password:", creds["password"])
    assert creds["username"] == username, "Invalid username"
    assert creds["password"] == password, "Invalid password"


if __name__ == "__main__":
    test()
