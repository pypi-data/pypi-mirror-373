"""
Module containing view on numpy node array with additional meta data.
"""

from __future__ import annotations

import numpy as np
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING

from pyCFS.data.io import cfs_types
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
from pyCFS.data.util import vprint

if TYPE_CHECKING:
    from pyCFS.data.io._CFSMeshDataModule import CFSMeshData


class CFSResultArray(np.ndarray):
    # TODO: fix getitem to hint correct type
    # noinspection PyUnresolvedReferences
    """
    Overload/Subclass of numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_
    adding attributes according to CFS HDF5 result data structure.

    Shapes supported in pyCFS:
    - (n, m, d) with n steps, m DOFs and d dimensions (mesh result data)
    - (n, d) with n steps and d dimensions (history result data)

    .. figure:: ../../../docs/source/resources/data_structures_CFSResultArray.png

    Parameters
    ----------
    input_array : array_like
        Input data, in any form that can be converted to an array.  This
        includes lists, lists of tuples, tuples, tuples of tuples, tuples
        of lists and ndarrays.
    quantity : str, optional
        Name of the quantity. The default is ``None``.
    region : str, optional
        Name of the region on which the result array is defined.
    step_values : np.ndarray, optional
        Step values (e.g. time stamps). The default is ``None``.
    dim_names : list[str], optional
        List of dimension labels. The default is ``None``.
    res_type : pyCFS.data.io.cfs_types.cfs_result_type, optional
        Enum indicating entity on which the result array is defined on. The default is ``None``.
    is_complex : bool, optional
        Flag if the data is written as complex valued data. The default is ``None``, in which case it is automatically
        defined based on the analysis type.
    multi_step_id : int, optional
        ID of the multi-step. The default is ``1``.
    analysis_type : pyCFS.data.io.cfs_types.cfs_analysis_type, optional
        Enum indicating the analysis type. The default is ``cfs_analysis_type.NO_ANALYSIS``.
    meta_data : dict, optional
        Dictionary containing all meta data, ignores all other meta data arguments if provided. The default is ``None``.

    Examples
    --------
    >>> from pyCFS.data.io import CFSResultArray
    >>> from pyCFS.data.io.cfs_types import cfs_result_type
    >>> data = [0,1,2,3]
    >>> result_array = CFSResultArray(data,quantity='quantity_name', region='region_name', step_value=0,
    >>>                               dim_names=['-'], res_type=cfs_result_type.NODE, is_complex=True,
    >>>                               multi_step_id=2, AnalysisType=cfs_analysis_type.STATIC)

    """

    def __new__(
        cls,
        input_array,
        quantity: str | None = None,
        region: str | None = None,
        step_values: np.ndarray | None = None,
        dim_names: List[str] | None = None,
        res_type: cfs_result_type = cfs_result_type.UNDEFINED,
        is_complex: bool | None = None,
        multi_step_id=1,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
        meta_data: Dict | None = None,
    ):
        # Input array is an already formed ndarray instance
        # Cast to be our class type
        obj = np.asarray(input_array).view(cls)

        if step_values is None:
            step_values = np.empty(0)
        else:
            step_values = np.asarray(step_values)
        # Add attributes
        obj.Quantity = quantity
        obj.Region = region
        obj.StepValues = step_values
        obj._DimNames = dim_names
        obj.ResType = res_type
        obj._IsComplex = is_complex
        obj.MultiStepID = multi_step_id
        obj.AnalysisType = analysis_type

        if meta_data is not None:
            obj.MetaData = meta_data

        return obj

    def __array_finalize__(self, obj, **kwargs):
        # ``self`` is a new object resulting from
        # ndarray.__new__(InfoArray, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        if obj is None:
            return
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'info', because this
        # method sees all creation of default objects - with the
        # InfoArray.__new__ constructor, but also with
        # arr.view(InfoArray).
        self.Quantity = getattr(obj, "Quantity", None)
        self.Region = getattr(obj, "Region", None)
        self.StepValues = getattr(obj, "StepValues", np.empty(0))
        self._DimNames = getattr(obj, "_DimNames", None)
        self.ResType = getattr(obj, "ResType", cfs_result_type.UNDEFINED)
        self._IsComplex = getattr(obj, "_IsComplex", False)
        self.MultiStepID = getattr(obj, "MultiStepID", 1)
        self.AnalysisType = getattr(obj, "AnalysisType", cfs_analysis_type.NO_ANALYSIS)

    @property
    def DimNames(self) -> List[str]:
        """
        List of dimension names.

        Returns a list of dimension names for the result array. If the dimension names are not set, it returns a
        default list of dimension names based on the shape of the array. If the last dimension has size 1,
        it returns a single dimension name "-". Otherwise, it generates numbered names "dim_0", "dim_1", etc.

        Returns
        -------
        List[str]
            List of dimension names.

        """
        if self._DimNames is None:
            if self.shape[-1] == 1:
                return ["-"]
            else:
                return [f"dim_{i}" for i in range(self.shape[-1])]
        else:
            return self._DimNames

    @DimNames.setter
    def DimNames(self, value: List[str] | None):
        if value is None:
            self._DimNames = None
        elif isinstance(value, list):
            self._DimNames = value
        else:
            raise ValueError("DimNames must be a list of strings")

    @property
    def IsComplex(self) -> bool:
        """
        Flag indicating if the data is complex.

        If the value is None, it is automatically determined based on the analysis type.
        If the analysis type is harmonic, multiharmonic, eigenfrequency, or eigenvalue, complex-valued data is assumed.

        Returns
        -------
        bool
            True if the data is complex, False if it is real

        """
        if self._IsComplex is None:
            is_complex_dict = {
                cfs_analysis_type.NO_ANALYSIS: False,
                cfs_analysis_type.STATIC: False,
                cfs_analysis_type.TRANSIENT: False,
                cfs_analysis_type.HARMONIC: True,
                cfs_analysis_type.MULTIHARMONIC: True,
                cfs_analysis_type.EIGENFREQUENCY: True,
                cfs_analysis_type.INVERSESOURCE: False,
                cfs_analysis_type.MULTI_SEQUENCE: False,
                cfs_analysis_type.BUCKLING: False,
                cfs_analysis_type.EIGENVALUE: True,
            }

            return is_complex_dict[self.AnalysisType]
        else:
            return self._IsComplex

    @IsComplex.setter
    def IsComplex(self, value: bool | None):
        if value is None:
            self._IsComplex = None
        elif isinstance(value, bool):
            self._IsComplex = value
        else:
            raise ValueError("IsComplex must be a boolean value")

    @property
    def ResultInfo(self) -> CFSResultInfo:
        return CFSResultInfo(
            quantity=self.Quantity,
            region=self.Region,
            res_type=self.ResType,
            dim_names=self.DimNames,
            step_values=self.StepValues,
            is_complex=self.IsComplex,
            multi_step_id=self.MultiStepID,
            analysis_type=self.AnalysisType,
            data_shape=self.shape,
        )

    # noinspection LongLine
    @property
    def MetaData(self) -> Dict:
        """
        CFS meta data of the result array.

        This property returns a dictionary containing the meta data of the result array, including information such
        as quantity, region, step values, dimension names, result type, complexity, multi-step ID, and analysis type.
        (AI-generated)

        Returns
        -------
        Dict
            A dictionary containing the meta data of the result array.

        Examples
        --------
        >>> from pyCFS.data.io import CFSResultArray
        >>> data = [0, 1, 2, 3]
        >>> result_array = CFSResultArray(data, quantity='quantity_name', region='region_name')
        >>> meta_data = result_array.MetaData
        >>> print(meta_data)
        {'Quantity': 'quantity_name', 'Region': 'region_name', 'StepValues': array([1.0,2.0,3.0,4.0], dtype=float64),
         'DimNames': ['-'], 'ResType': <cfs_result_type.UNDEFINED: 0>, 'IsComplex': False,
         'MultiStepID': 1, 'AnalysisType': <cfs_analysis_type.NO_ANALYSIS: 0>, 'DataShape': (4,10,1)}
        """
        return {
            "Quantity": self.Quantity,
            "Region": self.Region,
            "StepValues": self.StepValues,
            "DimNames": self.DimNames,
            "ResType": self.ResType,
            "IsComplex": self.IsComplex,
            "MultiStepID": self.MultiStepID,
            "AnalysisType": self.AnalysisType,
            "DataShape": self.shape,
        }

    @MetaData.setter
    def MetaData(self, meta_data: Dict):
        """Set CFS meta data"""
        if all(
            key in meta_data
            for key in (
                "Quantity",
                "Region",
                "StepValues",
                # "DimNames", # Optional
                "ResType",
                # "IsComplex", # Optional
                "MultiStepID",
                "AnalysisType",
            )
        ):
            self.Quantity = meta_data["Quantity"]
            self.Region = meta_data["Region"]
            self.StepValues = meta_data["StepValues"]
            if "DimNames" in meta_data:
                self.DimNames = meta_data["DimNames"]
            else:
                self.DimNames = None  # type: ignore[assignment]
            self.ResType = meta_data["ResType"]
            if "IsComplex" in meta_data:
                self.IsComplex = meta_data["IsComplex"]
            else:
                self.IsComplex = None  # type: ignore[assignment]
            self.MultiStepID = meta_data["MultiStepID"]
            self.AnalysisType = meta_data["AnalysisType"]
        else:
            # noinspection LongLine
            raise ValueError(
                "meta_data dictionary must contain keys: 'Quantity','Region','StepValues','ResType','MultiStepID','AnalysisType'"
            )
        if "IsComplex" in meta_data:
            self.IsComplex = meta_data["IsComplex"]
        else:
            self.IsComplex = None  # type: ignore[assignment]
        if "DimNames" in meta_data:
            self.DimNames = meta_data["DimNames"]
        else:
            self.DimNames = None  # type: ignore[assignment]

    @property
    def DataArray(self) -> np.ndarray:
        """return array as numpy ndarray"""
        if self.ndim == 3 and self.shape[2] == 1:
            return np.squeeze(np.array(self), axis=2)
        else:
            return np.array(self)

    def set_meta_data(
        self,
        quantity: str | None = None,
        region: str | None = None,
        step_values: np.ndarray | None = None,
        dim_names: List[str] | None = None,
        res_type: cfs_result_type | None = None,
        is_complex: bool | None = None,
        multi_step_id: int | None = None,
        analysis_type: cfs_analysis_type | None = None,
    ):
        """
        Set the meta data for the CFS result array. Leaves not provided arguments unchanged.

        This method allows setting various meta data attributes for the CFS result array, such as quantity, region,
        step values, dimension names, result type, complexity, multi-step ID, and analysis type. (AI-generated)

        Parameters
        ----------
        quantity : str, optional
            Name of the quantity. The default is ``None``.
        region : str, optional
            Name of the region on which the result array is defined. The default is ``None``.
        step_values : np.ndarray, optional
            Step values (e.g., time stamps). The default is ``None``.
        dim_names : list of str, optional
            List of dimension labels. The default is ``None``.
        res_type : cfs_result_type, optional
            Enum indicating the entity on which the result array is defined. The default is ``None``.
        is_complex : bool, optional
            Flag indicating if the data is complex. The default is ``None``.
        multi_step_id : int, optional
            ID of the multi-step. The default is ``None``.
        analysis_type : cfs_analysis_type, optional
            Enum indicating the analysis type. The default is ``None``.

        Examples
        --------
        >>> from pyCFS.data.io import CFSResultArray
        >>> from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
        >>> data = [0, 1, 2, 3]
        >>> result_array = CFSResultArray(data)
        >>> result_array.set_meta_data(quantity='quantity_name', region='region_name', step_values=np.array([0, 1, 2, 3]),
        >>>                            dim_names=['-'], res_type=cfs_result_type.NODE, is_complex=False, multi_step_id=1,
        >>>                            analysis_type=cfs_analysis_type.TRANSIENT)
        """
        if quantity is not None:
            self.Quantity = quantity
        if region is not None:
            self.Region = region
        if step_values is not None:
            self.StepValues = step_values
        if dim_names is not None:
            self.DimNames = dim_names
        if res_type is not None:
            self.ResType = res_type
        if is_complex is not None:
            self.IsComplex = is_complex
        if multi_step_id is not None:
            self.MultiStepID = multi_step_id
        if analysis_type is not None:
            self.AnalysisType = analysis_type

    @property
    def IsHistory(self) -> bool:
        return cfs_types.check_history(self.ResType)

    def require_shape(self, verbose=True) -> CFSResultArray:
        """
        Reshape the result array to the expected shape based on the number of dimensions and step values.

        Returns
        -------
        CFSResultArray
            The reshaped result array.

        """
        if len(self.shape) != len(set(self.shape)):
            vprint(
                f"Warning: Array shape {self.shape} is not unique! This can lead to unexpected results.",
                verbose=verbose,
            )

        correct_shape: Optional[Tuple] = None
        if self.IsHistory:
            if self.ndim == 1:
                if self.shape[0] == self.StepValues.size:
                    # Assume singe point history result
                    correct_shape = (self.shape[0], 1)
                else:
                    # Assume single step history result
                    correct_shape = (1, self.shape[0])
            elif self.ndim > 2:
                # Too many dimensions for history result
                return self.squeeze().require_shape()  # type: ignore[attr-defined]
            else:
                try:
                    self.check_result_array()
                except AssertionError:
                    # Axes are not in the correct order
                    correct_shape = (self.StepValues.size, len(self.DimNames))
                except Exception as e:
                    raise e
        else:
            match self.ndim:
                case 1:
                    if self.shape[0] == self.StepValues.size:
                        # Assume single point region scalar result
                        correct_shape = (self.shape[0], 1, 1)
                    elif self._DimNames is not None and self.shape[0] == len(self._DimNames):
                        # Assume single step point region vector result
                        correct_shape = (1, 1, self.shape[0])
                    else:
                        # Assume single step scalar result
                        correct_shape = (1, self.shape[0], 1)
                        if self.StepValues.size != 1:
                            self.StepValues = np.array([0.0])
                            print("Warning: StepValues set to [0.0] for single step scalar result")
                case 2:
                    if self.shape[0] == self.StepValues.size:
                        if self._DimNames is not None and self.shape[1] == len(self._DimNames):
                            # Assume single point region vector result
                            correct_shape = (self.shape[0], 1, self.shape[1])
                        else:
                            # Assume Scalar result
                            correct_shape = (self.shape[0], self.shape[1], 1)
                    else:
                        # Assume single time step vector result
                        correct_shape = (1, self.shape[0], self.shape[1])
                case _:
                    if self.ndim > 3:
                        return self.squeeze().require_shape()  # type: ignore[attr-defined]
                    else:
                        try:
                            self.check_result_array()
                        except AssertionError as e:
                            # Axes are not in the correct order
                            shape = list(self.shape)
                            if (
                                len(shape) != len(set(shape))
                                and self.StepValues.size != len(self.DimNames)
                                or len(set(shape)) == 1
                            ):
                                print("Warning: No unique shape found for result array")
                                raise e
                            if self.StepValues.size in shape:
                                shape.remove(self.StepValues.size)
                            if len(self.DimNames) in shape:
                                shape.remove(len(self.DimNames))
                            correct_shape = (self.StepValues.size, shape[0], len(self.DimNames))
                        except Exception as e:
                            raise e
        if correct_shape:
            return self.reshape(correct_shape)  # type: ignore[return-value]
        else:
            return self

    def sort_steps(self, idx_sort=None, return_idx=False) -> None | np.ndarray:
        """
        Sort the data array by increasing step values or custom order of step values.

        Parameters
        ----------
        idx_sort : np.ndarray, optional
            Index array used for sorting. If None, the array is sorted based on increasing `StepValues`. The default is None.
        return_idx : bool, optional
            If True, return the index array used for sorting. The default is False.

        Returns
        -------
        None or np.ndarray
            If `return_idx` is True, returns the index array used for sorting.
        """
        if idx_sort is None:
            idx_sort = np.argsort(self.StepValues)

        self[:] = self[idx_sort, ...]
        self.StepValues[:] = self.StepValues[idx_sort]

        if return_idx:
            return idx_sort
        else:
            return None

    def check_result_array(self, mesh: Optional[CFSMeshData] = None) -> bool:
        """
        Check result array for consistency and validity.

        Parameters
        ----------
        mesh: CFSMeshData, optional
            Mesh data object to check result array shapes against.

        Returns
        -------
        bool
            True if result array is valid, raises AssertionError otherwise.

        """
        if np.iscomplexobj(self):
            assert (
                self.IsComplex
            ), f"Data array for {self.ResultInfo} contains complex data, but IsComplex is set to False."
        else:
            if self.IsComplex:
                print(
                    f"Warning: Data array for {self.ResultInfo} is real valued, but IsComplex is set to True. "
                    "This leads to larger file size."
                )

        if np.any(np.isnan(self)):
            idx_nan = np.argwhere(np.isnan(self))
            print(f"Warning: Data array for {self.ResultInfo} contains NaN values at (step, dof, dim): {idx_nan}.")

        if cfs_types.check_history(self.ResType):
            ndim = 2
        else:
            ndim = 3

        assert (
            self.ndim == ndim
        ), f"Data array {self.ResultInfo} has invalid number of dimensions ({self.ndim} != {ndim})."
        assert self.shape[-1] == len(
            self.DimNames
        ), f"Data array {self.ResultInfo} dimension labels ({len(self.DimNames)}) mismatch with number of data dimensions ({self.shape[-1]})."  # noqa : E501
        assert self.shape[0] == len(
            self.StepValues
        ), f"Data array {self.ResultInfo} step values ({self.shape[0]}) mismatch with number of steps ({self.StepValues})."

        if mesh is not None:
            assert (
                self.Region in mesh.Regions
            ), f"Data array {self.ResultInfo} region not found in mesh regions {[reg.Name for reg in mesh.Regions]}."
            item_reg = mesh.get_region(self.Region)
            if self.ResType == cfs_result_type.NODE:
                assert (
                    self.shape[1] == item_reg.Nodes.size
                ), f"Data array {self.ResultInfo} mismatch of number of data points ({self.shape[1]}) with region nodes ({item_reg.Name}: {item_reg.Nodes.size})"  # noqa : E501
            if self.ResType == cfs_result_type.ELEMENT:
                assert (
                    self.shape[1] == item_reg.Elements.size
                ), f"Data array {self.ResultInfo} mismatch of number of data points ({self.shape[1]}) with region elements ({item_reg.Name}: {item_reg.Elements.size})"  # noqa : E501

        return True


