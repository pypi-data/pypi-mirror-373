"""This module contains functions for optimizing building schedules in a settlement."""

import cvxpy as cp
import geopandas as gpd
import numpy as np
import pandas as pd

from .sirtep_dataclasses import ProvisionSchedulerDataClass


def optimize_provision_building_schedule(
    houses: pd.DataFrame,
    services: pd.DataFrame,
    access_matrix: pd.DataFrame,
    max_area_per_period: int = 100000,
    num_periods: int = 40,
    ready_threshold: float = 0.99,
    verbose: bool = True,
) -> ProvisionSchedulerDataClass:
    """
    Function optimizes the building schedule for houses and services in a settlement.

    Args:
        houses (pd.DataFrame | gpd.GeoDataFrame): DataFrame with houses,
        must contain 'living_area' and 'population' columns.
        services (pd.DataFrame | gpd.GeoDataFrame): DataFrame with services,
        must contain 'service_area', 'capacity', and 'weight' columns.
        access_matrix (pd.DataFrame): DataFrame indicating access to services for each house,
        with houses as rows and services as columns.
        max_area_per_period (int): Maximum area that can be built in one period in square metres.
        num_periods (int): Number of periods for the optimization.
        ready_threshold (float): Threshold for considering a house or service as ready.
        verbose (bool): Whether to print optimization details.
    Returns:
        ProvisionSchedulerDataClass: Dataclass with optimization results, including:
            - x_val: Matrix of houses built in each period.
            - y_val: Matrix of services built in each period.
            - house_construction_period: Series with construction periods for each house.
            - service_construction_period: Series with construction periods for each service.
            - houses_per_period: Array with the number of houses built in each period.
            - services_per_period: Array with the number of services built in each period.
            - houses_area_per_period: Array with the total area of houses built in each period.
            - services_area_per_period: Array with the total area of services built in each period.
            - provided_per_period: Array with the total population served in each period.
            -periods: Array with the period numbers.
    """

    def _get_construction_periods(val_matrix, ids, threshold):
        periods = pd.Series(index=ids, dtype="Int64")
        for idx, obj_id in enumerate(ids):
            periods_built = np.where(val_matrix[idx] > threshold)[0]
            periods[obj_id] = periods_built[0] + 1 if len(periods_built) > 0 else pd.NA
        return periods

    house_ids = houses.index.copy()
    service_ids = services.index.copy()
    house_objects = houses["living_area"]
    service_objects = services["service_area"]
    population = houses["population"]
    capacity = services["capacity"]
    service_weights = services["weight"]

    n_houses = len(house_objects)
    n_services = len(service_objects)
    x = cp.Variable((n_houses, num_periods))
    y = cp.Variable((n_services, num_periods))

    constraints = [
        x >= 0,
        x <= 1,
        y >= 0,
        y <= 1,
        cp.sum(x, axis=1) <= 1,
        cp.sum(y, axis=1) <= 1,
    ]
    for p in range(num_periods):
        constraints.append(
            cp.sum(cp.multiply(x[:, p], house_objects.values)) + cp.sum(cp.multiply(y[:, p], service_objects.values))
            <= max_area_per_period
        )

    x_total = cp.sum(x, axis=1)
    y_total = cp.sum(y, axis=1)
    house_id_to_idx = {hid: i for i, hid in enumerate(house_ids)}
    service_id_to_idx = {sid: j for j, sid in enumerate(service_ids)}

    population_ready = [cp.multiply(x_total[house_id_to_idx[hid]], population.loc[hid]) for hid in house_ids]
    service_capacity_ready = [cp.multiply(y_total[service_id_to_idx[sid]], capacity.loc[sid]) for sid in service_ids]

    provided_per_house = []
    for hid in house_ids:
        i = house_id_to_idx[hid]
        available_service_ids = access_matrix.columns[access_matrix.loc[hid] == 1]
        if len(available_service_ids) == 0:
            provided_per_house.append(0)
            continue
        service_idxs = [service_id_to_idx[sid] for sid in available_service_ids]
        cap_vals = [service_capacity_ready[k] for k in service_idxs]
        service_place = cp.sum(cp.hstack(cap_vals))
        provided_per_house.append(cp.minimum(population_ready[i], service_place))

    total_provided = cp.sum(cp.vstack(provided_per_house))
    penalty_services = cp.sum(cp.multiply(service_weights.values, cp.multiply(1 - y_total, capacity.values)))
    penalty_houses = cp.sum(cp.multiply(house_objects.values, 1 - x_total))

    objective = cp.Maximize(total_provided - penalty_services - penalty_houses)
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.HIGHS, verbose=verbose)

    x_val = x.value
    y_val = y.value

    house_construction_period = _get_construction_periods(x_val, house_ids, ready_threshold)
    service_construction_period = _get_construction_periods(y_val, service_ids, ready_threshold)

    periods = np.arange(1, num_periods + 1)
    houses_per_period = np.sum(x_val, axis=0)
    services_per_period = np.sum(y_val, axis=0)
    houses_area_per_period = np.sum(x_val * house_objects.values[:, None], axis=0)
    services_area_per_period = np.sum(y_val * service_objects.values[:, None], axis=0)

    x_cum = np.cumsum(x_val, axis=1)
    y_cum = np.cumsum(y_val, axis=1)
    provided_per_period = []
    for p in range(num_periods):
        provided_per_house_p = []
        for hid in house_ids:
            i = house_id_to_idx[hid]
            available_service_ids = access_matrix.columns[access_matrix.loc[hid] == 1]
            service_idxs = [service_id_to_idx[sid] for sid in available_service_ids]
            pop_in_house = x_cum[i, p] * population.loc[hid]
            cap_servs = [y_cum[j, p] * capacity.loc[sid] for j, sid in zip(service_idxs, available_service_ids)]
            service_place = np.sum(cap_servs)
            provided_per_house_p.append(min(pop_in_house, service_place))
        provided_per_period.append(np.sum(provided_per_house_p))

    return ProvisionSchedulerDataClass(
        x_val,
        y_val,
        house_construction_period,
        service_construction_period,
        houses_per_period,
        services_per_period,
        houses_area_per_period,
        services_area_per_period,
        provided_per_period,
        periods,
    )


