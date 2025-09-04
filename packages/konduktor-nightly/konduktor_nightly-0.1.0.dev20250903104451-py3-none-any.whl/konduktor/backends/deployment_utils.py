"""Deployment utils: wraps CRUD operations for deployments"""

import json
import os
import random
import tempfile
import typing
from typing import Any, Dict, List, Optional, Tuple

import colorama
from kubernetes.client.exceptions import ApiException
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

import konduktor
from konduktor import config as konduktor_config
from konduktor import kube_client, logging
from konduktor.backends import constants as backend_constants
from konduktor.backends import pod_utils
from konduktor.utils import (
    common_utils,
    kubernetes_utils,
    validator,
)

if typing.TYPE_CHECKING:
    pass

logger = logging.get_logger(__name__)

# Use shared constants from konduktor.backends.constants
DEPLOYMENT_NAME_LABEL = backend_constants.DEPLOYMENT_NAME_LABEL
DEPLOYMENT_USERID_LABEL = backend_constants.USERID_LABEL
DEPLOYMENT_USER_LABEL = backend_constants.USER_LABEL
DEPLOYMENT_ACCELERATOR_LABEL = backend_constants.ACCELERATOR_LABEL
DEPLOYMENT_NUM_ACCELERATORS_LABEL = backend_constants.NUM_ACCELERATORS_LABEL
AIBRIX_NAME_LABEL = backend_constants.AIBRIX_NAME_LABEL

SECRET_BASENAME_LABEL = backend_constants.SECRET_BASENAME_LABEL

_DEPLOYMENT_METADATA_LABELS = {
    'deployment_name_label': DEPLOYMENT_NAME_LABEL,
    'deployment_userid_label': DEPLOYMENT_USERID_LABEL,
    'deployment_user_label': DEPLOYMENT_USER_LABEL,
    'deployment_accelerator_label': DEPLOYMENT_ACCELERATOR_LABEL,
    'deployment_num_accelerators_label': DEPLOYMENT_NUM_ACCELERATORS_LABEL,
    'model_name_label': AIBRIX_NAME_LABEL,
}


# actually just gets highest existing deployment number and adds 1
def get_next_deployment_number(cluster_name: str) -> int:
    """Get next number by counting existing Apoxy resources."""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        custom_api = kube_client.crd_api(context=context)

        # Count existing backends
        backends = custom_api.list_cluster_custom_object(
            group='core.apoxy.dev', version='v1alpha', plural='backends'
        )

        # Find the highest number
        max_number = 0
        for backend in backends.get('items', []):
            name = backend['metadata']['name']
            if name.startswith(f'{cluster_name}-backend-'):
                number = int(name.split('-')[-1])
                max_number = max(max_number, number)

        return max_number + 1
    except Exception as e:
        logger.warning(f'Error counting existing resources: {e}')
        return random.randint(100, 999)


