"""Jobset utils: wraps CRUD operations for jobsets"""

import enum
import json
import tempfile
import time
import typing
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import click
import colorama

if typing.TYPE_CHECKING:
    from datetime import timedelta

import konduktor
from konduktor import kube_client, logging
from konduktor.backends import constants as backend_constants
from konduktor.backends import pod_utils
from konduktor.utils import (
    common_utils,
    kubernetes_utils,
    log_utils,
)

if typing.TYPE_CHECKING:
    pass

logger = logging.get_logger(__name__)

JOBSET_API_GROUP = 'jobset.x-k8s.io'
JOBSET_API_VERSION = 'v1alpha2'
JOBSET_PLURAL = 'jobsets'

# Use shared constants from konduktor.backends.constants
JOBSET_NAME_LABEL = backend_constants.JOB_NAME_LABEL
JOBSET_USERID_LABEL = backend_constants.USERID_LABEL
JOBSET_USER_LABEL = backend_constants.USER_LABEL
JOBSET_ACCELERATOR_LABEL = backend_constants.ACCELERATOR_LABEL
JOBSET_NUM_ACCELERATORS_LABEL = backend_constants.NUM_ACCELERATORS_LABEL
JOBSET_MAX_EXECUTION_TIME_LABEL = backend_constants.MAX_EXECUTION_TIME_LABEL

SECRET_BASENAME_LABEL = backend_constants.SECRET_BASENAME_LABEL

_JOBSET_METADATA_LABELS = {
    'jobset_name_label': JOBSET_NAME_LABEL,
    'jobset_userid_label': JOBSET_USERID_LABEL,
    'jobset_user_label': JOBSET_USER_LABEL,
    'jobset_accelerator_label': JOBSET_ACCELERATOR_LABEL,
    'jobset_num_accelerators_label': JOBSET_NUM_ACCELERATORS_LABEL,
    'jobset_max_execution_time_label': JOBSET_MAX_EXECUTION_TIME_LABEL,
}


class JobNotFoundError(Exception):
    pass


class JobStatus(enum.Enum):
    SUSPENDED = 'SUSPENDED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    PENDING = 'PENDING'


if typing.TYPE_CHECKING:
    import konduktor


