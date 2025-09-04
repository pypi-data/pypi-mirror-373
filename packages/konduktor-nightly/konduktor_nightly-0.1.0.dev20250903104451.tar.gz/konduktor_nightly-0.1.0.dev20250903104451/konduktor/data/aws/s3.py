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

"""Amazon Web Services (AWS) S3 Storage."""

import enum
import hashlib
import os
import re
import shlex
import subprocess
import tempfile
import time
import typing
import uuid
from typing import Any, Dict, List, Optional, Tuple

import colorama

from konduktor import config, logging
from konduktor.adaptors import aws
from konduktor.adaptors.aws import boto3
from konduktor.backends import constants as backend_constants
from konduktor.data import constants, data_utils, storage_utils
from konduktor.utils import (
    annotations,
    base64_utils,
    common_utils,
    exceptions,
    kubernetes_utils,
    rich_utils,
    ux_utils,
)

if typing.TYPE_CHECKING:
    from konduktor.adaptors.aws import boto3

logger = logging.get_logger(__name__)

# Maximum number of concurrent rsync upload processes
_MAX_CONCURRENT_UPLOADS = 32

_CREDENTIAL_FILES = ['credentials', 'config']

AWS_SECRET_NAME = 'awscredentials'
AWS_CREDENTIALS_KEY = 'awscredentials'

DEFAULT_AWS_CREDENTIALS_DIR = '~/.aws/'
DEFAULT_AWS_CREDENTIAL_PATH = '~/.aws/credentials'
DEFAULT_AWS_CONFIG_PATH = '~/.aws/config'

_LOCK_PATH = '~/.konduktor/s3_storage.lock'


class AWSIdentityType(enum.Enum):
    """AWS identity type.

    The account type is determined by the current user identity, based on `aws
    configure list`. We will check the existence of the value in the output of
    `aws configure list` to determine the account type.
    """

    #       Name                    Value             Type    Location
    #       ----                    -----             ----    --------
    #    profile                     1234              env    ...
    # access_key     ****************abcd              sso
    # secret_key     ****************abcd              sso
    #     region                <not set>             None    None
    SSO = 'sso'
    ENV = 'env'
    IAM_ROLE = 'iam-role'
    CONTAINER_ROLE = 'container-role'
    CUSTOM_PROCESS = 'custom-process'
    ASSUME_ROLE = 'assume-role'

    #       Name                    Value             Type    Location
    #       ----                    -----             ----    --------
    #    profile                <not set>             None    None
    # access_key     ****************abcd shared-credentials-file
    # secret_key     ****************abcd shared-credentials-file
    #     region                us-east-1      config-file    ~/.aws/config
    SHARED_CREDENTIALS_FILE = 'shared-credentials-file'

    # IN GCS.PY
    def can_credential_expire(self) -> bool:
        """Check if the AWS identity type can expire.

        SSO,IAM_ROLE and CONTAINER_ROLE are temporary credentials and refreshed
        automatically. ENV and SHARED_CREDENTIALS_FILE are short-lived
        credentials without refresh.
        IAM ROLE:
        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
        SSO/Container-role refresh token:
        https://docs.aws.amazon.com/solutions/latest/dea-api/auth-refreshtoken.html
        """
        # TODO(hong): Add a CLI based check for the expiration of the temporary
        #  credentials
        expirable_types = {AWSIdentityType.ENV, AWSIdentityType.SHARED_CREDENTIALS_FILE}
        return self in expirable_types