def render_specs(
    task: 'konduktor.Task',
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    general = True
    if task.run and 'vllm.entrypoints.openai.api_server' in task.run:
        general = False

    # Calculate accelerator info for template
    assert task.resources is not None
    accelerator_type = task.resources.get_accelerator_type() or 'None'
    # For Deployments: GPUs per pod (not total across replicas)
    num_accelerators = task.resources.get_accelerator_count() or 0

    if task.run:
        task.run = task.run.replace('__KONDUKTOR_TASK_NAME__', task.name)
    with tempfile.NamedTemporaryFile() as temp:
        common_utils.fill_template(
            'deployment.yaml.j2',
            {
                'name': task.name,
                'user': common_utils.get_cleaned_username(),
                'accelerator_type': accelerator_type,
                'num_accelerators': str(num_accelerators),
                'min_replicas': task.serving.min_replicas if task.serving else 1,
                'max_replicas': task.serving.max_replicas if task.serving else 1,
                'ports': task.serving.ports if task.serving else 8000,
                'autoscaler': (
                    'true'
                    if (
                        task.serving
                        and task.serving.min_replicas != task.serving.max_replicas
                    )
                    else 'false'
                ),
                'general': general,
                **_DEPLOYMENT_METADATA_LABELS,
            },
            temp.name,
        )
        docs = common_utils.read_yaml_all(temp.name)

    deployment_spec = None
    service_spec = None
    autoscaler_spec = None

    for doc in docs:
        kind = doc.get('kind')
        if kind == 'Deployment':
            deployment_spec = doc
        elif kind == 'Service':
            service_spec = doc
        elif kind == 'PodAutoscaler' or kind == 'HorizontalPodAutoscaler':
            autoscaler_spec = doc

    # not every deployment + service will have podautoscaler
    if task.serving and task.serving.min_replicas == task.serving.max_replicas:
        autoscaler_spec = None

    if deployment_spec is None:
        raise ValueError('Deployment manifest not found.')
    if service_spec is None:
        raise ValueError('Service manifest not found.')

    # Validate specs before returning
    try:
        validator.validate_deployment_spec(deployment_spec)
        validator.validate_service_spec(service_spec)
        # Only validate HPA if it exists (APA doesn't have official schema)
        if autoscaler_spec and autoscaler_spec.get('kind') == 'HorizontalPodAutoscaler':
            validator.validate_horizontalpodautoscaler_spec(autoscaler_spec)
    except ValueError as e:
        raise ValueError(f'Spec validation failed: {e}')

    return deployment_spec, service_spec, autoscaler_spec or {}


# For general deployments, create resources as needed
def render_apoxy_spec(task: 'konduktor.Task') -> List[Dict[str, Any]]:
    """Renders the Apoxy specs for a general deployment."""
    general = True
    if task.run and 'vllm.entrypoints.openai.api_server' in task.run:
        general = False

    if not general:
        return []  # Only render for general deployments

    if task.run:
        task.run = task.run.replace('__KONDUKTOR_TASK_NAME__', task.name)

    unique_cluster_name = get_unique_cluster_name_from_tunnel()
    cluster_name = unique_cluster_name[:-3]
    deployment_number = get_next_deployment_number(unique_cluster_name)

    with tempfile.NamedTemporaryFile() as temp:
        common_utils.fill_template(
            'apoxy-deployment.yaml.j2',
            {
                'name': task.name,
                'user': common_utils.get_cleaned_username(),
                'ports': task.serving.ports if task.serving else 8000,
                'general': general,
                'cluster_name': cluster_name,
                'unique_cluster_name': unique_cluster_name,
                'deployment_number': deployment_number,
                **_DEPLOYMENT_METADATA_LABELS,
            },
            temp.name,
        )
        docs = common_utils.read_yaml_all(temp.name)
        return docs


def create_apoxy_resources(
    namespace: str,
    task: 'konduktor.Task',
    dryrun: bool = False,
) -> None:
    """Creates Apoxy resources for a general deployment."""

    apoxy_specs = render_apoxy_spec(task)

    if not apoxy_specs:
        return

    if dryrun:
        logger.debug(f'[DRYRUN] Would create Apoxy resources:\n{apoxy_specs}')
        return

    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        custom_api = kube_client.crd_api(context=context)

        for spec in apoxy_specs:
            kind = spec.get('kind')
            name = spec['metadata']['name']

            try:
                if kind == 'Backend':
                    custom_api.create_cluster_custom_object(
                        group='core.apoxy.dev',
                        version='v1alpha',
                        plural='backends',
                        body=spec,
                    )
                    logger.info(f'Apoxy Backend {name} created')
                elif kind == 'HTTPRoute':
                    custom_api.create_cluster_custom_object(
                        group='gateway.apoxy.dev',
                        version='v1',
                        plural='httproutes',
                        body=spec,
                    )
                    logger.info(f'Apoxy HTTPRoute {name} created')
            except Exception as e:
                if '409' in str(e) or 'AlreadyExists' in str(e):
                    try:
                        # Delete first, then create
                        if kind == 'Backend':
                            custom_api.delete_cluster_custom_object(
                                group='core.apoxy.dev',
                                version='v1alpha',
                                plural='backends',
                                name=name,
                            )
                            custom_api.create_cluster_custom_object(
                                group='core.apoxy.dev',
                                version='v1alpha',
                                plural='backends',
                                body=spec,
                            )
                        elif kind == 'HTTPRoute':
                            custom_api.delete_cluster_custom_object(
                                group='gateway.apoxy.dev',
                                version='v1',
                                plural='httproutes',
                                name=name,
                            )
                            custom_api.create_cluster_custom_object(
                                group='gateway.apoxy.dev',
                                version='v1',
                                plural='httproutes',
                                body=spec,
                            )
                        logger.info(f'Apoxy {kind} {name} deleted and recreated')
                    except Exception as delete_create_error:
                        logger.error(
                            f'Failed to delete and recreate {kind} {name}: '
                            f'{delete_create_error}'
                        )
                        raise
                elif '404' in str(e) or 'NotFound' in str(e):
                    logger.warning(f'Apoxy CRD for {kind} not found. Skipping {name}.')
                    logger.info('Make sure Apoxy is deployed and CRDs are ready.')
                    continue
                else:
                    raise
    except Exception as e:
        logger.error(f'Error creating Apoxy resources: {e}')


def create_deployment(
    namespace: str,
    task: 'konduktor.Task',
    pod_spec: Dict[str, Any],
    dryrun: bool = False,
) -> Optional[Dict[str, Any]]:
    """Creates a Kubernetes Deployment based on the task and pod spec."""

    assert task.resources is not None, 'Task resources are undefined'

    deployment_spec, _, _ = render_specs(task)

    # Inject deployment-specific pod metadata
    pod_utils.inject_deployment_pod_metadata(pod_spec, task)

    # Inject pod spec directly (like jobset logic)
    pod_utils.merge_pod_into_deployment_template(deployment_spec['spec'], pod_spec)

    if dryrun:
        logger.debug(f'[DRYRUN] Would create deployment:\n{deployment_spec}')
        return deployment_spec

    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        apps_api = kube_client.apps_api(context=context)
        deployment = apps_api.create_namespaced_deployment(
            namespace=namespace,
            body=deployment_spec,
        )
        logger.info(
            f'Deployment {colorama.Fore.CYAN}{colorama.Style.BRIGHT}'
            f'{task.name}{colorama.Style.RESET_ALL} created'
        )

        return deployment
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'Error creating deployment: {error_message}')
        except json.JSONDecodeError:
            logger.error(f'Error creating deployment: {err.body}')
        raise err


