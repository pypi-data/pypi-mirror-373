KONDUKTOR_IGNORE_FILE = '.konduktorignore'
GIT_IGNORE_FILE = '.gitignore'
KONDUKTOR_REMOTE_WORKDIR = '~/konduktor_workdir'
KONDUKTOR_LOGS_DIRECTORY = '~/konduktor_logs'

# Used for translate local file mounts to cloud storage. Please refer to
# konduktor/utils/controller_utils.py::maybe_translate_local_file_mounts_and_sync_up for
# more details.
# TODO(asaiacai): Unlike skypilot, we don't delete buckets after a job completes
# because we want to persists code, logs, and artifacts for debugging.
# yes it's a resource leak, but object store is
# so cheap and code/data is small in comparison.
FILE_MOUNTS_BUCKET_NAME = 'konduktor-filemounts-{username}-{user_hash}'
FILE_MOUNTS_LOCAL_TMP_DIR = 'konduktor-filemounts-files-{id}'
FILE_MOUNTS_REMOTE_TMP_DIR = '/tmp/konduktor-{}-filemounts-files'

# For API server, the use a temporary directory in the same path as the upload
# directory to avoid using a different block device, which may not allow hard
# linking. E.g., in our API server deployment on k8s, ~/.konduktor/ is mounted from a
# persistent volume, so any contents in ~/.konduktor/ cannot be hard linked elsewhere.
FILE_MOUNTS_LOCAL_TMP_BASE_PATH = '~/.konduktor/tmp/'
# Base path for two-hop file mounts translation. See
# controller_utils.translate_local_file_mounts_to_two_hop().
FILE_MOUNTS_CONTROLLER_TMP_BASE_PATH = '~/.konduktor/tmp/controller'


# Used when an managed jobs are created and
# files are synced up to the cloud.
FILE_MOUNTS_WORKDIR_SUBPATH = '{task_name}-{run_id}/workdir'
FILE_MOUNTS_SUBPATH = '{task_name}-{run_id}/local-file-mounts/{i}'
FILE_MOUNTS_TMP_SUBPATH = '{task_name}-{run_id}/tmp-files'

# Path to the file that contains the python path.
GET_PYTHON_PATH_CMD = 'which python3'
# Python executable, e.g., /opt/conda/bin/python3
PYTHON_CMD = f'$({GET_PYTHON_PATH_CMD})'
