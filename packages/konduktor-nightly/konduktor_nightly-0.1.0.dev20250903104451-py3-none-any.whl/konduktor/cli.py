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

"""The 'konduktor' command line tool.

Example usage:

  # See available commands.
  >> konduktor

  # Run a task, described in a yaml file.
  >> konduktor launch task.yaml

  # Show the list of scheduled jobs
  >> konduktor status

  # Tear down a specific job.
  >> konduktor down cluster_name

  # Tear down all scheduled jobs
  >> konduktor down -a

NOTE: the order of command definitions in this file corresponds to how they are
listed in "konduktor --help".  Take care to put logically connected commands close to
each other.
"""

import fnmatch
import os
import pathlib
import shlex
from base64 import b64encode
from typing import Any, Dict, List, Optional, Tuple

import click
import colorama
import dotenv
import prettytable
import yaml  # type: ignore
from rich.progress import track

import konduktor
from konduktor import check as konduktor_check
from konduktor import logging
from konduktor.backends import constants as backend_constants
from konduktor.backends import deployment_utils, jobset_utils
from konduktor.utils import (
    common_utils,
    kubernetes_utils,
    log_utils,
    ux_utils,
)

_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

logger = logging.get_logger(__name__)


def _parse_env_var(env_var: str) -> Tuple[str, str]:
    """Parse env vars into a (KEY, VAL) pair."""
    if '=' not in env_var:
        value = os.environ.get(env_var)
        if value is None:
            raise click.UsageError(f'{env_var} is not set in local environment.')
        return (env_var, value)
    ret = tuple(env_var.split('=', 1))
    if len(ret) != 2:
        raise click.UsageError(
            f'Invalid env var: {env_var}. Must be in the form of KEY=VALUE'
        )
    return ret[0], ret[1]


def _merge_env_vars(
    env_dict: Optional[Dict[str, str]], env_list: List[Tuple[str, str]]
) -> List[Tuple[str, str]]:
    """Merges all values from env_list into env_dict."""
    if not env_dict:
        return env_list
    for key, value in env_list:
        env_dict[key] = value
    return list(env_dict.items())


def _make_task_with_overrides(
    entrypoint: Tuple[str, ...],
    *,
    entrypoint_name: str = 'konduktor.Task',
    name: Optional[str] = None,
    workdir: Optional[str] = None,
    cloud: Optional[str] = None,
    gpus: Optional[str] = None,
    cpus: Optional[str] = None,
    memory: Optional[str] = None,
    instance_type: Optional[str] = None,
    num_nodes: Optional[int] = None,
    max_restarts: Optional[int] = None,
    completions: Optional[int] = None,
    image_id: Optional[str] = None,
    disk_size: Optional[int] = None,
    env: Optional[List[Tuple[str, str]]] = None,
    field_to_ignore: Optional[List[str]] = None,
    min_replicas: Optional[int] = None,
    max_replicas: Optional[int] = None,
    ports: Optional[int] = None,
    probe: Optional[str] = None,
) -> konduktor.Task:
    """Creates a task from an entrypoint with overrides.

    Returns:
        konduktor.Task
    """
    entrypoint = ' '.join(entrypoint)
    is_yaml, _ = _check_yaml(entrypoint)
    entrypoint: Optional[str]
    if is_yaml:
        # Treat entrypoint as a yaml.
        click.secho(f'{entrypoint_name} from YAML spec: ', fg='yellow', nl=False)
        click.secho(entrypoint, bold=True)
    else:
        if entrypoint is not None and len(entrypoint) == 0:
            raise ValueError(
                'no entrypoint specified, run with \n' '`konduktor launch task.yaml'
            )
        raise ValueError(f'{entrypoint} is not a valid YAML spec,')

    override_params = _parse_override_params(
        gpus=gpus,
        cpus=cpus,
        memory=memory,
        image_id=image_id,
        disk_size=disk_size,
    )

    serving_override_params = _parse_serving_override_params(
        num_nodes=num_nodes,
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        ports=ports,
        probe=probe,
    )

    if field_to_ignore is not None:
        _pop_and_ignore_fields_in_override_params(override_params, field_to_ignore)

    assert entrypoint is not None
    task_configs = common_utils.read_yaml_all(entrypoint)
    assert len(task_configs) == 1, 'Only single tasks are supported'
    task = konduktor.Task.from_yaml_config(task_configs[0], env)
    # Override.
    if workdir is not None:
        task.workdir = workdir

    task.set_resources_override(override_params)
    if task.serving:
        task.set_serving_override(serving_override_params)

    if max_restarts is not None:
        assert task.resources is not None
        task.resources.job_config['max_restarts'] = max_restarts
    if completions is not None:
        assert task.resources is not None
        task.resources.job_config['completions'] = completions
    if num_nodes is not None:
        task.num_nodes = num_nodes
    if name is not None:
        task.name = name
    return task