def create_service(
    namespace: str,
    task: 'konduktor.Task',
    dryrun: bool = False,
) -> Optional[Dict[str, Any]]:
    """Creates a Kubernetes Service based on the task and pod spec."""

    assert task.resources is not None, 'Task resources are undefined'

    _, service_spec, _ = render_specs(task)

    if dryrun:
        logger.debug(f'[DRYRUN] Would create service:\n{service_spec}')
        return service_spec

    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        core_api = kube_client.core_api(context=context)
        service = core_api.create_namespaced_service(
            namespace=namespace,
            body=service_spec,
        )
        logger.info(
            f'Service {colorama.Fore.CYAN}{colorama.Style.BRIGHT}'
            f'{task.name}{colorama.Style.RESET_ALL} created'
        )
        return service
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'Error creating service: {error_message}')
        except json.JSONDecodeError:
            logger.error(f'Error creating service: {err.body}')
        raise err


def create_autoscaler(namespace: str, task: 'konduktor.Task', dryrun: bool = False):
    _, _, autoscaler_spec = render_specs(task)

    if not autoscaler_spec:
        return

    # Decide if it's APA or HPA by looking at autoscaler_spec["kind"]
    kind = autoscaler_spec.get('kind')
    context = kubernetes_utils.get_current_kube_config_context_name()

    if dryrun:
        logger.debug(f'[DRYRUN] Would create {kind}:\n{autoscaler_spec}')
        return autoscaler_spec

    if kind == 'PodAutoscaler':
        custom_api = kube_client.crd_api(context=context)
        return custom_api.create_namespaced_custom_object(
            group='autoscaling.aibrix.ai',
            version='v1alpha1',
            namespace=namespace,
            plural='podautoscalers',
            body=autoscaler_spec,
        )
    elif kind == 'HorizontalPodAutoscaler':
        autoscaling_api = kube_client.autoscaling_api(context=context)
        return autoscaling_api.create_namespaced_horizontal_pod_autoscaler(
            namespace=namespace,
            body=autoscaler_spec,
        )


