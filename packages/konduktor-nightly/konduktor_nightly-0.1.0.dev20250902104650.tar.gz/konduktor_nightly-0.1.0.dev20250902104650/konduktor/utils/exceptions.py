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

"""Exceptions."""

import builtins
import traceback
import types
from typing import Any, Dict

# Return code for keyboard interruption and SIGTSTP
KEYBOARD_INTERRUPT_CODE = 130
SIGTSTP_CODE = 146
RSYNC_FILE_NOT_FOUND_CODE = 23
# Arbitrarily chosen value. Used in SkyPilot's storage mounting scripts
MOUNT_PATH_NON_EMPTY_CODE = 42
# Arbitrarily chosen value. Used to provision Kubernetes instance in Skypilot
INSUFFICIENT_PRIVILEGES_CODE = 52
# Return code when git command is ran in a dir that is not git repo
GIT_FATAL_EXIT_CODE = 128


def is_safe_exception(exc: Exception) -> bool:
    """Returns True if the exception is safe to send to clients.

    Safe exceptions are:
    1. Built-in exceptions
    2. Konduktor's own exceptions
    """
    module = type(exc).__module__

    # Builtin exceptions (e.g., ValueError, RuntimeError)
    if module == 'builtins':
        return True

    # Konduktor's own exceptions
    if module.startswith('konduktor.'):
        return True

    return False


def wrap_exception(exc: Exception) -> Exception:
    """Wraps non-safe exceptions into Konduktor exceptions

    This is used to wrap exceptions that are not safe to deserialize at clients.

    Examples include exceptions from cloud providers whose packages are not
    available at clients.
    """
    if is_safe_exception(exc):
        return exc

    return CloudError(
        message=str(exc),
        cloud_provider=type(exc).__module__.split('.')[0],
        error_type=type(exc).__name__,
    )


def serialize_exception(e: Exception) -> Dict[str, Any]:
    """Serialize the exception.

    This function also wraps any unsafe exceptions (e.g., cloud exceptions)
    into Konduktor's CloudError before serialization to ensure clients can
    deserialize them without needing cloud provider packages installed.
    """
    # Wrap unsafe exceptions before serialization
    e = wrap_exception(e)

    stacktrace = getattr(e, 'stacktrace', None)
    attributes = e.__dict__.copy()
    if 'stacktrace' in attributes:
        del attributes['stacktrace']
    for attr_k in list(attributes.keys()):
        attr_v = attributes[attr_k]
        if isinstance(attr_v, types.TracebackType):
            attributes[attr_k] = traceback.format_tb(attr_v)

    data = {
        'type': e.__class__.__name__,
        'message': str(e),
        'args': e.args,
        'attributes': attributes,
        'stacktrace': stacktrace,
    }
    return data


def deserialize_exception(serialized: Dict[str, Any]) -> Exception:
    """Deserialize the exception."""
    exception_type = serialized['type']
    if hasattr(builtins, exception_type):
        exception_class = getattr(builtins, exception_type)
    else:
        exception_class = globals().get(exception_type, None)
    if exception_class is None:
        # Unknown exception type.
        return Exception(f'{exception_type}: {serialized["message"]}')
    e = exception_class(*serialized['args'], **serialized['attributes'])
    if serialized['stacktrace'] is not None:
        setattr(e, 'stacktrace', serialized['stacktrace'])
    return e


class CloudError(Exception):
    """Wraps cloud-specific errors into a SkyPilot exception."""

    def __init__(self, message: str, cloud_provider: str, error_type: str):
        super().__init__(message)
        self.cloud_provider = cloud_provider
        self.error_type = error_type

    def __str__(self):
        return (
            f'{self.cloud_provider} error ({self.error_type}): ' f'{super().__str__()}'
        )


class CommandError(Exception):
    pass


class CreateSecretError(Exception):
    pass


class MissingSecretError(Exception):
    pass


class NotSupportedError(Exception):
    """Raised when a feature is not supported."""

    pass


class StorageError(Exception):
    pass


class StorageSpecError(ValueError):
    # Errors raised due to invalid specification of the Storage object
    pass


class StorageInitError(StorageError):
    # Error raised when Initialization fails - either due to permissions,
    # unavailable name, or other reasons.
    pass


class StorageBucketCreateError(StorageInitError):
    # Error raised when bucket creation fails.
    pass


class StorageBucketGetError(StorageInitError):
    # Error raised if attempt to fetch an existing bucket fails.
    pass


class StorageBucketDeleteError(StorageError):
    # Error raised if attempt to delete an existing bucket fails.
    pass


class StorageUploadError(StorageError):
    # Error raised when bucket is successfully initialized, but upload fails,
    # either due to permissions, ctrl-c, or other reasons.
    pass


class StorageSourceError(StorageSpecError):
    # Error raised when the source of the storage is invalid. E.g., does not
    # exist, malformed path, or other reasons.
    pass


class StorageNameError(StorageSpecError):
    # Error raised when the source of the storage is invalid. E.g., does not
    # exist, malformed path, or other reasons.
    pass


class StorageModeError(StorageSpecError):
    # Error raised when the storage mode is invalid or does not support the
    # requested operation (e.g., passing a file as source to MOUNT mode)
    pass


class StorageExternalDeletionError(StorageBucketGetError):
    # Error raised when the bucket is attempted to be fetched while it has been
    # deleted externally.
    pass


class NonExistentStorageAccountError(StorageExternalDeletionError):
    # Error raise when storage account provided through config.yaml or read
    # from store handle(local db) does not exist.
    pass


class NetworkError(Exception):
    """Raised when network fails."""

    pass


class CloudUserIdentityError(Exception):
    """Raised when the cloud identity is invalid."""

    pass


class ClusterOwnerIdentityMismatchError(Exception):
    """The cluster's owner identity does not match the current user identity."""

    pass


class NoCloudAccessError(Exception):
    """Raised when all clouds are disabled."""

    pass
