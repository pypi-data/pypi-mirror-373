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

"""Different cloud storage definitions. This modules responsibility
1.) Create the secrets for each cloud as k8s secrets
2.) Mount the secrets as volumes into each container
3.) Provide utilities/scripts for the pods to download files syncd
    to object storage

For each cloud/storage class we'll only have a single namespace at
`konduktor` and each run will correspond to a new folder e.g.
`s3://konduktor/my-llm-run-a34be-a3ebf`
"""

import enum
import os
import re
import urllib.parse
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union

from konduktor import check, config, logging
from konduktor.data import aws, constants, data_utils, gcp, registry, storage_utils
from konduktor.utils import annotations, common_utils, exceptions, schemas, ux_utils

logger = logging.get_logger(__file__)


@annotations.lru_cache(scope='global')
def get_cached_enabled_storage_clouds_or_refresh(
    raise_if_no_cloud_access: bool = False,
) -> List[str]:
    # This is a temporary solution until https://github.com/skypilot-org/skypilot/issues/1943 # noqa: E501
    # (asaiacai): This function does not do any actual checking right now.
    # this is temporary. In the future, we can cache to disk.
    # For now, we just print a warning to the user saying what
    # clouds are enabled and if the task fails to run `konduktor check`
    # to update the credentials.
    enabled_clouds = config.get_nested(('allowed_clouds',), [])
    if len(enabled_clouds) == 0:
        enabled_clouds = registry._STORE_ENABLED_CLOUDS
    else:
        enabled_clouds = [str(cloud) for cloud in enabled_clouds]
    logger.warning(
        f'Enabled storage clouds: {enabled_clouds}. Defaulting to '
        f'{enabled_clouds[0]}. If sync fails, '
        're-run `konduktor check` to verify credentials.'
    )
    return enabled_clouds


def _is_storage_cloud_enabled(
    cloud_name: str, try_fix_with_sky_check: bool = True
) -> bool:
    enabled_storage_clouds = get_cached_enabled_storage_clouds_or_refresh()
    if cloud_name in enabled_storage_clouds:
        return True
    if try_fix_with_sky_check:
        # TODO(zhwu): Only check the specified cloud to speed up.
        check.check(quiet=True)
        return _is_storage_cloud_enabled(cloud_name, try_fix_with_sky_check=False)
    return False


class StorageMode(enum.Enum):
    COPY = 'COPY'
    MOUNT = 'MOUNT'


class StoreType(enum.Enum):
    """Enum for the different types of stores."""

    GCS = 'GCS'
    S3 = 'S3'

    @classmethod
    def from_cloud(cls, cloud: str) -> 'StoreType':
        # these need to match the cloud store classes in konduktor/cloud_stores.py
        if cloud.lower() == 'gs':
            return StoreType.GCS
        elif cloud.lower() == 's3':
            return StoreType.S3
        else:
            with ux_utils.print_exception_no_traceback():
                raise ValueError(f'Unknown cloud: {cloud}')

    @classmethod
    def from_store(cls, store: 'storage_utils.AbstractStore') -> 'StoreType':
        if store.__repr__() == 'GcsStore':
            return StoreType.GCS
        elif store.__repr__() == 'S3Store':
            return StoreType.S3
        else:
            with ux_utils.print_exception_no_traceback():
                raise ValueError(f'Unknown store type: {store}')

    def store_prefix(self) -> str:
        if self == StoreType.GCS:
            return 'gs://'
        elif self == StoreType.S3:
            return 's3://'
        else:
            with ux_utils.print_exception_no_traceback():
                raise ValueError(f'Unknown store type: {self}')

    @classmethod
    def get_fields_from_store_url(
        cls, store_url: str
    ) -> Tuple['StoreType', str, str, Optional[str], Optional[str]]:
        """Returns the store type, bucket name, and sub path from
        a store URL, and the storage account name and region if applicable.

        Args:
            store_url: str; The store URL.
        """
        # The full path from the user config of IBM COS contains the region,
        # and Azure Blob Storage contains the storage account name, we need to
        # pass these information to the store constructor.
        storage_account_name = None
        region = None
        for store_type in StoreType:
            if store_url.startswith(store_type.store_prefix()):
                if store_type == StoreType.GCS:
                    bucket_name, sub_path = data_utils.split_gcs_path(store_url)
                elif store_type == StoreType.S3:
                    bucket_name, sub_path = data_utils.split_s3_path(store_url)
                return store_type, bucket_name, sub_path, storage_account_name, region
        raise ValueError(f'Unknown store URL: {store_url}')

    @classmethod
    def get_endpoint_url(cls, store: 'storage_utils.AbstractStore', path: str) -> str:
        """Generates the endpoint URL for a given store and path.

        Args:
            store: Store object implementing AbstractStore.
            path: Path within the store.

        Returns:
            Endpoint URL of the bucket as a string.
        """
        store_type = cls.from_store(store)
        bucket_endpoint_url = f'{store_type.store_prefix()}{path}'
        return bucket_endpoint_url


