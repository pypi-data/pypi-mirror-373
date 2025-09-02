"""This module contains schemas used to validate objects.

Schemas conform to the JSON Schema specification as defined at
https://json-schema.org/
"""

import enum
from typing import Any, Dict, List, Tuple

OVERRIDEABLE_CONFIG_KEYS: List[Tuple[str, ...]] = [
    ('kubernetes', 'pod_config'),
    ('kubernetes', 'provision_timeout'),
]


def _check_not_both_fields_present(field1: str, field2: str):
    return {
        'oneOf': [
            {'required': [field1], 'not': {'required': [field2]}},
            {'required': [field2], 'not': {'required': [field1]}},
            {'not': {'anyOf': [{'required': [field1]}, {'required': [field2]}]}},
        ]
    }


def _get_single_resources_schema():
    """Schema for a single resource in a resources list."""
    # To avoid circular imports, only import when needed.
    # pylint: disable=import-outside-toplevel
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'cpus': {
                'anyOf': [
                    {
                        'type': 'string',
                    },
                    {
                        'type': 'number',
                    },
                ],
            },
            'memory': {
                'anyOf': [
                    {
                        'type': 'string',
                    },
                    {
                        'type': 'number',
                    },
                ],
            },
            'accelerators': {
                'anyOf': [
                    {
                        'type': 'string',
                    },
                    {
                        'type': 'object',
                        'required': [],
                        'maxProperties': 1,
                        'additionalProperties': {'type': 'number'},
                    },
                ]
            },
            'disk_size': {
                'type': 'integer',
            },
            'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}},
            'image_id': {
                'anyOf': [
                    {
                        'type': 'string',
                    },
                    {
                        'type': 'object',
                        'required': [],
                    },
                    {
                        'type': 'null',
                    },
                ]
            },
            '_cluster_config_overrides': {
                'type': 'object',
            },
            'job_config': {'type': 'object'},
        },
    }


def _get_multi_resources_schema():
    multi_resources_schema = {
        k: v
        for k, v in _get_single_resources_schema().items()
        # Validation may fail if $schema is included.
        if k != '$schema'
    }
    return multi_resources_schema


def get_resources_schema():
    """Resource schema in task config."""
    single_resources_schema = _get_single_resources_schema()['properties']
    single_resources_schema.pop('accelerators')
    multi_resources_schema = _get_multi_resources_schema()
    return {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            **single_resources_schema,
            # We redefine the 'accelerators' field to allow one line list or
            # a set of accelerators.
            'accelerators': {
                # {'V100:1', 'A100:1'} will be
                # read as a string and converted to dict.
                'anyOf': [
                    {
                        'type': 'string',
                    },
                    {
                        'type': 'object',
                        'required': [],
                        'additionalProperties': {
                            'anyOf': [
                                {
                                    'type': 'null',
                                },
                                {
                                    'type': 'number',
                                },
                            ]
                        },
                    },
                    {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        },
                    },
                ]
            },
            'any_of': {
                'type': 'array',
                'items': multi_resources_schema,
            },
            'ordered': {
                'type': 'array',
                'items': multi_resources_schema,
            },
        },
    }


def _filter_schema(schema: dict, keys_to_keep: List[Tuple[str, ...]]) -> dict:
    """Recursively filter a schema to include only certain keys.

    Args:
        schema: The original schema dictionary.
        keys_to_keep: List of tuples with the path of keys to retain.

    Returns:
        The filtered schema.
    """
    # Convert list of tuples to a dictionary for easier access
    paths_dict: Dict[str, Any] = {}
    for path in keys_to_keep:
        current = paths_dict
        for step in path:
            if step not in current:
                current[step] = {}
            current = current[step]

    def keep_keys(
        current_schema: dict, current_path_dict: dict, new_schema: dict
    ) -> dict:
        # Base case: if we reach a leaf in the path_dict, we stop.
        if (
            not current_path_dict
            or not isinstance(current_schema, dict)
            or not current_schema.get('properties')
        ):
            return current_schema

        if 'properties' not in new_schema:
            new_schema = {
                key: current_schema[key]
                for key in current_schema
                # We do not support the handling of `oneOf`, `anyOf`, `allOf`,
                # `required` for now.
                if key not in {'properties', 'oneOf', 'anyOf', 'allOf', 'required'}
            }
            new_schema['properties'] = {}
        for key, sub_schema in current_schema['properties'].items():
            if key in current_path_dict:
                # Recursively keep keys if further path dict exists
                new_schema['properties'][key] = {}
                current_path_value = current_path_dict.pop(key)
                new_schema['properties'][key] = keep_keys(
                    sub_schema, current_path_value, new_schema['properties'][key]
                )

        return new_schema

    # Start the recursive filtering
    new_schema = keep_keys(schema, paths_dict, {})
    assert not paths_dict, f'Unprocessed keys: {paths_dict}'
    return new_schema


