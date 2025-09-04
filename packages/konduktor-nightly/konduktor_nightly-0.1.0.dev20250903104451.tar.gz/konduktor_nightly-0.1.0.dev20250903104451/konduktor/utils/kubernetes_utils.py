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

"""Kubernetes utilities."""

import functools
import math
import os
import re
import typing
from typing import Any, Dict, List, Optional, Tuple, Union

import filelock
import kubernetes
import yaml  # type: ignore

from konduktor import config, kube_client, logging
from konduktor.backends import constants as backend_constants
from konduktor.utils import common_utils, kubernetes_enums

if typing.TYPE_CHECKING:
    pass

DEFAULT_NAMESPACE = 'default'

DEFAULT_SERVICE_ACCOUNT_NAME = 'konduktor-service-account'

DNS_SUBDOMAIN_REGEX = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'

MEMORY_SIZE_UNITS = {
    'B': 1,
    'K': 2**10,
    'M': 2**20,
    'G': 2**30,
    'T': 2**40,
    'P': 2**50,
}

# The resource keys used by Kubernetes to track NVIDIA GPUs and Google on
# nodes. These keys are typically used in the node's status.allocatable
# or status.capacity fields to indicate the available resources on the node.
GPU_RESOURCE_KEY = 'nvidia.com/gpu'

NO_ACCELERATOR_HELP_MESSAGE = (
    'If your cluster contains GPUs, make sure '
    f'{GPU_RESOURCE_KEY} resource is available '
    'on the nodes and the node labels for identifying GPUs '
    '(e.g. `nvidia.com/gpu` are setup correctly. '
)

_K8S_CLIENT_LOCK_PATH = os.path.expanduser('~/.konduktor/k8s_client.lock')
_K8s_CLIENT_LOCK = filelock.FileLock(_K8S_CLIENT_LOCK_PATH)

logger = logging.get_logger(__name__)


class GPULabelFormatter:
    """Base class to define a GPU label formatter for a Kubernetes cluster

    A GPU label formatter is a class that defines how to use GPU type labels in
    a Kubernetes cluster. It is used by the Kubernetes cloud class to pick the
    key:value pair to use as node selector for GPU nodes.
    """

    @classmethod
    def get_label_key(cls, accelerator: Optional[str] = None) -> str:
        """Returns the label key for GPU type used by the Kubernetes cluster"""
        raise NotImplementedError

    @classmethod
    def get_label_keys(cls) -> List[str]:
        """Returns a list of label keys for GPU used by Kubernetes cluster."""
        raise NotImplementedError

    @classmethod
    def get_label_value(cls, accelerator: str) -> str:
        """Given a GPU type, returns the label value to be used"""
        raise NotImplementedError

    @classmethod
    def match_label_key(cls, label_key: str) -> bool:
        """Checks if the given label key matches the formatter's label keys"""
        raise NotImplementedError

    @classmethod
    def get_accelerator_from_label_value(cls, value: str) -> str:
        """Given a label value, returns the GPU type"""
        raise NotImplementedError

    @classmethod
    def validate_label_value(cls, value: str) -> Tuple[bool, str]:
        """Validates if the specified label value is correct.

        Used to check if the labelling on the cluster is correct and
        preemptively raise an error if it is not.

        Returns:
            bool: True if the label value is valid, False otherwise.
            str: Error message if the label value is invalid, None otherwise.
        """
        del value
        return True, ''


def get_gke_accelerator_name(accelerator: str) -> str:
    """Returns the accelerator name for GKE clusters.

    Uses the format - nvidia-tesla-<accelerator>.
    A100-80GB, H100-80GB, L4 are an exception. They use nvidia-<accelerator>.
    types are an exception as well keeping the given name.
    """
    if accelerator == 'H100':
        # H100 is named as H100-80GB in GKE.
        accelerator = 'H100-80GB'
    if accelerator in ('A100-80GB', 'L4', 'H100-80GB', 'H100-MEGA-80GB'):
        # A100-80GB, L4, H100-80GB and H100-MEGA-80GB
        # have a different name pattern.
        return 'nvidia-{}'.format(accelerator.lower())
    else:
        return 'nvidia-tesla-{}'.format(accelerator.lower())


