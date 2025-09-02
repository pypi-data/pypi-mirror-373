"""This module contains a custom validator for the JSON Schema specification.

The main motivation behind extending the existing JSON Schema validator is to
allow for case-insensitive enum matching since this is currently not supported
by the JSON Schema specification.
"""

import json
import time
from pathlib import Path

import jsonschema
import requests
from colorama import Fore, Style
from filelock import FileLock

from konduktor import logging

SCHEMA_VERSION = 'v1.32.0-standalone-strict'
SCHEMA_CACHE_PATH = Path.home() / '.konduktor/schemas'
SCHEMA_LOCK_PATH = SCHEMA_CACHE_PATH / '.lock'
CACHE_MAX_AGE_SECONDS = 86400  # 24 hours

# Schema URLs for different Kubernetes resources
SCHEMA_URLS = {
    'podspec': f'https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/{SCHEMA_VERSION}/podspec.json',
    'deployment': f'https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/{SCHEMA_VERSION}/deployment.json',
    'service': f'https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/{SCHEMA_VERSION}/service.json',
    'horizontalpodautoscaler': f'https://raw.githubusercontent.com/yannh/kubernetes-json-schema/master/{SCHEMA_VERSION}/horizontalpodautoscaler-autoscaling-v2.json',
}

logger = logging.get_logger(__name__)


def case_insensitive_enum(validator, enums, instance, schema):
    del validator, schema  # Unused.
    if instance.lower() not in [enum.lower() for enum in enums]:
        yield jsonschema.ValidationError(f'{instance!r} is not one of {enums!r}')


SchemaValidator = jsonschema.validators.extend(
    jsonschema.Draft7Validator,
    validators={'case_insensitive_enum': case_insensitive_enum},
)


def get_cached_schema(schema_type: str) -> dict:
    """Get cached schema for a specific Kubernetes resource type."""
    schema_url = SCHEMA_URLS.get(schema_type)
    if not schema_url:
        raise ValueError(f'Unknown schema type: {schema_type}')

    schema_file = SCHEMA_CACHE_PATH / f'{schema_type}.json'
    lock = FileLock(str(SCHEMA_LOCK_PATH))

    with lock:
        # Check if schema file exists and is fresh
        if schema_file.exists():
            age = time.time() - schema_file.stat().st_mtime
            # if fresh
            if age < CACHE_MAX_AGE_SECONDS:
                with open(schema_file, 'r') as f:
                    return json.load(f)

        # Download schema
        resp = requests.get(schema_url)
        resp.raise_for_status()

        SCHEMA_CACHE_PATH.mkdir(parents=True, exist_ok=True)
        with open(schema_file, 'w') as f:
            f.write(resp.text)

        return resp.json()


def _validate_k8s_spec(spec: dict, schema_type: str, resource_name: str) -> None:
    """Generic validation function for Kubernetes specs."""
    schema = get_cached_schema(schema_type)

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(spec), key=lambda e: e.path)

    if not errors:
        return

    formatted = [
        f'- {error.message}'
        + (f" at path: {' → '.join(str(p) for p in error.path)}" if error.path else '')
        for error in errors
    ]

    # Clean log
    logger.debug('Invalid k8s %s spec/config:\n%s', resource_name, '\n'.join(formatted))

    # Color only in CLI
    formatted_colored = [
        f'{Fore.RED}- {error.message}'
        + (f" at path: {' → '.join(str(p) for p in error.path)}" if error.path else '')
        + Style.RESET_ALL
        for error in errors
    ]

    raise ValueError(
        f'\n{Fore.RED}Invalid k8s {resource_name} spec/config: {Style.RESET_ALL}\n'
        + '\n'.join(formatted_colored)
    )


def validate_pod_spec(pod_spec: dict) -> None:
    """Validate a Kubernetes pod spec."""
    _validate_k8s_spec(pod_spec, 'podspec', 'pod')


def validate_deployment_spec(deployment_spec: dict) -> None:
    """Validate a Kubernetes deployment spec."""
    _validate_k8s_spec(deployment_spec, 'deployment', 'deployment')


def validate_service_spec(service_spec: dict) -> None:
    """Validate a Kubernetes service spec."""
    _validate_k8s_spec(service_spec, 'service', 'service')


def validate_horizontalpodautoscaler_spec(hpa_spec: dict) -> None:
    """Validate a Kubernetes HorizontalPodAutoscaler spec."""
    _validate_k8s_spec(hpa_spec, 'horizontalpodautoscaler', 'horizontalpodautoscaler')
