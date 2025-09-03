# Proprietary Changes made for Trainy under the Trainy Software License
# Original source: skypilot: https://github.com/skypilot-org/skypilot
# which is Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The local machine's public key should not be uploaded to the remote VM, because
it will cause private/public key pair mismatch when the user tries to launch new
VM from that remote VM using SkyPilot, e.g., the node is used as a jobs
controller. (Lambda cloud is an exception, due to the limitation of the cloud
provider. See the comments in setup_lambda_authentication)
"""

import functools
import os
from typing import Tuple

import filelock

from konduktor import logging
from konduktor.utils import common_utils

logger = logging.get_logger(__name__)

_SSH_KEY_PATH_PREFIX = '~/.konduktor/clients/{user_hash}/ssh'

MAX_TRIALS = 64


def get_ssh_key_and_lock_path() -> Tuple[str, str, str]:
    user_hash = common_utils.get_user_hash()
    user_ssh_key_prefix = _SSH_KEY_PATH_PREFIX.format(user_hash=user_hash)
    os.makedirs(os.path.expanduser(user_ssh_key_prefix), exist_ok=True, mode=0o700)
    private_key_path = os.path.join(user_ssh_key_prefix, 'konduktor-key')
    public_key_path = os.path.join(user_ssh_key_prefix, 'konduktor-key.pub')
    lock_path = os.path.join(user_ssh_key_prefix, '.__internal-konduktor-key.lock')
    return private_key_path, public_key_path, lock_path


def _generate_rsa_key_pair() -> Tuple[str, str]:
    # Keep the import of the cryptography local to avoid expensive
    # third-party imports when not needed.
    # pylint: disable=import-outside-toplevel
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(
        backend=default_backend(), public_exponent=65537, key_size=2048
    )

    private_key = (
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        .decode('utf-8')
        .strip()
    )

    public_key = (
        key.public_key()
        .public_bytes(
            serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
        )
        .decode('utf-8')
        .strip()
    )

    return public_key, private_key


def _save_key_pair(
    private_key_path: str, public_key_path: str, private_key: str, public_key: str
) -> None:
    key_dir = os.path.dirname(private_key_path)
    os.makedirs(key_dir, exist_ok=True, mode=0o700)

    with open(
        private_key_path,
        'w',
        encoding='utf-8',
        opener=functools.partial(os.open, mode=0o600),
    ) as f:
        f.write(private_key)

    with open(
        public_key_path,
        'w',
        encoding='utf-8',
        opener=functools.partial(os.open, mode=0o644),
    ) as f:
        f.write(public_key)


def get_or_generate_keys() -> Tuple[str, str]:
    """Returns the aboslute private and public key paths."""
    private_key_path, public_key_path, lock_path = get_ssh_key_and_lock_path()
    private_key_path = os.path.expanduser(private_key_path)
    public_key_path = os.path.expanduser(public_key_path)
    lock_path = os.path.expanduser(lock_path)

    lock_dir = os.path.dirname(lock_path)
    # We should have the folder ~/.konduktor/generated/ssh to have 0o700 permission,
    # as the ssh configs will be written to this folder as well in
    # backend_utils.SSHConfigHelper
    os.makedirs(lock_dir, exist_ok=True, mode=0o700)
    with filelock.FileLock(lock_path, timeout=10):
        if not os.path.exists(private_key_path):
            public_key, private_key = _generate_rsa_key_pair()
            _save_key_pair(private_key_path, public_key_path, private_key, public_key)
    assert os.path.exists(public_key_path), (
        'Private key found, but associated public key '
        f'{public_key_path} does not exist.'
    )
    return private_key_path, public_key_path