class GKELabelFormatter(GPULabelFormatter):
    """GKE label formatter

    GKE nodes by default are populated with `cloud.google.com/gke-accelerator`
    label, which is used to identify the GPU type.
    """

    GPU_LABEL_KEY = 'cloud.google.com/gke-accelerator'
    ACCELERATOR_COUNT_LABEL_KEY = 'cloud.google.com/gke-accelerator-count'

    @classmethod
    def get_label_key(cls, accelerator: Optional[str] = None) -> str:
        return cls.GPU_LABEL_KEY

    @classmethod
    def get_label_keys(cls) -> List[str]:
        return [cls.GPU_LABEL_KEY]

    @classmethod
    def match_label_key(cls, label_key: str) -> bool:
        return label_key in cls.get_label_keys()

    @classmethod
    def get_label_value(cls, accelerator: str) -> str:
        return get_gke_accelerator_name(accelerator)

    @classmethod
    def get_accelerator_from_label_value(cls, value: str) -> str:
        if value.startswith('nvidia-tesla-'):
            return value.replace('nvidia-tesla-', '').upper()
        elif value.startswith('nvidia-'):
            acc = value.replace('nvidia-', '').upper()
            if acc == 'H100-80GB':
                # H100 can be either H100-80GB or H100-MEGA-80GB in GKE
                # we map H100 ---> H100-80GB and keep H100-MEGA-80GB
                # to distinguish between a3-high and a3-mega instances
                return 'H100'
            return acc
        else:
            raise ValueError(f'Invalid accelerator name in GKE cluster: {value}')


class GFDLabelFormatter(GPULabelFormatter):
    """GPU Feature Discovery label formatter

    NVIDIA GPUs nodes are labeled by GPU feature discovery
    e.g. nvidia.com/gpu.product=NVIDIA-H100-80GB-HBM3
    https://github.com/NVIDIA/gpu-feature-discovery

    GPU feature discovery is included as part of the
    NVIDIA GPU Operator:
    https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/overview.html

    This LabelFormatter can't be used in autoscaling clusters since accelerators
    may map to multiple label, so we're not implementing `get_label_value`
    """

    LABEL_KEY = 'nvidia.com/gpu.product'

    @classmethod
    def get_label_key(cls, accelerator: Optional[str] = None) -> str:
        return cls.LABEL_KEY

    @classmethod
    def get_label_keys(cls) -> List[str]:
        return [cls.LABEL_KEY]

    @classmethod
    def get_label_value(cls, accelerator: str) -> str:
        """An accelerator can map to many Nvidia GFD labels
        (e.g., A100-80GB-PCIE vs. A100-SXM4-80GB).
        As a result, we do not support get_label_value for GFDLabelFormatter."""
        raise NotImplementedError

    @classmethod
    def match_label_key(cls, label_key: str) -> bool:
        return label_key == cls.LABEL_KEY

    @classmethod
    def get_accelerator_from_label_value(cls, value: str) -> str:
        """Searches against a canonical list of NVIDIA GPUs and pattern
        matches the canonical GPU name against the GFD label.
        """
        canonical_gpu_names = [
            'A100-80GB',
            'A100',
            'A10G',
            'H100',
            'K80',
            'M60',
            'T4g',
            'T4',
            'V100',
            'A10',
            'P4000',
            'P100',
            'P40',
            'P4',
            'L40',
            'L4',
        ]
        for canonical_name in canonical_gpu_names:
            # A100-80G accelerator is A100-SXM-80GB or A100-PCIE-80GB
            if canonical_name == 'A100-80GB' and re.search(r'A100.*-80GB', value):
                return canonical_name
            # Use word boundary matching to prevent substring matches
            elif re.search(rf'\b{re.escape(canonical_name)}\b', value):
                return canonical_name

        # If we didn't find a canonical name:
        # 1. remove 'NVIDIA-' (e.g., 'NVIDIA-RTX-A6000' -> 'RTX-A6000')
        # 2. remove 'GEFORCE-' (e.g., 'NVIDIA-GEFORCE-RTX-3070' -> 'RTX-3070')
        # 3. remove 'RTX-' (e.g. 'RTX-6000' -> 'RTX6000')
        return (
            value.upper()
            .replace('NVIDIA-', '')
            .replace('GEFORCE-', '')
            .replace('RTX-', 'RTX')
        )


