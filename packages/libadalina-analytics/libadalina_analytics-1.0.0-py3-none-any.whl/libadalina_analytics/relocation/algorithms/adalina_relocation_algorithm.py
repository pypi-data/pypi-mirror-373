from libadalina_core.sedona_utils import DataFrame, EPSGFormats
from libadalina_analytics.utils import GeometryFormats
from .adalina_algorithms import run_hierarchy_with_distance_threshold
from ..models import AdalinaData, AdalinaSolution, AdalinaAlgorithmOptions
from ..models.adalina_solution import get_solution_csv_AMELIA
import pandas as pd

from ..models.relocation_resource import RelocationResource


def relocation_algorithm(data: DataFrame,
                         epsg: EPSGFormats,
                         id_column: str = 'id',
                         geometry_column: str = 'geometry',
                         geometry_format: GeometryFormats = GeometryFormats.WKT,
                         max_distance_assignment: float | None = None,
                         max_distance_relocation: float | None = None,
                         demand_column: str | None = None,
                         server_column: str | None = None,
                         resources: list[RelocationResource] | None = None,
                         timelimit: int = 60) -> pd.DataFrame | None:
    user_input: dict = {
        "epsg": epsg,
        "geometry_type": geometry_format,
        "geometry": geometry_column,
        "timelimit": timelimit
    }
    if id_column is not None:
        user_input["IDs"] = id_column
    if max_distance_assignment is not None:
        user_input["max_distance_assignment"] = max_distance_assignment
    if max_distance_relocation is not None:
        user_input["max_distance_relocation"] = max_distance_relocation
    if demand_column is not None:
        user_input["demand"] = demand_column
    if resources is not None:
        user_input["resources"] = [{
            'name': resource.column_name,
            'amount': resource.amount
        } for resource in resources]
    if server_column is not None:
        user_input["is_server"] = server_column

    data = AdalinaData.from_Amelia(amelia_file=data,
                                   user_input=user_input
                                   )

    # 4 - RUN ADALINA HIERARCHICAL ALGORITHM
    options = AdalinaAlgorithmOptions()  # I keep the default options
    _, all_solutions = run_hierarchy_with_distance_threshold(data, options)

    if len(all_solutions) == 0:
        return None

    return get_solution_csv_AMELIA(all_solutions[-1], data, epsg, geometry_format)
