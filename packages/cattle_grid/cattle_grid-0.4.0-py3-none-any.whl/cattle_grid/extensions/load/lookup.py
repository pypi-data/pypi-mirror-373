from typing import List
from cattle_grid.extensions import Extension
from cattle_grid.model.lookup import LookupMethod


def ordered_lookups(extensions: List[Extension]) -> List[LookupMethod]:
    """Returns a list of LookupMethod ordered by lookup order"""
    sorted_extensions = sorted(
        extensions, key=lambda extension: extension.lookup_order or 0, reverse=True
    )

    return [
        extension.lookup_method
        for extension in sorted_extensions
        if extension.lookup_method
    ]
