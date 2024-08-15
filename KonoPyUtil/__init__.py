"""
 .----------------.  .----------------.  .-----------------. .----------------.
| .--------------. || .--------------. || .--------------. || .--------------. |
| |  ___  ____   | || |     ____     | || | ____  _____  | || |     ____     | |
| | |_  ||_  _|  | || |   .'    `.   | || ||_   \|_   _| | || |   .'    `.   | |
| |   | |_/ /    | || |  /  .--.  \  | || |  |   \ | |   | || |  /  .--.  \  | |
| |   |  __'.    | || |  | |    | |  | || |  | |\ \| |   | || |  | |    | |  | |
| |  _| |  \ \_  | || |  \  `--'  /  | || | _| |_\   |_  | || |  \  `--'  /  | |
| | |____||____| | || |   `.____.'   | || ||_____|\____| | || |   `.____.'   | |
| |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'


KonoPyUtil Library
~~~~~~~~~~~~~~~~~~
KonoPyUtil is a library of convenience fuctions, written in Python, for Kono Analytics and anyone else who wants to use it.

Basic usage:
   >>> import KonoPyUtil as kpu
   >>> credentials = kpu.set_credentials('.env')
   >>> query = "SELECT TOP 10 * FROM [mytable];"
   >>> df = kpu.data_query(query)

:license: Apache 2.0, see LICENSE for more details.
"""

from .__version__ import (
    __title__,
    __description__,
    __url__,
    __version__,
    __author__,
    __author_email__,
    __license__,
    __copyright__,
)

from .dbutils import (
    data_query,
    command_query,
    write_dataframe,
    get_engine,
)
from .credentials import (
    set_credentials,
)
from .datasets import list_datasets, load_dataset
from .soccer import get_elo_season, get_elo_match, validate_elo_df
from .other import get_txptc_plans
from .ipinfo_util import geocode_ip
import logging


logging.getLogger(__name__).addHandler(logging.NullHandler())