# LABEL_FORMATTER_REGISTRY stores the label formats that will try to
# discover the accelerator type from. The order of the list is important, as
# it will be used to determine the priority of the label formats when
# auto-detecting the GPU label type.
LABEL_FORMATTER_REGISTRY = [GKELabelFormatter, GFDLabelFormatter]

# Mapping of autoscaler type to label formatter
AUTOSCALER_TO_LABEL_FORMATTER = {
    kubernetes_enums.KubernetesAutoscalerType.GKE: GKELabelFormatter,
}


@functools.lru_cache()
def get_current_kube_config_context_name() -> Optional[str]:
    """Get the current kubernetes context from the kubeconfig file

    Returns:
        str | None: The current kubernetes context if it exists, None otherwise
    """
    k8s = kubernetes
    try:
        _, current_context = k8s.config.list_kube_config_contexts()
        return current_context['name']
    except k8s.config.config_exception.ConfigException:
        return None


@functools.lru_cache(maxsize=10)
def get_kubernetes_nodes(context: Optional[str] = None) -> List[Any]:
    """Gets the kubernetes nodes in the context.

    If context is None, gets the nodes in the current context.
    """
    if context is None:
        context = get_current_kube_config_context_name()

    nodes = (
        kube_client.core_api(context)
        .list_node(_request_timeout=kubernetes.API_TIMEOUT)
        .items
    )
    return nodes


@functools.lru_cache()
def detect_gpu_label_formatter(
    context: Optional[str],
) -> Tuple[Optional[GPULabelFormatter], Dict[str, List[Tuple[str, str]]]]:
    """Detects the GPU label formatter for the Kubernetes cluster

    Returns:
        GPULabelFormatter: The GPU label formatter for the cluster, if found.
        Dict[str, List[Tuple[str, str]]]: A mapping of nodes and the list of
             labels on each node. E.g., {'node1': [('label1', 'value1')]}
    """
    # Get all labels across all nodes
    node_labels: Dict[str, List[Tuple[str, str]]] = {}
    nodes = get_kubernetes_nodes(context)
    for node in nodes:
        node_labels[node.metadata.name] = []
        for label, value in node.metadata.labels.items():
            node_labels[node.metadata.name].append((label, value))

    label_formatter = None

    # Check if the node labels contain any of the GPU label prefixes
    for lf in LABEL_FORMATTER_REGISTRY:
        for _, label_list in node_labels.items():
            for label, _ in label_list:
                if lf.match_label_key(label):
                    label_formatter = lf()
                    return label_formatter, node_labels

    return label_formatter, node_labels


@functools.lru_cache()
def get_kube_config_context_namespace(context_name: Optional[str] = None) -> str:
    """Get the current kubernetes context namespace from the kubeconfig file

    Returns:
        str | None: The current kubernetes context namespace if it exists, else
            the default namespace.
    """
    k8s = kubernetes
    ns_path = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
    # If using in-cluster context, get the namespace from the service account
    # namespace file. Uses the same logic as adaptors.kubernetes._load_config()
    # to stay consistent with in-cluster config loading.
    if context_name == kube_client.in_cluster_context_name() or context_name is None:
        if os.path.exists(ns_path):
            with open(ns_path, encoding='utf-8') as f:
                return f.read().strip()
    # If not in-cluster, get the namespace from kubeconfig
    try:
        contexts, current_context = k8s.config.list_kube_config_contexts()
        if context_name is None:
            context = current_context
        else:
            context = next((c for c in contexts if c['name'] == context_name), None)
            if context is None:
                return DEFAULT_NAMESPACE

        if 'namespace' in context['context']:
            return context['context']['namespace']
        else:
            return DEFAULT_NAMESPACE
    except k8s.config.config_exception.ConfigException:
        return DEFAULT_NAMESPACE


