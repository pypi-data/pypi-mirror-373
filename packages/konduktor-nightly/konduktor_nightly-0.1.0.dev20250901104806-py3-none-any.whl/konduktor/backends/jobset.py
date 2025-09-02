"""Batch job execution via k8s jobsets
https://jobset.sigs.k8s.io/
https://kueue.sigs.k8s.io/docs/tasks/run/jobsets/
"""

import threading
import time
import typing
from typing import Dict, Optional, Tuple

import colorama

if typing.TYPE_CHECKING:
    import konduktor
    from konduktor.data import storage as storage_lib

from konduktor import config, logging
from konduktor.backends import backend, jobset_utils, pod_utils
from konduktor.utils import kubernetes_utils, log_utils, rich_utils, ux_utils

Path = str
logger = logging.get_logger(__file__)

POLL_INTERVAL = 5
DEFAULT_ATTACH_TIMEOUT = 86400  # 1 day
FLUSH_LOGS_TIMEOUT = 5


class JobsetError(Exception):
    pass


def _raise_job_error(job):
    """Checks a jobs conditions and statuses for error"""
    for condition in job.status.conditions:
        if 'ConfigIssue' in condition.message:
            raise ValueError(
                'Job failed with '
                f'{colorama.Style.BRIGHT}{colorama.Fore.RED}'
                f'ConfigIssue: ErrImagePull.{colorama.Style.RESET_ALL} '
                f'Check that your '
                f'{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}'
                f'`image_id`{colorama.Style.RESET_ALL} is correct and '
                f'your container credentials are correct. Image specified '
                f'in your task definition is '
                f'{colorama.Style.BRIGHT}{colorama.Fore.RED}'
                f'`{job.spec.template.spec.containers[0].image}`'
                f'{colorama.Style.RESET_ALL}'
            )
        elif 'BackoffLimitExceeded' == condition.reason:
            raise JobsetError('Job failed with non-zero exit code.')
    logger.error(
        'Job failed with unknown error. Check jobset status in k8s with '
        f'{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}'
        f'`kubectl get job -o yaml {job.metadata.name}`'
        f'{colorama.Style.RESET_ALL}'
    )


def _wait_for_jobset_start(namespace: str, job_name: str):
    time.sleep(2)
    start = time.time()
    timeout = config.get_nested(
        ('kubernetes', 'provision_timeout'),
        default_value=DEFAULT_ATTACH_TIMEOUT,
    )

    while True:
        jobsets = jobset_utils.get_jobset(namespace, job_name)
        assert jobsets is not None, (
            f'Jobset {job_name} ' f'not found in namespace {namespace}'
        )
        if 'status' in jobsets:
            if jobsets['status']['replicatedJobsStatus'][0]['ready']:
                logger.info(
                    f'task '
                    f'{colorama.Fore.CYAN}{colorama.Style.BRIGHT}{job_name}'
                    f'{colorama.Style.RESET_ALL} ready'
                )
                break
            elif jobsets['status']['replicatedJobsStatus'][0]['succeeded']:
                return
            elif jobsets['status']['replicatedJobsStatus'][0]['failed']:
                logger.info(
                    f'job '
                    f'{colorama.Fore.CYAN}{colorama.Style.BRIGHT}{job_name}'
                    f'{colorama.Style.RESET_ALL} '
                    f'{colorama.Fore.RED}{colorama.Style.BRIGHT}failed{colorama.Style.RESET_ALL}'
                )
                job = jobset_utils.get_job(namespace, job_name)
                _raise_job_error(job)
                return
        if timeout != -1 and time.time() - start > timeout:
            logger.error(
                f'{colorama.Style.BRIGHT}'
                f'{colorama.Fore.RED}Job timed out to schedule.'
                f'{colorama.Style.RESET_ALL}. Deleting job'
            )
            jobset_utils.delete_jobset(namespace, job_name)
            raise JobsetError(
                'Job failed to start within '
                f'timeout of {timeout} seconds. '
                f'Increase or disable timeout '
                f'{colorama.Style.BRIGHT}'
                '`konduktor.provision_timeout: -1`'
                f'{colorama.Style.RESET_ALL}'
            )
        time.sleep(POLL_INTERVAL)