_TASK_OPTIONS = [
    click.option(
        '--workdir',
        required=False,
        type=click.Path(exists=True, file_okay=False),
        help=(
            'If specified, sync this dir to the remote working directory, '
            'where the task will be invoked. '
            'Overrides the "workdir" config in the YAML if both are supplied.'
        ),
    ),
    click.option(
        '--cloud',
        required=False,
        type=str,
        help=(
            'The cloud to use. If specified, overrides the "resources.cloud" '
            'config. Passing "none" resets the config. [defunct] currently '
            'only supports a single cloud'
        ),
    ),
    click.option(
        '--num-nodes',
        required=False,
        type=int,
        help=(
            'Number of nodes to execute the task on. '
            'Overrides the "num_nodes" config in the YAML if both are '
            'supplied.'
        ),
    ),
    click.option(
        '--max-restarts',
        required=False,
        type=int,
        help=(
            'Maximum number of jobset restarts allowed. Overrides YAML.'
            'Overrides the "max_restarts" config in the YAML if both are '
            'supplied.'
        ),
    ),
    click.option(
        '--completions',
        required=False,
        type=int,
        help=(
            'Number of successful completions required. Overrides YAML.'
            'Overrides the "completions" config in the YAML if both are '
            'supplied.'
        ),
    ),
    click.option(
        '--cpus',
        default=None,
        type=str,
        required=False,
        help=(
            'Number of vCPUs each instance must have (e.g., '
            '``--cpus=4`` (exactly 4) or ``--cpus=4+`` (at least 4)). '
            'This is used to automatically select the instance type.'
        ),
    ),
    click.option(
        '--memory',
        default=None,
        type=str,
        required=False,
        help=(
            'Amount of memory each instance must have in GB (e.g., '
            '``--memory=16`` (exactly 16GB), ``--memory=16+`` (at least 16GB))'
        ),
    ),
    click.option(
        '--disk-size',
        default=None,
        type=int,
        required=False,
        help=('OS disk size in GBs.'),
    ),
    click.option(
        '--image-id',
        required=False,
        default=None,
        help=(
            'Custom image id for launching the instances. '
            'Passing "none" resets the config.'
        ),
    ),
    click.option(
        '--env-file',
        required=False,
        type=dotenv.dotenv_values,
        help="""\
        Path to a dotenv file with environment variables to set on the remote
        node.

        If any values from ``--env-file`` conflict with values set by
        ``--env``, the ``--env`` value will be preferred.""",
    ),
    click.option(
        '--env',
        required=False,
        type=_parse_env_var,
        multiple=True,
        help="""\
        Environment variable to set on the remote node.
        It can be specified multiple times.
        Examples:

        \b
        1. ``--env MY_ENV=1``: set ``$MY_ENV`` on the cluster to be 1.

        2. ``--env MY_ENV2=$HOME``: set ``$MY_ENV2`` on the cluster to be the
        same value of ``$HOME`` in the local environment where the CLI command
        is run.

        3. ``--env MY_ENV3``: set ``$MY_ENV3`` on the cluster to be the
        same value of ``$MY_ENV3`` in the local environment.""",
    ),
]
_TASK_OPTIONS_WITH_NAME = [
    click.option(
        '--name',
        '-n',
        required=False,
        type=str,
        help=(
            'Task name. Overrides the "name" '
            'config in the YAML if both are supplied.'
        ),
    ),
] + _TASK_OPTIONS
_EXTRA_RESOURCES_OPTIONS = [
    click.option(
        '--gpus',
        required=False,
        type=str,
        help=(
            'Type and number of GPUs to use. Example values: '
            '"V100:8", "V100" (short for a count of 1)'
            'If a new cluster is being launched by this command, this is the '
            'resources to provision. If an existing cluster is being reused, this'
            " is seen as the task demand, which must fit the cluster's total "
            'resources and is used for scheduling the task. '
            'Overrides the "accelerators" '
            'config in the YAML if both are supplied. '
            'Passing "none" resets the config.'
        ),
    ),
]
_EXTRA_SERVING_OPTIONS = [
    click.option(
        '--min-replicas',
        required=False,
        type=int,
        help=(
            'Minimum number of replicas to run for the service. '
            'Overrides the "min_replicas" field in the YAML if both '
            'are supplied.'
        ),
    ),
    click.option(
        '--max-replicas',
        required=False,
        type=int,
        help=(
            'Maximum number of replicas to allow for the service. '
            'Overrides the "max_replicas" field in the YAML if both '
            'are supplied.'
        ),
    ),
    click.option(
        '--ports',
        required=False,
        type=int,
        help=(
            'The container port on which your service will listen for HTTP '
            'traffic. Overrides the "ports" field in the YAML if both '
            'are supplied.'
        ),
    ),
    click.option(
        '--probe',
        required=False,
        type=str,
        help=(
            'The HTTP path to use for health checks (liveness, readiness, and '
            'startup probes). Overrides the "probe" field in the YAML '
            'if both are supplied. The service should respond with HTTP 200 on '
            'this path when healthy.'
        ),
    ),
]


def _get_click_major_version():
    return int(click.__version__.split('.', maxsplit=1)[0])


_RELOAD_ZSH_CMD = 'source ~/.zshrc'
_RELOAD_BASH_CMD = 'source ~/.bashrc'


def _add_click_options(options: List[click.Option]):
    """A decorator for adding a list of click option decorators."""

    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def _parse_override_params(
    gpus: Optional[str] = None,
    cpus: Optional[str] = None,
    memory: Optional[str] = None,
    image_id: Optional[str] = None,
    disk_size: Optional[int] = None,
) -> Dict[str, Any]:
    """Parses the override parameters into a dictionary."""
    override_params: Dict[str, Any] = {}
    if gpus is not None:
        if gpus.lower() == 'none':
            override_params['accelerators'] = None
        else:
            override_params['accelerators'] = gpus
    if cpus is not None:
        if cpus.lower() == 'none':
            override_params['cpus'] = None
        else:
            override_params['cpus'] = cpus
    if memory is not None:
        if memory.lower() == 'none':
            override_params['memory'] = None
        else:
            override_params['memory'] = memory
    if image_id is not None:
        if image_id.lower() == 'none':
            override_params['image_id'] = None
        else:
            override_params['image_id'] = image_id
    if disk_size is not None:
        override_params['disk_size'] = disk_size
    return override_params


def _parse_serving_override_params(
    num_nodes: Optional[int] = None,
    min_replicas: Optional[int] = None,
    max_replicas: Optional[int] = None,
    ports: Optional[int] = None,
    probe: Optional[str] = None,
) -> Dict[str, Any]:
    """Parses the relevant serving override parameters into a dictionary."""
    override_params: Dict[str, Any] = {}
    if num_nodes is not None:
        override_params['num_nodes'] = num_nodes
    if min_replicas is not None:
        override_params['min_replicas'] = min_replicas
    if max_replicas is not None:
        override_params['max_replicas'] = max_replicas
    if ports is not None:
        override_params['ports'] = ports
    if probe is not None:
        override_params['probe'] = probe

    return override_params


def _launch_with_confirm(
    task: konduktor.Task,
    *,
    dryrun: bool,
    detach_run: bool,
    no_confirm: bool,
    serving: bool,
):
    """Launch a cluster with a Task."""

    confirm_shown = False
    if not no_confirm:
        # Prompt if (1) --cluster is None, or (2) cluster doesn't exist, or (3)
        # it exists but is STOPPED.
        if serving:
            prompt = (
                f'Launching a new deployment {colorama.Style.BRIGHT}'
                f'{colorama.Fore.GREEN}{task.name}{colorama.Style.RESET_ALL}. '
                'Proceed?'
            )
        else:
            prompt = (
                f'Launching a new job {colorama.Style.BRIGHT}'
                f'{colorama.Fore.GREEN}{task.name}{colorama.Style.RESET_ALL}. '
                'Proceed?'
            )
        if prompt is not None:
            confirm_shown = True
            click.confirm(prompt, default=True, abort=True, show_default=True)

    if not confirm_shown:
        if serving:
            click.secho(f'Creating deployment {task.name}...', fg='yellow')
        else:
            click.secho(f'Running task {task.name}...', fg='yellow')
    return konduktor.launch(
        task,
        dryrun=dryrun,
        detach_run=detach_run,
    )