def create_jobset(
    namespace: str,
    task: 'konduktor.Task',
    pod_spec: Dict[str, Any],
    dryrun: bool = False,
) -> Optional[Dict[str, Any]]:
    """Creates a jobset based on the task definition and pod spec
    and returns the created jobset spec
    """
    assert task.resources is not None, 'Task resources are undefined'
    accelerator_type = task.resources.get_accelerator_type() or 'None'
    num_accelerators = task.resources.get_accelerator_count() or 0
    labels = task.resources.labels if task.resources.labels else {}
    with tempfile.NamedTemporaryFile() as temp:
        common_utils.fill_template(
            'jobset.yaml.j2',
            {
                'job_name': task.name,
                'user_id': common_utils.user_and_hostname_hash(),
                'num_nodes': task.num_nodes,
                'user': common_utils.get_cleaned_username(),
                'accelerator_type': accelerator_type,
                'num_accelerators': num_accelerators,
                'completions': task.resources.get_completions(),
                'max_restarts': task.resources.get_max_restarts(),
                'max_execution_time': labels.get('maxRunDurationSeconds', None),
                **_JOBSET_METADATA_LABELS,
            },
            temp.name,
        )
        jobset_spec = common_utils.read_yaml(temp.name)
        # Inject JobSet metadata (labels and annotations)
        pod_utils.inject_jobset_metadata(jobset_spec, task)

    # Merge pod spec into JobSet template
    pod_utils.merge_pod_into_jobset_template(jobset_spec, pod_spec)
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        jobset = kube_client.crd_api(context=context).create_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            body=jobset_spec['jobset'],
            dry_run='All' if dryrun else None,
        )
        logger.info(
            f'task {colorama.Fore.CYAN}{colorama.Style.BRIGHT}'
            f'{task.name}{colorama.Style.RESET_ALL} created'
        )
        return jobset
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error creating jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def list_jobset(namespace: str) -> Optional[Dict[str, Any]]:
    """Lists all jobsets in this namespace"""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).list_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error listing jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def get_jobset(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves jobset in this namespace"""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).get_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            name=job_name,
        )
        return response
    except kube_client.api_exception() as err:
        if err.status == 404:
            raise JobNotFoundError(
                f"Jobset '{job_name}' " f"not found in namespace '{namespace}'."
            )
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error getting jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def delete_jobset(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Deletes jobset in this namespace

    Args:
        namespace: Namespace where jobset exists
        job_name: Name of jobset to delete

    Returns:
        Response from delete operation
    """
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).delete_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            name=job_name,
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error deleting jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error deleting jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def stop_jobset(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Stops jobset in this namespace"""
    context = kubernetes_utils.get_current_kube_config_context_name()
    try:
        # First check if the job exists
        get_jobset(namespace, job_name)

        # Apply patch to suspend the jobset and add annotations
        # Time is in UTC but gets converted to local timezone in the konduktor status UI
        patch = {
            'spec': {'suspend': True},
            'metadata': {
                'annotations': {
                    backend_constants.STOP_USERID_LABEL: (
                        common_utils.user_and_hostname_hash()
                    ),
                    backend_constants.STOP_USERNAME_LABEL: (
                        common_utils.get_cleaned_username()
                    ),
                }
            },
        }
        response = kube_client.crd_api(context=context).patch_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            name=job_name,
            body=patch,
        )

        # Also suspend the associated Kueue workload to prevent automatic resumption
        try:
            # Find the workload for this jobset
            workloads = kube_client.crd_api(
                context=context
            ).list_namespaced_custom_object(
                group='kueue.x-k8s.io',
                version='v1beta1',
                namespace=namespace,
                plural='workloads',
            )
            for workload in workloads.get('items', []):
                if workload['metadata']['name'].startswith(f'jobset-{job_name}-'):
                    # Suspend the workload
                    workload_patch = {'spec': {'active': False}}
                    kube_client.crd_api(context=context).patch_namespaced_custom_object(
                        group='kueue.x-k8s.io',
                        version='v1beta1',
                        namespace=namespace,
                        plural='workloads',
                        name=workload['metadata']['name'],
                        body=workload_patch,
                    )
                    break
        except Exception:
            # If workload suspension fails, continue (JobSet suspension still worked)
            pass

        return response
    except kube_client.api_exception() as e:
        if e.status == 404:
            raise JobNotFoundError(f'Job {job_name} not found in namespace {namespace}')
        else:
            raise e


def start_jobset(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Starts jobset in this namespace"""
    context = kubernetes_utils.get_current_kube_config_context_name()
    try:
        # First check if the job exists
        get_jobset(namespace, job_name)

        # Apply patch to resume the jobset and remove suspension annotations
        patch = {
            'spec': {'suspend': False},
            'metadata': {
                'annotations': {
                    backend_constants.STOP_USERID_LABEL: None,
                    backend_constants.STOP_USERNAME_LABEL: None,
                }
            },
        }
        response = kube_client.crd_api(context=context).patch_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            name=job_name,
            body=patch,
        )

        # Also reactivate the associated Kueue workload
        try:
            # Find the workload for this jobset
            workloads = kube_client.crd_api(
                context=context
            ).list_namespaced_custom_object(
                group='kueue.x-k8s.io',
                version='v1beta1',
                namespace=namespace,
                plural='workloads',
            )
            for workload in workloads.get('items', []):
                if workload['metadata']['name'].startswith(f'jobset-{job_name}-'):
                    # Reactivate the workload
                    workload_patch = {'spec': {'active': True}}
                    kube_client.crd_api(context=context).patch_namespaced_custom_object(
                        group='kueue.x-k8s.io',
                        version='v1beta1',
                        namespace=namespace,
                        plural='workloads',
                        name=workload['metadata']['name'],
                        body=workload_patch,
                    )
                    break
        except Exception:
            # If workload reactivation fails, continue (JobSet resumption still worked)
            pass

        return response
    except kube_client.api_exception() as e:
        if e.status == 404:
            raise JobNotFoundError(f'Job {job_name} not found in namespace {namespace}')
        else:
            raise e