def _experimental_task_schema() -> dict:
    config_override_schema = _filter_schema(
        get_config_schema(), OVERRIDEABLE_CONFIG_KEYS
    )
    return {
        'experimental': {
            'type': 'object',
            'required': [],
            'additionalProperties': False,
            'properties': {
                'config_overrides': config_override_schema,
            },
        }
    }


def get_task_schema():
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'name': {
                'type': 'string',
            },
            'workdir': {
                'type': 'string',
            },
            'event_callback': {
                'type': 'string',
            },
            'num_nodes': {
                'type': 'integer',
            },
            # resources config is validated separately using RESOURCES_SCHEMA
            'resources': {
                'type': 'object',
            },
            # storage config is validated separately using STORAGE_SCHEMA
            'file_mounts': {
                'type': 'object',
            },
            # service config is validated separately using SERVICE_SCHEMA
            'service': {
                'type': 'object',
            },
            # serving config is validated separately using SERVING_SCHEMA
            'serving': {
                'type': 'object',
            },
            'setup': {
                'type': 'string',
            },
            'run': {
                'type': 'string',
            },
            'envs': {
                'type': 'object',
                'required': [],
                'patternProperties': {
                    # Checks env keys are valid env var names.
                    '^[a-zA-Z_][a-zA-Z0-9_]*$': {'type': ['string', 'null']}
                },
                'additionalProperties': False,
            },
            # inputs and outputs are experimental
            'inputs': {
                'type': 'object',
                'required': [],
                'maxProperties': 1,
                'additionalProperties': {'type': 'number'},
            },
            'outputs': {
                'type': 'object',
                'required': [],
                'maxProperties': 1,
                'additionalProperties': {'type': 'number'},
            },
            **_experimental_task_schema(),
        },
    }


def get_cluster_schema():
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'type': 'object',
        'required': ['cluster', 'auth'],
        'additionalProperties': False,
        'properties': {
            'cluster': {
                'type': 'object',
                'required': ['ips', 'name'],
                'additionalProperties': False,
                'properties': {
                    'ips': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        },
                    },
                    'name': {
                        'type': 'string',
                    },
                },
            },
            'auth': {
                'type': 'object',
                'required': ['ssh_user', 'ssh_private_key'],
                'additionalProperties': False,
                'properties': {
                    'ssh_user': {
                        'type': 'string',
                    },
                    'ssh_private_key': {
                        'type': 'string',
                    },
                },
            },
            'python': {
                'type': 'string',
            },
        },
    }


class RemoteIdentityOptions(enum.Enum):
    """Enum for remote identity types.

    Some clouds (e.g., AWS, Kubernetes) also allow string values for remote
    identity, which map to the service account/role to use. Those are not
    included in this enum.
    """

    LOCAL_CREDENTIALS = 'LOCAL_CREDENTIALS'
    SERVICE_ACCOUNT = 'SERVICE_ACCOUNT'
    NO_UPLOAD = 'NO_UPLOAD'


def get_default_remote_identity(cloud: str) -> str:
    """Get the default remote identity for the specified cloud."""
    if cloud == 'kubernetes':
        return RemoteIdentityOptions.SERVICE_ACCOUNT.value
    return RemoteIdentityOptions.LOCAL_CREDENTIALS.value


_REMOTE_IDENTITY_SCHEMA = {
    'remote_identity': {
        'type': 'string',
        'case_insensitive_enum': [option.value for option in RemoteIdentityOptions],
    }
}

_REMOTE_IDENTITY_SCHEMA_KUBERNETES = {
    'remote_identity': {
        'anyOf': [
            {'type': 'string'},
            {'type': 'object', 'additionalProperties': {'type': 'string'}},
        ]
    },
}


