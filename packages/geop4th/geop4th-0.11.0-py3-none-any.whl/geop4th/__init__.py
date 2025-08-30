# geop4th/__init__.py : expose the main modules of GEOP4TH package
# These modules will be imported when using: from geop4th import *

# Transverse tools
from .geobricks import *
from .graphics.ncplot import *
from .graphics.cmapgenerator import *

# Local declinations of workflows
from .download import (
    download_fr,
    download_wl,
    )
from .workflows.format import (
    cwatm,
    )
from .workflows.standardize import (
    standardize_fr,
    )

# Graphical class
from .graphics import (
    trajplot,
    ncplot,
    cmapgenerator,
    )

# from .graphics.visualization_advanced import *

# dev tools
# from .graphics.monitor_memory import * 