def list_models(namespace: str) -> List[str]:
    """
    Returns a list of unique model names in the namespace,
    based on label DEPLOYMENT_NAME_LABEL=`trainy.ai/deployment-name`.
    """
    context = kubernetes_utils.get_current_kube_config_context_name()
    apps = kube_client.apps_api(context)
    core = kube_client.core_api(context)
    crds = kube_client.crd_client(context)

    label_selector = DEPLOYMENT_NAME_LABEL
    model_names: set[str] = set()

    # --- Deployments ---
    for deploy in apps.list_namespaced_deployment(
        namespace, label_selector=label_selector
    ).items:
        labels = getattr(deploy.metadata, 'labels', {}) or {}
        name = labels.get(DEPLOYMENT_NAME_LABEL)
        if name:
            model_names.add(name)

    # --- Services ---
    for svc in core.list_namespaced_service(
        namespace, label_selector=label_selector
    ).items:
        labels = getattr(svc.metadata, 'labels', {}) or {}
        name = labels.get(DEPLOYMENT_NAME_LABEL)
        if name:
            model_names.add(name)

    # --- PodAutoscalers ---
    # APA
    try:
        apa_list = crds.list_namespaced_custom_object(
            group='autoscaling.aibrix.ai',
            version='v1alpha1',
            namespace=namespace,
            plural='podautoscalers',
        )
        for apa in apa_list.get('items', []):
            labels = apa.get('metadata', {}).get('labels', {}) or {}
            name = labels.get(DEPLOYMENT_NAME_LABEL)
            if name:
                model_names.add(name)
    except ApiException as e:
        if e.status != 404:
            # re-raise if it's not just missing CRD
            raise
        # otherwise ignore, cluster just doesn't have Aibrix CRDs
        logger.warning('Skipping APA lookup. Aibrix CRDs not found in cluster')

    # HPA
    autoscaling_api = kube_client.autoscaling_api(context=context)
    hpa_list = autoscaling_api.list_namespaced_horizontal_pod_autoscaler(
        namespace=namespace
    )
    for hpa in hpa_list.items:
        labels = getattr(hpa.metadata, 'labels', {}) or {}
        name = labels.get(DEPLOYMENT_NAME_LABEL)
        if name:
            model_names.add(name)

    return sorted(model_names)


def is_autoscaler_ready(autoscaler_obj: dict) -> bool:
    """
    Returns True if the autoscaler (PodAutoscaler or HPA) is considered healthy.
    For PodAutoscaler: AbleToScale == True.
    For HPA: AbleToScale == True, or presence of the HPA is enough if no conditions.
    """
    try:
        if hasattr(autoscaler_obj, 'to_dict'):
            autoscaler_obj = autoscaler_obj.to_dict()
        conditions = autoscaler_obj.get('status', {}).get('conditions', []) or []

        # If conditions exist, look for AbleToScale == True
        for cond in conditions:
            cond_type = cond.get('type')
            cond_status = cond.get('status')
            if cond_type == 'AbleToScale' and cond_status == 'True':
                return True

        # If no conditions are present (common for HPAs), assume
        # it's fine as soon as object exists
        if not conditions:
            return True

    except Exception as e:
        logger.warning(f'Error checking autoscaler readiness: {e}')
    return False


def build_autoscaler_map(namespace: str, context: str) -> dict[str, dict]:
    """Fetch all APAs and HPAs and combine into 1 dict keyed by deployment name."""
    autoscalers = {}

    # --- Aibrix APAs ---
    try:
        crd_api = kube_client.crd_api(context=context)
        apa_list = crd_api.list_namespaced_custom_object(
            group='autoscaling.aibrix.ai',
            version='v1alpha1',
            namespace=namespace,
            plural='podautoscalers',
        )
        for apa in apa_list.get('items', []):
            labels = apa.get('metadata', {}).get('labels', {}) or {}
            dep_name = labels.get(DEPLOYMENT_NAME_LABEL)
            if dep_name:
                autoscalers[dep_name] = apa
    except Exception as e:
        logger.warning(f'Error fetching APAs: {e}')

    # --- Standard HPAs ---
    try:
        autoscaling_api = kube_client.autoscaling_api(context=context)
        hpa_list = autoscaling_api.list_namespaced_horizontal_pod_autoscaler(
            namespace=namespace
        )
        for hpa in hpa_list.items:
            labels = getattr(hpa.metadata, 'labels', {}) or {}
            dep_name = labels.get(DEPLOYMENT_NAME_LABEL)
            if dep_name and dep_name not in autoscalers:
                autoscalers[dep_name] = hpa.to_dict()
    except Exception as e:
        logger.warning(f'Error fetching HPAs: {e}')

    return autoscalers


