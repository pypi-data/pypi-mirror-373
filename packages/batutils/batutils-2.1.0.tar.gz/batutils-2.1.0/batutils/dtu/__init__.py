"""This is the main API module of datetimeutils of batutils.

The intended use case is to go:
```python
from batutils import dtu
```

And then use `dtu` in your code as it serves as the "official" API of the
package.
"""
from batutils.dtu.structs import *

from batutils.dtu.shortcuts import *

from batutils.dtu.casting import *
from batutils.dtu.formatting import *
from batutils.dtu.parsers import *

from batutils import __version__ as VERSION  # noqa
