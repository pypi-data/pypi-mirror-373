"""
Custom Retrier.
"""

from __future__ import annotations

from random import random
from typing import Any, Tuple, Union

import requests
from requests.adapters import Retry


class APIRetry(Retry):
    """API retrier."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise retry."""

        # overrides
        if "status_forcelist" not in kwargs:
            kwargs["status_forcelist"] = [
                requests.codes.bad_gateway,
                requests.codes.service_unavailable,
                requests.codes.gateway_timeout,
            ]
        if "backoff_factor" not in kwargs:
            kwargs["backoff_factor"] = BackoffFactor((0.5, 1.0))

        super().__init__(*args, **kwargs)


class BackoffFactor:
    """Random backoff coefficient."""

    def __init__(self, factor: Union[float, Tuple[float, float]] = (0.0, 1.0)) -> None:
        """Initialise backof coefficient."""

        if isinstance(factor, (tuple, list)):
            if len(factor) != 2:
                raise ValueError("Factor range must be a pair")
            min, max = factor
            if not isinstance(min, (int, float)) or min < 0:
                raise TypeError("Factor range minimum must be a non-negative real number")
            if not isinstance(max, (int, float)) or max < 0:
                raise TypeError("Factor range maximum must be a non-negative real number")
            if min > max:
                raise ValueError("Factor range minimum must not be greater than maximum")
        else:
            if not isinstance(factor, (int, float)) or factor < 0:
                raise TypeError("Factor must be a non-negative real number")
            min = max = factor

        self.min, self.range = min, max - min

    @property
    def _value(self) -> float:
        return self.min + random() * self.range  # nosec

    def __mul__(self, x: float) -> float:
        return self._value.__mul__(x)

    def __rmul__(self, x: float) -> float:
        return self._value.__rmul__(x)

    def __truediv__(self, x: float) -> float:
        return self._value.__truediv__(x)

    def __rtruediv__(self, x: float) -> float:
        return self._value.__rtruediv__(x)

    def __add__(self, x: float) -> float:
        return self._value.__add__(x)

    def __radd__(self, x: float) -> float:
        return self._value.__radd__(x)

    def __sub__(self, x: float) -> float:
        return self._value.__sub__(x)

    def __rsub__(self, x: float) -> float:
        return self._value.__rsub__(x)

    def __int__(self) -> int:
        return self._value.__int__()

    def __float__(self) -> float:
        return self._value.__float__()
