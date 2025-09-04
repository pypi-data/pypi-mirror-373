import time
import typing
from typing import Dict, Optional

import colorama

if typing.TYPE_CHECKING:
    import konduktor
    from konduktor.data import storage as storage_lib

from kubernetes.client.exceptions import ApiException

from konduktor import config, kube_client, logging
from konduktor.backends import backend, deployment_utils, pod_utils
from konduktor.utils import kubernetes_utils, rich_utils, ux_utils

Path = str
logger = logging.get_logger(__file__)

POLL_INTERVAL = 5
DEFAULT_ATTACH_TIMEOUT = 300


class DeploymentError(Exception):
    pass


def _wait_for_all_ready(namespace: str, name: str):
    """Wait for Deployment, Service, and Autoscaler readiness."""
    time.sleep(2)
    start = time.time()
    timeout = config.get_nested(
        ('kubernetes', 'provision_timeout'),
        default_value=DEFAULT_ATTACH_TIMEOUT,
    )

    while True:
        context = kubernetes_utils.get_current_kube_config_context_name()

        # Directly read objects instead of listing everything
        try:
            deployment = kube_client.apps_api(context).read_namespaced_deployment(
                name=name, namespace=namespace
            )
            deployments_map = {name: deployment}
        except ApiException:
            deployments_map = {}

        try:
            service = kube_client.core_api(context).read_namespaced_service(
                name=name, namespace=namespace
            )
            services_map = {name: service}
        except ApiException:
            services_map = {}

        autoscaler = deployment_utils.get_autoscaler(namespace, name)
        autoscalers_map = {name: autoscaler} if autoscaler else {}

        status = deployment_utils.get_model_status(
            name, deployments_map, services_map, autoscalers_map
        )

        is_ready = (
            status['deployment'] == 'ready'
            and status['service'] == 'ready'
            and (status['autoscaler'] == 'ready' or status['autoscaler'] is None)
        )

        states = {
            'Deployment': status['deployment'],
            'Service': status['service'],
            'Autoscaler': status['autoscaler'],
        }

        # Figure out which components are missing
        missing_parts = [name for name, state in states.items() if state == 'missing']

        if missing_parts:
            deployment_utils.delete_serving_specs(name, namespace)
            missing_str = ', '.join(missing_parts)
            raise DeploymentError(
                f'Deployment failed. '
                f'The following components are missing: {missing_str}.'
            )

        if is_ready:
            logger.info(
                f'task {colorama.Fore.CYAN}{colorama.Style.BRIGHT}'
                f'{name}{colorama.Style.RESET_ALL} ready'
            )
            return

        if timeout != -1 and time.time() - start > timeout:
            logger.error(
                f'{colorama.Style.BRIGHT}{colorama.Fore.RED}'
                f'Model timed out waiting for readiness.'
                f'{colorama.Style.RESET_ALL}'
                f'Final status:\n{status}'
            )
            deployment_utils.delete_serving_specs(name, namespace)
            raise DeploymentError(
                f'Model failed to become ready within {timeout} seconds.\n'
            )

        time.sleep(POLL_INTERVAL)


class DeploymentBackend(backend.Backend):
    NAME = 'deployment'

    def check_resources_fit_cluster(self, task: 'konduktor.Task') -> bool:
        return True

    def add_storage_objects(self, task: 'konduktor.Task') -> None:
        pass

    def register_info(self, **kwargs) -> None:
        pass

    def _sync_file_mounts(
        self,
        all_file_mounts: Optional[Dict[Path, Path]],
        storage_mounts: Optional[Dict[Path, 'storage_lib.Storage']],
    ) -> None:
        pass

    def _sync_workdir(self, workdir: str) -> None:
        pass

    def _post_execute(self) -> None:
        pass

    def _execute(
        self,
        task: 'konduktor.Task',
        detach_run: bool = False,
        dryrun: bool = False,
    ) -> Optional[str]:
        """Execute a task by launching a long-running Deployment."""

        pod_spec = pod_utils.create_pod_spec(task)
        context = kubernetes_utils.get_current_kube_config_context_name()
        namespace = kubernetes_utils.get_kube_config_context_namespace(context)

        if not dryrun and task.serving:
            deployment_utils.create_deployment(
                namespace=namespace,
                task=task,
                pod_spec=pod_spec['kubernetes']['pod_config'],
                dryrun=dryrun,
            )

            deployment_utils.create_service(
                namespace=namespace,
                task=task,
                dryrun=dryrun,
            )

            deployment_utils.create_autoscaler(
                namespace=namespace,
                task=task,
                dryrun=dryrun,
            )

            # Apoxy resources for general deployments only when endpoint: trainy
            if deployment_utils.get_endpoint_type_from_config() == 'trainy':
                deployment_utils.create_apoxy_resources(
                    namespace=namespace,
                    task=task,
                    dryrun=dryrun,
                )

        if not dryrun and not detach_run:
            with ux_utils.print_exception_no_traceback():
                with rich_utils.safe_status(
                    ux_utils.spinner_message('waiting for resources to be ready.\n')
                ):
                    _wait_for_all_ready(namespace, task.name)
            logger.info(
                f"Model '{task.name}' is ready. "
                f'Run `konduktor serve status` for details.'
            )
        else:
            logger.info('detaching from run.')

        return task.name