def get_model_status(
    name: str,
    deployments: dict[str, Any],
    services: dict[str, Any],
    autoscalers: dict[str, dict],
) -> Dict[str, Optional[str]]:
    """Check the status of Deployment, Service, and Autoscaler."""
    status = {
        'deployment': 'missing',
        'service': 'missing',
        'autoscaler': None,
    }

    # --- Deployment ---
    if name in deployments:
        d = deployments[name]
        ready = (d.status.ready_replicas or 0) if d.status else 0
        desired = (d.spec.replicas or 0) if d.spec else 0
        status['deployment'] = 'ready' if ready == desired else 'pending'

    # --- Service ---
    if name in services:
        s = services[name]
        labels = getattr(s.metadata, 'labels', {}) or {}
        is_vllm = AIBRIX_NAME_LABEL in labels

        if is_vllm:
            status['service'] = 'ready'
        else:
            lb_ready = False
            if s.status and s.status.load_balancer and s.status.load_balancer.ingress:
                ingress = s.status.load_balancer.ingress
                if ingress and (ingress[0].ip or ingress[0].hostname):
                    lb_ready = True
            status['service'] = 'ready' if lb_ready else 'pending'

    # --- Autoscaler ---
    if name in autoscalers:
        a = autoscalers[name]
        status['autoscaler'] = 'ready' if is_autoscaler_ready(a) else 'pending'
    else:
        status['autoscaler'] = None

    return status


def get_deployment(namespace: str, job_name: str) -> Optional[Any]:
    context = kubernetes_utils.get_current_kube_config_context_name()
    apps_api = kube_client.apps_api(context=context)
    try:
        return apps_api.read_namespaced_deployment(name=job_name, namespace=namespace)
    except ApiException as e:
        if e.status == 404:
            return None
        raise


def get_service(namespace: str, job_name: str) -> Optional[Any]:
    context = kubernetes_utils.get_current_kube_config_context_name()
    core_api = kube_client.core_api(context=context)
    try:
        return core_api.read_namespaced_service(name=job_name, namespace=namespace)
    except ApiException as e:
        if e.status == 404:
            return None
        raise


def get_autoscaler(namespace: str, job_name: str) -> Optional[Any]:
    context = kubernetes_utils.get_current_kube_config_context_name()
    # --- Try Aibrix APA first ---
    crd_api = kube_client.crd_api(context=context)
    try:
        return crd_api.get_namespaced_custom_object(
            group='autoscaling.aibrix.ai',
            version='v1alpha1',
            namespace=namespace,
            plural='podautoscalers',
            name=f'{job_name}-apa',
        )
    except ApiException as e:
        if e.status != 404:
            raise
        # Fall through to check HPA

    # --- Try built‑in Kubernetes HPA ---
    try:
        autoscaling_api = kube_client.autoscaling_api(context=context)
        return autoscaling_api.read_namespaced_horizontal_pod_autoscaler(
            name=f'{job_name}-hpa', namespace=namespace
        ).to_dict()
    except ApiException as e:
        if e.status == 404:
            return None
        raise


def delete_deployment(namespace: str, name: str) -> Optional[Dict[str, Any]]:
    """Deletes a Kubernetes Deployment in the given namespace.

    Args:
        namespace: Namespace where the deployment exists.
        name: Name of the deployment to delete.

    Returns:
        Response from delete operation, or None on error.
    """
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.apps_api(context=context).delete_namespaced_deployment(
            name=name,
            namespace=namespace,
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'Error deleting deployment: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'Error deleting deployment: {error_message}')
        else:
            raise err
    return None


def delete_service(namespace: str, name: str) -> Optional[Dict[str, Any]]:
    """Deletes a Kubernetes Service in the given namespace.

    Args:
        namespace: Namespace where the service exists.
        name: Name of the service to delete.

    Returns:
        Response from delete operation, or None on error.
    """
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.core_api(context=context).delete_namespaced_service(
            name=name,
            namespace=namespace,
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'Error deleting service: {error_message}')
        except json.JSONDecodeError:
            logger.error(f'Error deleting service: {err.body}')
        raise err
    return None


def delete_autoscaler(namespace: str, name: str) -> Optional[Dict[str, Any]]:
    """Deletes either an Aibrix PodAutoscaler or a HorizontalPodAutoscaler."""
    context = kubernetes_utils.get_current_kube_config_context_name()

    # --- Try delete APA first ---
    try:
        custom_api = kube_client.crd_api(context=context)
        response = custom_api.delete_namespaced_custom_object(
            group='autoscaling.aibrix.ai',
            version='v1alpha1',
            namespace=namespace,
            plural='podautoscalers',
            name=f'{name}-apa',
        )
        return response
    except kube_client.api_exception() as err:
        # If not found, try HPA
        try:
            error_body = json.loads(err.body)
            if err.status != 404:
                raise
        except Exception:
            if getattr(err, 'status', None) != 404:
                raise

    # --- Try delete HPA ---
    try:
        autoscaling_api = kube_client.autoscaling_api(context=context)
        return autoscaling_api.delete_namespaced_horizontal_pod_autoscaler(
            name=f'{name}-hpa',
            namespace=namespace,
        )
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'Error deleting Pod Autoscaler: {error_message}')
        except json.JSONDecodeError:
            logger.error(f'Error deleting Pod Autoscaler: {err.body}')
        raise err


