"""Public interface for the :mod:`fspin` package.

Importing ``fspin`` makes the :class:`RateControl` class available as
``rate`` along with the convenience helpers :func:`spin` and :func:`loop`.
"""

from .RateControl import RateControl as rate
from .RateControl import spin
from .RateControl import loop
