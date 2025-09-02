import numpy as np
import numpy.typing as npt
from typing import Dict, TypeAlias, Union, Tuple, List, TypedDict

# from pyCFS.data.io.cfs_types import cfs_result_type

pyCFSsimObject: TypeAlias = object
pyCFSparam: TypeAlias = int | float | str
pyCFSparamVec: TypeAlias = (
    npt.NDArray[np.int32]
    | npt.NDArray[np.int64]
    | npt.NDArray[np.float32]
    | npt.NDArray[np.float64]
    | npt.NDArray[np.str_]
)
resultScalar: TypeAlias = int | float | bool
resultVec: TypeAlias = Union[npt.NDArray[np.float32], npt.NDArray[np.float64], npt.NDArray[np.complex64], npt.NDArray]
resultDict: TypeAlias = Dict[str, resultVec | resultScalar | Tuple[resultScalar]]
nestedResultDict: TypeAlias = Dict[str, Dict[str, Dict[str, resultDict]]]


class sensorArrayResult(TypedDict):
    data: resultVec
    columns: List[str]


sensorArrayResultPacket = Dict[str, sensorArrayResult]


class runMetaData(TypedDict):
    xml_template: str
    mat_template: str
    jou_template: str
    other_files: Dict[str, str]
    X: pyCFSparamVec
    run_start: str
    run_finish: str
    note: str


class resultDump(TypedDict):
    results_hdf: List[nestedResultDict]
    results_sensor_array: List[sensorArrayResultPacket]
    meta_data: runMetaData


__all__ = [
    "pyCFSparam",
    "pyCFSparamVec",
    "resultVec",
    "resultDict",
    "nestedResultDict",
    "sensorArrayResult",
]