def delete_serving_specs(name: str, namespace: str) -> None:
    for kind, delete_fn in [
        ('deployment', delete_deployment),
        ('service', delete_service),
        ('podautoscaler', delete_autoscaler),
    ]:
        try:
            delete_fn(namespace, name)
            logger.info(f'Deleted {kind}: {name}')
        except Exception as e:
            logger.debug(f'Failed to delete {kind} {name}: {e}')


def _get_resource_summary(deployment) -> str:
    """Extract and format pod resource information from a deployment.

    Args:
        deployment: Kubernetes deployment object

    Returns:
        Formatted string with resource information (GPU, CPU, memory)
    """
    if not deployment:
        return '?'

    try:
        containers = deployment.spec.template.spec.containers
        if not containers:
            return '?'
        container = containers[0]
        res = container.resources.requests or {}

        cpu = res.get('cpu', '?')
        mem = res.get('memory', '?')
        gpu = res.get('nvidia.com/gpu') or res.get('trainy.ai/gpu')

        # Try to extract GPU type from deployment labels
        labels = deployment.metadata.labels or {}
        accelerator_type = labels.get('trainy.ai/accelerator', 'L4O')

        gpu_str = f'{accelerator_type}:{gpu}' if gpu else 'None'
        return f'{gpu_str}\n{cpu} CPU\n{mem}'
    except Exception:
        return '?'


def get_envoy_external_ip() -> Optional[str]:
    context = kubernetes_utils.get_current_kube_config_context_name()
    core_api = kube_client.core_api(context=context)
    try:
        services = core_api.list_namespaced_service(namespace='envoy-gateway-system')
        for svc in services.items:
            if svc.spec.type == 'LoadBalancer' and 'envoy' in svc.metadata.name:
                ingress = svc.status.load_balancer.ingress
                if ingress:
                    return ingress[0].ip or ingress[0].hostname
    except Exception:
        pass
    return None


def get_unique_cluster_name_from_tunnel() -> str:
    """Get cluster name from the apoxy deployment command."""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        apps_api = kube_client.apps_api(context=context)

        # Get the apoxy deployment
        deployment = apps_api.read_namespaced_deployment(
            name='apoxy', namespace='default'
        )

        # Extract cluster name from the command
        containers = deployment.spec.template.spec.containers
        if containers and len(containers) > 0:
            command = containers[0].command
            if (
                command
                and len(command) >= 4
                and command[1] == 'tunnel'
                and command[2] == 'run'
            ):
                return command[3]  # The cluster name is the 4th argument

        logger.warning('Could not extract cluster name from apoxy deployment command')

    except Exception as e:
        logger.warning(f'Error getting cluster name from apoxy deployment: {e}')

    return 'default'


def get_endpoint_type_from_config() -> str:
    """Get the endpoint type from konduktor config.

    Returns:
        'trainy' for Apoxy endpoints (default)
        'direct' for LoadBalancer IP endpoints
    """
    try:
        # Use the proper config system that handles KONDUKTOR_CONFIG env var
        endpoint_type = konduktor_config.get_nested(('serving', 'endpoint'), 'trainy')
        return endpoint_type.lower()
    except Exception as e:
        logger.warning(f'Error reading endpoint config: {e}')

    # Default to trainy if config not found or error
    return 'trainy'


def _get_loadbalancer_endpoint_with_port(service_name: str) -> str:
    """Helper function to get LoadBalancer endpoint with port."""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        core_api = kube_client.core_api(context=context)

        # Get the service
        service = core_api.read_namespaced_service(
            name=service_name, namespace='default'
        )

        # Check if it's LoadBalancer type
        if service.spec.type == 'LoadBalancer':
            ingress = service.status.load_balancer.ingress
            if ingress and len(ingress) > 0:
                ip = ingress[0].ip
                if ip:
                    return f'{ip}:{service.spec.ports[0].port}'

        # If not LoadBalancer or no IP, return pending
        return '<pending>'

    except Exception:
        return '<pending>'


