"""Accelerator registry."""

_ACCELERATORS = ['A100', 'A100-80GB', 'B200', 'H100', 'H200', 'L40S', 'T4', 'L40']


def canonicalize_accelerator_name(accelerator: str) -> str:
    """Returns the canonical accelerator name."""

    # Common case: do not read the catalog files.
    mapping = {name.lower(): name for name in _ACCELERATORS}
    if accelerator.lower() in mapping:
        return mapping[accelerator.lower()]

    raise ValueError(
        f'Accelerator name {accelerator!r} is not supported. '
        f'Please choose one of {_ACCELERATORS}.'
    )
