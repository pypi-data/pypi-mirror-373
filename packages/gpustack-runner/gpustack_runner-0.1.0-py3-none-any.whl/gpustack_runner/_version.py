# Auto-generated file, do not edit.

__all__ = [
    "__version__",
    "version",
    "__version_tuple__",
    "version_tuple",
    "__commit_id__",
    "commit_id",
]

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Tuple
    from typing import Union

    VERSION_TUPLE = Tuple[Union[int, str], ...]
    COMMIT_ID = Union[str, None]
else:
    VERSION_TUPLE = object
    COMMIT_ID = object

__version__: str
version: str
__version_tuple__: VERSION_TUPLE
version_tuple: VERSION_TUPLE
__commit_id__: COMMIT_ID
commit_id: COMMIT_ID

__version__ = version = '0.1.0'
__version_tuple__ = version_tuple = (0, 1, 0)
try:
    from ._version_appendix import git_commit
    __commit_id__ = commit_id = git_commit
except ImportError:
    __commit_id__ = commit_id = None