def get_vllm_deployment_endpoint(force_direct: bool = False) -> str:
    """Get the endpoint for vLLM/Aibrix deployments based on config."""
    if force_direct:
        # Force direct endpoint display regardless of config
        endpoint_type = 'direct'
    else:
        endpoint_type = get_endpoint_type_from_config()

    if endpoint_type == 'direct':
        try:
            aibrix_endpoint = get_envoy_external_ip()
            return aibrix_endpoint or '<pending>'
        except Exception:
            return '<pending>'
    else:
        try:
            cluster_name = get_unique_cluster_name_from_tunnel()
            return f'{cluster_name[:-3]}.trainy.us'
        except Exception:
            # Fallback to direct endpoint if trainy.us not available
            try:
                aibrix_endpoint = get_envoy_external_ip()
                if aibrix_endpoint:
                    # Aibrix deployments route through Envoy Gateway on port 80
                    return f'{aibrix_endpoint}'
            except Exception:
                pass
            return '<pending>'


def get_general_deployment_endpoint(
    service_name: str, force_direct: bool = False
) -> str:
    """Get the endpoint for a general deployment based on config."""
    if force_direct:
        # Force direct endpoint display regardless of config
        endpoint_type = 'direct'
    else:
        endpoint_type = get_endpoint_type_from_config()

    if endpoint_type == 'direct':
        # Use LoadBalancer IP with port
        return _get_loadbalancer_endpoint_with_port(service_name)
    else:
        # Use Apoxy (trainy.us) - existing logic
        try:
            context = kubernetes_utils.get_current_kube_config_context_name()
            custom_api = kube_client.crd_api(context=context)

            # Query route with label selector using the original task name
            routes = custom_api.list_cluster_custom_object(
                group='gateway.apoxy.dev',
                version='v1',
                plural='httproutes',
                label_selector=f'task_name={service_name}',
            )

            # Extract endpoint_name from the route labels
            if routes.get('items') and len(routes['items']) > 0:
                route = routes['items'][0]  # Should only be one route with this label
                labels = route.get('metadata', {}).get('labels', {})
                endpoint_name = labels.get('endpoint_name')
                if endpoint_name:
                    return endpoint_name

            # Fallback if no route found - try direct LoadBalancer endpoint
            return _get_loadbalancer_endpoint_with_port(service_name)

        except Exception as e:
            logger.warning(f'Endpoint error for general deployment {service_name}: {e}')
            # Fallback to direct LoadBalancer endpoint on error
            return _get_loadbalancer_endpoint_with_port(service_name)


