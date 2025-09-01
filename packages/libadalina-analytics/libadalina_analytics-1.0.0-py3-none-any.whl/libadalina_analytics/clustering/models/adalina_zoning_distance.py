from pydantic import BaseModel, Field, field_validator

_zoning_functions = ["euclidean", "manhattan", "chebyshev", "haversine", "hamming", "canberra", "braycurtis", "jaccard", "matching", "dice", "kulsinski", "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath"]

class ClusteringDistance(BaseModel):
    name: str = Field(description='Name of the column')
    weight: int | None = Field(description='Weight of the column', default=1)
    function: str | None = Field(description='Function used to compute the distance', default=None)

    @field_validator('function')
    def validate_func(cls, v):
        if v is not None and v not in _zoning_functions:
            raise ValueError(f'Function must be one of {_zoning_functions}')
        return v