class S3Store(storage_utils.AbstractStore):
    """S3Store inherits from Storage Object and represents the backend
    for S3 buckets.
    """

    # k8s secret name for aws credentials
    _AWS_SECRET_NAME = f'{AWS_SECRET_NAME}-{common_utils.user_and_hostname_hash()}'
    _AWS_CREDENTIALS_KEY = AWS_CREDENTIALS_KEY

    _DEFAULT_REGION = 'us-east-1'
    _ACCESS_DENIED_MESSAGE = 'Access Denied'
    _CUSTOM_ENDPOINT_REGIONS = [
        'ap-east-1',
        'me-south-1',
        'af-south-1',
        'eu-south-1',
        'eu-south-2',
        'ap-south-2',
        'ap-southeast-3',
        'ap-southeast-4',
        'me-central-1',
        'il-central-1',
    ]

    _INDENT_PREFIX = '    '

    _STATIC_CREDENTIAL_HELP_STR = (
        'Run the following commands:'
        f'\n{_INDENT_PREFIX}  $ aws configure'
        f'\n{_INDENT_PREFIX}  $ aws configure list '
        '# Ensure that this shows identity is set.'
        f'\n{_INDENT_PREFIX}For more info: '
        'https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html'  # pylint: disable=line-too-long
    )

    _REPR = 'S3Store'

    def __init__(
        self,
        name: str,
        source: str,
        region: Optional[str] = _DEFAULT_REGION,
        is_sky_managed: Optional[bool] = False,
        sync_on_reconstruction: Optional[bool] = True,
        _bucket_sub_path: Optional[str] = None,
    ):
        self.client: 'boto3.client.Client'  # type: ignore[name-defined]
        self.bucket: 'constants.StorageHandle'
        if region in self._CUSTOM_ENDPOINT_REGIONS:
            logger.warning(
                'AWS opt-in regions are not supported for S3. '
                f'Falling back to default region '
                f'{self._DEFAULT_REGION} for bucket {name!r}.'
            )
            region = self._DEFAULT_REGION
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

    # IN GCS.PY
    def _validate(self):
        if self.source is not None and isinstance(self.source, str):
            if self.source.startswith('s3://'):
                assert self.name == data_utils.split_s3_path(self.source)[0], (
                    'S3 Bucket is specified as path, the name should be the'
                    ' same as S3 bucket.'
                )
                assert data_utils.verify_s3_bucket(self.name), (
                    f'Source specified as {self.source}, an S3 bucket. ',
                    'S3 Bucket should exist.',
                )
            # if self.source.startswith('gs://'):
            #     assert self.name == data_utils.split_gcs_path(self.source)[0], (
            #         'GCS Bucket is specified as path, the name should be '
            #         'the same as GCS bucket.'
            #     )
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

    # IN GCS.PY
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validates the name of the S3 store.

        Source for rules:
        https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
        """

        def _raise_no_traceback_name_error(err_str):
            with ux_utils.print_exception_no_traceback():
                raise exceptions.StorageNameError(err_str)

        if name is not None and isinstance(name, str):
            # Check for overall length
            if not 3 <= len(name) <= 63:
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} must be between 3 (min) '
                    'and 63 (max) characters long.'
                )

            # Check for valid characters and start/end with a number or letter
            pattern = r'^[a-z0-9][-a-z0-9._]*[a-z0-9]$'
            if not re.match(pattern, name):
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} can consist only of '
                    'lowercase letters, numbers, dots (.), and hyphens (-). '
                    'It must begin and end with a letter or number.'
                )

            # Check for two adjacent periods
            if '..' in name:
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} must not contain '
                    'two adjacent periods.'
                )

            # Check for IP address format
            ip_pattern = r'^(?:\d{1,3}\.){3}\d{1,3}$'
            if re.match(ip_pattern, name):
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} must not be formatted as '
                    'an IP address (for example, 192.168.5.4).'
                )

            # Check for 'xn--' prefix
            if name.startswith('xn--'):
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} must not start with the '
                    'prefix "xn--".'
                )

            # Check for '-s3alias' suffix
            if name.endswith('-s3alias'):
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} must not end with the '
                    'suffix "-s3alias".'
                )

            # Check for '--ol-s3' suffix
            if name.endswith('--ol-s3'):
                _raise_no_traceback_name_error(
                    f'Invalid store name: name {name} must not end with the '
                    'suffix "--ol-s3".'
                )
        else:
            _raise_no_traceback_name_error('Store name must be specified.')
        return name

    # IN GCS.PY
    def initialize(self):
        """Initializes the S3 store object on the cloud.

        Initialization involves fetching bucket if exists, or creating it if
        it does not.

        Raises:
          StorageBucketCreateError: If bucket creation fails
          StorageBucketGetError: If fetching existing bucket fails
          StorageInitError: If general initialization fails.
        """
        self.client = data_utils.create_s3_client(self.region)
        self.bucket, is_new_bucket = self._get_bucket()
        if self.is_sky_managed is None:
            # If is_sky_managed is not specified, then this is a new storage
            # object (i.e., did not exist in global_user_state) and we should
            # set the is_sky_managed property.
            # If is_sky_managed is specified, then we take no action.
            self.is_sky_managed = is_new_bucket

    # IN GCS.PY
    def upload(self):
        """Uploads source to store bucket.

        Upload must be called by the Storage handler - it is not called on
        Store initialization.

        Raises:
            StorageUploadError: if upload fails.
        """
        try:
            if isinstance(self.source, list):
                self.batch_aws_rsync(self.source, create_dirs=True)
            elif self.source is not None:
                if self.source.startswith('s3://'):
                    pass
                # elif self.source.startswith('gs://'):
                #     self._transfer_to_s3()
                # elif self.source.startswith('r2://'):
                #     self._transfer_to_s3()
                else:
                    self.batch_aws_rsync([self.source])
        except exceptions.StorageUploadError:
            raise
        except Exception as e:
            raise exceptions.StorageUploadError(
                f'Upload failed for store {self.name}'
            ) from e

    # IN GCS.PY
    def delete(self) -> None:
        deleted_by_skypilot = self._delete_s3_bucket(self.name)
        if deleted_by_skypilot:
            msg_str = f'Deleted S3 bucket {self.name}.'
        else:
            msg_str = (
                f'S3 bucket {self.name} may have been deleted '
                f'externally. Removing from local state.'
            )
        logger.info(f'{colorama.Fore.GREEN}{msg_str}' f'{colorama.Style.RESET_ALL}')

    # IN GCS.PY
    def get_handle(self) -> 'constants.StorageHandle':
        return aws.resource('s3').Bucket(self.name)

    # FROM data/storage.py but matches GCS.PY batch_gsutil_rsync() (s3 specific)
    def batch_aws_rsync(
        self, source_path_list: List['constants.Path'], create_dirs: bool = False
    ) -> None:
        """Invokes aws s3 sync to batch upload a list of local paths to S3

        AWS Sync by default uses 10 threads to upload files to the bucket.  To
        increase parallelism, modify max_concurrent_requests in your aws config
        file (Default path: ~/.aws/config).

        Since aws s3 sync does not support batch operations, we construct
        multiple commands to be run in parallel.

        Args:
            source_path_list: List of paths to local files or directories
            create_dirs: If the local_path is a directory and this is set to
                False, the contents of the directory are directly uploaded to
                root of the bucket. If the local_path is a directory and this is
                set to True, the directory is created in the bucket root and
                contents are uploaded to it.
        """
        sub_path = f'/{self._bucket_sub_path}' if self._bucket_sub_path else ''

        def get_file_sync_command(base_dir_path, file_names):
            includes = ' '.join(
                [f'--include {shlex.quote(file_name)}' for file_name in file_names]
            )
            base_dir_path = shlex.quote(base_dir_path)
            sync_command = (
                'aws s3 sync --no-follow-symlinks --exclude="*" '
                f'{includes} {base_dir_path} '
                f's3://{self.name}{sub_path}'
            )
            return sync_command

        def get_dir_sync_command(src_dir_path, dest_dir_name):
            # we exclude .git directory from the sync
            excluded_list = storage_utils.get_excluded_files(src_dir_path)
            excluded_list.append('.git/*')
            excludes = ' '.join(
                [f'--exclude {shlex.quote(file_name)}' for file_name in excluded_list]
            )
            src_dir_path = shlex.quote(src_dir_path)
            sync_command = (
                f'aws s3 sync --no-follow-symlinks {excludes} '
                f'{src_dir_path} '
                f's3://{self.name}{sub_path}/{dest_dir_name}'
            )
            return sync_command

        # Generate message for upload
        if len(source_path_list) > 1:
            source_message = f'{len(source_path_list)} paths'
        else:
            source_message = source_path_list[0]

        log_path = logging.generate_tmp_logging_file_path(
            constants._STORAGE_LOG_FILE_NAME
        )
        sync_path = f'{source_message} -> s3://{self.name}{sub_path}/'
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

    # IN GCS.PY
    def _get_bucket(self) -> Tuple['constants.StorageHandle', bool]:
        """Obtains the S3 bucket.

        If the bucket exists, this method will return the bucket.
        If the bucket does not exist, there are three cases:
          1) Raise an error if the bucket source starts with s3://
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
        s3 = aws.resource('s3')
        bucket = s3.Bucket(self.name)

        try:
            # Try Public bucket case.
            # This line does not error out if the bucket is an external public
            # bucket or if it is a user's bucket that is publicly
            # accessible.
            self.client.head_bucket(Bucket=self.name)
            self._validate_existing_bucket()
            return bucket, False
        except aws.botocore_exceptions().ClientError as e:
            error_code = e.response['Error']['Code']
            # AccessDenied error for buckets that are private and not owned by
            # user.
            if error_code == '403':
                command = f'aws s3 ls {self.name}'
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageBucketGetError(
                        f'Bucket {self.name} does not exist.'
                        + f' To debug, consider running `{command}`.'
                    ) from e
            # Bucket already exists but we tried to create it. Continue
            elif error_code == '409':
                command = f'aws s3 ls {self.name}'
                logger.info(
                    f'Bucket {self.name} already exists. Skipping '
                    f'creation. To check, consider running `{command}`'
                )

        if isinstance(self.source, str) and self.source.startswith('s3://'):
            with ux_utils.print_exception_no_traceback():
                raise exceptions.StorageBucketGetError(
                    'Attempted to use a non-existent bucket as a source: '
                    f'{self.source}. Consider using `aws s3 ls '
                    f'{self.source}` to debug.'
                )

        # If bucket cannot be found in both private and public settings,
        # the bucket is to be created by Sky. However, creation is skipped if
        # Store object is being reconstructed for deletion or re-mount with
        # sky start, and error is raised instead.
        if self.sync_on_reconstruction:
            bucket = self._create_s3_bucket(self.name, self.region)
            return bucket, True
        else:
            # Raised when Storage object is reconstructed for sky storage
            # delete or to re-mount Storages with sky start but the storage
            # is already removed externally.
            raise exceptions.StorageExternalDeletionError(
                'Attempted to fetch a non-existent bucket: ' f'{self.name}'
            )

    # IN GCS.PY
    def _download_file(self, remote_path: str, local_path: str) -> None:
        """Downloads file from remote to local on s3 bucket
        using the boto3 API

        Args:
          remote_path: str; Remote path on S3 bucket
          local_path: str; Local path on user's device
        """
        self.bucket.download_file(remote_path, local_path)

    # IN GCS.PY
    def _create_s3_bucket(
        self, bucket_name: str, region=_DEFAULT_REGION
    ) -> 'constants.StorageHandle':
        """Creates S3 bucket with specific name in specific region

        Args:
          bucket_name: str; Name of bucket
          region: str; Region name, e.g. us-west-1, us-east-2
        Raises:
          StorageBucketCreateError: If bucket creation fails.
        """
        s3_client = self.client
        try:
            create_bucket_config: Dict[str, Any] = {'Bucket': bucket_name}
            # If default us-east-1 region of create_bucket API is used,
            # the LocationConstraint must not be specified.
            # Reference: https://stackoverflow.com/a/51912090
            if region is not None and region != 'us-east-1':
                create_bucket_config['CreateBucketConfiguration'] = {
                    'LocationConstraint': region
                }
            s3_client.create_bucket(**create_bucket_config)
            logger.info(
                f'  {colorama.Style.DIM}Created S3 bucket {bucket_name!r} in '
                f'{region or "us-east-1"}{colorama.Style.RESET_ALL}'
            )

            # Add AWS tags configured in config.yaml to the bucket.
            # This is useful for cost tracking and external cleanup.
            bucket_tags = config.get_nested(('aws', 'labels'), {})
            if bucket_tags:
                s3_client.put_bucket_tagging(
                    Bucket=bucket_name,
                    Tagging={
                        'TagSet': [
                            {'Key': k, 'Value': v} for k, v in bucket_tags.items()
                        ]
                    },
                )

        except aws.botocore_exceptions().ClientError as e:
            with ux_utils.print_exception_no_traceback():
                raise exceptions.StorageBucketCreateError(
                    f'Attempted to create a bucket {self.name} but failed.'
                ) from e
        return aws.resource('s3').Bucket(bucket_name)

    # NOT IN GCS.PY but FROM data/storage.py (s3 specific)
    def _execute_s3_remove_command(
        self, command: str, bucket_name: str, hint_operating: str, hint_failed: str
    ) -> bool:
        try:
            with rich_utils.safe_status(ux_utils.spinner_message(hint_operating)):
                subprocess.check_output(command.split(' '), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if 'NoSuchBucket' in e.output.decode('utf-8'):
                logger.debug(f'Bucket {bucket_name} does not exist.')
                return False
            else:
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageBucketDeleteError(
                        f'{hint_failed}' f'Detailed error: {e.output}'
                    )
        return True

    # IN GCS.PY
    def _delete_s3_bucket(self, bucket_name: str) -> bool:
        """Deletes S3 bucket, including all objects in bucket

        Args:
            bucket_name: str; Name of bucket

        Returns:
            bool; True if bucket was deleted, False if it was deleted externally.

        Raises:
            StorageBucketDeleteError: If deleting the bucket fails.
        """
        # Deleting objects is very slow programatically
        # (i.e. bucket.objects.all().delete() is slow).
        # In addition, standard delete operations (i.e. via `aws s3 rm`)
        # are slow, since AWS puts deletion markers.
        # https://stackoverflow.com/questions/49239351/why-is-it-so-much-slower-to-delete-objects-in-aws-s3-than-it-is-to-create-them
        # The fastest way to delete is to run `aws s3 rb --force`,
        # which removes the bucket by force.
        remove_command = f'aws s3 rb s3://{bucket_name} --force'
        success = self._execute_s3_remove_command(
            remove_command,
            bucket_name,
            f'Deleting S3 bucket [green]{bucket_name}[/]',
            f'Failed to delete S3 bucket {bucket_name}.',
        )
        if not success:
            return False

        # Wait until bucket deletion propagates on AWS servers
        while data_utils.verify_s3_bucket(bucket_name):
            time.sleep(0.1)
        return True

    # NOT IN GCS.PY but FROM data/storage.py (s3 specific)
    def _delete_s3_bucket_sub_path(self, bucket_name: str, sub_path: str) -> bool:
        """Deletes the sub path from the bucket."""
        remove_command = f'aws s3 rm s3://{bucket_name}/{sub_path}/ --recursive'
        return self._execute_s3_remove_command(
            remove_command,
            bucket_name,
            f'Removing objects from S3 bucket ' f'[green]{bucket_name}/{sub_path}[/]',
            f'Failed to remove objects from S3 bucket {bucket_name}/{sub_path}.',
        )

    @classmethod
    @annotations.lru_cache(scope='global', maxsize=1)
    def _aws_configure_list(cls) -> Optional[bytes]:
        proc = subprocess.run(
            'aws configure list',
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            return None
        return proc.stdout

    @classmethod
    def _sso_credentials_help_str(cls, expired: bool = False) -> str:
        help_str = 'Run the following commands (must use AWS CLI v2):'
        if not expired:
            help_str += f'\n{cls._INDENT_PREFIX}  $ aws configure sso'
        help_str += (
            f'\n{cls._INDENT_PREFIX}  $ aws sso login --profile <profile_name>'
            f'\n{cls._INDENT_PREFIX}For more info: '
            'https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html'
        )
        return help_str

    @classmethod
    @annotations.lru_cache(
        scope='global', maxsize=1
    )  # Cache since getting identity is slow.
    def _sts_get_caller_identity(cls) -> Optional[List[List[str]]]:
        try:
            sts = aws.client('sts', check_credentials=False)
            # The caller identity contains 3 fields: UserId, Account, Arn.
            # 1. 'UserId' is unique across all AWS entity, which looks like
            # "AROADBQP57FF2AEXAMPLE:role-session-name"
            # 2. 'Account' can be shared by multiple users under the same
            # organization
            # 3. 'Arn' is the full path to the user, which can be reused when
            # the user is deleted and recreated.
            # Refer to: <https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html>
            # and <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable>
            user_info = sts.get_caller_identity()
            # Allow fallback to AccountId if UserId does not match, because:
            # 1. In the case where multiple IAM users belong a single root account,
            # those users normally share the visibility of the VMs, so we do not
            # need to identity them with each other. (There can be some cases,
            # when an IAM user is given a limited permission by the admin, we may
            # ignore that case for now, or print out a warning if the underlying
            # userid changed for a cluster).
            # 2. In the case where the multiple users belong to an organization,
            # those users will have different account id, so fallback works.
            user_ids = [user_info['UserId'], user_info['Account']]
        except aws.botocore_exceptions().NoCredentialsError as e:
            with ux_utils.print_exception_no_traceback():
                raise exceptions.CloudUserIdentityError(
                    'AWS credentials are not set. '
                    f'{cls._STATIC_CREDENTIAL_HELP_STR}\n'
                    f'{cls._INDENT_PREFIX}Details: `aws sts '
                    'get-caller-identity` failed with error:'
                    f' {common_utils.format_exception(e, use_bracket=True)}.'
                ) from None
        except aws.botocore_exceptions().ClientError as e:
            with ux_utils.print_exception_no_traceback():
                raise exceptions.CloudUserIdentityError(
                    'Failed to access AWS services with credentials. '
                    'Make sure that the access and secret keys are correct.'
                    f' {cls._STATIC_CREDENTIAL_HELP_STR}\n'
                    f'{cls._INDENT_PREFIX}Details: `aws sts '
                    'get-caller-identity` failed with error:'
                    f' {common_utils.format_exception(e, use_bracket=True)}.'
                ) from None
        except aws.botocore_exceptions().InvalidConfigError as e:
            # pylint: disable=import-outside-toplevel
            import awscli
            from packaging import version

            awscli_version = version.parse(awscli.__version__)
            if awscli_version < version.parse(
                '1.27.10'
            ) and 'configured to use SSO' in str(e):
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.CloudUserIdentityError(
                        'awscli is too old to use SSO.'
                        'Run the following command to upgrade:'
                        f'\n{cls._INDENT_PREFIX}  $ pip install awscli>=1.27.10'
                        f'\n{cls._INDENT_PREFIX}You may need to log into SSO again '
                        f'after upgrading. {cls._sso_credentials_help_str()}'
                    ) from None
            with ux_utils.print_exception_no_traceback():
                raise exceptions.CloudUserIdentityError(
                    f'Invalid AWS configuration.\n'
                    f'  Reason: {common_utils.format_exception(e, use_bracket=True)}.'
                ) from None
        except aws.botocore_exceptions().TokenRetrievalError:
            # This is raised when the access token is expired, which mainly
            # happens when the user is using temporary credentials or SSO
            # login.
            with ux_utils.print_exception_no_traceback():
                raise exceptions.CloudUserIdentityError(
                    'AWS access token is expired.'
                    f' {cls._sso_credentials_help_str(expired=True)}'
                ) from None
        except Exception as e:  # pylint: disable=broad-except
            with ux_utils.print_exception_no_traceback():
                raise exceptions.CloudUserIdentityError(
                    f'Failed to get AWS user.\n'
                    f'  Reason: {common_utils.format_exception(e, use_bracket=True)}.'
                ) from None
        # TODO: Return a list of identities in the profile when we support
        #   automatic switching for AWS. Currently we only support one identity.
        return [user_ids]

    # IN GCS.PY
    @classmethod
    @annotations.lru_cache(
        scope='global', maxsize=1
    )  # Cache since getting identity is slow.
    def get_user_identities(cls) -> List[List[str]]:
        """Returns a [UserId, Account] list that uniquely identifies the user.

        These fields come from `aws sts get-caller-identity` and are cached
        locally by `aws configure list` output. The identities are assumed to
        be stable for the duration of the `sky` process. Modifying the
        credentials while the `sky` process is running will not affect the
        identity returned by this function.

        We permit the same actual user to:

          - switch between different root accounts (after which both elements
            of the list will be different) and have their clusters owned by
            each account be protected; or

          - within the same root account, switch between different IAM
            users, and treat [user_id=1234, account=A] and
            [user_id=4567, account=A] to be the *same*. Namely, switching
            between these IAM roles within the same root account will cause
            the first element of the returned list to differ, and will allow
            the same actual user to continue to interact with their clusters.
            Note: this is not 100% safe, since the IAM users can have very
            specific permissions, that disallow them to access the clusters
            but it is a reasonable compromise as that could be rare.

        Returns:
            A list of strings that uniquely identifies the user on this cloud.
            For identity check, we will fallback through the list of strings
            until we find a match, and print a warning if we fail for the
            first string.

        Raises:
            exceptions.CloudUserIdentityError: if the user identity cannot be
                retrieved.
        """
        stdout = cls._aws_configure_list()
        if stdout is None:
            # `aws configure list` is not available, possible reasons:
            # - awscli is not installed but credentials are valid, e.g. run from
            #   an EC2 instance with IAM role
            # - aws credentials are not set, proceed anyway to get unified error
            #   message for users
            return cls._sts_get_caller_identity()
        config_hash = hashlib.md5(stdout).hexdigest()[:8]  # noqa: F841
        # Getting aws identity cost ~1s, so we cache the result with the output of
        # `aws configure list` as cache key. Different `aws configure list` output
        # can have same aws identity, our assumption is the output would be stable
        # in real world, so the number of cache files would be limited.
        # TODO(aylei): consider using a more stable cache key and evalute eviction.
        # TODO:(ryan) ??? Ignoring caching for now (returning early)
        return cls._sts_get_caller_identity()
        # cache_path = catalog_common.get_catalog_path(
        #     f'aws/.cache/user-identity-{config_hash}.txt')
        # if os.path.exists(cache_path):
        #     try:
        #         with open(cache_path, 'r', encoding='utf-8') as f:
        #             return json.loads(f.read())
        #     except json.JSONDecodeError:
        #         # cache is invalid, ignore it and fetch identity again
        #         pass
        #
        # result = cls._sts_get_caller_identity()
        # with open(cache_path, 'w', encoding='utf-8') as f:
        #     f.write(json.dumps(result))
        # return result

    # IN GCS.PY
    @classmethod
    def get_active_user_identity_str(cls) -> Optional[str]:
        user_identity = cls.get_active_user_identity()
        if user_identity is None:
            return None
        identity_str = f'{user_identity[0]} [account={user_identity[1]}]'
        return identity_str

    # IN GCS.PY
    @classmethod
    @annotations.lru_cache(scope='global', maxsize=1)
    def check_credentials(cls) -> Tuple[bool, Optional[str]]:
        """Checks if the user has access credentials to AWS."""

        dependency_installation_hints = (
            'AWS dependencies are not installed. '
            'Run the following commands:'
            f'\n{cls._INDENT_PREFIX}  $ pip install boto3 botocore awscli'
            f'\n{cls._INDENT_PREFIX}Credentials may also need to be set. '
            f'{cls._STATIC_CREDENTIAL_HELP_STR}'
        )

        # Checks if the AWS CLI is installed properly
        proc = subprocess.run(
            'aws --version',
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            return False, dependency_installation_hints
        try:
            # Checks if aws boto is installed properly
            # pylint: disable=import-outside-toplevel, unused-import
            import boto3  # noqa: F401
            import botocore  # noqa: F401
        except ImportError:
            return False, dependency_installation_hints

        # Checks if AWS credentials 1) exist and 2) are valid.
        # https://stackoverflow.com/questions/53548737/verify-aws-credentials-with-boto3
        try:
            identity_str = cls.get_active_user_identity_str()  # noqa: F841
        except exceptions.CloudUserIdentityError as e:
            return False, str(e)

        static_credential_exists = os.path.isfile(
            os.path.expanduser('~/.aws/credentials')
        )
        hints = None
        identity_type = cls._current_identity_type()
        single_cloud_hint = (
            ' It will work if you use AWS only, but will cause problems '
            'if you want to use multiple clouds. To set up static credentials, '
            'try: aws configure'
        )
        if identity_type == AWSIdentityType.SSO:
            hints = 'AWS SSO is set.'
            if static_credential_exists:
                hints += (
                    ' To ensure multiple clouds work correctly, please use Konduktor '
                    'with static credentials (e.g., ~/.aws/credentials) by unsetting '
                    'the AWS_PROFILE environment variable.'
                )
            else:
                hints += single_cloud_hint
        elif identity_type == AWSIdentityType.IAM_ROLE:
            # When using an IAM role, the credentials may not exist in the
            # ~/.aws/credentials file. So we don't check for the existence of the
            # file. This will happen when the user is on a VM (or
            # jobs-controller) created by an SSO account, i.e. the VM will be
            # assigned the IAM role: skypilot-v1.
            hints = f'AWS IAM role is set.{single_cloud_hint}'
        elif identity_type == AWSIdentityType.CONTAINER_ROLE:
            # Similar to the IAM ROLE, an ECS container may not store credentials
            # in the ~/.aws/credentials file. So we don't check for the existence of
            # the file. i.e. the container will be assigned the IAM role of the
            # task: skypilot-v1.
            hints = f'AWS container-role is set.{single_cloud_hint}'
        elif identity_type == AWSIdentityType.CUSTOM_PROCESS:
            # Similar to the IAM ROLE, a custom process may not store credentials
            # in the ~/.aws/credentials file. So we don't check for the existence of
            # the file. i.e. the custom process will be assigned the IAM role of the
            # task: skypilot-v1.
            hints = f'AWS custom-process is set.{single_cloud_hint}'
        elif identity_type == AWSIdentityType.ASSUME_ROLE:
            # When using ASSUME ROLE, the credentials are coming from a different
            # source profile. So we don't check for the existence of ~/.aws/credentials.
            # i.e. the assumed role will be assigned the IAM role of the
            # task: skypilot-v1.
            hints = f'AWS assume-role is set.{single_cloud_hint}'
        elif identity_type == AWSIdentityType.ENV:
            # When using ENV vars, the credentials are coming from the environment
            # variables. So we don't check for the existence of ~/.aws/credentials.
            # i.e. the identity is not determined by the file.
            hints = f'AWS env is set.{single_cloud_hint}'
        else:
            # This file is required because it is required by the VMs launched on
            # other clouds to access private s3 buckets and resources like EC2.
            # `get_active_user_identity` does not guarantee this file exists.
            if not static_credential_exists:
                return (
                    False,
                    '~/.aws/credentials does not exist. '
                    + cls._STATIC_CREDENTIAL_HELP_STR,
                )

        try:
            s3 = aws.client('s3')

            suffix = uuid.uuid4().hex[:6]
            test_bucket = f'konduktor-check-s3-{int(time.time())}-{suffix}'

            try:
                s3.create_bucket(Bucket=test_bucket)

                time.sleep(1)

                s3.get_bucket_location(Bucket=test_bucket)
                s3.list_objects_v2(Bucket=test_bucket, MaxKeys=1)

                # Object-related checks
                s3.put_object(Bucket=test_bucket, Key='test.txt', Body='hello')
                s3.get_object(Bucket=test_bucket, Key='test.txt')
                s3.delete_object(Bucket=test_bucket, Key='test.txt')

            finally:
                # Always attempt to clean up, even if earlier checks failed
                try:
                    s3.delete_bucket(Bucket=test_bucket)
                except Exception:
                    raise RuntimeError(
                        'AWS S3 delete bucket permission is missing. '
                        'Please check your policy.\n'
                    )

        except Exception:
            return False, (
                'One or more AWS S3 permissions are missing. '
                'Please check your policy.\n'
            )

        logger.info(
            f'AWS credentials are valid '
            f'for the current identity {logging.CHECK_MARK_EMOJI}'
        )
        logger.info('Creating k8s secret with AWS credentials...')
        set_ok, result = cls.set_secret_credentials()
        if not set_ok:
            logger.error(f'Failed to create k8s secret with AWS credentials: {result}')
            return False, result
        return True, hints

    @classmethod
    def _current_identity_type(cls) -> Optional[AWSIdentityType]:
        stdout = cls._aws_configure_list()
        if stdout is None:
            return None
        output = stdout.decode()

        # We determine the identity type by looking at the output of
        # `aws configure list`. The output looks like:
        #   Name                   Value         Type    Location
        #   ----                   -----         ----    --------
        #   profile                <not set>     None    None
        #   access_key     *       <not set>     sso     None
        #   secret_key     *       <not set>     sso     None
        #   region                 <not set>     None    None
        # We try to determine the identity type by looking for the
        # string "sso"/"iam-role" in the output, i.e. the "Type" column.

        def _is_access_key_of_type(type_str: str) -> bool:
            # The dot (.) does not match line separators.
            results = re.findall(rf'access_key.*{type_str}', output)
            if len(results) > 1:
                raise RuntimeError(f'Unexpected `aws configure list` output:\n{output}')
            return len(results) == 1

        for identity_type in AWSIdentityType:
            if _is_access_key_of_type(identity_type.value):
                return identity_type
        return AWSIdentityType.SHARED_CREDENTIALS_FILE

    # IN GCS.PY
    @classmethod
    def set_secret_credentials(cls) -> Tuple[bool, Optional[str]]:
        """
        Set the k8s secret storing the AWS credentials
        """
        context = kubernetes_utils.get_current_kube_config_context_name()
        namespace = kubernetes_utils.get_kube_config_context_namespace()

        # Check if credentials are provided via environment
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

        if access_key and secret_key:
            logger.info('Using AWS credentials from env')
            credentials_dir = tempfile.mkdtemp()
            credentials_path = os.path.join(credentials_dir, 'credentials')
            config_path = os.path.join(credentials_dir, 'config')

            with open(credentials_path, 'w') as f:
                f.write(f"""[default]
            aws_access_key_id = {access_key}
            aws_secret_access_key = {secret_key}
            """)

            with open(config_path, 'w') as f:
                f.write(f"""[default]
            region = {region}
            """)
        else:
            logger.info('Using AWS credentils from ~/.aws/')
            credentials_dir = DEFAULT_AWS_CREDENTIALS_DIR

        credentials_files = [
            os.path.expanduser(os.path.join(credentials_dir, f))
            for f in _CREDENTIAL_FILES
        ]

        secret_metadata = {
            'labels': {
                backend_constants.SECRET_KIND_LABEL: 'S3',
            },
        }

        ok, result = kubernetes_utils.set_secret(
            secret_name=cls._AWS_SECRET_NAME,
            namespace=namespace,
            context=context,
            data={
                cls._AWS_CREDENTIALS_KEY: base64_utils.zip_base64encode(
                    credentials_files
                )
            },
            secret_metadata=secret_metadata,
        )
        if not ok:
            logger.error(f'Failed to set AWS credentials in k8s secret: \n{result}')
            return False, result
        else:
            logger.info(
                f'AWS credentials set in k8s secret: {cls._AWS_SECRET_NAME} '
                f'in namespace {namespace} in context {context} '
                f'{logging.CHECK_MARK_EMOJI}'
            )

        try:
            identity = aws.client('sts').get_caller_identity()
            logger.info(
                f"Using AWS credentials for ARN: {identity['Arn']} "
                f"(UserId: {identity['UserId']}, Account: {identity['Account']})"
            )
        except Exception as e:
            logger.warning(f'Could not fetch caller identity: {e}')

        return True, None

    # IN GCS.PY
    @classmethod
    def get_k8s_credential_name(cls) -> str:
        return cls._AWS_SECRET_NAME


class S3CloudStorage(storage_utils.CloudStorage):
    """S3 Storage."""

    # List of commands to install AWS CLI
    _GET_AWSCLI = [
        'command -v aws >/dev/null 2>&1 || ('
        'apt-get update && apt-get install -y curl unzip && '
        'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && '  # noqa: E501
        'unzip awscliv2.zip && '
        './aws/install -i ~/aws-cli -b ~/bin && '
        'export PATH=$HOME/bin:$PATH && '
        'rm -rf aws awscliv2.zip'
        ') && export PATH=$HOME/bin:$PATH'
    ]

    _STORE: typing.Type[storage_utils.AbstractStore] = S3Store

    # IN GCS.PY
    def is_directory(self, url: str) -> bool:
        """Returns whether S3 'url' is a directory.

        In cloud object stores, a "directory" refers to a regular object whose
        name is a prefix of other objects.
        """
        s3 = aws.resource('s3')
        bucket_name, path = data_utils.split_s3_path(url)
        bucket = s3.Bucket(bucket_name)

        num_objects = 0
        for obj in bucket.objects.filter(Prefix=path):
            num_objects += 1
            if obj.key == path:
                return False
            # If there are more than 1 object in filter, then it is a directory
            if num_objects == 3:
                return True

        # A directory with few or no items
        return True

    # IN GCS.PY
    def make_sync_dir_command(self, source: str, destination: str) -> str:
        """Downloads using AWS CLI."""
        # AWS Sync by default uses 10 threads to upload files to the bucket.
        # To increase parallelism, modify max_concurrent_requests in your
        # aws config file (Default path: ~/.aws/config).
        all_commands = list(self._GET_AWSCLI)

        all_commands.append(f'aws s3 sync --no-follow-symlinks {source} {destination}')
        return ' && '.join(all_commands)

    # IN GCS.PY
    def make_sync_file_command(self, source: str, destination: str) -> str:
        all_commands = list(self._GET_AWSCLI)

        all_commands.append(f'aws s3 cp {source} {destination}')
        return ' && '.join(all_commands)