def get_job(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Gets a specific job from a jobset by name and worker index

    Args:
        namespace: Namespace where job exists
        job_name: Name of jobset containing the job
        worker_id: Index of the worker job to get (defaults to 0)

    Returns:
        Job object if found
    """
    try:
        # Get the job object using the job name
        # pattern {jobset-name}-workers-0-{worker_id}
        job_name = f'{job_name}-workers-0'
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.batch_api(context=context).read_namespaced_job(
            name=job_name, namespace=namespace
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error getting job: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error getting job: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def _parse_timestamp_filter(timestamp_str: str) -> datetime:
    """Parse timestamp string into datetime object for filtering

    Supported formats:
    - "08/06/25 03:54PM" (full datetime)
    - "08/06/25" (date only)
    - "03:54PM" (time only, uses today's date)
    """

    # Try different formats
    formats = [
        '%m/%d/%y %I:%M%p',  # 08/06/25 03:54PM (full datetime)
        '%m/%d/%y',  # 08/06/25 (date only)
        '%I:%M%p',  # 03:54PM (time only)
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)

            # Handle time-only format (add today's date)
            if fmt == '%I:%M%p':
                today = datetime.now().strftime('%m/%d/%y')
                dt = datetime.strptime(f'{today} {timestamp_str}', '%m/%d/%y %I:%M%p')

            # If no timezone info, assume local timezone and convert to UTC
            if dt.tzinfo is None:
                if fmt in ['%m/%d/%y %I:%M%p', '%I:%M%p']:
                    # For display format, convert from local time to UTC
                    # Get current local timezone offset
                    local_offset = time.timezone if not time.daylight else time.altzone
                    # Convert local time to UTC by adding the offset
                    # (since timezone is negative)
                    dt = dt.replace(tzinfo=timezone.utc) + timedelta(
                        seconds=abs(local_offset)
                    )
                else:
                    dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    raise ValueError(
        f"Unable to parse timestamp '{timestamp_str}'. "
        f"Supported formats: '08/06/25 03:54PM', '08/06/25', '03:54PM'"
    )


def _format_timestamp(timestamp: str) -> str:
    """Format timestamp as MM/DD/YY HH:MMAM/PM in local timezone"""
    # Parse UTC timestamp and convert to local time
    dt_utc = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').replace(
        tzinfo=timezone.utc
    )
    dt_local = dt_utc.astimezone()  # Convert to local timezone
    return dt_local.strftime('%m/%d/%y %I:%M%p')


def _get_job_start_time(job: Dict[str, Any]) -> str:
    for condition in job['status']['conditions']:
        if condition['reason'] == 'ResumeJobs':
            return condition.get('lastTransitionTime', '')
    return '-'


def _get_end_time_from_conditions(job: Dict[str, Any]) -> str:
    """Extract end time from JobSet conditions (Completed or Failed)"""
    conditions = job.get('status', {}).get('conditions', [])
    for condition in conditions:
        # Look for terminal conditions with status=True
        if (
            condition.get('type') in ['Completed', 'Failed']
            and condition.get('status') == 'True'
        ):
            return condition.get('lastTransitionTime', '')
    return '-'


def _get_time_delta(delta: 'timedelta') -> Tuple[str, 'timedelta']:
    total_seconds = int(delta.total_seconds())

    days, remainder = divmod(total_seconds, 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)  # 60 seconds in a minute

    days_str = f'{days} day{"s" if days != 1 else ""}, ' if days > 0 else ''
    hours_str = f'{hours} hr{"s" if hours != 1 else ""}, ' if hours > 0 else ''
    minutes_str = (
        f'{minutes} min{"s" if minutes != 1 else ""}'
        if minutes > 0 and days == 0
        else ''
    )

    seconds_str = (
        f'{seconds} sec{"s" if seconds != 1 else ""}'
        if seconds > 0 and days == 0 and hours == 0 and minutes == 0
        else ''
    )

    result = f'{days_str}{hours_str}{minutes_str}{seconds_str}'
    return result if result else '<1 minute', delta


def _get_job_length(start_time: str, end_time: str) -> str:
    if start_time == '-' or end_time == '-':
        return '-'
    else:
        start = datetime.strptime(start_time, '%m/%d/%y %I:%M%p')
        end = datetime.strptime(end_time, '%m/%d/%y %I:%M%p')
        delta, _ = _get_time_delta(end - start)
        return delta


def show_status_table(
    namespace: str,
    all_users: bool,
    limit: Optional[int] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
):
    """Compute cluster table values and display with optional filtering and pagination.

    Args:
        namespace: Kubernetes namespace to search
        all_users: Whether to show jobs from all users
        limit: Maximum number of jobs to display
        after: Show jobs created after this timestamp
        before: Show jobs created before this timestamp
    """
    # TODO(zhwu): Update the information for autostop clusters.

    def _get_status_string_colorized(
        status: Dict[str, Any], job: Dict[str, Any]
    ) -> str:
        # Handle case where status might be empty or missing
        if not status:
            return (
                f'{colorama.Fore.YELLOW}'
                f'{JobStatus.PENDING.name}{colorama.Style.RESET_ALL}'
            )

        terminalState = status.get('terminalState', None)
        if terminalState and terminalState.upper() == JobStatus.COMPLETED.name.upper():
            return (
                f'{colorama.Fore.GREEN}'
                f'{JobStatus.COMPLETED.name}{colorama.Style.RESET_ALL}'
            )
        elif terminalState and terminalState.upper() == JobStatus.FAILED.name.upper():
            return (
                f'{colorama.Fore.RED}'
                f'{JobStatus.FAILED.name}{colorama.Style.RESET_ALL}'
            )
        elif status.get('replicatedJobsStatus', [{}])[0].get('ready', False):
            return (
                f'{colorama.Fore.CYAN}'
                f'{JobStatus.ACTIVE.name}{colorama.Style.RESET_ALL}'
            )
        elif status.get('replicatedJobsStatus', [{}])[0].get('suspended', False):
            # Check if this was manually suspended
            annotations = job.get('metadata', {}).get('annotations', {})
            if annotations.get(backend_constants.STOP_USERID_LABEL):
                username = annotations.get(
                    backend_constants.STOP_USERNAME_LABEL, 'unknown'
                )
                return (
                    f'{colorama.Fore.BLUE}'
                    f'{JobStatus.SUSPENDED.name} '
                    f'(by {username}){colorama.Style.RESET_ALL}'
                )
            else:
                return (
                    f'{colorama.Fore.BLUE}'
                    f'{JobStatus.SUSPENDED.name} (by system){colorama.Style.RESET_ALL}'
                )
        else:
            return (
                f'{colorama.Fore.YELLOW}'
                f'{JobStatus.PENDING.name}{colorama.Style.RESET_ALL}'
            )

    def _get_resources(job: Dict[str, Any]) -> str:
        num_pods = int(
            job['spec']['replicatedJobs'][0]['template']['spec']['parallelism']
        )  # noqa: E501
        resources = job['spec']['replicatedJobs'][0]['template']['spec']['template'][
            'spec'
        ]['containers'][0]['resources']['limits']  # noqa: E501
        cpu, memory = resources['cpu'], resources['memory']
        accelerator = job['metadata']['labels'].get(JOBSET_ACCELERATOR_LABEL, None)
        num_accelerators = job['metadata']['labels'].get(
            JOBSET_NUM_ACCELERATORS_LABEL, None
        )
        if accelerator:
            if num_accelerators:
                accelerator_with_count = f'{accelerator}:{num_accelerators}'
            else:
                accelerator_with_count = accelerator
            return f'{num_pods}x({cpu}CPU, {memory}MEM, {accelerator_with_count})'
        else:
            return f'{num_pods}x({cpu}CPU, {memory}MEM)'

    if all_users:
        columns = [
            'NAME',
            'USER',
            'STATUS',
            'RESOURCES',
            'SUBMITTED',
            'START TIME',
            'END TIME',
            'DURATION',
        ]
    else:
        columns = [
            'NAME',
            'STATUS',
            'RESOURCES',
            'SUBMITTED',
            'START TIME',
            'END TIME',
            'DURATION',
        ]
    job_table = log_utils.create_table(columns)
    job_specs = list_jobset(namespace)
    assert job_specs is not None, 'Retrieving jobs failed'

    # Parse timestamp filters if provided
    after_dt = None
    before_dt = None
    if after:
        try:
            after_dt = _parse_timestamp_filter(after)
        except ValueError as e:
            click.secho(f'Error parsing --after timestamp: {e}', fg='red', err=True)
            return
    if before:
        try:
            before_dt = _parse_timestamp_filter(before)
        except ValueError as e:
            click.secho(f'Error parsing --before timestamp: {e}', fg='red', err=True)
            return

    rows = []
    for job in job_specs['items']:
        # Apply timestamp filtering
        if after_dt or before_dt:
            job_creation_time = datetime.strptime(
                job['metadata']['creationTimestamp'], '%Y-%m-%dT%H:%M:%SZ'
            ).replace(tzinfo=timezone.utc)

            if after_dt and job_creation_time <= after_dt:
                continue
            if before_dt and job_creation_time >= before_dt:
                continue
        # Get start time
        start_time = _get_job_start_time(job)
        if start_time != '-':
            start_time = _format_timestamp(start_time)

        # Get submitted time (how long ago)
        time_delta = datetime.now(timezone.utc) - datetime.strptime(
            job['metadata']['creationTimestamp'], '%Y-%m-%dT%H:%M:%SZ'
        ).replace(tzinfo=timezone.utc)
        submitted_time, _ = _get_time_delta(time_delta)

        # Get end time (from JobSet conditions)
        end_time = _get_end_time_from_conditions(job)
        if end_time != '-':
            end_time = _format_timestamp(end_time)

        job_length = _get_job_length(start_time, end_time)

        if all_users:
            rows.append(
                [
                    job['metadata']['name'],
                    job['metadata']['labels'][JOBSET_USERID_LABEL],
                    _get_status_string_colorized(job.get('status', {}), job),
                    _get_resources(job),
                    submitted_time,
                    start_time,
                    end_time,
                    job_length,
                    job['metadata']['creationTimestamp'],
                ]
            )
        elif (
            not all_users
            and job['metadata']['labels'][JOBSET_USER_LABEL]
            == common_utils.get_cleaned_username()
        ):
            rows.append(
                [
                    job['metadata']['name'],
                    _get_status_string_colorized(job.get('status', {}), job),
                    _get_resources(job),
                    submitted_time,
                    start_time,
                    end_time,
                    job_length,
                    job['metadata']['creationTimestamp'],
                ]
            )

    # Sort by creation timestamp (most recent first)
    rows = sorted(rows, key=lambda x: x[-1], reverse=True)

    # Apply limit if specified
    if limit and limit > 0:
        rows = rows[:limit]

    # Show pagination info if applicable
    total_jobs = len(job_specs['items'])
    filtered_jobs = len(rows)

    if limit or after or before:
        filter_info = []
        if after:
            filter_info.append(f'after {after}')
        if before:
            filter_info.append(f'before {before}')
        if limit:
            filter_info.append(f'limit {limit}')

        filter_str = ', '.join(filter_info)
        click.secho(f'Showing {filtered_jobs} jobs ({filter_str})', fg='yellow')
        if total_jobs != filtered_jobs:
            click.secho(f'Total jobs in namespace: {total_jobs}', fg='yellow')

    # Remove the sorting timestamp and add rows to table
    for row in rows:
        job_table.add_row(row[:-1])
    print(job_table)
