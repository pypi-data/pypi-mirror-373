"""This module contains dataclasses for scheduler optimization entities"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ProvisionSchedulerDataClass:
    """
    A dataclass to hold scheduler-related data.

    Attributes:
        x_val (list): X-axis values for plotting.
        y_val (list): Y-axis values for plotting.
        house_construction_period (list): Construction periods for each house.
        service_construction_period (list): Construction periods for each service.
        houses_per_period (list): Number of houses built in each period.
        services_per_period (list): Number of services built in each period.
        houses_area_per_period (list): Total area of houses built in each period.
        services_area_per_period (list): Total area of services built in each period.
        provided_per_period (list): Total population served in each period.
        periods (list): List of period numbers.
    """

    x_val: np.ndarray[np.ndarray[float | None]]
    y_val: np.ndarray[np.ndarray[float | None]]
    house_construction_period: pd.Series
    service_construction_period: pd.Series
    houses_per_period: np.ndarray[float | None]
    services_per_period: np.ndarray[float | None]
    houses_area_per_period: np.ndarray[float | None]
    services_area_per_period: np.ndarray[float | None]
    provided_per_period: list[float | None]
    periods: np.ndarray[ int | None]
