"""
Compatibility glue accross python versions
"""


"""
We can get rid of this Iterable workaround the day we drop support for Python 3.9.
Not before.
"""
try:
    # until Python 3.9 and from 3.6. Will raise deprecation warning but works.
    # Will fail >=3.10
    from typing import Iterable
except AttributeError:
    # For >=3.10.
    # The import would work in earlier Python version, but will fail when used as Iterable[Foo]
    from collections.abc import Iterable