def show_status_table(namespace: str, all_users: bool, force_direct: bool = False):
    """Display status of Konduktor Serve models."""
    context = kubernetes_utils.get_current_kube_config_context_name()

    # Build lookup maps (deployment_name -> object)
    apps_api = kube_client.apps_api(context)
    core_api = kube_client.core_api(context)

    deployments_map = {}
    for d in apps_api.list_namespaced_deployment(namespace=namespace).items:
        name = (d.metadata.labels or {}).get(DEPLOYMENT_NAME_LABEL)
        if name is not None:
            deployments_map[name] = d

    services_map = {}
    for s in core_api.list_namespaced_service(namespace=namespace).items:
        name = (s.metadata.labels or {}).get(DEPLOYMENT_NAME_LABEL)
        if name is not None:
            services_map[name] = s

    autoscalers_map = build_autoscaler_map(namespace, context or '')

    model_names = list_models(namespace)
    if not model_names:
        Console().print(
            f'[yellow]No deployments found in namespace {namespace}.[/yellow]'
        )
        return

    Console().print()
    title = '[bold]KONDUKTOR SERVE[/bold]'
    is_ci = os.environ.get('CI') or os.environ.get('BUILDKITE')

    # Get Aibrix endpoint once for all Aibrix deployments
    aibrix_endpoint = get_vllm_deployment_endpoint(force_direct)

    table = Table(title=title, box=box.ASCII if is_ci else box.ROUNDED)
    if all_users:
        table.add_column('User', style='magenta', no_wrap=True)
    table.add_column('Name', style='cyan', no_wrap=True)
    table.add_column('Status', no_wrap=True)
    table.add_column('Summary', style='bold', no_wrap=True)
    table.add_column('Endpoint', style='yellow', no_wrap=True)
    table.add_column('Replicas', style='dim', no_wrap=True)
    table.add_column('Resources', style='white', no_wrap=True)

    unowned = 0

    for idx, name in enumerate(model_names):
        deployment = deployments_map.get(name)
        service = services_map.get(name)
        autoscaler = autoscalers_map.get(name)

        # Extract owner
        owner = None
        for resource in [deployment, service, autoscaler]:
            if not resource:
                continue
            metadata = (
                resource.metadata
                if hasattr(resource, 'metadata')
                else resource.get('metadata', {})
            )
            labels = (
                metadata.labels
                if hasattr(metadata, 'labels')
                else metadata.get('labels', {})
            )
            if labels:
                owner = labels.get('trainy.ai/username')
            if owner:
                break

        if not all_users and owner != common_utils.get_cleaned_username():
            unowned += 1
            continue

        # Status
        status = get_model_status(name, deployments_map, services_map, autoscalers_map)
        states = [status['deployment'], status['service'], status['autoscaler']]

        def emoji_line(label: str, state: str) -> str:
            emoji_map = {
                'ready': '✅',
                'pending': '❓',
                'missing': '❌',
            }
            return f"{label}: {emoji_map.get(state, '❓')}"

        summary_lines = [
            emoji_line('Deploym', status['deployment'] or 'missing'),
            emoji_line('Service', status['service'] or 'missing'),
        ]
        if status['autoscaler'] is not None:
            summary_lines.append(
                emoji_line('AScaler', status['autoscaler'] or 'missing')
            )
        summary = '\n'.join(summary_lines)

        # Overall status
        if any(s == 'missing' for s in states):
            status_text = Text('FAILED', style='red')
        else:
            if status['autoscaler'] is not None:
                status_text = (
                    Text('READY', style='green')
                    if all(s == 'ready' for s in states)
                    else Text('PENDING', style='yellow')
                )
            else:
                status_text = (
                    Text('READY', style='green')
                    if (
                        status['deployment'] == 'ready' and status['service'] == 'ready'
                    )
                    else Text('PENDING', style='yellow')
                )

        # Extract labels from deployment, service, or fallback to empty dict
        labels = {}
        if deployment and hasattr(deployment.metadata, 'labels'):
            labels = deployment.metadata.labels or {}
        elif service and hasattr(service.metadata, 'labels'):
            labels = service.metadata.labels or {}
        else:
            labels = {}

        endpoint_str = '<pending>'
        if AIBRIX_NAME_LABEL in labels:
            # Aibrix deployment - use the pre-computed endpoint
            endpoint_str = aibrix_endpoint
        else:
            # General deployment
            endpoint_str = get_general_deployment_endpoint(name, force_direct)

        # Replicas
        ready_replicas = (
            str(deployment.status.ready_replicas or 0) if deployment else '?'
        )
        desired_replicas = str(deployment.spec.replicas or 0) if deployment else '?'
        replicas_text = Text()
        replicas_text.append(
            f'Ready: {ready_replicas}/{desired_replicas}\n', style='bold white'
        )
        if status['autoscaler']:
            spec = (
                autoscaler.get('spec', {})
                if isinstance(autoscaler, dict)
                else getattr(autoscaler, 'spec', {})
            )
            min_r = str(spec.get('minReplicas', spec.get('min_replicas', '?')))
            max_r = str(spec.get('maxReplicas', spec.get('max_replicas', '?')))
            replicas_text.append(f'Min  : {min_r}\n', style='bold white')
            replicas_text.append(f'Max  : {max_r}', style='bold white')

        # Resources
        resources_text = _get_resource_summary(deployment)

        # Row
        if all_users:
            table.add_row(
                owner or '(unknown)',
                name,
                status_text,
                summary,
                endpoint_str,
                replicas_text,
                resources_text,
            )
        else:
            table.add_row(
                name, status_text, summary, endpoint_str, replicas_text, resources_text
            )

        if idx != len(model_names) - 1:
            table.add_row(*([''] * len(table.columns)))

    if len(model_names) == unowned:
        Console().print(
            f'[yellow]No deployments created by you found '
            f'in namespace {namespace}. Try --all-users.[/yellow]'
        )
        return

    Console().print(table)