class CFSResultInfo:
    """
    Data structure containing result information for one result.

    .. figure:: ../../../docs/source/resources/data_structures_CFSResultInfo.png

    """

    def __init__(
        self,
        quantity: str | None = None,
        region: str | None = None,
        res_type=cfs_result_type.UNDEFINED,
        dim_names: List[str] | None = None,
        step_values: np.ndarray | None = None,
        is_complex=False,
        multi_step_id=1,
        analysis_type=cfs_analysis_type.NO_ANALYSIS,
        data_shape: tuple = (),
    ) -> None:

        if step_values is None:
            step_values = np.empty(0)
        if dim_names is None:
            dim_names = ["-"]

        self.Quantity = quantity
        self.Region = region
        self.ResType = res_type
        self.DimNames = dim_names
        self.StepValues = step_values
        self.IsComplex = is_complex
        self.MultiStepID = multi_step_id
        self.AnalysisType = analysis_type
        self.DataShape = data_shape

    @classmethod
    def from_meta_data(cls, meta_data: Dict):
        return cls(
            quantity=meta_data["Quantity"],
            region=meta_data["Region"],
            res_type=meta_data["ResType"],
            dim_names=meta_data["DimNames"],
            step_values=meta_data["StepValues"],
            is_complex=meta_data["IsComplex"],
            multi_step_id=meta_data["MultiStepID"],
            analysis_type=meta_data["AnalysisType"],
            data_shape=meta_data["DataShape"],
        )

    @property
    def MetaData(self) -> Dict:
        return {
            "Quantity": self.Quantity,
            "Region": self.Region,
            "StepValues": self.StepValues,
            "DimNames": self.DimNames,
            "ResType": self.ResType,
            "IsComplex": self.IsComplex,
            "MultiStepID": self.MultiStepID,
            "AnalysisType": self.AnalysisType,
            "DataShape": self.DataShape,
        }

    def __eq__(self, other: object | str) -> bool:
        if isinstance(other, str):
            return self.Quantity == other
        if isinstance(other, CFSResultInfo):
            return self.Quantity == other.Quantity and self.Region == other.Region and self.ResType == other.ResType
        else:
            raise Exception(f"Comparison for types {type(self)} - {type(other)} not implemented")

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        complex_str = {0: "real", 1: "complex"}
        return f"'{self.Quantity}' ({complex_str[self.IsComplex]}) defined in '{self.Region}' on {self.ResType}"
