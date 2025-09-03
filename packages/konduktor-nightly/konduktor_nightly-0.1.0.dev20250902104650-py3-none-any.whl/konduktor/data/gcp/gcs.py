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

"""Google Cloud Platform Storage."""

import enum
import os
import re
import shlex
import subprocess
import time
import typing
from typing import List, Optional, Tuple

import colorama

if typing.TYPE_CHECKING:
    from google.cloud import storage as gcs_storage

from konduktor import logging
from konduktor.adaptors import gcp
from konduktor.backends import constants as backend_constants
from konduktor.data import constants, data_utils, storage_utils
from konduktor.data.gcp import utils
from konduktor.utils import (
    base64_utils,
    common_utils,
    exceptions,
    kubernetes_utils,
    rich_utils,
    ux_utils,
)

logger = logging.get_logger(__name__)

# Maximum number of concurrent rsync upload processes
_MAX_CONCURRENT_UPLOADS = 32

# Env var pointing to any service account key. If it exists, this path takes
# priority over the DEFAULT_GCP_APPLICATION_CREDENTIAL_PATH below, and will be
# used instead for Konduktro-launched instances. This is the same behavior as
# gcloud:
# https://cloud.google.com/docs/authentication/provide-credentials-adc#local-key
_GCP_APPLICATION_CREDENTIAL_ENV = 'GOOGLE_APPLICATION_CREDENTIALS'
# NOTE: do not expanduser() on this path. It's used as a destination path on the
# remote cluster.
DEFAULT_GCP_APPLICATION_CREDENTIAL_PATH: str = (
    '~/.config/gcloud/' 'application_default_credentials.json'
)
DEFAULT_GCP_CREDENTIALS_DIR = '~/.config/gcloud'

# TODO(wei-lin): config_default may not be the config in use.
# See: https://github.com/skypilot-org/skypilot/pull/1539
# NOTE: do not expanduser() on this path. It's used as a destination path on the
# remote cluster.
GCP_CONFIG_PATH = '~/.config/gcloud/configurations/config_default'

# Minimum set of files under ~/.config/gcloud that grant GCP access.
_CREDENTIAL_FILES = [
    'credentials.db',
    'access_tokens.db',
    'configurations',
    'legacy_credentials',
    'active_config',
    'application_default_credentials.json',
]

# k8s secret name for gcp credentials
GCP_SECRET_NAME = 'gcpcredentials'
GCP_CREDENTIALS_KEY = 'gcpcredentials'

# NOTE: do not expanduser() on this path. It's used as a destination path on the
# remote cluster.
_GCLOUD_INSTALLATION_LOG = '~/.konduktor/logs/gcloud_installation.log'
_GCLOUD_VERSION = '424.0.0'
# Need to be run with /bin/bash
# We factor out the installation logic to keep it align in both spot
# controller and cloud stores.
GOOGLE_SDK_INSTALLATION_COMMAND: str = f'pushd /tmp &>/dev/null && \
    {{ gcloud --help > /dev/null 2>&1 || \
    {{ mkdir -p {os.path.dirname(_GCLOUD_INSTALLATION_LOG)} && \
    wget --quiet https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-{_GCLOUD_VERSION}-linux-x86_64.tar.gz > {_GCLOUD_INSTALLATION_LOG} && \
    tar xzf google-cloud-sdk-{_GCLOUD_VERSION}-linux-x86_64.tar.gz >> {_GCLOUD_INSTALLATION_LOG} && \
    rm -rf ~/google-cloud-sdk >> {_GCLOUD_INSTALLATION_LOG}  && \
    mv google-cloud-sdk ~/ && \
    ~/google-cloud-sdk/install.sh -q >> {_GCLOUD_INSTALLATION_LOG} 2>&1 && \
    echo "source ~/google-cloud-sdk/path.bash.inc > /dev/null 2>&1" >> ~/.bashrc && \
    source ~/google-cloud-sdk/path.bash.inc >> {_GCLOUD_INSTALLATION_LOG} 2>&1; }}; }} && \
    popd &>/dev/null'  # noqa: E501


class GCPIdentityType(enum.Enum):
    """GCP identity type.

    The account type is determined by the current user identity, based on
    the identity email.
    """

    # Example of a service account email:
    #   skypilot-v1@xxxx.iam.gserviceaccount.com
    SERVICE_ACCOUNT = 'iam.gserviceaccount.com'

    SHARED_CREDENTIALS_FILE = ''

    def can_credential_expire(self) -> bool:
        return self == GCPIdentityType.SHARED_CREDENTIALS_FILE


