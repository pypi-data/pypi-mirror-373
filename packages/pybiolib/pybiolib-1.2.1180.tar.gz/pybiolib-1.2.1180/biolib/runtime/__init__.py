import warnings

from biolib._runtime.runtime import Runtime as _Runtime


def set_main_result_prefix(result_prefix: str) -> None:
    warnings.warn(
        'The "biolib.runtime.set_main_result_prefix" function is deprecated. '
        'It will be removed in future releases from mid 2024. '
        'Please use "from biolib.sdk import Runtime" and then "Runtime.set_main_result_prefix" instead.',
        DeprecationWarning,
        stacklevel=2,
    )
    _Runtime.set_main_result_prefix(result_prefix)