def check_credentials(
    context: Optional[str], timeout: int = kube_client.API_TIMEOUT
) -> Tuple[bool, Optional[str]]:
    """Check if the credentials in kubeconfig file are valid

    Args:
        context (Optional[str]): The Kubernetes context to use. If none, uses
            in-cluster auth to check credentials, if available.
        timeout (int): Timeout in seconds for the test API call

    Returns:
        bool: True if credentials are valid, False otherwise
        str: Error message if credentials are invalid, None otherwise
    """
    try:
        namespace = get_kube_config_context_namespace(context)
        kube_client.core_api(context).list_namespaced_pod(
            namespace, _request_timeout=timeout
        )
        return True, None
    except ImportError:
        return False, (
            '`kubernetes` package is not installed. '
            'Install it with: pip install kubernetes'
        )
    except kube_client.api_exception() as e:
        # Check if the error is due to invalid credentials
        if e.status == 401:
            return (
                False,
                'Invalid credentials - do you have permission '
                'to access the cluster?',
            )
        else:
            return False, f'Failed to communicate with the cluster: {str(e)}'
    except kube_client.config_exception() as e:
        return False, f'Invalid configuration file: {str(e)}'
    except kube_client.max_retry_error():
        return False, (
            'Failed to communicate with the cluster - timeout. '
            'Check if your cluster is running and your network '
            'is stable.'
        )
    except ValueError as e:
        return False, common_utils.format_exception(e)
    except Exception as e:  # pylint: disable=broad-except
        return False, (
            'An error occurred: '
            f'{common_utils.format_exception(e, use_bracket=True)}'
        )


def parse_cpu_or_gpu_resource(resource_qty_str: str) -> Union[int, float]:
    resource_str = str(resource_qty_str)
    if resource_str[-1] == 'm':
        # For example, '500m' rounds up to 1.
        return math.ceil(int(resource_str[:-1]) / 1000)
    else:
        return float(resource_str)


def parse_memory_resource(resource_qty_str: str, unit: str = 'B') -> Union[int, float]:
    """Returns memory size in chosen units given a resource quantity string."""
    if unit not in MEMORY_SIZE_UNITS:
        valid_units = ', '.join(MEMORY_SIZE_UNITS.keys())
        raise ValueError(f'Invalid unit: {unit}. Valid units are: {valid_units}')

    resource_str = str(resource_qty_str)
    bytes_value: Union[int, float]
    try:
        bytes_value = int(resource_str)
    except ValueError:
        memory_size = re.sub(r'([KMGTPB]+)', r' \1', resource_str)
        number, unit_index = [item.strip() for item in memory_size.split()]
        unit_index = unit_index[0]
        bytes_value = float(number) * MEMORY_SIZE_UNITS[unit_index]
    return bytes_value / MEMORY_SIZE_UNITS[unit]


