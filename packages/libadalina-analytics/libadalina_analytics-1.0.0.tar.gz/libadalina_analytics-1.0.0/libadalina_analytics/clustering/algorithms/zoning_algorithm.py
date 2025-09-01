from libadalina_analytics.utils import GeometryFormats
from .zoning_model_simple import AdalinaZoningModelSimple
from libadalina_core.sedona_utils import DataFrame, EPSGFormats

from ..models.adalina_zoning_data import AdalinaZoningData
from ..models.adalina_zoning_distance import ClusteringDistance
from ..models.adalina_zoning_solution import AdalinaZoningSolution


def clustering_algorithm(data: DataFrame,
                         epsg: EPSGFormats,
                         geometry_column: str = 'geometry',
                         geometry_format: GeometryFormats = GeometryFormats.WKT,
                         weight_column: str | None = None,
                         k_min: int | None = None,
                         k_max: int | None = None,
                         f_min: float | None = None,
                         distances: list[ClusteringDistance] | None = None,
                         timelimit: int = 60) -> AdalinaZoningSolution | None:
    user_input: dict = {
        "epsg": epsg,
        "geometry_type": geometry_format,
        "geometry": geometry_column,
        "timelimit": timelimit
    }
    if weight_column is not None:
        user_input["weight"] = weight_column
    if k_min is not None:
        user_input["Kmin"] = k_min
    if k_max is not None:
        user_input["Kmax"] = k_max
    if f_min is not None:
        user_input["Fmin"] = f_min
    if distances is not None:
        user_input["distances"] = [{
            'name': distance.name,
            'weight': distance.weight,
            'func': distance.function
        } for distance in distances]

    data = AdalinaZoningData.from_Amelia(amelia_file=data, user_input=user_input)

    model = AdalinaZoningModelSimple(data)

    _ = model.run(timelimit=timelimit)

    sol = model.get_solution(False)

    return sol