def get_serving_schema():
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'type': 'object',
        'anyOf': [
            {'required': ['min_replicas']},
            {'required': ['max_replicas']},
        ],
        'additionalProperties': False,
        'properties': {
            'min_replicas': {
                'type': 'integer',
                'minimum': 1,
                'description': 'Minimum number of replicas for autoscaling.',
            },
            'max_replicas': {
                'type': 'integer',
                'minimum': 1,
                'description': 'Maximum number of replicas for autoscaling.',
            },
            'ports': {
                # this could easily be an integer, but I made it
                # more vague on purpose so I can use a float to test
                # the json schema validator later down the line
                'type': 'number',
                'minimum': 1,
                'description': 'The containerPort and service port '
                'used by the model server.',
            },
            'probe': {
                'type': 'string',
                'description': 'The livenessProbe, readinessProbe, and startupProbe '
                'path used by the model server.',
            },
        },
    }


def get_storage_schema():
    # pylint: disable=import-outside-toplevel
    from konduktor.data import storage
    from konduktor.registry import registry

    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'name': {
                'type': 'string',
            },
            'source': {
                'anyOf': [
                    {
                        'type': 'string',
                    },
                    {'type': 'array', 'minItems': 1, 'items': {'type': 'string'}},
                ]
            },
            'store': {
                'type': 'string',
                'case_insensitive_enum': [type for type in registry._REGISTRY],
            },
            'persistent': {
                'type': 'boolean',
            },
            'mode': {
                'type': 'string',
                'case_insensitive_enum': [mode.value for mode in storage.StorageMode],
            },
            '_bucket_sub_path': {
                'type': 'string',
            },
            '_force_delete': {
                'type': 'boolean',
            },
        },
    }


def get_job_schema():
    """Schema for a job spec, which is defined under resources."""
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'completions': {
                'type': 'integer',
                'minimum': 1,
            },
            'max_restarts': {
                'type': 'integer',
            },
        },
    }


def get_config_schema():
    # pylint: disable=import-outside-toplevel
    from konduktor.data import registry
    from konduktor.utils import kubernetes_enums

    cloud_configs = {
        'kubernetes': {
            'type': 'object',
            'required': [],
            'additionalProperties': False,
            'properties': {
                'pod_config': {
                    'type': 'object',
                    'required': [],
                    # Allow arbitrary keys since validating pod spec is hard
                    'additionalProperties': True,
                },
                'custom_metadata': {
                    'type': 'object',
                    'required': [],
                    # Allow arbitrary keys since validating metadata is hard
                    'additionalProperties': True,
                    # Disallow 'name' and 'namespace' keys in this dict
                    'not': {
                        'anyOf': [{'required': ['name']}, {'required': ['namespace']}]
                    },
                },
                'provision_timeout': {
                    'type': 'integer',
                },
                'autoscaler': {
                    'type': 'string',
                    'case_insensitive_enum': [
                        type.value for type in kubernetes_enums.KubernetesAutoscalerType
                    ],
                },
            },
        },
    }

    admin_policy_schema = {
        'type': 'string',
        # Check regex to be a valid python module path
        'pattern': (r'^[a-zA-Z_][a-zA-Z0-9_]*' r'(\.[a-zA-Z_][a-zA-Z0-9_]*)+$'),
    }

    allowed_clouds = {
        # A list of cloud names that are allowed to be used
        'type': 'array',
        'required': ['items'],
        'items': {
            'type': 'string',
            'case_insensitive_enum': (list(registry._REGISTRY.keys())),
        },
    }

    logs_configs = {
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'backend': {
                'type': 'string',
                'case_insensitive_enum': ['loki', 'victoria'],
            },
        },
    }

    gpu_configs = {
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'disable_ecc': {
                'type': 'boolean',
            },
        },
    }

    tailscale_configs = {
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'secret_name': {
                'type': 'string',
            },
        },
    }

    ssh_configs = {
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'enable': {
                'type': 'boolean',
            },
        },
    }

    serving_configs = {
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'endpoint': {
                'type': 'string',
                'case_insensitive_enum': ['trainy', 'direct'],
                'default': 'trainy',
            },
        },
    }

    for cloud, config in cloud_configs.items():
        if cloud == 'kubernetes':
            config['properties'].update(_REMOTE_IDENTITY_SCHEMA_KUBERNETES)
        else:
            config['properties'].update(_REMOTE_IDENTITY_SCHEMA)
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'type': 'object',
        'required': [],
        'additionalProperties': False,
        'properties': {
            'admin_policy': admin_policy_schema,
            'nvidia_gpus': gpu_configs,
            'allowed_clouds': allowed_clouds,
            'logs': logs_configs,
            'tailscale': tailscale_configs,
            'ssh': ssh_configs,
            'serving': serving_configs,
            **cloud_configs,
        },
    }
