VERSION = 'v1'

KONDUKTOR = 'KONDUKTOR'
KONDUKTOR_SERVICE_ACCOUNT_ID = KONDUKTOR + '-' + VERSION
KONDUKTOR_SERVICE_ACCOUNT_EMAIL_TEMPLATE = (
    '{account_id}@{project_id}.iam.gserviceaccount.com'
)
KONDUKTOR_SERVICE_ACCOUNT_CONFIG = {
    'displayName': f'KONDUKTOR Service Account ({VERSION})',
}

# Those roles will be always added.
# NOTE: `serviceAccountUser` allows the head node to create workers with
# a serviceAccount. `roleViewer` allows the head node to run bootstrap_gcp.
DEFAULT_SERVICE_ACCOUNT_ROLES = [
    'roles/storage.admin',
    'roles/iam.serviceAccountUser',
    'roles/iam.roleViewer',
]

# A list of permissions required to run Konduktor on GCP.
# Keep this in sync with https://docs.skypilot.co/en/latest/cloud-setup/cloud-permissions/gcp.html # noqa: E501
STORAGE_MINIMAL_PERMISSIONS = [
    'iam.roles.get',
    # We now skip the check for `iam.serviceAccounts.actAs` permission for
    # simplicity as it can be granted at the service-account level.
    # Check: sky.provision.gcp.config::_is_permission_satisfied
    # 'iam.serviceAccounts.actAs',
    'iam.serviceAccounts.get',
    'serviceusage.services.enable',
    'serviceusage.services.list',
    'serviceusage.services.use',
    'storage.buckets.create',
    'storage.buckets.get',
    'storage.buckets.delete',
    'storage.objects.create',
    'storage.objects.delete',
    'storage.objects.update',
    'storage.objects.get',
    'storage.objects.list',
    'resourcemanager.projects.get',
]
