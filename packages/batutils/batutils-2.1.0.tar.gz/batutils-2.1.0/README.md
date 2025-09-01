# Team Batcave Python Toolkit

The `batutils` is a fork of the `batutils` package in order to continue its 
development and maintenance beyond Team Batcave's lifespan.  

It is a smooshup of a few Python packages from the CCP Tools Team of old (Team 
Batcave).

Our two most commonly used internal packages, called `datetimeutils` and 
`typeutils` were too _generically_ named for Pypi.org and since they were 
both used in something like 80-90% of our other projects, it made sense to 
just smoosh them together in one module, and thus, the `batutils` package 
was born.

Here's the README of the [Date Time Utils](batutils/dtu/README.md) submodule.

Here's the README of the [Type Utils](batutils/tpu/README.md) submodule.


### Changes from `ccptools`

The `legacyapi` submodule has been removed.


## Date-Time Utils

The old `datetimeutils` package is now included here as the `dtu` submodule.

```python
from batutils import dtu
```

## Structs

Importing `*` from the `structs` submodule will import all of the most 
commonly used imports in our projects:
```python
from typing import *  # For type annotation

import abc  # For interfaces (Abstract Base Classes)
import dataclasses  # For dataclass structs
import decimal  # Used whenever we're handling money
import enum  # Also used for struct creation
import logging  # Used pretty much everywhere
import re  # Used surprisingly frequently
import time  # Very commonly used
```

Note that datetime is not included in this. That's because tt'll also import 
the aliases from the Datetime Utils (`batutils.dtu.structs.aliases`) 
package instead:

```python
Date = datetime.date
Time = datetime.time
Datetime = datetime.datetime
TimeDelta = datetime.timedelta
TzInfo = datetime.tzinfo
TimeZone = datetime.timezone
```

Furthermore, it'll also include a few of the most commonly used utility 
classes from the Type Utils submodule:

- The `Singleton` Meta Class 
- The `Empty` and `EmptyDict` classes as well as the `if_empty` method
- The `EnumEx` base class for Enums with the `from_any` class method

So in most cases we can cover something like 90% of any imports we tend to 
need in every Python file with a single line:

```python
from batutils.structs import *
```