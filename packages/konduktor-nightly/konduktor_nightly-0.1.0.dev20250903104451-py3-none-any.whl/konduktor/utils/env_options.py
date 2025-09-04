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

"""Global environment options for konduktor."""

import enum
import os
from typing import Dict


class Options(enum.Enum):
    """Environment variables for SkyPilot."""

    # (env var name, default value)
    IS_DEVELOPER = ('KONDUKTOR_DEV', False)
    SHOW_DEBUG_INFO = ('KONDUKTOR_DEBUG', True)
    DISABLE_LOGGING = ('KONDUKTOR_DISABLE_USAGE_COLLECTION', False)
    MINIMIZE_LOGGING = ('KONDUKTOR_MINIMIZE_LOGGING', False)
    SUPPRESS_SENSITIVE_LOG = ('KONDUKTOR_SUPPRESS_SENSITIVE_LOG', False)
    # Internal: this is used to skip the cloud user identity check, which is
    # used to protect cluster operations in a multi-identity scenario.
    # Currently, this is only used in the job and serve controller, as there
    # will not be multiple identities, and skipping the check can increase
    # robustness.
    SKIP_CLOUD_IDENTITY_CHECK = ('KONDUKTOR_SKIP_CLOUD_IDENTITY_CHECK', False)

    def __init__(self, env_var: str, default: bool) -> None:
        self.env_var = env_var
        self.default = default

    def __repr__(self) -> str:
        return self.env_var

    def get(self) -> bool:
        """Check if an environment variable is set to True."""
        return os.getenv(self.env_var, str(self.default)).lower() in ('true', '1')

    @property
    def env_key(self) -> str:
        """The environment variable key name."""
        return self.value[0]

    @classmethod
    def all_options(cls) -> Dict[str, bool]:
        """Returns all options as a dictionary."""
        return {option.env_key: option.get() for option in list(Options)}