def combine_pod_config_fields(
    cluster_yaml_path: str,
    cluster_config_overrides: Dict[str, Any],
) -> None:
    """Adds or updates fields in the YAML with fields from the ~/.konduktor/config's
    kubernetes.pod_spec dict.
    This can be used to add fields to the YAML that are not supported by
    yet, or require simple configuration (e.g., adding an
    imagePullSecrets field).
    Note that new fields are added and existing ones are updated. Nested fields
    are not completely replaced, instead their objects are merged. Similarly,
    if a list is encountered in the config, it will be appended to the
    destination list.
    For example, if the YAML has the following:
        ```
        ...
        node_config:
            spec:
                containers:
                    - name: ray
                    image: rayproject/ray:nightly
        ```
    and the config has the following:
        ```
        kubernetes:
            pod_config:
                spec:
                    imagePullSecrets:
                        - name: my-secret
        ```
    then the resulting YAML will be:
        ```
        ...
        node_config:
            spec:
                containers:
                    - name: ray
                    image: rayproject/ray:nightly
                imagePullSecrets:
                    - name: my-secret
        ```
    """
    with open(cluster_yaml_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()
    yaml_obj = yaml.safe_load(yaml_content)
    # We don't use override_configs in `konduktor_config.get_nested`, as merging
    # the pod config requires special handling.
    kubernetes_config = config.get_nested(
        ('kubernetes', 'pod_config'), default_value={}, override_configs={}
    )
    override_pod_config = cluster_config_overrides.get('kubernetes', {}).get(
        'pod_config', {}
    )
    config.merge_k8s_configs(override_pod_config, kubernetes_config)

    yaml_obj['kubernetes']['pod_config'] = override_pod_config

    # Write the updated YAML back to the file
    common_utils.dump_yaml(cluster_yaml_path, yaml_obj)


def combine_metadata_fields(cluster_yaml_path: str) -> None:
    """Updates the metadata for all Kubernetes objects created with
    fields from the ~/.konduktor/config's kubernetes.custom_metadata dict.

    Obeys the same add or update semantics as combine_pod_config_fields().
    """

    with open(cluster_yaml_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()
    yaml_obj = yaml.safe_load(yaml_content)
    custom_metadata = config.get_nested(('kubernetes', 'custom_metadata'), {})

    # List of objects in the cluster YAML to be updated
    combination_destinations = [
        # Service accounts
        yaml_obj['provider']['autoscaler_service_account']['metadata'],
        yaml_obj['provider']['autoscaler_role']['metadata'],
        yaml_obj['provider']['autoscaler_role_binding']['metadata'],
        yaml_obj['provider']['autoscaler_service_account']['metadata'],
        # Pod spec
        yaml_obj['available_node_types']['ray_head_default']['node_config']['metadata'],
        # Services for pods
        *[svc['metadata'] for svc in yaml_obj['provider']['services']],
    ]

    for destination in combination_destinations:
        config.merge_k8s_configs(custom_metadata, destination)

    # Write the updated YAML back to the file
    common_utils.dump_yaml(cluster_yaml_path, yaml_obj)


def merge_custom_metadata(original_metadata: Dict[str, Any]) -> None:
    """Merges original metadata with custom_metadata from config

    Merge is done in-place, so return is not required
    """
    custom_metadata = config.get_nested(('kubernetes', 'custom_metadata'), {})
    config.merge_k8s_configs(custom_metadata, original_metadata)


def check_nvidia_runtime_class(context: Optional[str] = None) -> bool:
    """Checks if the 'nvidia' RuntimeClass exists in the cluster"""
    # Fetch the list of available RuntimeClasses
    runtime_classes = kube_client.node_api(context).list_runtime_class()

    # Check if 'nvidia' RuntimeClass exists
    nvidia_exists = any(rc.metadata.name == 'nvidia' for rc in runtime_classes.items)
    return nvidia_exists


def check_secret_exists(
    secret_name: str, namespace: str, context: Optional[str]
) -> Tuple[bool, Union[str, Dict[str, Any]]]:
    """Checks if a secret exists in a namespace

    Args:
        secret_name: Name of secret to check
        namespace: Namespace to check
    Returns:
        bool: True if the secret exists, False otherwise
        str: response payload if True, error string otherwise
    """

    try:
        response = kube_client.core_api(context).read_namespaced_secret(
            secret_name, namespace, _request_timeout=kube_client.API_TIMEOUT
        )
    except kube_client.api_exception() as e:
        if e.status == 404:
            return False, str(e)
        raise
    else:
        return True, response


def set_secret(
    secret_name: str,
    namespace: str,
    context: Optional[str],
    data: Dict[str, str],
    secret_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Create/update a secret in a namespace. Values are encoded to base64.
    `secret` must be base64 encoded ie
    ```
    base64.b64encode(secret).decode()
    ```
    """
    with _K8s_CLIENT_LOCK:
        user_hash = common_utils.get_user_hash()

        full_name = (
            secret_metadata.get('name')
            if secret_metadata and 'name' in secret_metadata
            else secret_name
        )
        assert isinstance(full_name, str), 'Secret name must be a string'

        metadata: Dict[str, Any] = {
            'name': full_name,
            'labels': {
                'parent': 'konduktor',
                backend_constants.SECRET_OWNER_LABEL: user_hash,
                backend_constants.SECRET_BASENAME_LABEL: secret_name,
            },
        }

        if secret_metadata:
            metadata['labels'].update(secret_metadata.get('labels', {}))

        custom_metadata = config.get_nested(('kubernetes', 'custom_metadata'), {})
        config.merge_k8s_configs(metadata, custom_metadata)

        secret = kubernetes.client.V1Secret(
            metadata=kubernetes.client.V1ObjectMeta(**metadata),
            type='Opaque',
            data=data,
        )

        secret_exists, _ = check_secret_exists(
            secret_name=full_name,
            namespace=namespace,
            context=context,
        )

        try:
            if secret_exists:
                kube_client.core_api(context).patch_namespaced_secret(
                    full_name, namespace, secret
                )
            else:
                kube_client.core_api(context).create_namespaced_secret(
                    namespace, secret
                )
        except kube_client.api_exception() as e:
            return False, str(e)
        else:
            logger.debug(
                f'Secret {full_name} in namespace {namespace} '
                f'in context {context} created/updated'
            )
            return True, None


def list_secrets(
    namespace: str,
    context: Optional[str],
    label_filter: Optional[str] = None,
) -> List[kubernetes.client.V1Secret]:
    """List all secrets in a namespace, optionally filtering by label."""
    secrets = kube_client.core_api(context).list_namespaced_secret(namespace).items
    if label_filter:
        key, val = label_filter.split('=', 1)
        return [
            s
            for s in secrets
            if s.metadata.labels and s.metadata.labels.get(key) == val
        ]
    return secrets


def delete_secret(
    name: str,
    namespace: str,
    context: Optional[str],
) -> Tuple[bool, Optional[str]]:
    """Deletes a secret by name in the given namespace/context."""
    try:
        kube_client.core_api(context).delete_namespaced_secret(name, namespace)
        logger.debug(f'Secret {name} deleted from namespace {namespace}')
        return True, None
    except kube_client.api_exception() as e:
        return False, str(e)


def get_secret_kind(secret: kubernetes.client.V1Secret) -> Optional[str]:
    """Get the konduktor-specific kind of a secret, if labeled."""
    if secret.metadata.labels:
        return secret.metadata.labels.get(backend_constants.SECRET_KIND_LABEL)
    return None


def get_autoscaler_type() -> Optional[kubernetes_enums.KubernetesAutoscalerType]:
    """Returns the autoscaler type by reading from config"""
    autoscaler_type = config.get_nested(('kubernetes', 'autoscaler'), None)
    if autoscaler_type is not None:
        autoscaler_type = kubernetes_enums.KubernetesAutoscalerType(autoscaler_type)
    return autoscaler_type


# TODO(asaiacai): some checks here for CRDs for jobset and Kueue CRDs, queues, etc.
def is_label_valid(label_key: str, label_value: str) -> Tuple[bool, Optional[str]]:
    # Kubernetes labels can be of the format <domain>/<key>: <value>
    key_regex = re.compile(
        # Look-ahead to ensure proper domain formatting up to a slash
        r'^(?:(?=[a-z0-9]([-a-z0-9.]*[a-z0-9])?\/)'
        # Match domain: starts and ends with alphanum up to 253 chars
        # including a slash in the domain.
        r'[a-z0-9]([-a-z0-9.]{0,251}[a-z0-9])?\/)?'
        # Match key: starts and ends with alphanum, upto to 63 chars.
        r'[a-z0-9]([-a-z0-9_.]{0,61}[a-z0-9])?$'
    )
    value_regex = re.compile(r'^([a-zA-Z0-9]([-a-zA-Z0-9_.]{0,61}[a-zA-Z0-9])?)?$')
    key_valid = bool(key_regex.match(label_key))
    value_valid = bool(value_regex.match(label_value))
    error_msg = None
    condition_msg = (
        'Value must consist of alphanumeric characters or '
        "'-', '_', '.', and must be no more than 63 "
        'characters in length.'
    )
    if not key_valid:
        error_msg = f'Invalid label key {label_key} for Kubernetes. ' f'{condition_msg}'
    if not value_valid:
        error_msg = (
            f'Invalid label value {label_value} for Kubernetes. ' f'{condition_msg}'
        )
    if not key_valid or not value_valid:
        return False, error_msg
    return True, None


def is_k8s_resource_name_valid(name):
    """Returns whether or not a k8s name is valid (must consist of
    lower case alphanumeric characters or -, and must start and end
    with alphanumeric characters)"""
    return re.match(DNS_SUBDOMAIN_REGEX, name)
