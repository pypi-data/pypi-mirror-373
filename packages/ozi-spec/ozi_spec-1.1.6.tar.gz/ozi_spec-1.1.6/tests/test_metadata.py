# noqa: INP001
import sys
import warnings


def test_metadata() -> None:
    if sys.version_info < (3, 11):
        warnings.filterwarnings('ignore')
        from ozi_spec import METADATA
    else:
        from ozi_spec import METADATA
    METADATA.asdict()