def _wait_for_jobset_completion(namespace: str, job_name: str) -> Tuple[bool, str]:
    while True:
        jobsets = jobset_utils.get_jobset(namespace, job_name)
        assert jobsets is not None, (
            f'Jobset {job_name} ' f'not found in namespace {namespace}'
        )
        if jobsets['status']['replicatedJobsStatus'][0]['succeeded']:
            msg = (
                f'task '
                f'{colorama.Fore.CYAN}{colorama.Style.BRIGHT}{job_name}'
                f'{colorama.Style.RESET_ALL} {colorama.Fore.GREEN}'
                f'{colorama.Style.BRIGHT}finished{colorama.Style.RESET_ALL}'
            )
            return True, msg
        elif jobsets['status']['replicatedJobsStatus'][0]['failed']:
            msg = (
                f'task '
                f'{colorama.Fore.CYAN}{colorama.Style.BRIGHT}{job_name}'
                f'{colorama.Style.RESET_ALL} {colorama.Fore.RED}'
                f'{colorama.Style.BRIGHT}failed{colorama.Style.RESET_ALL}'
            )
            return False, msg
        time.sleep(POLL_INTERVAL)


class JobsetBackend(backend.Backend):
    def _sync_file_mounts(
        self,
        all_file_mounts: Optional[Dict[Path, Path]],
        storage_mounts: Optional[Dict[Path, 'storage_lib.Storage']],
    ) -> None:
        """Syncs files/directories to cloud storage before job launch.

        This uploads any local files/dirs to cloud storage so they can be downloaded
        by the pods when they start.
        """
        pass

    def _sync_workdir(self, workdir: str) -> None:
        """Syncs the working directory to cloud storage before job launch."""

        pass

    def _post_execute(self) -> None:
        """
        TODO(asaiacai): add some helpful messages/commands that a user can run
        to inspect the status of their jobset.
        """
        pass

    def _execute(
        self, task: 'konduktor.Task', detach_run: bool = False, dryrun: bool = False
    ) -> Optional[str]:
        """Executes the task on the cluster. By creating a jobset

        Returns:
            Job id if the task is submitted to the cluster, None otherwise.
        """

        # we should consider just building an image with the cloud provider
        # sdks baked in. These can initialize and pull files first before
        # the working container starts.

        # first define the pod spec then create the jobset definition
        pod_spec = pod_utils.create_pod_spec(task)
        context = kubernetes_utils.get_current_kube_config_context_name()
        namespace = kubernetes_utils.get_kube_config_context_namespace(context)
        # TODO(asaiacai): need to set env variables in pod
        jobset_response = jobset_utils.create_jobset(
            namespace,
            task,
            pod_spec['kubernetes']['pod_config'],
            dryrun=dryrun,
        )

        if not dryrun and not detach_run:
            with ux_utils.print_exception_no_traceback():
                with rich_utils.safe_status(
                    ux_utils.spinner_message(
                        'waiting for job to start. ' 'Press Ctrl+C to detach. \n'
                    )
                ):
                    _wait_for_jobset_start(namespace, task.name)
                try:
                    assert jobset_response is not None
                    log_thread = threading.Thread(
                        target=log_utils.tail_logs,
                        args=(jobset_response,),
                        daemon=True,
                    )
                    logger.info('streaming logs...')
                    log_thread.start()
                    is_success, msg = _wait_for_jobset_completion(namespace, task.name)
                    log_thread.join(timeout=2.0)  # give the job sometime to flush logs
                    if not is_success:
                        logger.error(msg)
                    else:
                        logger.info(msg)
                except KeyboardInterrupt:
                    logger.info('detaching from log stream...')
                except Exception as err:
                    logger.error(
                        f'Check if job resources are '
                        f'active/queued with '
                        f'{colorama.Style.BRIGHT}'
                        f'`konduktor status`'
                        f'{colorama.Style.RESET_ALL}'
                    )
                    raise JobsetError(f'error: {err}')
        else:
            logger.info('detaching from run.')
        return task.name
