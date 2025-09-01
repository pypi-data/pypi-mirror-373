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

"""Utility functions for the storage module."""

import glob
import os
import shlex
import subprocess
import typing
from typing import List, Optional

import colorama

if typing.TYPE_CHECKING:
    from konduktor.data.constants import SourceType, StorageHandle


from konduktor import constants, logging
from konduktor.utils import common_utils, exceptions

logger = logging.get_logger(__name__)

_FILE_EXCLUSION_FROM_GITIGNORE_FAILURE_MSG = (
    f'{colorama.Fore.YELLOW}Warning: Files/dirs '
    'specified in .gitignore will be uploaded '
    'to the cloud storage for {path!r}'
    'due to the following error: {error_msg!r}'
)


def get_excluded_files_from_konduktorignore(src_dir_path: str) -> List[str]:
    """List files and patterns ignored by the .konduktor file
    in the given source directory.
    """
    excluded_list: List[str] = []
    expand_src_dir_path = os.path.expanduser(src_dir_path)
    konduktorignore_path = os.path.join(
        expand_src_dir_path, constants.KONDUKTOR_IGNORE_FILE
    )

    try:
        with open(konduktorignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Make parsing consistent with rsync.
                    # Rsync uses '/' as current directory.
                    if line.startswith('/'):
                        line = '.' + line
                    else:
                        line = '**/' + line
                    # Find all files matching the pattern.
                    matching_files = glob.glob(
                        os.path.join(expand_src_dir_path, line), recursive=True
                    )
                    # Process filenames to comply with cloud rsync format.
                    for i in range(len(matching_files)):
                        matching_files[i] = os.path.relpath(
                            matching_files[i], expand_src_dir_path
                        )
                    excluded_list.extend(matching_files)
    except IOError as e:
        logger.warning(
            f'Error reading {konduktorignore_path}: '
            f'{common_utils.format_exception(e, use_bracket=True)}'
        )

    return excluded_list


def get_excluded_files_from_gitignore(src_dir_path: str) -> List[str]:
    """Lists files and patterns ignored by git in the source directory

    Runs `git status --ignored` which returns a list of excluded files and
    patterns read from .gitignore and .git/info/exclude using git.
    `git init` is run if SRC_DIR_PATH is not a git repository and removed
    after obtaining excluded list.

    Returns:
        List[str] containing files and patterns to be ignored.  Some of the
        patterns include, **/mydir/*.txt, !myfile.log, or file-*/.
    """
    expand_src_dir_path = os.path.expanduser(src_dir_path)

    git_exclude_path = os.path.join(expand_src_dir_path, '.git/info/exclude')
    gitignore_path = os.path.join(expand_src_dir_path, constants.GIT_IGNORE_FILE)

    git_exclude_exists = os.path.isfile(git_exclude_path)
    gitignore_exists = os.path.isfile(gitignore_path)

    # This command outputs a list to be excluded according to .gitignore
    # and .git/info/exclude
    filter_cmd = (
        f'git -C {shlex.quote(expand_src_dir_path)} ' 'status --ignored --porcelain=v1'
    )
    excluded_list: List[str] = []

    if git_exclude_exists or gitignore_exists:
        try:
            output = subprocess.run(
                filter_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            # when the SRC_DIR_PATH is not a git repo and .git
            # does not exist in it
            if e.returncode == exceptions.GIT_FATAL_EXIT_CODE:
                if 'not a git repository' in e.stderr:
                    # Check if the user has 'write' permission to
                    # SRC_DIR_PATH
                    if not os.access(expand_src_dir_path, os.W_OK):
                        error_msg = 'Write permission denial'
                        logger.warning(
                            _FILE_EXCLUSION_FROM_GITIGNORE_FAILURE_MSG.format(
                                path=src_dir_path, error_msg=error_msg
                            )
                        )
                        return excluded_list
                    init_cmd = f'git -C {expand_src_dir_path} init'
                    try:
                        subprocess.run(
                            init_cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=True,
                        )
                        output = subprocess.run(
                            filter_cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=True,
                            text=True,
                        )
                    except subprocess.CalledProcessError as init_e:
                        logger.warning(
                            _FILE_EXCLUSION_FROM_GITIGNORE_FAILURE_MSG.format(
                                path=src_dir_path, error_msg=init_e.stderr
                            )
                        )
                        return excluded_list
                    if git_exclude_exists:
                        # removes all the files/dirs created with 'git init'
                        # under .git/ except .git/info/exclude
                        remove_files_cmd = (
                            f'find {expand_src_dir_path}'
                            f'/.git -path {git_exclude_path}'
                            ' -prune -o -type f -exec rm -f '
                            '{} +'
                        )
                        remove_dirs_cmd = (
                            f'find {expand_src_dir_path}'
                            f'/.git -path {git_exclude_path}'
                            ' -o -type d -empty -delete'
                        )
                        subprocess.run(
                            remove_files_cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=True,
                        )
                        subprocess.run(
                            remove_dirs_cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=True,
                        )

        output_list = output.stdout.split('\n')
        for line in output_list:
            # FILTER_CMD outputs items preceded by '!!'
            # to specify excluded files/dirs
            # e.g., '!! mydir/' or '!! mydir/myfile.txt'
            if line.startswith('!!'):
                to_be_excluded = line[3:]
                if line.endswith('/'):
                    # aws s3 sync and gsutil rsync require * to exclude
                    # files/dirs under the specified directory.
                    to_be_excluded += '*'
                excluded_list.append(to_be_excluded)
    return excluded_list


def get_excluded_files(src_dir_path: str) -> List[str]:
    # TODO: this could return a huge list of files,
    # should think of ways to optimize.
    """List files and directories to be excluded."""
    expand_src_dir_path = os.path.expanduser(src_dir_path)
    konduktorignore_path = os.path.join(
        expand_src_dir_path, constants.KONDUKTOR_IGNORE_FILE
    )
    if os.path.exists(konduktorignore_path):
        logger.info(
            f'  {colorama.Style.DIM}'
            f'Excluded files to sync to cluster based on '
            f'{constants.KONDUKTOR_IGNORE_FILE}.'
            f'{colorama.Style.RESET_ALL}'
        )
        return get_excluded_files_from_konduktorignore(src_dir_path)
    logger.info(
        f'  {colorama.Style.DIM}'
        f'Excluded files to sync to cluster based on '
        f'{constants.GIT_IGNORE_FILE}.'
        f'{colorama.Style.RESET_ALL}'
    )
    return get_excluded_files_from_gitignore(src_dir_path)


class AbstractStore:
    """AbstractStore abstracts away the different storage types exposed by
    different clouds.

    Storage objects are backed by AbstractStores, each representing a store
    present in a cloud.
    """

    class StoreMetadata:
        """A pickle-able representation of Store

        Allows store objects to be written to and reconstructed from
        global_user_state.
        """

        def __init__(
            self,
            *,
            name: str,
            source: Optional['SourceType'],
            region: Optional[str] = None,
            is_sky_managed: Optional[bool] = None,
            _bucket_sub_path: Optional[str] = None,
        ):
            self.name = name
            self.source = source
            self.region = region
            self.is_sky_managed = is_sky_managed
            self._bucket_sub_path = _bucket_sub_path

        def __repr__(self):
            return (
                f'StoreMetadata('
                f'\n\tname={self.name},'
                f'\n\tsource={self.source},'
                f'\n\tregion={self.region},'
                f'\n\tis_sky_managed={self.is_sky_managed},'
                f'\n\t_bucket_sub_path={self._bucket_sub_path}'
            )

    def __init__(
        self,
        name: str,
        source: Optional['SourceType'],
        region: Optional[str] = None,
        is_sky_managed: Optional[bool] = None,
        sync_on_reconstruction: Optional[bool] = True,
        _bucket_sub_path: Optional[str] = None,
    ):
        """Initialize AbstractStore

        Args:
            name: Store name
            source: Data source for the store
            region: Region to place the bucket in
            is_sky_managed: Whether the store is managed by Sky. If None, it
              must be populated by the implementing class during initialization.

        Raises:
            StorageBucketCreateError: If bucket creation fails
            StorageBucketGetError: If fetching existing bucket fails
            StorageInitError: If general initialization fails
        """
        self.name = name
        self.source = source
        self.region = region
        self.is_sky_managed = is_sky_managed
        self.sync_on_reconstruction = sync_on_reconstruction
        self._bucket_sub_path = _bucket_sub_path
        # Whether sky is responsible for the lifecycle of the Store.
        self._validate()
        self.initialize()

    @property
    def bucket_sub_path(self) -> Optional[str]:
        """Get the bucket_sub_path."""
        return self._bucket_sub_path

    @classmethod
    def from_metadata(cls, metadata: StoreMetadata, **override_args):
        """Create a Store from a StoreMetadata object.

        Used when reconstructing Storage and Store objects from
        global_user_state.
        """
        return cls(
            name=override_args.get('name', metadata.name),
            source=override_args.get('source', metadata.source),
            region=override_args.get('region', metadata.region),
        )

    def get_metadata(self) -> StoreMetadata:
        return self.StoreMetadata(
            name=self.name,
            source=self.source,
            region=self.region,
        )

    def initialize(self):
        """Initializes the Store object on the cloud.

        Initialization involves fetching bucket if exists, or creating it if
        it does not.

        Raises:
          StorageBucketCreateError: If bucket creation fails
          StorageBucketGetError: If fetching existing bucket fails
          StorageInitError: If general initialization fails.
        """
        pass

    def _validate(self) -> None:
        """Runs validation checks on class args"""
        pass

    def upload(self) -> None:
        """Uploads source to the store bucket

        Upload must be called by the Storage handler - it is not called on
        Store initialization.
        """
        raise NotImplementedError

    def delete(self) -> None:
        """Removes the Storage object from the cloud."""
        raise NotImplementedError

    def get_handle(self) -> 'StorageHandle':
        """Returns the storage handle for use by the execution backend to attach
        to VM/containers
        """
        raise NotImplementedError

    def download_remote_dir(self, local_path: str) -> None:
        """Downloads directory from remote bucket to the specified
        local_path

        Args:
          local_path: Local path on user's device
        """
        raise NotImplementedError

    def _download_file(self, remote_path: str, local_path: str) -> None:
        """Downloads file from remote to local on Store

        Args:
          remote_path: str; Remote file path on Store
          local_path: str; Local file path on user's device
        """
        raise NotImplementedError

    def mount_command(self, mount_path: str) -> str:
        """Returns the command to mount the Store to the specified mount_path.

        Includes the setup commands to install mounting tools.

        Args:
          mount_path: str; Mount path on remote server
        """
        raise NotImplementedError

    def __deepcopy__(self, memo):
        # S3 Client and GCS Client cannot be deep copied, hence the
        # original Store object is returned
        return self

    def _validate_existing_bucket(self):
        """Validates the storage fields for existing buckets."""
        # Check if 'source' is None, this is only allowed when Storage is in
        # either MOUNT mode or COPY mode with sky-managed storage.
        # Note: In COPY mode, a 'source' being None with non-sky-managed
        # storage is already handled as an error in _validate_storage_spec.
        if self.source is None:
            # Retrieve a handle associated with the storage name.
            # This handle links to sky managed storage if it exists.
            raise NotImplementedError("We don't handle empty sources for now")

    @classmethod
    def check_credentials(cls):
        """
        Check if the credentials stored on client are valid for the store.
        This function always runs after check_credentials_from_secret. If
        the credentials work, we create/update the secret on the cluster.
        """
        raise NotImplementedError

    @classmethod
    def set_secret_credentials(cls):
        """
        Set the k8s secret storing the credentials for the store.
        """
        raise NotImplementedError

    # TODO(zhwu): Make the return type immutable.
    @classmethod
    def get_user_identities(cls) -> Optional[List[List[str]]]:
        """(Advanced) Returns all available user identities of this cloud.

        The user "identity" is associated with each SkyPilot cluster they
        create. This is used in protecting cluster operations, such as
        provision, teardown and status refreshing, in a multi-identity
        scenario, where the same user/device can switch between different
        cloud identities. We check that the user identity matches before:
            - Provisioning/starting a cluster
            - Stopping/tearing down a cluster
            - Refreshing the status of a cluster

        Design choices:
          1. We allow the operations that can correctly work with a different
             user identity, as a user should have full control over all their
             clusters (no matter which identity it belongs to), e.g.,
             submitting jobs, viewing logs, auto-stopping, etc.
          2. A cloud implementation can optionally switch between different
             identities if required for cluster operations. In this case,
             the cloud implementation should return multiple identities
             as a list. E.g., our Kubernetes implementation can use multiple
             kubeconfig contexts to switch between different identities.

        The choice of what constitutes an identity is up to each cloud's
        implementation. In general, to suffice for the above purposes,
        ensure that different identities should imply different sets of
        resources are used when the user invoked each cloud's default
        CLI/API.

        An identity is a list of strings. The list is in the order of
        strictness, i.e., the first element is the most strict identity, and
        the last element is the least strict identity.
        When performing an identity check between the current active identity
        and the owner identity associated with a cluster, we compare the two
        lists in order: if a position does not match, we go to the next. To
        see an example, see the docstring of the AWS.get_user_identities.

        Example identities (see cloud implementations):
            - AWS: [UserId, AccountId]
            - GCP: [email address + project ID]
            - Azure: [email address + subscription ID]
            - Kubernetes: [context name]

        Example return values:
            - AWS: [[UserId, AccountId]]
            - GCP: [[email address + project ID]]
            - Azure: [[email address + subscription ID]]
            - Kubernetes: [[current active context], [context 2], ...]

        Returns:
            None if the cloud does not have a concept of user identity
            (access protection will be disabled for these clusters);
            otherwise a list of available identities with the current active
            identity being the first element. Most clouds have only one identity
            available, so the returned list will only have one element: the
            current active identity.

        Raises:
            exceptions.CloudUserIdentityError: If the user identity cannot be
                retrieved.
        """
        return None

    @classmethod
    def get_active_user_identity(cls) -> Optional[List[str]]:
        """Returns currently active user identity of this cloud

        See get_user_identities for definition of user identity.

        Returns:
            None if the cloud does not have a concept of user identity;
            otherwise the current active identity.
        """
        identities = cls.get_user_identities()
        return identities[0] if identities is not None else None

    @classmethod
    def get_k8s_credential_name(cls) -> str:
        """Returns the name of the k8s secret storing the credentials for the store."""
        raise NotImplementedError


class CloudStorage:
    """Interface for a cloud object store."""

    # this needs to be overridden by the subclass
    _STORE: typing.Type[AbstractStore]

    def is_directory(self, url: str) -> bool:
        """Returns whether 'url' is a directory.

        In cloud object stores, a "directory" refers to a regular object whose
        name is a prefix of other objects.
        """
        raise NotImplementedError

    def make_sync_dir_command(self, source: str, destination: str) -> str:
        """Makes a runnable bash command to sync a 'directory'."""
        raise NotImplementedError

    def make_sync_file_command(self, source: str, destination: str) -> str:
        """Makes a runnable bash command to sync a file."""
        raise NotImplementedError

    def check_credentials(self):
        """Checks if the user has access credentials to this cloud."""
        return self._STORE.check_credentials()

    def check_credentials_from_secret(self):
        """Checks if the user has access credentials to this cloud."""
        return self._STORE.check_credentials_from_secret()

    def set_secret_credentials(self):
        """Set the credentials from the secret"""
        return self._STORE.set_secret_credentials()