def _check_yaml(entrypoint: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Checks if entrypoint is a readable YAML file.

    Args:
        entrypoint: Path to a YAML file.
    """
    is_yaml = True
    config: Optional[List[Dict[str, Any]]] = None
    result = None
    shell_splits = shlex.split(entrypoint)
    yaml_file_provided = len(shell_splits) == 1 and (
        shell_splits[0].endswith('yaml') or shell_splits[0].endswith('.yml')
    )
    invalid_reason = ''
    try:
        with open(entrypoint, 'r', encoding='utf-8') as f:
            try:
                config = list(yaml.safe_load_all(f))
                if config:
                    result = config[0]
                else:
                    result = {}
                if isinstance(result, str):
                    # 'konduktor exec cluster ./my_script.sh'
                    is_yaml = False
            except yaml.YAMLError as e:
                if yaml_file_provided:
                    logger.debug(e)
                    detailed_error = f'\nYAML Error: {e}\n'
                    invalid_reason = (
                        'contains an invalid configuration. '
                        'Please check syntax.\n'
                        f'{detailed_error}'
                    )
                is_yaml = False

    except OSError:
        if yaml_file_provided:
            entry_point_path = os.path.expanduser(entrypoint)
            if not os.path.exists(entry_point_path):
                invalid_reason = (
                    'does not exist. Please check if the path' ' is correct.'
                )
            elif not os.path.isfile(entry_point_path):
                invalid_reason = (
                    'is not a file. Please check if the path' ' is correct.'
                )
            else:
                invalid_reason = (
                    'yaml.safe_load() failed. Please check if the' ' path is correct.'
                )
        is_yaml = False
    if not is_yaml:
        if yaml_file_provided:
            click.confirm(
                f'{entrypoint!r} looks like a yaml path but {invalid_reason}\n'
                'It will be treated as a command to be run remotely. Continue?',
                abort=True,
            )
    return is_yaml, result


def _pop_and_ignore_fields_in_override_params(
    params: Dict[str, Any], field_to_ignore: List[str]
) -> None:
    """Pops and ignores fields in override params.

    Args:
        params: Override params.
        field_to_ignore: Fields to ignore.

    Returns:
        Override params with fields ignored.
    """
    if field_to_ignore is not None:
        for field in field_to_ignore:
            field_value = params.pop(field, None)
            if field_value is not None:
                click.secho(
                    f'Override param {field}={field_value} is ignored.', fg='yellow'
                )


class _NaturalOrderGroup(click.Group):
    """Lists commands in the order defined in this script.

    Reference: https://github.com/pallets/click/issues/513
    """

    def list_commands(self, ctx):
        return self.commands.keys()

    def invoke(self, ctx):
        return super().invoke(ctx)


class _DocumentedCodeCommand(click.Command):
    """Corrects help strings for documented commands such that --help displays
    properly and code blocks are rendered in the official web documentation.
    """

    def get_help(self, ctx):
        help_str = ctx.command.help
        ctx.command.help = help_str.replace('.. code-block:: bash\n', '\b')
        return super().get_help(ctx)


@click.group(cls=_NaturalOrderGroup, context_settings=_CONTEXT_SETTINGS)
@click.version_option(konduktor.__version__, '--version', '-v', prog_name='konduktor')
@click.version_option(
    konduktor.__commit__,
    '--commit',
    '-c',
    prog_name='konduktor',
    message='%(prog)s, commit %(version)s',
    help='Show the commit hash and exit',
)
def cli():
    pass


@cli.command()
@click.option(
    '--all-users',
    '-u',
    default=False,
    is_flag=True,
    required=False,
    help='Show all clusters, including those not owned by the ' 'current user.',
)
@click.option(
    '--limit',
    '-l',
    default=None,
    type=int,
    help='Maximum number of jobs to display (e.g., --limit 100)',
)
@click.option(
    '--after',
    default=None,
    type=str,
    help=(
        'Show jobs created after this timestamp '
        '(e.g., --after "08/06/25 03:54PM", --after "08/06/25", --after "03:54PM")'
    ),
)
@click.option(
    '--before',
    default=None,
    type=str,
    help=(
        'Show jobs created before this timestamp '
        '(e.g., --before "08/06/25 03:54PM", --before "08/06/25", --before "03:54PM")'
    ),
)
# pylint: disable=redefined-builtin
def status(
    all_users: bool, limit: Optional[int], after: Optional[str], before: Optional[str]
):
    # NOTE(dev): Keep the docstring consistent between the Python API and CLI.
    """Shows list of all the jobs with optional filtering and pagination

    Args:
        all_users (bool): whether to show all jobs for all users
        limit (Optional[int]): maximum number of jobs to display
        after (Optional[str]): show jobs created after this timestamp
        before (Optional[str]): show jobs created before this timestamp

    Examples:
        konduktor status --limit 10
        konduktor status --before "08/06/25 03:53PM"
        konduktor status --all-users --limit 10 --after "08/06/25 03:53PM"

    Note:
        When using --before or --after timestamps, passing in "08/06/25" is
        equivalent to passing in "08/06/25 00:00".
        When using --before or --after timestamps, passing in "03:53PM" is
        equivalent to passing in "03:53:00PM".
        Timestamps shown in "konduktor startus" are truncated and are in the
        local timezone. ex. "03:53:55PM" --> "03:53PM"
        and would show up in --after "03:53PM" but not in --before "03:53PM"
        despite status showing as "03:53PM".
    """
    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    user = common_utils.user_and_hostname_hash() if not all_users else 'All'
    click.secho(f'User: {user}', fg='green', bold=True)
    click.secho('Jobs', fg='cyan', bold=True)
    jobset_utils.show_status_table(
        namespace, all_users=all_users, limit=limit, after=after, before=before
    )


@cli.command()
@click.option(
    '--status',
    is_flag=True,
    default=False,
    help=(
        'If specified, do not show logs but exit with a status code for the '
        "job's status: 0 for succeeded, or 1 for all other statuses."
    ),
)
@click.option(
    '--follow/--no-follow',
    is_flag=True,
    default=True,
    help=(
        'Follow the logs of a job. '
        'If --no-follow is specified, print the log so far and exit. '
        '[default: --follow]'
    ),
)
@click.option(
    '--num-lines',
    '--num_lines' '-n',
    default=-1,
    type=int,
    help=(
        'The number of lines to display from the end of the log file. '
        'Default is -1 (no limit).'
    ),
)
@click.option(
    '--node-rank',
    '--node_rank',
    '-N',
    default=0,
    type=int,
    help='The node rank to tail logs from.',
)
@click.argument('job_id', type=str, nargs=1)
# TODO(zhwu): support logs by job name
def logs(
    status: bool,
    job_id: str,
    follow: bool,
    num_lines: int,
    node_rank: int,
):
    # NOTE(dev): Keep the docstring consistent between the Python API and CLI.
    """Retrieve/tail the log of a job."""
    if status:
        raise click.UsageError('`--status` is being deprecated)')

    # Check if the job exists
    if not job_id:
        raise click.UsageError('Please provide a job ID.')

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)

    # Verify the job exists before attempting to tail logs
    # TODO(asaiacai): unify the 404 logic under jobset_utils
    try:
        _ = jobset_utils.get_jobset(namespace, job_id)
    except jobset_utils.JobNotFoundError:
        click.secho(
            f"Job '{job_id}' not found in namespace '{namespace}'. "
            f'Job may have been `konduktor down`. '
            f'Check your jobs with '
            f'{colorama.Style.BRIGHT}`konduktor status`'
            f'{colorama.Style.RESET_ALL}.',
            fg='yellow',
        )

    log_utils.tail_logs(
        job_id,
        worker_id=node_rank,
        follow=follow,
        num_logs=num_lines,
    )


@cli.command(cls=_DocumentedCodeCommand)
@click.argument(
    'entrypoint',
    required=False,
    type=str,
    nargs=-1,
)
@click.option(
    '--dryrun',
    default=False,
    is_flag=True,
    help='If True, do not actually run the job.',
)
@click.option(
    '--detach-run',
    '-d',
    default=False,
    is_flag=True,
    help=(
        'If True, as soon as a job is submitted, return from this call '
        'and do not stream execution logs.'
    ),
)
@_add_click_options(_TASK_OPTIONS_WITH_NAME + _EXTRA_RESOURCES_OPTIONS)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    default=False,
    required=False,
    # Disabling quote check here, as there seems to be a bug in pylint,
    # which incorrectly recognizes the help string as a docstring.
    # pylint: disable=bad-docstring-quotes
    help='Skip confirmation prompt.',
)
def launch(
    entrypoint: Tuple[str, ...],
    dryrun: bool,
    detach_run: bool,
    name: Optional[str],
    workdir: Optional[str],
    cloud: Optional[str],
    gpus: Optional[str],
    cpus: Optional[str],
    memory: Optional[str],
    num_nodes: Optional[int],
    max_restarts: Optional[int],
    completions: Optional[int],
    image_id: Optional[str],
    env_file: Optional[Dict[str, str]],
    env: List[Tuple[str, str]],
    disk_size: Optional[int],
    yes: bool,
):
    """Launch a task.

    If ENTRYPOINT points to a valid YAML file, it is read in as the task
    specification. Otherwise, it is interpreted as a bash command.
    """
    # NOTE(dev): Keep the docstring consistent between the Python API and CLI.
    env = _merge_env_vars(env_file, env)

    task = _make_task_with_overrides(
        entrypoint=entrypoint,
        name=name,
        workdir=workdir,
        cloud=cloud,
        gpus=gpus,
        cpus=cpus,
        memory=memory,
        num_nodes=num_nodes,
        max_restarts=max_restarts,
        completions=completions,
        image_id=image_id,
        env=env,
        disk_size=disk_size,
        # serving stuff
        min_replicas=None,
        max_replicas=None,
        ports=None,
        probe=None,
    )

    click.secho(
        f'Considered resources ({task.num_nodes} nodes):', fg='green', bold=True
    )
    table_kwargs = {
        'hrules': prettytable.FRAME,
        'vrules': prettytable.NONE,
        'border': True,
    }
    headers = ['CPUs', 'Mem (GB)', 'GPUs']
    table = log_utils.create_table(headers, **table_kwargs)
    assert task.resources is not None
    table.add_row(
        [task.resources.cpus, task.resources.memory, task.resources.accelerators]
    )
    print(table)

    if task.serving:
        raise click.UsageError(
            'Serving information detected. Use '
            '`konduktor serve launch` instead for serving.'
        )
    try:
        _launch_with_confirm(
            task,
            dryrun=dryrun,
            detach_run=detach_run,
            no_confirm=yes,
            serving=bool(task.serving),
        )
    except KeyboardInterrupt:
        click.secho(
            f'Detaching... manage your job {task.name} with the following commands:',
            fg='yellow',
            bold=True,
        )

    click.secho(
        ux_utils.command_hint_messages(ux_utils.CommandHintType.JOB, task.name),
        fg='green',
        bold=True,
    )


@cli.command(cls=_DocumentedCodeCommand)
@click.argument(
    'jobs',
    nargs=-1,
    required=False,
)
@click.option('--all', '-a', default=None, is_flag=True, help='Tear down all jobs.')
@click.option(
    '--all-users',
    '--all_users',
    default=False,
    is_flag=True,
    help='Include other users for teardown',
)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    default=False,
    required=False,
    help='Skip confirmation prompt.',
)
def down(
    jobs: List[str],
    all: Optional[bool],
    all_users: Optional[bool],
    yes: bool,
):
    # NOTE(dev): Keep the docstring consistent between the Python API and CLI.
    """Tear down job(s).

    JOB is the name of the job to tear down.  If both
    JOB and ``--all`` are supplied, the latter takes precedence.

    Tearing down a job will delete all associated containers (all billing
    stops), and any data on the containers disks will be lost.  Accelerators
    (e.g., GPUs) that are part of the job will be deleted too.

    Wildcard patterns are supported using * characters.
    Examples: "test-*" matches all jobs starting with "test-",
    "*-gpu" matches all jobs ending with "-gpu".

    Examples:

    .. code-block:: bash

      # Tear down a specific job.
      konduktor down cluster_name
      \b
      # Tear down multiple jobs.
      konduktor down job1 job2
      \b
      # Tear down all jobs matching a pattern.
      konduktor down "test-*"
      \b
      # Tear down all of this users jobs.
      konduktor down -a
      konduktor down --all

      # Tear down all jobs across all users
      konduktor down --all --all-users

    """

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    jobs_response = jobset_utils.list_jobset(namespace)
    assert jobs_response
    jobs_specs = [
        job
        for job in jobs_response['items']
        if (
            job['metadata']['labels'][jobset_utils.JOBSET_USERID_LABEL]
            == common_utils.user_and_hostname_hash()
            and not all_users
        )
    ]

    if all:
        assert jobs_specs is not None, f'No jobs found in namespace {namespace}'
        assert len(jobs_specs) > 0, f'No jobs found in namespace {namespace}'
        jobs = [job['metadata']['name'] for job in jobs_specs]
    elif jobs:
        # Get all available jobs to match against patterns
        if len(jobs_specs) == 0:
            raise click.ClickException(f'No jobs found in namespace {namespace}')

        all_job_names = [job['metadata']['name'] for job in jobs_specs]
        matched_jobs = []

        for job_pattern in jobs:
            # Use fnmatch for both wildcard and exact pattern matching
            pattern_matches = fnmatch.filter(all_job_names, job_pattern)
            if not pattern_matches:
                click.secho(
                    f'Warning: No jobs found matching pattern "{job_pattern}"',
                    fg='yellow',
                    err=True,
                )
            matched_jobs.extend(pattern_matches)

        # Remove duplicates while preserving order
        seen = set()
        jobs = []
        for job in matched_jobs:
            if job not in seen:
                seen.add(job)
                jobs.append(job)

        if not jobs:
            raise click.ClickException(
                f'No matching jobs found check status with '
                f'{colorama.Style.BRIGHT}konduktor status{colorama.Style.RESET_ALL}'
            )
    else:
        raise click.ClickException(
            'No jobs specified. Use --all to tear down '
            'all jobs or specify job names/patterns.'
        )

    if not yes:
        # Prompt if (1) --cluster is None, or (2) cluster doesn't exist, or (3)
        # it exists but is STOPPED.
        prompt = (
            f'Tearing down job(s) {colorama.Style.BRIGHT} '
            f'{colorama.Fore.GREEN}{jobs}{colorama.Style.RESET_ALL}. '
            'Proceed?'
        )
        if prompt is not None:
            click.confirm(prompt, default=True, abort=True, show_default=True)

    for job in track(jobs, description='Tearing down job(s)...'):
        jobset_utils.delete_jobset(namespace, job)


@cli.command(cls=_DocumentedCodeCommand)
@click.argument(
    'jobs',
    nargs=-1,
    required=False,
)
@click.option('--all', '-a', default=None, is_flag=True, help='Suspend all jobs.')
@click.option(
    '--all-users',
    '--all_users',
    default=False,
    is_flag=True,
    help='Include other users for suspension',
)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    default=False,
    required=False,
    help='Skip confirmation prompt.',
)
def stop(
    jobs: List[str],
    all: Optional[bool],
    all_users: Optional[bool],
    yes: bool,
):
    """Suspend job(s) (manual/user-initiated).

    JOB is the name of the job to suspend. If both
    JOB and ``--all`` are supplied, the latter takes precedence.

    Suspending a job will pause execution and mark the job as SUSPENDED (by user).
    The job can be resumed later with `konduktor start`.

    If a job is suspended by the system (e.g., due to queueing),
    it will show as SUSPENDED (by system).

    Wildcard patterns are supported using * characters.
    Examples: "my_job-*" matches all jobs starting with "my_job-",
    "*-gpu" matches all jobs ending with "-gpu".

    Examples:

    .. code-block:: bash

      # Suspend a specific job.
      konduktor stop my_job
      \b
      # Suspend multiple jobs.
      konduktor stop my_job1 my_job2
      \b
      # Suspend all jobs matching a pattern.
      konduktor stop "my_job-*"
      \b
      # Suspend all of this users jobs.
      konduktor stop -a
      konduktor stop --all

      # Suspend all jobs across all users
      konduktor stop --all --all-users

    """

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    jobs_response = jobset_utils.list_jobset(namespace)
    assert jobs_response
    jobs_specs = [
        job
        for job in jobs_response['items']
        if (
            job['metadata']['labels'][jobset_utils.JOBSET_USERID_LABEL]
            == common_utils.user_and_hostname_hash()
            and not all_users
        )
    ]

    if all:
        assert jobs_specs is not None, f'No jobs found in namespace {namespace}'
        assert len(jobs_specs) > 0, f'No jobs found in namespace {namespace}'
        jobs = [job['metadata']['name'] for job in jobs_specs]
    elif jobs:
        # Get all available jobs to match against patterns
        if len(jobs_specs) == 0:
            raise click.ClickException(f'No jobs found in namespace {namespace}')

        all_job_names = [job['metadata']['name'] for job in jobs_specs]
        matched_jobs = []

        for job_pattern in jobs:
            # Use fnmatch for both wildcard and exact pattern matching
            pattern_matches = fnmatch.filter(all_job_names, job_pattern)
            if not pattern_matches:
                click.secho(
                    f'Warning: No jobs found matching pattern "{job_pattern}"',
                    fg='yellow',
                    err=True,
                )
            matched_jobs.extend(pattern_matches)

        # Remove duplicates while preserving order
        seen = set()
        jobs = []
        for job in matched_jobs:
            if job not in seen:
                seen.add(job)
                jobs.append(job)

        if not jobs:
            raise click.ClickException(
                f'No matching jobs found check status with '
                f'{colorama.Style.BRIGHT}konduktor status{colorama.Style.RESET_ALL}'
            )
    else:
        raise click.ClickException(
            'No jobs specified. Use --all to suspend '
            'all jobs or specify job names/patterns.'
        )

    if not yes:
        # Prompt for confirmation
        prompt = (
            f'Suspending job(s) {colorama.Style.BRIGHT} '
            f'{colorama.Fore.GREEN}{jobs}{colorama.Style.RESET_ALL}. '
            'Proceed?'
        )
        if prompt is not None:
            click.confirm(prompt, default=True, abort=True, show_default=True)

    for job in track(jobs, description='Suspending job(s)...'):
        jobset_utils.stop_jobset(namespace, job)

    click.secho(
        ux_utils.command_hint_messages(ux_utils.CommandHintType.JOB_STOP, jobs),
        fg='green',
        bold=True,
    )


@cli.command(cls=_DocumentedCodeCommand)
@click.argument(
    'jobs',
    nargs=-1,
    required=False,
)
@click.option(
    '--all', '-a', default=None, is_flag=True, help='Resume all suspended jobs.'
)
@click.option(
    '--all-users',
    '--all_users',
    default=False,
    is_flag=True,
    help='Include other users for resumption',
)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    default=False,
    required=False,
    help='Skip confirmation prompt.',
)
def start(
    jobs: List[str],
    all: Optional[bool],
    all_users: Optional[bool],
    yes: bool,
):
    """Resume suspended job(s) (manual/user-initiated).

    JOB is the name of the job to resume. If both
    JOB and ``--all`` are supplied, the latter takes precedence.

    Resuming a job will restart execution from where it was suspended.
    Only suspended jobs can be resumed.

    This command works for both manually suspended jobs (SUSPENDED by user)
    and system-suspended jobs (SUSPENDED by system).

    Wildcard patterns are supported using * characters.
    Examples: "my_job-*" matches all jobs starting with "my_job-",
    "*-gpu" matches all jobs ending with "-gpu".

    Examples:

    .. code-block:: bash

      # Resume a specific job.
      konduktor start my_job
      \b
      # Resume multiple jobs.
      konduktor start my_job1 my_job2
      \b
      # Resume all jobs matching a pattern.
      konduktor start "my_job-*"
      \b
      # Resume all of this users suspended jobs.
      konduktor start -a
      konduktor start --all

      # Resume all suspended jobs across all users
      konduktor start --all --all-users

    """

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    jobs_response = jobset_utils.list_jobset(namespace)
    assert jobs_response
    jobs_specs = [
        job
        for job in jobs_response['items']
        if (
            job['metadata']['labels'][jobset_utils.JOBSET_USERID_LABEL]
            == common_utils.user_and_hostname_hash()
            and not all_users
        )
    ]

    if all:
        # Only get suspended jobs when using --all
        suspended_jobs = [
            job['metadata']['name']
            for job in jobs_specs
            if job.get('status', {})
            .get('replicatedJobsStatus', [{}])[0]
            .get('suspended', False)
        ]
        if not suspended_jobs:
            raise click.ClickException(
                f'No suspended jobs found in namespace {namespace}'
            )
        jobs = suspended_jobs
    elif jobs:
        # Get all available jobs to match against patterns
        if len(jobs_specs) == 0:
            raise click.ClickException(f'No jobs found in namespace {namespace}')

        all_job_names = [job['metadata']['name'] for job in jobs_specs]
        matched_jobs = []

        for job_pattern in jobs:
            # Use fnmatch for both wildcard and exact pattern matching
            pattern_matches = fnmatch.filter(all_job_names, job_pattern)
            if not pattern_matches:
                click.secho(
                    f'Warning: No jobs found matching pattern "{job_pattern}"',
                    fg='yellow',
                    err=True,
                )
            matched_jobs.extend(pattern_matches)

        # Remove duplicates while preserving order
        seen = set()
        jobs = []
        for job in matched_jobs:
            if job not in seen:
                seen.add(job)
                jobs.append(job)

        if not jobs:
            raise click.ClickException(
                f'No matching jobs found check status with '
                f'{colorama.Style.BRIGHT}konduktor status{colorama.Style.RESET_ALL}'
            )
    else:
        raise click.ClickException(
            'No jobs specified. Use --all to resume '
            'all suspended jobs or specify job names/patterns.'
        )

    if not yes:
        # Prompt for confirmation
        prompt = (
            f'Resuming job(s) {colorama.Style.BRIGHT} '
            f'{colorama.Fore.GREEN}{jobs}{colorama.Style.RESET_ALL}. '
            'Proceed?'
        )
        if prompt is not None:
            click.confirm(prompt, default=True, abort=True, show_default=True)

    for job in track(jobs, description='Resuming job(s)...'):
        jobset_utils.start_jobset(namespace, job)


@cli.command(cls=_DocumentedCodeCommand)
@click.argument(
    'clouds',
    required=True,
    type=str,
    nargs=-1,
)
def check(clouds: Tuple[str]):
    """Check which clouds are available to use for storage

    This checks storage credentials for a cloud supported by konduktor. If a
    cloud is detected to be inaccessible, the reason and correction steps will
    be shown.

    If CLOUDS are specified, checks credentials for only those clouds.

    The enabled clouds are cached and form the "search space" to be considered
    for each task.

    Examples:

    .. code-block:: bash

      # Check only specific clouds - gs, s3.
      konduktor check gs
      konduktor check s3
    """
    clouds_arg = clouds if len(clouds) > 0 else None
    konduktor_check.check(clouds=clouds_arg)


class KeyValueType(click.ParamType):
    name = 'key=value'

    def convert(self, value, param, ctx):
        if '=' not in value:
            self.fail(f'{value!r} is not a valid key=value pair', param, ctx)
        key, val = value.split('=', 1)
        return key, val


_SECRET_CREATE_OPTIONS = [
    click.option(
        '--inline',
        type=KeyValueType(),
        help='Key=value pair to store as an env secret (only valid with --kind env).',
    ),
    click.option(
        '--from-file',
        '--from_file',
        type=click.Path(dir_okay=False),
        help='Path to a single file to store as a secret.',
    ),
    click.option(
        '--from-directory',
        '--from_directory',
        type=click.Path(file_okay=False),
        help='Path to a directory to store as a multi-file secret.',
    ),
    click.option(
        '--kind',
        default='default',
        type=click.Choice(['default', 'env', 'git-ssh']),
        help='Type of secret being created. More kinds coming soon.',
    ),
]


@cli.group(cls=_NaturalOrderGroup)
def secret():
    """Manage secrets used in Konduktor.

    USAGE: konduktor secret COMMAND

    \b
    Use one of the following COMMANDS:
      create [FLAGS] [NAME]
      delete [NAME]
      list [FLAGS]

    \b
    Examples:
      konduktor secret create --kind git-ssh --from-file=~/.ssh/id_rsa my-ssh-name
      konduktor secret create --kind env --inline FOO=bar my-env-name
      konduktor delete my-ssh-name
      konduktor secret list

    \b
    For details on COMMAND ARGS:
      konduktor secret create -h
      konduktor secret list -h
    """


@_add_click_options(_SECRET_CREATE_OPTIONS)
@secret.command()
@click.argument('name', required=True)
def create(kind, from_file, from_directory, inline, name):
    """Create a new secret."""

    if not kubernetes_utils.is_k8s_resource_name_valid(name):
        raise click.BadParameter(
            f'Invalid secret name: {name}. '
            f'Name must consist of lower case alphanumeric characters or -, '
            f'and must start and end with alphanumeric characters.',
        )

    basename = name
    secret_name = f'{basename}-{common_utils.get_user_hash()}'

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)

    from_file = os.path.expanduser(from_file) if from_file else None
    from_directory = os.path.expanduser(from_directory) if from_directory else None

    sources = [bool(from_file), bool(from_directory), bool(inline)]

    if sources.count(True) > 1:
        raise click.UsageError(
            'Only one of --from-file, --from-directory, or --inline can be used.\n'
            'Examples:\n'
            f'  {colorama.Style.BRIGHT}konduktor secret create --kind git-ssh '
            f'--from-file=~/.ssh/id_rsa my-ssh-name\n{colorama.Style.RESET_ALL}'
            f'  {colorama.Style.BRIGHT}konduktor secret create --kind env '
            f'--inline FOO=bar my-env-name{colorama.Style.RESET_ALL}'
        )

    if sources.count(True) == 0:
        raise click.UsageError(
            'You must specify one of --from-file, --from-directory, or --inline.\n'
            'Examples:\n'
            f'  {colorama.Style.BRIGHT}konduktor secret create --kind git-ssh '
            f'--from-file=~/.ssh/id_rsa my-ssh-name\n{colorama.Style.RESET_ALL}'
            f'  {colorama.Style.BRIGHT}konduktor secret create --kind env '
            f'--inline FOO=bar my-env-name{colorama.Style.RESET_ALL}'
        )

    if from_file and not os.path.isfile(from_file):
        raise click.BadParameter(
            f'--from-file {from_file} does not exist or is not a file'
        )
    if from_directory and not os.path.isdir(from_directory):
        raise click.BadParameter(
            f'--from-directory {from_directory} does not exist or is not a directory'
        )

    if kind == 'git-ssh' and not from_file:
        raise click.UsageError(
            '--kind git-ssh requires --from-file (not --from-directory or --inline). \n'
            'Example:\n'
            f'  {colorama.Style.BRIGHT}konduktor secret create --kind git-ssh '
            f'--from-file=~/.ssh/id_rsa my-ssh-name{colorama.Style.RESET_ALL}'
        )
    if kind == 'env' and not inline:
        raise click.UsageError(
            '--kind env requires --inline (not --from-file or --from-directory). \n'
            'Example:\n'
            f'  {colorama.Style.BRIGHT}konduktor secret create --kind env '
            f'--inline FOO=bar my-env-name{colorama.Style.RESET_ALL}'
        )

    data = {}
    if from_directory:
        click.echo(f'Creating secret from directory: {from_directory}')
        base_path = pathlib.Path(from_directory)
        for path in base_path.rglob('*'):
            if path.is_file():
                rel_path = path.relative_to(base_path)
                with open(path, 'rb') as f:
                    data[str(rel_path)] = b64encode(f.read()).decode()
    elif from_file:
        click.echo(f'Creating secret from file: {from_file}')
        key = os.path.basename(from_file)
        if kind == 'git-ssh':
            key = 'gitkey'
        try:
            with open(from_file, 'rb') as f:
                data[key] = b64encode(f.read()).decode()
        except OSError as e:
            raise click.ClickException(f'Failed to read {kind} file {from_file}: {e}')
    else:
        click.echo('Creating secret from inline key=value pair')
        key, value = inline
        data = {key: b64encode(value.encode()).decode()}

    secret_metadata = {
        'name': secret_name,
        'labels': {
            'parent': 'konduktor',
            backend_constants.SECRET_OWNER_LABEL: common_utils.get_user_hash(),
            backend_constants.SECRET_BASENAME_LABEL: basename,
            backend_constants.SECRET_KIND_LABEL: kind or None,
        },
    }

    # Limit --kind git-ssh secret to 1 max per user
    # Overwrites if user trying to create more than 1
    if kind == 'git-ssh':
        user_hash = common_utils.get_user_hash()
        label_selector = f'{backend_constants.SECRET_OWNER_LABEL}={user_hash}'
        existing = kubernetes_utils.list_secrets(
            namespace, context, label_filter=label_selector
        )
        for s in existing:
            labels = s.metadata.labels or {}
            if labels.get(backend_constants.SECRET_KIND_LABEL) == 'git-ssh':
                old_name = s.metadata.name
                click.echo(f'Found existing git-ssh secret: {old_name}, deleting it.')
                kubernetes_utils.delete_secret(
                    name=old_name, namespace=namespace, context=context
                )
                break

    ok, err = kubernetes_utils.set_secret(
        secret_name=secret_name,
        namespace=namespace,
        context=context,
        data=data,
        secret_metadata=secret_metadata,
    )
    if not ok:
        raise click.ClickException(f'Failed to create secret: {err}')
    click.secho(f'Secret {basename} created in namespace {namespace}.', fg='green')


@secret.command()
@click.argument('name', required=True)
def delete(name):
    """Delete a secret by name."""

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    user_hash = common_utils.get_user_hash()

    label_selector = f'{backend_constants.SECRET_OWNER_LABEL}={user_hash}'
    secrets = kubernetes_utils.list_secrets(
        namespace, context, label_filter=label_selector
    )

    matches = [
        s
        for s in secrets
        if s.metadata.labels
        and s.metadata.labels.get(backend_constants.SECRET_BASENAME_LABEL) == name
    ]

    if not matches:
        raise click.ClickException(
            f'No secret named "{name}" owned by you found in namespace {namespace}.'
        )
    elif len(matches) > 1:
        raise click.ClickException(f'Multiple secrets with basename "{name}" found.')

    full_name = matches[0].metadata.name

    ok, err = kubernetes_utils.delete_secret(full_name, namespace, context)
    if not ok:
        raise click.ClickException(f'Failed to delete secret: {err}')
    click.secho(f'Secret {name} deleted from namespace {namespace}.', fg='yellow')


@secret.command(name='list')
@click.option(
    '--all-users',
    '--all_users',
    '-u',
    is_flag=True,
    default=False,
    help='Show all secrets, including those not owned by the current user.',
)
def list_secrets(all_users: bool):
    """List secrets in the namespace.
    Defaults to only your secrets unless --all-users is set."""

    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)

    if not all_users:
        user_hash = common_utils.get_user_hash()
        username = common_utils.get_cleaned_username()
        label_selector = f'{backend_constants.SECRET_OWNER_LABEL}={user_hash}'
        secrets = kubernetes_utils.list_secrets(
            namespace, context, label_filter=label_selector
        )
    else:
        secrets = kubernetes_utils.list_secrets(namespace, context)

    if not secrets:
        if all_users:
            click.secho(f'No secrets found in {namespace}.', fg='yellow')
        else:
            click.secho(f'No secrets found for {username} in {namespace}.', fg='yellow')
        return

    if all_users:
        click.secho(f'All secrets in {namespace} namespace:\n', bold=True)
    else:
        click.secho(f'Secrets in {namespace} namespace owned by you:\n', bold=True)

    for s in secrets:
        labels = s.metadata.labels or {}
        basename = labels.get(backend_constants.SECRET_BASENAME_LABEL, s.metadata.name)
        kind = labels.get(backend_constants.SECRET_KIND_LABEL, '(none)')
        owner = labels.get(backend_constants.SECRET_OWNER_LABEL, '(none)')

        if all_users:
            click.echo(f'{basename:30}   kind={kind:10}   owner={owner}')
        else:
            click.echo(f'{basename:30}   kind={kind:10}')


@cli.group(cls=_NaturalOrderGroup)
def serve():
    """Manage LLM serving with Konduktor.

    USAGE: konduktor serve COMMAND

    \b
    Use one of the following COMMANDS:
      launch
      down
      status

    \b
    Examples:
      konduktor serve launch my-deployment
      konduktor serve down my-deployment
      konduktor serve status

    \b
    For details on COMMAND ARGS:
      konduktor serve launch -h
      konduktor serve down -h
      konduktor serve status -h
    """
    pass


@serve.command(name='launch')
@click.argument(
    'entrypoint',
    required=False,
    type=str,
    nargs=-1,
)
@click.option(
    '--dryrun',
    default=False,
    is_flag=True,
    help='If True, do not actually run the job.',
)
@click.option(
    '--detach-run',
    '-d',
    default=False,
    is_flag=True,
    help=(
        'If True, as soon as a job is submitted, return from this call '
        'and do not stream execution logs.'
    ),
)
@_add_click_options(
    _TASK_OPTIONS_WITH_NAME + _EXTRA_RESOURCES_OPTIONS + _EXTRA_SERVING_OPTIONS
)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    default=False,
    required=False,
    # Disabling quote check here, as there seems to be a bug in pylint,
    # which incorrectly recognizes the help string as a docstring.
    # pylint: disable=bad-docstring-quotes
    help='Skip confirmation prompt.',
)
def serve_launch(
    entrypoint: Tuple[str, ...],
    dryrun: bool,
    detach_run: bool,
    name: Optional[str],
    workdir: Optional[str],
    cloud: Optional[str],
    gpus: Optional[str],
    cpus: Optional[str],
    memory: Optional[str],
    num_nodes: Optional[int],
    max_restarts: Optional[int],
    completions: Optional[int],
    image_id: Optional[str],
    env_file: Optional[Dict[str, str]],
    env: List[Tuple[str, str]],
    disk_size: Optional[int],
    min_replicas: Optional[int],
    max_replicas: Optional[int],
    ports: Optional[int],
    probe: Optional[str],
    yes: bool,
):
    """Launch a deployment to serve.

    If ENTRYPOINT points to a valid YAML file, it is read in as the task
    specification. Otherwise, it is interpreted as a bash command.
    """
    # NOTE(dev): Keep the docstring consistent between the Python API and CLI.
    env = _merge_env_vars(env_file, env)

    task = _make_task_with_overrides(
        entrypoint=entrypoint,
        name=name,
        workdir=workdir,
        cloud=cloud,
        gpus=gpus,
        cpus=cpus,
        memory=memory,
        num_nodes=num_nodes,
        max_restarts=max_restarts,
        completions=completions,
        image_id=image_id,
        env=env,
        disk_size=disk_size,
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        ports=ports,
        probe=probe,
    )

    click.secho(
        f'Considered resources ({task.num_nodes} nodes):', fg='green', bold=True
    )
    table_kwargs = {
        'hrules': prettytable.FRAME,
        'vrules': prettytable.NONE,
        'border': True,
    }
    headers = ['CPUs', 'Mem (GB)', 'GPUs']
    table = log_utils.create_table(headers, **table_kwargs)
    assert task.resources is not None
    table.add_row(
        [task.resources.cpus, task.resources.memory, task.resources.accelerators]
    )
    print(table)

    if not task.serving:
        raise click.UsageError(
            'No serving information detected. '
            'Use `konduktor launch` instead for workloads.'
        )

    job_name = _launch_with_confirm(
        task,
        dryrun=dryrun,
        detach_run=detach_run,
        no_confirm=yes,
        serving=bool(task.serving),
    )

    click.secho(f'Deployment Name: {job_name}', fg='green', bold=True)


@serve.command(name='down')
@click.argument('names', nargs=-1, required=False)
@click.option(
    '--all', '-a', default=False, is_flag=True, help='Tear down all deployments.'
)
@click.option(
    '--yes',
    '-y',
    is_flag=True,
    default=False,
    required=False,
    help='Skip confirmation prompt.',
)
def serve_down(
    names: List[str],
    all: bool,
    yes: bool,
):
    """Tear down deployments (Deployment, Service, PodAutoscaler).

    Use --all or -a to tear down all deployments.

    Examples:

    \b
      konduktor serve down my-deployment
      konduktor serve down -a
    """
    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)

    all_models = deployment_utils.list_models(namespace)

    if all:
        names = all_models
        if not names:
            logger.warning(
                f'No deployments found in namespace '
                f'{namespace}, but continuing teardown.'
            )
    elif names:
        matched = []
        for pattern in names:
            matched.extend(fnmatch.filter(all_models, pattern))
        names = sorted(set(matched))
        if not names:
            raise click.ClickException(
                f'No matching deployments found. Check with: '
                f'{colorama.Style.BRIGHT}konduktor serve '
                f'status{colorama.Style.RESET_ALL}'
            )
    else:
        raise click.ClickException(
            'No deployments specified. Use --all to tear down all deplotments '
            'or pass names/patterns.'
        )

    if not yes:
        prompt = (
            f'Tearing down deployment(s) '
            f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}{names}'
            f'{colorama.Style.RESET_ALL}. '
            f'Proceed?'
        )
        click.confirm(prompt, default=True, abort=True, show_default=True)

    for name in track(names, description='Tearing down deployment(s)...'):
        deployment_utils.delete_serving_specs(name, namespace)


@serve.command(name='status')
@click.option(
    '--all-users',
    '-u',
    default=False,
    is_flag=True,
    required=False,
    help='Show all deployments, including those not owned by the ' 'current user.',
)
@click.option(
    '--direct',
    '-d',
    default=False,
    is_flag=True,
    required=False,
    help='Force display of direct IP endpoints instead of trainy.us endpoints.',
)
def serve_status(all_users: bool, direct: bool):
    """Show status of deployments launched via `konduktor serve launch`."""
    context = kubernetes_utils.get_current_kube_config_context_name()
    namespace = kubernetes_utils.get_kube_config_context_namespace(context)
    deployment_utils.show_status_table(
        namespace, all_users=all_users, force_direct=direct
    )


def main():
    try:
        return cli(standalone_mode=False)
    except click.exceptions.Abort:
        click.secho('Detaching...', fg='yellow', bold=True)
        return None


if __name__ == '__main__':
    main()
