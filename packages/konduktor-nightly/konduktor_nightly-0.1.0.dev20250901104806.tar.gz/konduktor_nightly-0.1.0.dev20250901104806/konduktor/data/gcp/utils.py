import copy
from typing import List

from konduktor.data.gcp import constants


def get_minimal_permissions() -> List[str]:
    permissions = copy.copy(constants.STORAGE_MINIMAL_PERMISSIONS)
    return permissions
