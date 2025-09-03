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

"""Credential checks: check cloud credentials and enable clouds.

Our architecture is client-server and requires that credentials are stored
as a secret in the cluster. This makes it so that cluster admins can just
deploy credentials (s3, gcs, r2) once to the namespace. Users then during job
use the secret stored for mounting credentials to pods. Users running must also
have the credentials present on their local machine, otherwise they won't be able to
upload files to object storage.

We have to check that the credentials are valid on the client side.
If the check fails, then we will attempt to check the credentials present on the client.
If these credentials are valid, we update the secret on the cluster, and
run the job as usual.
If these credentials are not valid, we fail the job and alert the user.

"""

import traceback
import typing
from typing import Iterable, List, Optional, Tuple

import click
import colorama

from konduktor import config as konduktor_config
from konduktor import logging
from konduktor.data import registry
from konduktor.utils import rich_utils

if typing.TYPE_CHECKING:
    from konduktor.data import storage_utils

logger = logging.get_logger(__name__)


def check(
    quiet: bool = False,
    clouds: Optional[Iterable[str]] = None,
) -> List[str]:
    echo = (
        (lambda *_args, **_kwargs: None)
        if quiet
        else lambda *args, **kwargs: click.echo(*args, **kwargs, color=True)
    )
    echo('Checking credentials to enable clouds storage for Konduktor.')
    enabled_clouds = []
    disabled_clouds = []

    def check_one_cloud(
        cloud_tuple: Tuple[str, 'storage_utils.CloudStorage'],
    ) -> None:
        cloud_repr, cloud = cloud_tuple
        with rich_utils.safe_status(f'Checking {cloud_repr}...'):
            try:
                logger.info(f'Checking {cloud_repr} local client credentials...')
                ok, reason = cloud.check_credentials()
            except Exception:  # pylint: disable=broad-except
                # Catch all exceptions to prevent a single cloud from blocking
                # the check for other clouds.
                ok, reason = False, traceback.format_exc()
        status_msg = 'enabled' if ok else 'disabled'
        styles = {'fg': 'green', 'bold': False} if ok else {'dim': True}
        echo('  ' + click.style(f'{cloud_repr}: {status_msg}', **styles) + ' ' * 30)
        if ok:
            enabled_clouds.append(cloud_repr)
            if reason is not None:
                echo(f'    Hint: {reason}')
        else:
            disabled_clouds.append(cloud_repr)
            echo(f'    Reason: {reason}')

    def get_cloud_tuple(cloud_name: str) -> Tuple[str, 'storage_utils.CloudStorage']:
        # Validates cloud_name and returns a tuple of the cloud's name and
        # the cloud object. Includes special handling for Cloudflare.
        cloud_obj = registry._REGISTRY.get(cloud_name, None)
        assert cloud_obj is not None, f'Cloud {cloud_name!r} not found'
        return cloud_name, cloud_obj

    def get_all_clouds():
        return tuple([c for c in registry._REGISTRY.keys()])

    if clouds is not None:
        cloud_list = clouds
    else:
        cloud_list = get_all_clouds()
    clouds_to_check = [get_cloud_tuple(c) for c in cloud_list]

    # Use allowed_clouds from config if it exists, otherwise check all clouds.
    # Also validate names with get_cloud_tuple.
    config_allowed_cloud_names = [
        c for c in konduktor_config.get_nested(('allowed_clouds',), get_all_clouds())
    ]
    # Use disallowed_cloud_names for logging the clouds that will be disabled
    # because they are not included in allowed_clouds in config.yaml.
    disallowed_cloud_names = [
        c for c in get_all_clouds() if c not in config_allowed_cloud_names
    ]
    # Check only the clouds which are allowed in the config.
    clouds_to_check = [c for c in clouds_to_check if c[0] in config_allowed_cloud_names]

    for cloud_tuple in sorted(clouds_to_check):
        check_one_cloud(cloud_tuple)

    # Cloudflare is not a real cloud in registry.CLOUD_REGISTRY, and should
    # not be inserted into the DB (otherwise `sky launch` and other code would
    # error out when it's trying to look it up in the registry).
    enabled_clouds_set = {
        cloud for cloud in enabled_clouds if not cloud.startswith('Cloudflare')
    }
    disabled_clouds_set = {
        cloud for cloud in disabled_clouds if not cloud.startswith('Cloudflare')
    }

    # Determine the set of enabled clouds: (previously enabled clouds + newly
    # enabled clouds - newly disabled clouds) intersected with
    # config_allowed_clouds, if specified in config.yaml.
    # This means that if a cloud is already enabled and is not included in
    # allowed_clouds in config.yaml, it will be disabled.
    all_enabled_clouds = enabled_clouds_set - disabled_clouds_set

    disallowed_clouds_hint = None
    if disallowed_cloud_names:
        disallowed_clouds_hint = (
            '\nNote: The following clouds were disabled because they were not '
            'included in allowed_clouds in ~/.konduktor/config.yaml: '
            f'{", ".join([c for c in disallowed_cloud_names])}'
        )
    if not all_enabled_clouds:
        echo(
            click.style(
                'No cloud is enabled. Konduktor will not be able to run any '
                'task. Run `konduktor check` for more info.',
                fg='red',
                bold=True,
            )
        )
        if disallowed_clouds_hint:
            echo(click.style(disallowed_clouds_hint, dim=True))
        raise SystemExit()
    else:
        clouds_arg = ' ' + ' '.join(disabled_clouds) if clouds is not None else ''
        echo(
            click.style(
                '\nTo enable a cloud, follow the hints above and rerun: ', dim=True
            )
            + click.style(f'konduktor check {clouds_arg}', bold=True)
            + '\n'
            + click.style(
                'If any problems remain, refer to detailed docs at: '
                'https://trainy.mintlify.app',  # pylint: disable=line-too-long
                dim=True,
            )
        )

        if disallowed_clouds_hint:
            echo(click.style(disallowed_clouds_hint, dim=True))

        # Pretty print for UX.
        if not quiet:
            enabled_clouds_str = '\n  ' + '\n  '.join(
                [_format_enabled_storage(cloud) for cloud in sorted(all_enabled_clouds)]
            )
            echo(
                f'\n{colorama.Fore.GREEN}{logging.PARTY_POPPER_EMOJI} '
                f'Enabled clouds {logging.PARTY_POPPER_EMOJI}'
                f'{colorama.Style.RESET_ALL}{enabled_clouds_str}'
            )
    return enabled_clouds


def _format_enabled_storage(cloud_name: str) -> str:
    return f'{colorama.Fore.GREEN}{cloud_name}{colorama.Style.RESET_ALL}'