def optimize_building_schedule(
    objects: pd.DataFrame, max_periods: int = 40, max_speed_per_period: int = 10000, verbose: bool = False
) -> pd.DataFrame:
    """
    Function optimizes building schedule based on priority.
    Args:
        objects (pd.DataFrame | gpd.GeoDataFrame): objects to construct. Should contain following columns:
        - area: object area in square metres
        - priority: non-unique priorities to build object on
        max_periods (int): maximum number of periods to build
        max_speed_per_period (int): maximum speed of building per period
        verbose (bool): whether to print optimization details
    Returns:
         pd.DataFrame: optimized building schedule
    """

    areas = objects["area"].to_numpy()
    priorities = objects["priority"].to_numpy()
    names = objects.index.astype(str)
    n = len(objects)

    x = cp.Variable((n, max_periods), nonneg=True)

    score = priorities / areas
    objective = cp.Maximize(cp.sum(cp.multiply(x, score[:, None])))

    constraints = [cp.sum(x[i, :]) <= 1 for i in range(n)]
    for p in range(max_periods):
        constraints.append(cp.sum(cp.multiply(x[:, p], areas)) <= max_speed_per_period)

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.HIGHS, verbose=verbose)

    if problem.status != cp.OPTIMAL:
        raise RuntimeError(f"Optimization failed, problem status: {problem.status}")

    result = []
    for i, name in enumerate(names):
        for p in range(max_periods):
            percent = x.value[i, p]
            if percent > 1e-4:
                result.append(
                    {
                        "name": name,
                        "period": p + 1,
                        "percent_built": percent,
                        "area": areas[i],
                        "priority": priorities[i],
                    }
                )
    schedule_df = pd.DataFrame(result)
    return schedule_df