def _run_output(cmd):
    proc = subprocess.run(
        cmd, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    return proc.stdout.decode('ascii')


def is_api_disabled(endpoint: str, project_id: str) -> bool:
    proc = subprocess.run(
        (
            f'gcloud services list --project {project_id} '
            f' | grep {endpoint}.googleapis.com'
        ),
        check=False,
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    return proc.returncode != 0


class GcsStore(storage_utils.AbstractStore):
    """GcsStore inherits from Storage Object and represents the backend
    for GCS buckets.
    """

    # k8s secret name for gcp credentials
    _GCP_SECRET_NAME = f'{GCP_SECRET_NAME}-{common_utils.user_and_hostname_hash()}'
    _GCP_CREDENTIALS_KEY = GCP_CREDENTIALS_KEY

    _ACCESS_DENIED_MESSAGE = 'AccessDeniedException'

    _INDENT_PREFIX = '    '
    _DEPENDENCY_HINT = (
        'GCP tools are not installed. Run the following commands:\n'
        # Install the Google Cloud SDK:
        f'{_INDENT_PREFIX}  $ pip install google-api-python-client\n'
        f'{_INDENT_PREFIX}  $ conda install -c conda-forge '
        'google-cloud-sdk -y'
    )

    _CREDENTIAL_HINT = (
        'Run the following commands:\n'
        # This authenticates the CLI to make `gsutil` work:
        f'{_INDENT_PREFIX}  $ gcloud init\n'
        # This will generate
        # ~/.config/gcloud/application_default_credentials.json.
        f'{_INDENT_PREFIX}  $ gcloud auth application-default login\n'
    )
    _APPLICATION_CREDENTIAL_HINT = (
        'Run the following commands:\n'
        f'{_INDENT_PREFIX}  $ gcloud auth application-default login\n'
        f'{_INDENT_PREFIX}Or set the environment variable '
        'GOOGLE_APPLICATION_CREDENTIALS '
        'to the path of your service account key file.\n'
    )

    _REPR = 'GcsStore'

    def __init__(
        self,
        name: str,
        source: str,
        region: Optional[str] = 'us-central1',
        is_sky_managed: Optional[bool] = False,
        sync_on_reconstruction: Optional[bool] = True,
        _bucket_sub_path: Optional[str] = None,
    ):
        self.client: 'gcs_storage.Client'
        self.bucket: 'constants.StorageHandle'
        super().__init__(
            name,
            source,
            region,
            is_sky_managed,
            sync_on_reconstruction,
            _bucket_sub_path,
        )

    def __repr__(self):
        return self._REPR

    def _validate(self):
        if self.source is not None and isinstance(self.source, str):
            # if self.source.startswith('s3://'):
            #     assert self.name == data_utils.split_s3_path(self.source)[0], (
            #         'S3 Bucket is specified as path, the name should be the'
            #         ' same as S3 bucket.')
            #     assert data_utils.verify_s3_bucket(self.name), (
            #         f'Source specified as {self.source}, an S3 bucket. ',
            #         'S3 Bucket should exist.')
            if self.source.startswith('gs://'):
                assert self.name == data_utils.split_gcs_path(self.source)[0], (
                    'GCS Bucket is specified as path, the name should be '
                    'the same as GCS bucket.'
                )
            # elif data_utils.is_az_container_endpoint(self.source):
            #     storage_account_name, container_name, _ = (
            #         data_utils.split_az_path(self.source))
            #     assert self.name == container_name, (
            #         'Azure bucket is specified as path, the name should be '
            #         'the same as Azure bucket.')
            #     assert data_utils.verify_az_bucket(
            #         storage_account_name, self.name), (
            #             f'Source specified as {self.source}, an Azure bucket. '
            #             'Azure bucket should exist.')
            # elif self.source.startswith('r2://'):
            #     assert self.name == data_utils.split_r2_path(self.source)[0], (
            #         'R2 Bucket is specified as path, the name should be '
            #         'the same as R2 bucket.')
            #     assert data_utils.verify_r2_bucket(self.name), (
            #         f'Source specified as {self.source}, a R2 bucket. ',
            #         'R2 Bucket should exist.')
            # elif self.source.startswith('cos://'):
            #     assert self.name == data_utils.split_cos_path(self.source)[0], (
            #         'COS Bucket is specified as path, the name should be '
            #         'the same as COS bucket.')
            #     assert data_utils.verify_ibm_cos_bucket(self.name), (
            #         f'Source specified as {self.source}, a COS bucket. ',
            #         'COS Bucket should exist.')
        # Validate name
        self.name = self.validate_name(self.name)

    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validates the name of the GCS store.

        Source for rules: https://cloud.google.com/storage/docs/buckets#naming
        """

        def _raise_no_traceback_name_error(err_str):
            with ux_utils.print_exception_no_traceback():
                raise exceptions.StorageNameError(err_str)

        if name is not None and isinstance(name, str):
            # Check for overall length
            if not 3 <= len(name) <= 222:
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} must contain 3-222 ' 'characters.'
                )

            # Check for valid characters and start/end with a number or letter
            pattern = r'^[a-z0-9][-a-z0-9._]*[a-z0-9]$'
            if not re.match(pattern, name):
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} can only contain '
                    'lowercase letters, numeric characters, dashes (-), '
                    'underscores (_), and dots (.). Spaces are not allowed. '
                    'Names must start and end with a number or letter.'
                )

            # Check for 'goog' prefix and 'google' in the name
            if name.startswith('goog') or any(
                s in name for s in ['google', 'g00gle', 'go0gle', 'g0ogle']
            ):
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} cannot begin with the '
                    '"goog" prefix or contain "google" in various forms.'
                )

            # Check for dot-separated components length
            components = name.split('.')
            if any(len(component) > 63 for component in components):
                _raise_no_traceback_name_error(
                    'Invalid store name: Dot-separated components in name '
                    f'{name} can be no longer than 63 characters.'
                )

            if '..' in name or '.-' in name or '-.' in name:
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} must not contain two '
                    'adjacent periods or a dot next to a hyphen.'
                )

            # Check for IP address format
            ip_pattern = r'^(?:\d{1,3}\.){3}\d{1,3}$'
            if re.match(ip_pattern, name):
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} cannot be represented as '
                    'an IP address in dotted-decimal notation '
                    '(for example, 192.168.5.4).'
                )
        else:
            _raise_no_traceback_name_error('Store name must be specified.')
        return name

    def initialize(self):
        """Initializes the GCS store object on the cloud.

        Initialization involves fetching bucket if exists, or creating it if
        it does not.

        Raises:
          StorageBucketCreateError: If bucket creation fails
          StorageBucketGetError: If fetching existing bucket fails
          StorageInitError: If general initialization fails.
        """
        self.client = gcp.storage_client()
        self.bucket, is_new_bucket = self._get_bucket()
        if self.is_sky_managed is None:
            # If is_sky_managed is not specified, then this is a new storage
            # object (i.e., did not exist in global_user_state) and we should
            # set the is_sky_managed property.
            # If is_sky_managed is specified, then we take no action.
            self.is_sky_managed = is_new_bucket

    def upload(self):
        """Uploads source to store bucket.

        Upload must be called by the Storage handler - it is not called on
        Store initialization.

        Raises:
            StorageUploadError: if upload fails.
        """
        try:
            if isinstance(self.source, list):
                self.batch_gsutil_rsync(self.source, create_dirs=True)
            elif self.source is not None:
                if self.source.startswith('gs://'):
                    pass
                elif self.source.startswith('s3://'):
                    self._transfer_to_gcs()
                elif self.source.startswith('r2://'):
                    self._transfer_to_gcs()
                else:
                    # If a single directory is specified in source, upload
                    # contents to root of bucket by suffixing /*.
                    self.batch_gsutil_rsync([self.source])
        except exceptions.StorageUploadError:
            raise
        except Exception as e:
            raise exceptions.StorageUploadError(
                f'Upload failed for store {self.name}'
            ) from e

    def delete(self) -> None:
        deleted_by_skypilot = self._delete_gcs_bucket(self.name)
        if deleted_by_skypilot:
            msg_str = f'Deleted GCS bucket {self.name}.'
        else:
            msg_str = (
                f'GCS bucket {self.name} may have been deleted '
                f'externally. Removing from local state.'
            )
        logger.info(f'{colorama.Fore.GREEN}{msg_str}' f'{colorama.Style.RESET_ALL}')

    def get_handle(self) -> 'constants.StorageHandle':
        return self.client.get_bucket(self.name)

    def batch_gsutil_cp(
        self, source_path_list: List['constants.Path'], create_dirs: bool = False
    ) -> None:
        """Invokes gsutil cp -n to batch upload a list of local paths

        -n flag to gsutil cp checks the existence of an object before uploading,
        making it similar to gsutil rsync. Since it allows specification of a
        list of files, it is faster than calling gsutil rsync on each file.
        However, unlike rsync, files are compared based on just their filename,
        and any updates to a file would not be copied to the bucket.
        """
        # Generate message for upload
        if len(source_path_list) > 1:
            source_message = f'{len(source_path_list)} paths'
        else:
            source_message = source_path_list[0]

        # If the source_path list contains a directory, then gsutil cp -n
        # copies the dir as is to the root of the bucket. To copy the
        # contents of directory to the root, add /* to the directory path
        # e.g., /mydir/*
        source_path_list = [
            str(path) + '/*' if (os.path.isdir(path) and not create_dirs) else str(path)
            for path in source_path_list
        ]
        copy_list = '\n'.join(
            os.path.abspath(os.path.expanduser(p)) for p in source_path_list
        )
        gsutil_alias, alias_gen = data_utils.get_gsutil_command()
        sub_path = f'/{self._bucket_sub_path}' if self._bucket_sub_path else ''
        sync_command = (
            f'{alias_gen}; echo "{copy_list}" | {gsutil_alias} '
            f'cp -e -n -r -I gs://{self.name}{sub_path}'
        )

        log_path = logging.generate_tmp_logging_file_path(
            constants._STORAGE_LOG_FILE_NAME
        )

        with rich_utils.safe_status(
            ux_utils.spinner_message(
                f'Syncing {source_message} -> ' f'gs://{self.name}{sub_path}'
            )
        ):
            data_utils.run_upload_cli(
                sync_command,
                self._ACCESS_DENIED_MESSAGE,
                bucket_name=self.name,
                log_path=log_path,
            )

    def batch_gsutil_rsync(
        self, source_path_list: List['constants.Path'], create_dirs: bool = False
    ) -> None:
        """Invokes gsutil rsync to batch upload a list of local paths

        Since gsutil rsync does not support include commands, We use negative
        look-ahead regex to exclude everything else than the path(s) we want to
        upload.

        Since gsutil rsync does not support batch operations, we construct
        multiple commands to be run in parallel.

        Args:
            source_path_list: List of paths to local files or directories
            create_dirs: If the local_path is a directory and this is set to
                False, the contents of the directory are directly uploaded to
                root of the bucket. If the local_path is a directory and this is
                set to True, the directory is created in the bucket root and
                contents are uploaded to it.
        """

        def get_file_sync_command(base_dir_path, file_names):
            sync_format = '|'.join(file_names)
            gsutil_alias, alias_gen = data_utils.get_gsutil_command()
            base_dir_path = shlex.quote(base_dir_path)
            sync_command = (
                f'{alias_gen}; {gsutil_alias} '
                f"rsync -e -x '^(?!{sync_format}$).*' "
                f'{base_dir_path} gs://{self.name}{sub_path}'
            )
            return sync_command

        def get_dir_sync_command(src_dir_path, dest_dir_name):
            excluded_list = storage_utils.get_excluded_files(src_dir_path)
            # we exclude .git directory from the sync
            excluded_list.append(r'^\.git/.*$')
            excludes = '|'.join(excluded_list)
            gsutil_alias, alias_gen = data_utils.get_gsutil_command()
            src_dir_path = shlex.quote(src_dir_path)
            sync_command = (
                f'{alias_gen}; {gsutil_alias} '
                f"rsync -e -r -x '({excludes})' {src_dir_path} "
                f'gs://{self.name}{sub_path}/{dest_dir_name}'
            )
            return sync_command

        sub_path = f'/{self._bucket_sub_path}' if self._bucket_sub_path else ''
        # Generate message for upload
        if len(source_path_list) > 1:
            source_message = f'{len(source_path_list)} paths'
        else:
            source_message = source_path_list[0]

        log_path = logging.generate_tmp_logging_file_path(
            constants._STORAGE_LOG_FILE_NAME
        )
        sync_path = f'{source_message} -> gs://{self.name}{sub_path}/'
        with rich_utils.safe_status(
            ux_utils.spinner_message(f'Syncing {sync_path}', log_path=log_path)
        ):
            data_utils.parallel_upload(
                source_path_list,
                get_file_sync_command,
                get_dir_sync_command,
                log_path,
                self.name,
                self._ACCESS_DENIED_MESSAGE,
                create_dirs=create_dirs,
                max_concurrent_uploads=_MAX_CONCURRENT_UPLOADS,
            )
        logger.info(
            ux_utils.finishing_message(f'Storage synced: {sync_path}', log_path)
        )

    def _get_bucket(self) -> Tuple['constants.StorageHandle', bool]:
        """Obtains the GCS bucket.
        If the bucket exists, this method will connect to the bucket.

        If the bucket does not exist, there are three cases:
          1) Raise an error if the bucket source starts with gs://
          2) Return None if bucket has been externally deleted and
             sync_on_reconstruction is False
          3) Create and return a new bucket otherwise

        Raises:
            StorageSpecError: If externally created bucket is attempted to be
                mounted without specifying storage source.
            StorageBucketCreateError: If creating the bucket fails
            StorageBucketGetError: If fetching a bucket fails
            StorageExternalDeletionError: If externally deleted storage is
                attempted to be fetched while reconstructing the storage for
                'sky storage delete' or 'sky start'
        """
        try:
            bucket = self.client.get_bucket(self.name)
            self._validate_existing_bucket()
            return bucket, False
        except gcp.not_found_exception() as e:
            if isinstance(self.source, str) and self.source.startswith('gs://'):
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageBucketGetError(
                        'Attempted to use a non-existent bucket as a source: '
                        f'{self.source}'
                    ) from e
            else:
                # If bucket cannot be found (i.e., does not exist), it is to be
                # created by Sky. However, creation is skipped if Store object
                # is being reconstructed for deletion or re-mount with
                # sky start, and error is raised instead.
                if self.sync_on_reconstruction:
                    bucket = self._create_gcs_bucket(self.name, self.region)
                    return bucket, True
                else:
                    # This is raised when Storage object is reconstructed for
                    # sky storage delete or to re-mount Storages with sky start
                    # but the storage is already removed externally.
                    raise exceptions.StorageExternalDeletionError(
                        'Attempted to fetch a non-existent bucket: ' f'{self.name}'
                    ) from e
        except gcp.forbidden_exception():
            # Try public bucket to see if bucket exists
            logger.info('External Bucket detected; Connecting to external bucket...')
            try:
                a_client = gcp.anonymous_storage_client()
                bucket = a_client.bucket(self.name)
                # Check if bucket can be listed/read from
                next(bucket.list_blobs())
                return bucket, False
            except (gcp.not_found_exception(), ValueError) as e:
                command = f'gsutil ls gs://{self.name}'
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageBucketGetError(
                        f'Bucket {self.name} does not exist.'
                        + f' To debug, consider running `{command}`.'
                    ) from e

    def _download_file(self, remote_path: str, local_path: str) -> None:
        """Downloads file from remote to local on GS bucket

        Args:
          remote_path: str; Remote path on GS bucket
          local_path: str; Local path on user's device
        """
        blob = self.bucket.blob(remote_path)
        blob.download_to_filename(local_path, timeout=None)

    def _create_gcs_bucket(
        self, bucket_name: str, region='us-central1'
    ) -> 'constants.StorageHandle':
        """Creates GCS bucket with specific name in specific region

        Args:
          bucket_name: str; Name of bucket
          region: str; Region name, e.g. us-central1, us-west1
        """
        try:
            bucket = self.client.bucket(bucket_name)
            bucket.storage_class = 'STANDARD'
            new_bucket = self.client.create_bucket(bucket, location=region)
        except gcp.conflict_exception():
            # it's fine to pass this exception since
            # this means the bucket already exists
            pass
        except Exception as e:  # pylint: disable=broad-except
            with ux_utils.print_exception_no_traceback():
                raise exceptions.StorageBucketCreateError(
                    f'Attempted to create a bucket {self.name} but failed.'
                ) from e
        logger.info(
            f'  {colorama.Style.DIM}Created GCS bucket {new_bucket.name!r} in '
            f'{new_bucket.location} with storage class '
            f'{new_bucket.storage_class}{colorama.Style.RESET_ALL}'
        )
        return new_bucket

    def _delete_gcs_bucket(self, bucket_name: str) -> bool:
        """Deletes GCS bucket, including all objects in bucket

        Args:
          bucket_name: str; Name of bucket

        Returns:
         bool; True if bucket was deleted, False if it was deleted externally.
        """

        with rich_utils.safe_status(
            ux_utils.spinner_message(f'Deleting GCS bucket [green]{bucket_name}')
        ):
            try:
                self.client.get_bucket(bucket_name)
            except gcp.forbidden_exception() as e:
                # Try public bucket to see if bucket exists
                with ux_utils.print_exception_no_traceback():
                    raise PermissionError(
                        'External Bucket detected. User not allowed to delete '
                        'external bucket.'
                    ) from e
            except gcp.not_found_exception():
                # If bucket does not exist, it may have been deleted externally.
                # Do a no-op in that case.
                logger.debug(f'Bucket {bucket_name} does not exist.')
                return False
            try:
                gsutil_alias, alias_gen = data_utils.get_gsutil_command()
                remove_obj_command = (
                    f'{alias_gen};{gsutil_alias} ' f'rm -r gs://{bucket_name}'
                )
                subprocess.check_output(
                    remove_obj_command,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    executable='/bin/bash',
                )
                return True
            except subprocess.CalledProcessError as e:
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageBucketDeleteError(
                        f'Failed to delete GCS bucket {bucket_name}.'
                        f'Detailed error: {e.output}'
                    )

    @classmethod
    def _find_application_key_path(cls) -> str:
        # Check the application default credentials in the environment variable.
        # If the file does not exist, fallback to the default path.
        application_key_path = os.environ.get(_GCP_APPLICATION_CREDENTIAL_ENV, None)
        if application_key_path is not None:
            if not os.path.isfile(os.path.expanduser(application_key_path)):
                raise FileNotFoundError(
                    f'{_GCP_APPLICATION_CREDENTIAL_ENV}={application_key_path},'
                    ' but the file does not exist.'
                )
            return application_key_path
        if not os.path.isfile(
            os.path.expanduser(DEFAULT_GCP_APPLICATION_CREDENTIAL_PATH)
        ):
            # Fallback to the default application credential path.
            raise FileNotFoundError(DEFAULT_GCP_APPLICATION_CREDENTIAL_PATH)
        return DEFAULT_GCP_APPLICATION_CREDENTIAL_PATH

    @classmethod
    def _get_identity_type(cls) -> Optional[GCPIdentityType]:
        try:
            account = cls.get_active_user_identity()
        except exceptions.CloudUserIdentityError:
            return None
        if account is None:
            return None
        assert account is not None
        if GCPIdentityType.SERVICE_ACCOUNT.value in account[0]:
            return GCPIdentityType.SERVICE_ACCOUNT
        return GCPIdentityType.SHARED_CREDENTIALS_FILE

    @classmethod
    def get_project_id(cls, dryrun: bool = False) -> str:
        if dryrun:
            return 'dryrun-project-id'
        # pylint: disable=import-outside-toplevel
        from google import auth  # type: ignore

        _, project_id = auth.default()
        if project_id is None:
            raise exceptions.CloudUserIdentityError(
                'Failed to get GCP project id. Please make sure you have '
                'run the following: \n'
                f'{cls._INDENT_PREFIX}gcloud init; \n'
                f'{cls._INDENT_PREFIX}gcloud auth application-default login'
            )
        return project_id

    @classmethod
    def get_user_identities(cls) -> List[List[str]]:
        """Returns the email address + project id of the active user."""
        try:
            account = _run_output(
                'gcloud auth list --filter=status:ACTIVE ' '--format="value(account)"'
            )
            account = account.strip()
        except subprocess.CalledProcessError as e:
            with ux_utils.print_exception_no_traceback():
                raise exceptions.CloudUserIdentityError(
                    f'Failed to get GCP user identity with unknown '
                    f'exception.\n'
                    '  Reason: '
                    f'{common_utils.format_exception(e, use_bracket=True)}'
                ) from e
        if not account:
            with ux_utils.print_exception_no_traceback():
                raise exceptions.CloudUserIdentityError(
                    'No GCP account is activated. Try running `gcloud '
                    'auth list --filter=status:ACTIVE '
                    '--format="value(account)"` and ensure it correctly '
                    'returns the current user.'
                )
        try:
            project_id = cls.get_project_id()
        except Exception as e:  # pylint: disable=broad-except
            with ux_utils.print_exception_no_traceback():
                raise exceptions.CloudUserIdentityError(
                    f'Failed to get GCP user identity with unknown '
                    f'exception.\n'
                    '  Reason: '
                    f'{common_utils.format_exception(e, use_bracket=True)}'
                ) from e
        # TODO: Return a list of identities in the profile when we support
        #   automatic switching for GCP. Currently we only support one identity.
        return [[f'{account} [project_id={project_id}]']]

    def get_active_user_identity_str(cls) -> Optional[str]:
        user_identity = cls.get_active_user_identity()
        if user_identity is None:
            return None
        return user_identity[0].replace('\n', '')

    @classmethod
    def check_credentials(cls) -> Tuple[bool, Optional[str]]:
        """
        Check if the credentials are valid for GCS store.
        """
        try:
            # Check google-api-python-client installation.
            import googleapiclient  # noqa: F401
            from google import auth  # type: ignore

            # Check the installation of google-cloud-sdk.
            _run_output('gcloud --version')
        except (ImportError, subprocess.CalledProcessError) as e:
            return False, (
                f'{cls._DEPENDENCY_HINT}\n'
                f'{cls._INDENT_PREFIX}Credentials may also need to be set. '
                f'{cls._CREDENTIAL_HINT}\n'
                f'{cls._INDENT_PREFIX}Details: '
                f'{common_utils.format_exception(e, use_bracket=True)}'
            )

        identity_type = cls._get_identity_type()
        if identity_type == GCPIdentityType.SHARED_CREDENTIALS_FILE:
            # This files are only required when using the shared credentials
            # to access GCP. They are not required when using service account.
            try:
                # These files are required because they will be synced to remote
                # VMs for `gsutil` to access private storage buckets.
                # `auth.default()` does not guarantee these files exist.
                for file in [
                    '~/.config/gcloud/access_tokens.db',
                    '~/.config/gcloud/credentials.db',
                ]:
                    if not os.path.isfile(os.path.expanduser(file)):
                        raise FileNotFoundError(file)
            except FileNotFoundError as e:
                return False, (
                    f'Credentails are not set. '
                    f'{cls._CREDENTIAL_HINT}\n'
                    f'{cls._INDENT_PREFIX}Details: '
                    f'{common_utils.format_exception(e, use_bracket=True)}'
                )

            try:
                cls._find_application_key_path()
            except FileNotFoundError as e:
                return False, (
                    f'Application credentials are not set. '
                    f'{cls._APPLICATION_CREDENTIAL_HINT}\n'
                    f'{cls._INDENT_PREFIX}Details: '
                    f'{common_utils.format_exception(e, use_bracket=True)}'
                )

        try:
            # Check if application default credentials are set.
            project_id = cls.get_project_id()

            # Check if the user is activated.
            identity = cls.get_active_user_identity()
        except (
            auth.exceptions.DefaultCredentialsError,
            exceptions.CloudUserIdentityError,
        ) as e:
            # See also: https://stackoverflow.com/a/53307505/1165051
            return False, (
                'Getting project ID or user identity failed. You can debug '
                'with `gcloud auth list`. To fix this, '
                f'{cls._CREDENTIAL_HINT[0].lower()}'
                f'{cls._CREDENTIAL_HINT[1:]}\n'
                f'{cls._INDENT_PREFIX}Details: '
                f'{common_utils.format_exception(e, use_bracket=True)}'
            )

        # Check APIs.
        apis = (
            ('cloudresourcemanager', 'Cloud Resource Manager'),
            ('iam', 'Identity and Access Management (IAM)'),
            ('storage', 'Cloud Storage'),
        )
        enabled_api = False
        for endpoint, display_name in apis:
            if is_api_disabled(endpoint, project_id):
                # For 'compute': ~55-60 seconds for the first run. If already
                # enabled, ~1s. Other API endpoints take ~1-5s to enable.
                if endpoint == 'compute':
                    suffix = ' (free of charge; this may take a minute)'
                else:
                    suffix = ' (free of charge)'
                print(f'\nEnabling {display_name} API{suffix}...')
                t1 = time.time()
                proc = subprocess.run(
                    f'gcloud services enable {endpoint}.googleapis.com '
                    f'--project {project_id}',
                    check=False,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                if proc.returncode == 0:
                    enabled_api = True
                    print(f'Done. Took {time.time() - t1:.1f} secs.')

        if enabled_api:
            print(
                '\nHint: Enabled GCP API(s) may take a few minutes to take '
                'effect. If any Konduktor commands/calls failed, retry after '
                'some time.'
            )

        # noqa: F401
        import google.auth

        # This takes user's credential info from "~/.config/gcloud/application_default_credentials.json".  # noqa: E501
        credentials, project = google.auth.default()
        crm = gcp.build(
            'cloudresourcemanager', 'v1', credentials=credentials, cache_discovery=False
        )
        gcp_minimal_permissions = utils.get_minimal_permissions()
        permissions = {'permissions': gcp_minimal_permissions}
        request = crm.projects().testIamPermissions(resource=project, body=permissions)
        with ux_utils.print_exception_no_traceback():
            ret_permissions = request.execute().get('permissions', [])
        diffs = set(gcp_minimal_permissions).difference(set(ret_permissions))
        if diffs:
            identity_str = identity[0] if identity else None
            return False, (
                'The following permissions are not enabled for the current '
                f'GCP identity ({identity_str}):\n    '
                f'{diffs}\n    '
                'For more details, visit: https://konduktor.readthedocs.io//en/latest/cloud-setup/cloud-permissions/gcp.html'
            )  # noqa: E501
        logger.info(
            f'GCP credentials are valid '
            f'for the current identity {logging.CHECK_MARK_EMOJI}'
        )
        logger.info('Creating k8s secret with GCP credentials...')
        set_ok, result = cls.set_secret_credentials()
        if not set_ok:
            logger.error(f'Failed to create k8s secret with GCP credentials: {result}')
            return False, result
        return True, None

    @classmethod
    def set_secret_credentials(cls) -> Tuple[bool, Optional[str]]:
        """
        Set the k8s secret storing the GCP credentials
        """
        context = kubernetes_utils.get_current_kube_config_context_name()
        namespace = kubernetes_utils.get_kube_config_context_namespace()
        credentials_dir = os.environ.get('CLOUDSDK_CONFIG', DEFAULT_GCP_CREDENTIALS_DIR)
        credentials_files = [
            os.path.expanduser(os.path.join(credentials_dir, f))
            for f in _CREDENTIAL_FILES
        ]

        secret_metadata = {
            'labels': {
                backend_constants.SECRET_KIND_LABEL: 'GCS',
            },
        }

        ok, result = kubernetes_utils.set_secret(
            secret_name=cls._GCP_SECRET_NAME,
            namespace=namespace,
            context=context,
            data={
                cls._GCP_CREDENTIALS_KEY: base64_utils.zip_base64encode(
                    credentials_files
                )
            },
            secret_metadata=secret_metadata,
        )
        if not ok:
            logger.error(f'Failed to set GCP credentials in k8s secret: \n{result}')
            return False, result
        else:
            logger.info(
                f'GCP credentials set in k8s secret: {cls._GCP_SECRET_NAME} '
                f'in namespace {namespace} in context {context} '
                f'{logging.CHECK_MARK_EMOJI}'
            )
        return True, None

    @classmethod
    def get_k8s_credential_name(cls) -> str:
        return cls._GCP_SECRET_NAME


class GcsCloudStorage(storage_utils.CloudStorage):
    """Google Cloud Storage."""

    # We use gsutil as a basic implementation.  One pro is that its -m
    # multi-threaded download is nice, which frees us from implementing
    # parellel workers on our end.
    # The gsutil command is part of the Google Cloud SDK, and we reuse
    # the installation logic here.
    _INSTALL_GSUTIL = GOOGLE_SDK_INSTALLATION_COMMAND
    _STORE: typing.Type[storage_utils.AbstractStore] = GcsStore

    @property
    def _gsutil_command(self):
        gsutil_alias, alias_gen = data_utils.get_gsutil_command()
        return (
            f'{alias_gen}; GOOGLE_APPLICATION_CREDENTIALS='
            f'{DEFAULT_GCP_APPLICATION_CREDENTIAL_PATH}; '
            # Explicitly activate service account. Unlike the gcp packages
            # and other GCP commands, gsutil does not automatically pick up
            # the default credential keys when it is a service account.
            'gcloud auth activate-service-account '
            '--key-file=$GOOGLE_APPLICATION_CREDENTIALS '
            '2> /dev/null || true; '
            f'{gsutil_alias}'
        )

    def is_directory(self, url: str) -> bool:
        """Returns whether 'url' is a directory.
        In cloud object stores, a "directory" refers to a regular object whose
        name is a prefix of other objects.
        """
        commands = [self._INSTALL_GSUTIL]
        commands.append(f'{self._gsutil_command} ls -d {url}')
        command = ' && '.join(commands)
        p = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            shell=True,
            check=True,
            executable='/bin/bash',
        )
        out = p.stdout.decode().strip()
        # Edge Case: Gcloud command is run for first time #437
        out = out.split('\n')[-1]
        # If <url> is a bucket root, then we only need `gsutil` to succeed
        # to make sure the bucket exists. It is already a directory.
        _, key = data_utils.split_gcs_path(url)
        if not key:
            return True
        # Otherwise, gsutil ls -d url will return:
        #   --> url.rstrip('/')          if url is not a directory
        #   --> url with an ending '/'   if url is a directory
        if not out.endswith('/'):
            assert out == url.rstrip('/'), (out, url)
            return False
        url = url if url.endswith('/') else (url + '/')
        assert out == url, (out, url)
        return True

    def make_sync_dir_command(self, source: str, destination: str) -> str:
        """Downloads a directory using gsutil."""
        download_via_gsutil = (
            f'{self._gsutil_command} ' f'rsync -e -r {source} {destination}'
        )
        all_commands = [self._INSTALL_GSUTIL]
        all_commands.append(download_via_gsutil)
        return ' && '.join(all_commands)

    def make_sync_file_command(self, source: str, destination: str) -> str:
        """Downloads a file using gsutil."""
        download_via_gsutil = f'{self._gsutil_command} ' f'cp {source} {destination}'
        all_commands = [self._INSTALL_GSUTIL]
        all_commands.append(download_via_gsutil)
        return ' && '.join(all_commands)
