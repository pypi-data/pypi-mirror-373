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

"""Serving: configuration for long-running serving deployments."""

from typing import Any, Dict, Optional, Union

from konduktor import logging
from konduktor.utils import common_utils, schemas, ux_utils

logger = logging.get_logger(__name__)


class Serving:
    """Serving: configuration for deployments.

    Immutable once created. Use `copy()` to create a modified copy.

    Used:
    * to represent serving config in tasks
    """

    _VERSION = 1

    def __init__(
        self,
        min_replicas: Optional[int] = None,
        max_replicas: Optional[int] = None,
        ports: Optional[int] = 8000,
        probe: Optional[str] = '/health',
    ):
        self._version = self._VERSION

        if min_replicas is None and max_replicas is None:
            with ux_utils.print_exception_no_traceback():
                raise ValueError(
                    'At least one of min_replicas or ' 'max_replicas must be specified.'
                )

        if min_replicas is None:
            min_replicas = max_replicas
        if max_replicas is None:
            max_replicas = min_replicas

        if min_replicas is not None and min_replicas <= 0:
            with ux_utils.print_exception_no_traceback():
                raise ValueError('min_replicas must be >= 1')

        if (
            max_replicas is not None
            and min_replicas is not None
            and max_replicas < min_replicas
        ):
            with ux_utils.print_exception_no_traceback():
                raise ValueError(
                    f'max_replicas ({max_replicas}) must '
                    f'be >= min_replicas ({min_replicas})'
                )

        self._min_replicas = min_replicas
        self._max_replicas = max_replicas
        self._ports = ports
        self._probe = probe

    @property
    def min_replicas(self) -> int:
        assert self._min_replicas is not None
        return self._min_replicas

    @property
    def max_replicas(self) -> int:
        assert self._max_replicas is not None
        return self._max_replicas

    @property
    def ports(self) -> int:
        assert self._ports is not None
        return self._ports

    @property
    def probe(self) -> Optional[str]:
        return self._probe

    def get(self, key: str, default=None):
        return {
            'min_replicas': self._min_replicas,
            'max_replicas': self._max_replicas,
            'ports': self._ports,
            'probe': self._probe,
        }.get(key, default)

    def copy(self, **override) -> 'Serving':
        """Returns a copy of this Serving with fields overridden."""
        return Serving(
            min_replicas=override.pop('min_replicas', self._min_replicas),
            max_replicas=override.pop('max_replicas', self._max_replicas),
            ports=override.pop('ports', self._ports),
            probe=override.pop('probe', self._probe),
        )

    @classmethod
    def from_yaml_config(
        cls, config: Optional[Dict[str, Any]], task_run: Optional[str] = None
    ) -> Optional['Serving']:
        if config is None:
            return None
        common_utils.validate_schema(
            config,
            schemas.get_serving_schema(),
            'Invalid serving config YAML: ',
        )

        if 'min_replicas' not in config and 'max_replicas' not in config:
            raise ValueError(
                'At least one of min_replicas or '
                'max_replicas must be specified in serving'
            )

        # Determine default probe based on deployment type
        default_probe = None  # No probing by default for general deployments
        if task_run and 'vllm.entrypoints.openai.api_server' in task_run:
            default_probe = '/health'  # Aibrix deployments get /health by default

        return cls(
            min_replicas=config.get('min_replicas', None),
            max_replicas=config.get('max_replicas', None),
            ports=config.get('ports', 8000),
            probe=config.get('probe', default_probe),
        )

    def to_yaml_config(self) -> Dict[str, Union[int, str]]:
        config: Dict[str, Union[int, str]] = {
            'min_replicas': self._min_replicas or 1,
            'max_replicas': self._max_replicas or 1,
            'ports': self._ports or 8000,
        }
        # Only include probe if it's not None
        if self._probe is not None:
            config['probe'] = self._probe
        return config
