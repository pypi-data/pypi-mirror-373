from konduktor.data.aws import S3CloudStorage
from konduktor.data.gcp import GcsCloudStorage

# Maps bucket's URIs prefix(scheme) to its corresponding storage class

_REGISTRY = {
    'gs': GcsCloudStorage(),
    's3': S3CloudStorage(),
    # TODO(asaiacai): Add other cloud stores here
    # 'r2': R2CloudStorage(),
    # 'cos': IBMCosCloudStorage(),
    # 'oci': OciCloudStorage(),
    # # TODO: This is a hack, as Azure URL starts with https://, we should
    # # refactor the registry to be able to take regex, so that Azure blob can
    # # be identified with `https://(.*?)\.blob\.core\.windows\.net`
    # 'https': AzureBlobCloudStorage()
}

_STORE_ENABLED_CLOUDS = list(_REGISTRY.keys())