# this should match the above StoreType enum
STORE_TYPES = Literal[StoreType.GCS, StoreType.S3]


class Storage(object):
    """Storage objects handle persistent and large volume storage in the sky.

    Storage represents an abstract data store containing large data files
    required by the task. Compared to file_mounts, storage is faster and
    can persist across runs, requiring fewer uploads from your local machine.

    A storage object can be used in either MOUNT mode or COPY mode. In MOUNT
    mode (the default), the backing store is directly "mounted" to the remote
    VM, and files are fetched when accessed by the task and files written to the
    mount path are also written to the remote store. In COPY mode, the files are
    pre-fetched and cached on the local disk and writes are not replicated on
    the remote store.

    Behind the scenes, storage automatically uploads all data in the source
    to a backing object store in a particular cloud (S3/GCS/Azure Blob).

      Typical Usage: (See examples/playground/storage_playground.py)
        storage = Storage(name='imagenet-bucket', source='~/Documents/imagenet')

        # Move data to S3
        storage.add_store('S3')

        # Move data to Google Cloud Storage
        storage.add_store('GCS')

        # Delete Storage for both S3 and GCS
        storage.delete()
    """

    class StorageMetadata(object):
        """A pickle-able tuple of:

        - (required) Storage name.
        - (required) Source
        - (optional) Storage mode.
        - (optional) Set of stores managed by sky added to the Storage object
        """

        def __init__(
            self,
            *,
            storage_name: Optional[str],
            source: Optional[constants.SourceType],
            mode: Optional[StorageMode] = None,
            sky_stores: Optional[
                Dict[StoreType, 'storage_utils.AbstractStore.StoreMetadata']
            ] = None,
        ):
            assert storage_name is not None or source is not None
            self.storage_name = storage_name
            self.source = source
            self.mode = mode

            # Only stores managed by sky are stored here in the
            # global_user_state
            self.sky_stores = {} if sky_stores is None else sky_stores

        def __repr__(self):
            return (
                f'StorageMetadata('
                f'\n\tstorage_name={self.storage_name},'
                f'\n\tsource={self.source},'
                f'\n\tmode={self.mode},'
                f'\n\t{self.sky_stores}'
            )

        def add_store(self, store: 'storage_utils.AbstractStore') -> None:
            storetype = StoreType.from_store(store)
            self.sky_stores[storetype] = store.get_metadata()

        def remove_store(self, store: 'storage_utils.AbstractStore') -> None:
            storetype = StoreType.from_store(store)
            if storetype in self.sky_stores:
                del self.sky_stores[storetype]

    def __init__(
        self,
        name: Optional[str] = None,
        source: Optional[constants.SourceType] = None,
        stores: Optional[List[STORE_TYPES]] = None,
        persistent: Optional[bool] = True,
        mode: StorageMode = StorageMode.COPY,
        sync_on_reconstruction: Optional[bool] = True,
        _is_sky_managed: Optional[bool] = False,
        _bucket_sub_path: Optional[str] = None,
    ) -> None:
        """Initializes a Storage object.

        Three fields are required: the name of the storage, the source
        path where the data is initially located, and the default mount
        path where the data will be mounted to on the cloud.

        Storage object validation depends on the name, source and mount mode.
        There are four combinations possible for name and source inputs:

        - name is None, source is None: Underspecified storage object.
        - name is not None, source is None: If MOUNT mode, provision an empty
            bucket with name <name>. If COPY mode, raise error since source is
            required.
        - name is None, source is not None: If source is local, raise error
            since name is required to create destination bucket. If source is
            a bucket URL, use the source bucket as the backing store (if
            permissions allow, else raise error).
        - name is not None, source is not None: If source is local, upload the
            contents of the source path to <name> bucket. Create new bucket if
            required. If source is bucket url - raise error. Name should not be
            specified if the source is a URL; name will be inferred from source.

        Args:
          name: str; Name of the storage object. Typically used as the
            bucket name in backing object stores.
          source: str, List[str]; File path where the data is initially stored.
            Can be a single local path, a list of local paths, or a cloud URI
            (s3://, gs://, etc.). Local paths do not need to be absolute.
          stores: Optional; Specify pre-initialized stores (S3Store, GcsStore).
          persistent: bool; Whether to persist across konduktor launches.
          mode: StorageMode; Specify how the storage object is manifested on
            the remote VM. Can be either MOUNT or COPY. Defaults to MOUNT.
          sync_on_reconstruction: bool; [defunct] Whether to sync the
            data if the storage object is found in the global_user_state
            and reconstructed from there. This is set to
            false when the Storage object is created not for direct use
          _is_sky_managed: Optional[bool]; [defunct] Indicates if the storage is managed
            by Sky. Without this argument, the controller's behavior differs
            from the local machine. For example, if a bucket does not exist:
            Local Machine (is_sky_managed=True) →
            Controller (is_sky_managed=False).
            With this argument, the controller aligns with the local machine,
            ensuring it retains the is_sky_managed information from the YAML.
            During teardown, if is_sky_managed is True, the controller should
            delete the bucket. Otherwise, it might mistakenly delete only the
            sub-path, assuming is_sky_managed is False.
          _bucket_sub_path: Optional[str]; The subdirectory to use for the
            storage object.
        """
        self.name: str
        self.source = source
        self.persistent = persistent
        self.mode = mode
        assert mode in StorageMode
        self.stores: Dict[StoreType, Optional['storage_utils.AbstractStore']] = {}
        if stores is not None:
            for store in stores:
                self.stores[store] = None
        self.sync_on_reconstruction = sync_on_reconstruction
        self._is_sky_managed = _is_sky_managed
        self._bucket_sub_path = _bucket_sub_path

        # TODO(romilb, zhwu): This is a workaround to support storage deletion
        # for spot. Once sky storage supports forced management for external
        # buckets, this can be deprecated.
        self.force_delete = False

        # Validate and correct inputs if necessary
        self._validate_storage_spec(name)

        if self.source is not None:
            # If source is a pre-existing bucket, connect to the bucket
            # If the bucket does not exist, this will error out
            if isinstance(self.source, str):
                if self.source.startswith('gs://'):
                    self.add_store(StoreType.GCS)
                elif self.source.startswith('s3://'):
                    self.add_store(StoreType.S3)

    @staticmethod
    def _validate_source(
        source: constants.SourceType,
        mode: StorageMode,
        sync_on_reconstruction: Optional[bool] = None,
    ) -> Tuple[constants.SourceType, bool]:
        """Validates the source path.

        Args:
          source: str; File path where the data is initially stored. Can be a
            local path or a cloud URI (s3://, gs://, r2:// etc.).
            Local paths do not need to be absolute.
          mode: StorageMode; StorageMode of the storage object

        Returns:
          Tuple[source, is_local_source]
          source: str; The source path.
          is_local_path: bool; Whether the source is a local path. False if URI.
        """

        def _check_basename_conflicts(source_list: List[str]) -> None:
            """Checks if two paths in source_list have the same basename."""
            basenames = [os.path.basename(s) for s in source_list]
            conflicts = {x for x in basenames if basenames.count(x) > 1}
            if conflicts:
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageSourceError(
                        'Cannot have multiple files or directories with the '
                        'same name in source. Conflicts found for: '
                        f'{", ".join(conflicts)}'
                    )

        def _validate_local_source(local_source):
            if local_source.endswith('/'):
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageSourceError(
                        'Storage source paths cannot end with a slash '
                        '(try "/mydir: /mydir" or "/myfile: /myfile"). '
                        f'Found source={local_source}'
                    )
            # Local path, check if it exists
            full_src = os.path.abspath(os.path.expanduser(local_source))
            # Only check if local source exists if it is synced to the bucket
            if not os.path.exists(full_src) and sync_on_reconstruction:
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageSourceError(
                        'Local source path does not' f' exist: {local_source}'
                    )
            # Raise warning if user's path is a symlink
            elif os.path.islink(full_src):
                logger.warning(
                    f'Source path {source} is a symlink. '
                    'Referenced contents are uploaded, matching '
                    'the default behavior for S3 and GCS syncing.'
                )

        # Check if source is a list of paths
        if isinstance(source, list):
            # Check for conflicts in basenames
            _check_basename_conflicts(source)
            # Validate each path
            for local_source in source:
                _validate_local_source(local_source)
            is_local_source = True
        else:
            # Check if str source is a valid local/remote URL
            split_path = urllib.parse.urlsplit(source)
            if split_path.scheme == '':
                _validate_local_source(source)
                # Check if source is a file - throw error if it is
                full_src = os.path.abspath(os.path.expanduser(source))
                if os.path.isfile(full_src):
                    with ux_utils.print_exception_no_traceback():
                        raise exceptions.StorageSourceError(
                            'Storage source path cannot be a file - only'
                            ' directories are supported as a source. '
                            'To upload a single file, specify it in a list '
                            f'by writing source: [{source}]. Note '
                            'that the file will be uploaded to the root of the '
                            'bucket and will appear at <destination_path>/'
                            f'{os.path.basename(source)}. Alternatively, you '
                            'can directly upload the file to the VM without '
                            'using a bucket by writing <destination_path>: '
                            f'{source} in the file_mounts section of your YAML'
                        )
                is_local_source = True
            elif split_path.scheme in ['s3', 'gs', 'https', 'r2', 'cos']:
                is_local_source = False
                # Storage mounting does not support mounting specific files from
                # cloud store - ensure path points to only a directory
                if mode == StorageMode.MOUNT:
                    if split_path.scheme != 'https' and (
                        (
                            split_path.scheme != 'cos'
                            and split_path.path.strip('/') != ''
                        )
                        or (
                            split_path.scheme == 'cos'
                            and not re.match(r'^/[-\w]+(/\s*)?$', split_path.path)
                        )
                    ):
                        # regex allows split_path.path to include /bucket
                        # or /bucket/optional_whitespaces while considering
                        # cos URI's regions (cos://region/bucket_name)
                        with ux_utils.print_exception_no_traceback():
                            raise exceptions.StorageModeError(
                                'MOUNT mode does not support'
                                ' mounting specific files from cloud'
                                ' storage. Please use COPY mode or'
                                ' specify only the bucket name as'
                                ' the source.'
                            )
            else:
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageSourceError(
                        f'Supported paths: local, s3://, gs://, https://, '
                        f'r2://, cos://. Got: {source}'
                    )
        return source, is_local_source

    def _validate_storage_spec(self, name: Optional[str]) -> None:
        """Validates the storage spec and updates local fields if necessary."""

        def validate_name(name):
            """Checks for validating the storage name.

            Checks if the name starts the s3, gcs or r2 prefix and raise error
            if it does. Store specific validation checks (e.g., S3 specific
            rules) happen in the corresponding store class.
            """
            prefix = name.split('://')[0]
            prefix = prefix.lower()
            if prefix in ['s3', 'gs', 'https', 'r2', 'cos']:
                with ux_utils.print_exception_no_traceback():
                    raise exceptions.StorageNameError(
                        'Prefix detected: `name` cannot start with '
                        f'{prefix}://. If you are trying to use an existing '
                        'bucket created outside of SkyPilot, please specify it '
                        'using the `source` field (e.g. '
                        '`source: s3://mybucket/`). If you are trying to '
                        'create a new bucket, please use the `store` field to '
                        'specify the store type (e.g. `store: s3`).'
                    )

        if self.source is None:
            # If the mode is COPY, the source must be specified
            if self.mode == StorageMode.COPY:
                # Check if a Storage object already exists in global_user_state
                # (e.g. used as scratch previously). Such storage objects can be
                # mounted in copy mode even though they have no source in the
                # yaml spec (the name is the source).
                # TODO(asaiacai): remove references to global_user_state
                # handle = global_user_state.get_handle_from_storage_name(name)
                handle = None
                if handle is None:
                    with ux_utils.print_exception_no_traceback():
                        raise exceptions.StorageSourceError(
                            'New storage object: source must be specified when '
                            'using COPY mode.'
                        )
            else:
                # If source is not specified in COPY mode, the intent is to
                # create a bucket and use it as scratch disk. Name must be
                # specified to create bucket.
                if not name:
                    with ux_utils.print_exception_no_traceback():
                        raise exceptions.StorageSpecError(
                            'Storage source or storage name must be specified.'
                        )
            assert name is not None, handle
            validate_name(name)
            self.name = name
            return
        elif self.source is not None:
            source, is_local_source = Storage._validate_source(
                self.source, self.mode, self.sync_on_reconstruction
            )
            if not name:
                if is_local_source:
                    with ux_utils.print_exception_no_traceback():
                        raise exceptions.StorageNameError(
                            'Storage name must be specified if the source is ' 'local.'
                        )
                else:
                    assert isinstance(source, str)
                    # Set name to source bucket name and continue
                    name = urllib.parse.urlsplit(source).netloc
                    assert name is not None, source
                    self.name = name
                    return
            else:
                if is_local_source:
                    # If name is specified and source is local, upload to bucket
                    assert name is not None, source
                    validate_name(name)
                    self.name = name
                    return
                else:
                    # Both name and source should not be specified if the source
                    # is a URI. Name will be inferred from the URI.
                    with ux_utils.print_exception_no_traceback():
                        raise exceptions.StorageSpecError(
                            'Storage name should not be specified if the '
                            'source is a remote URI.'
                        )
        raise exceptions.StorageSpecError(
            f'Validation failed for storage source {self.source}, name '
            f'{self.name} and mode {self.mode}. Please check the arguments.'
        )

    def _add_store_from_metadata(
        self, sky_stores: Dict[StoreType, 'storage_utils.AbstractStore.StoreMetadata']
    ) -> None:
        """Reconstructs Storage.stores from sky_stores.

        Reconstruct AbstractStore objects from sky_store's metadata and
        adds them into Storage.stores
        """
        for s_type, s_metadata in sky_stores.items():
            # When initializing from global_user_state, we override the
            # source from the YAML
            try:
                if s_type == StoreType.S3:
                    store = aws.S3Store.from_metadata(
                        s_metadata,
                        source=self.source,
                        sync_on_reconstruction=self.sync_on_reconstruction,
                    )
                elif s_type == StoreType.GCS:
                    store = gcp.GcsStore.from_metadata(
                        s_metadata,
                        source=self.source,
                        sync_on_reconstruction=self.sync_on_reconstruction,
                    )
                # elif s_type == StoreType.AZURE:
                #     assert isinstance(s_metadata,
                #                       AzureBlobStore.AzureBlobStoreMetadata)
                #     store = AzureBlobStore.from_metadata(
                #         s_metadata,
                #         source=self.source,
                #         sync_on_reconstruction=self.sync_on_reconstruction)
                # elif s_type == StoreType.R2:
                #     store = R2Store.from_metadata(
                #         s_metadata,
                #         source=self.source,
                #         sync_on_reconstruction=self.sync_on_reconstruction)
                # elif s_type == StoreType.IBM:
                #     store = IBMCosStore.from_metadata(
                #         s_metadata,
                #         source=self.source,
                #         sync_on_reconstruction=self.sync_on_reconstruction)
                else:
                    with ux_utils.print_exception_no_traceback():
                        raise ValueError(f'Unknown store type: {s_type}')
            # Following error is caught when an externally removed storage
            # is attempted to be fetched.
            except exceptions.StorageExternalDeletionError:
                logger.debug(
                    f'Storage object {self.name!r} was attempted '
                    'to be reconstructed while the corresponding '
                    'bucket was externally deleted.'
                )
                continue

            self._add_store(store, is_reconstructed=True)

    @classmethod
    def from_metadata(cls, metadata: StorageMetadata, **override_args) -> 'Storage':
        """Create Storage from StorageMetadata object.

        Used when reconstructing Storage object and AbstractStore objects from
        global_user_state.
        """
        # Name should not be specified if the source is a cloud store URL.
        source = override_args.get('source', metadata.source)
        name = override_args.get('name', metadata.storage_name)
        # If the source is a list, it consists of local paths
        if not isinstance(source, list) and data_utils.is_cloud_store_url(source):
            name = None

        storage_obj = cls(
            name=name,
            source=source,
            sync_on_reconstruction=override_args.get('sync_on_reconstruction', True),
        )

        # For backward compatibility
        if hasattr(metadata, 'mode'):
            if metadata.mode:
                storage_obj.mode = override_args.get('mode', metadata.mode)

        return storage_obj

    def add_store(
        self, store_type: Union[str, StoreType], region: Optional[str] = None
    ) -> 'storage_utils.AbstractStore':
        """Initializes and adds a new store to the storage.

        Invoked by the optimizer after it has selected a store to
        add it to Storage.

        Args:
          store_type: StoreType; Type of the storage [S3, GCS, AZURE, R2, IBM]
          region: str; Region to place the bucket in. Caller must ensure that
            the region is valid for the chosen store_type.
        """
        if isinstance(store_type, str):
            store_type = StoreType(store_type)

        store_cls: Type['storage_utils.AbstractStore']
        if store_type == StoreType.GCS:
            store_cls = gcp.GcsStore
        elif store_type == StoreType.S3:
            store_cls = aws.S3Store
        else:
            with ux_utils.print_exception_no_traceback():
                raise exceptions.StorageSpecError(
                    f'{store_type} not supported as a Store.'
                )

        # Initialize store object and get/create bucket
        try:
            assert self.source is not None
            store = store_cls(
                name=self.name,
                source=self.source,
                region=region,
                sync_on_reconstruction=self.sync_on_reconstruction,
                is_sky_managed=self._is_sky_managed,
                _bucket_sub_path=self._bucket_sub_path,
            )
        except exceptions.StorageBucketCreateError:
            # Creation failed, so this must be sky managed store. Add failure
            # to state.
            logger.error(
                f'Could not create {store_type} store ' f'with name {self.name}.'
            )
            raise
        except exceptions.StorageBucketGetError:
            # Bucket get failed, so this is not sky managed. Do not update state
            logger.error(f'Could not get {store_type} store ' f'with name {self.name}.')
            raise
        except exceptions.StorageInitError:
            logger.error(
                f'Could not initialize {store_type} store with '
                f'name {self.name}. General initialization error.'
            )
            raise
        except exceptions.StorageSpecError:
            logger.error(
                f'Could not mount externally created {store_type}'
                f'store with name {self.name!r}.'
            )
            raise

        # Add store to storage
        self._add_store(store)

        # Upload source to store
        self._sync_store(store)

        return store

    def _add_store(
        self, store: 'storage_utils.AbstractStore', is_reconstructed: bool = False
    ):
        # Adds a store object to the storage
        store_type = StoreType.from_store(store)
        self.stores[store_type] = store

    def delete(self, store_type: Optional[StoreType] = None) -> None:
        """Deletes data for all sky-managed storage objects.

        If a storage is not managed by sky, it is not deleted from the cloud.
        User must manually delete any object stores created outside of sky.

        Args:
            store_type: StoreType; Specific cloud store to remove from the list
              of backing stores.
        """
        if not self.stores:
            logger.info('No backing stores found. Deleting storage.')
        if store_type:
            store = self.stores[store_type]
            assert store is not None
            # We delete a store from the cloud if it's sky managed. Else just
            # remove handle and return
            if self.force_delete:
                store.delete()
            # Remove store from bookkeeping
            del self.stores[store_type]
        else:
            for _, store in self.stores.items():
                assert store is not None
                if self.force_delete:
                    store.delete()
            self.stores = {}

    def sync_all_stores(self):
        """Syncs the source and destinations of all stores in the Storage"""
        for _, store in self.stores.items():
            self._sync_store(store)

    def _sync_store(self, store: 'storage_utils.AbstractStore'):
        """Runs the upload routine for the store and handles failures"""

        def warn_for_git_dir(source: str):
            if os.path.isdir(os.path.join(source, '.git')):
                logger.warning(
                    f"'.git' directory under '{self.source}' "
                    'is excluded during sync.'
                )

        try:
            if self.source is not None:
                if isinstance(self.source, str):
                    warn_for_git_dir(self.source)
                else:
                    for source in self.source:
                        warn_for_git_dir(source)
            store.upload()
        except exceptions.StorageUploadError:
            logger.error(
                f'Could not upload {self.source!r} to store ' f'name {store.name!r}.'
            )
            raise

    @classmethod
    def from_yaml_config(cls, config: Dict[str, Any]) -> 'Storage':
        common_utils.validate_schema(
            config, schemas.get_storage_schema(), 'Invalid storage YAML: '
        )

        name = config.pop('name', None)
        source = config.pop('source', None)
        store = config.pop('store', None)
        mode_str = config.pop('mode', None)
        force_delete = config.pop('_force_delete', None)
        if force_delete is None:
            force_delete = False

        if isinstance(mode_str, str):
            # Make mode case insensitive, if specified
            mode = StorageMode(mode_str.upper())
        else:
            # Make sure this keeps the same as the default mode in __init__
            mode = StorageMode.MOUNT
        persistent = config.pop('persistent', None)
        if persistent is None:
            persistent = True

        assert not config, f'Invalid storage args: {config.keys()}'

        # Validation of the config object happens on instantiation.
        storage_obj = cls(name=name, source=source, persistent=persistent, mode=mode)
        if store is not None:
            storage_obj.add_store(StoreType(store.upper()))

        # Add force deletion flag
        storage_obj.force_delete = force_delete
        return storage_obj

    def to_yaml_config(self) -> Dict[str, str]:
        config = {}

        def add_if_not_none(key: str, value: Optional[Any]):
            if value is not None:
                config[key] = value

        name = None
        if (
            self.source is None
            or not isinstance(self.source, str)
            or not data_utils.is_cloud_store_url(self.source)
        ):
            # Remove name if source is a cloud store URL
            name = self.name
        add_if_not_none('name', name)
        add_if_not_none('source', self.source)

        stores = None
        if len(self.stores) > 0:
            stores = ','.join([store.value for store in self.stores])
        add_if_not_none('store', stores)
        add_if_not_none('persistent', self.persistent)
        add_if_not_none('mode', self.mode.value)
        if self.force_delete:
            config['_force_delete'] = True
        return config
