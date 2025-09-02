"""
Module defining data structures describing the result data.

.. figure:: ../../../docs/source/resources/data_structures_overview.png

"""

from __future__ import annotations

import collections
import textwrap

import numpy as np
from typing import List, Dict, Sequence, Optional, TYPE_CHECKING

from pyCFS.data.io import CFSRegData

from pyCFS.data.io._CFSArrayModule import CFSResultArray, CFSResultInfo
from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type, check_history
from pyCFS.data.util import progressbar, vprint

from pyCFS.data._v_def import v_def

if TYPE_CHECKING:
    from pyCFS.data.io._CFSMeshDataModule import CFSMeshData


# noinspection PyAttributeOutsideInit
class CFSResultContainer:
    """
    Data structure containing result data (one object supports currently a single MultiStep only!)

    .. figure:: ../../../docs/source/resources/data_structures_CFSResultData.png

    Parameters
    ----------
    data : Sequence[pyCFS.data.io.CFSResultArray], optional
        Sqeuence of result arrays. The default is ``None`` in which case the result data object will be initialized empty.
    analysis_type : pyCFS.data.io.cfs_types.cfs_analysis_type, optional
        Analysis type to overwrite the one specified in data. Definitions based on pyCFS.data.io.cfs_types.cfs_analysis_type.
    multi_step_id : int, optional
        MultiStep (also known as SequenceStep) ID to overwrite the one specified in data.
    verbosity : int, optional
        Verbosity level <=1000 ; see _v_def.py for predefined levels. Default is v_def.release.

    Attributes
    ----------
    AnalysisType : pyCFS.data.io.cfs_types.cfs_analysis_type
        Analysis type. Definitions based on pyCFS.data.io.cfs_types.cfs_analysis_type. The default is ``NO_ANALYSIS``.
    MultiStepID : int
        MultiStep (also known as SequenceStep) ID. The default value is ``1``.
    Data : List[pyCFS.data.io.CFSResultArray]
        List of data arrays containing result data (with metadata).
    ResultInfo : List[pyCFS.data.io.CFSResultInfo]
        List of structures containing information about the corresponding CFSResultArray object in self.Data.
    StepValues : numpy.ndarray
        Step Values of MultiStep property. All data sets of one MultiStep must have the same step values currently!

    Notes
    -----
    -  ``extract_quantity_region`` Return CFSResult of extracted quantity and region.

    -  ``get_data_array`` Return CFSResultArray for certain quantity and region.

    -  ``get_data_arrays`` Return list of CFSResultArrays for certain quantities and regions.

    -  ``get_multi_step_step_values`` Get step values for a specific multi-step ID.

    -  ``set_multi_step_step_values`` Set step values for a specific multi-step ID.

    -  ``set_multi_step_analysis_type`` Set analysis type for a specific multi-step ID.

    -  ``combine_with`` Merges result data structures

    -  ``add_data_array`` Add data using CFSResultArray or np.ndarray in combination with meta_data

    -  ``add_data`` Add data to CFSResultData object

    -  ``sort_steps`` Sort data arrays by increasing step values.

    -  ``check_result`` Check result data for consistency and validity.

    -  ``require_container`` Static method to ensure input is a CFSResultContainer object.

    Examples
    --------
    >>> import numpy
    >>> from pyCFS.data.io import CFSResultArray, CFSResultContainer
    >>> from pyCFS.data.io.cfs_types import cfs_result_type
    >>> data = numpy.array([0,1,2,3])
    >>> result_array = CFSResultArray(data,quantity='quantity_name', region='region_name', step_value=0,
    >>>                               dim_names=['-'], defined_on=cfs_result_type.NODE, is_complex=True)
    >>> result_data = CFSResultContainer(data=[result_array],multi_step_id=2)

    """

    def __init__(
        self,
        data: Sequence[CFSResultArray] | None = None,
        analysis_type: Optional[cfs_analysis_type] = None,
        multi_step_id: Optional[int] = None,
        verbosity=v_def.release,
    ):
        self._Verbosity = verbosity
        self._AnalysisType = cfs_analysis_type.NO_ANALYSIS
        self._MultiStepID = 1
        self.Data: List[CFSResultArray] = []  # List of Result Data Arrays
        if data is not None:
            if isinstance(data, collections.abc.Sequence):
                if len(data) > 0:
                    # Check if all arrays hav the same MultiStepID and AnalysisType
                    analysis_type_set = set([item.AnalysisType for item in data])
                    multi_step_id_set = set([item.MultiStepID for item in data])
                    if len(analysis_type_set) > 1 or len(multi_step_id_set) > 1:
                        print(
                            "Warning: Data arrays have different AnalysisType or MultiStepID! "
                            "Using first data array's AnalysisType and MultiStepID."
                        )
                    # Use metadata of first data array to set MultiStepID and AnalysisType
                    self.AnalysisType = data[0].AnalysisType
                    self.MultiStepID = data[0].MultiStepID

                    for item in data:
                        self.add_data_array(item)
            else:
                raise TypeError("'data' must be a Sequence of CFSResultArray objects!")
        if analysis_type is not None:
            self.AnalysisType = analysis_type
        if multi_step_id is not None:
            self.MultiStepID = multi_step_id

    def __repr__(self) -> str:
        return f"""MultiStep {self.MultiStepID}: {self.AnalysisType}, {self.StepValues.size} steps"""

    # noinspection PyArgumentList
    def __str__(self) -> str:
        info_str = str().join([f" - {ri}\n" for ri in self.ResultInfo])
        return textwrap.dedent(
            f"MultiStep {self.MultiStepID}: {self.AnalysisType}, {self.StepValues.size} steps \n{info_str}"
        )

    def __getitem__(self, index: int | slice) -> CFSResultContainer:
        """
        Extract steps from a CFSResultData object.

        Parameters
        ----------
        index : int | slice
            Indices to extract from CFSResultData object.

        Returns
        -------
        pyCFS.data.io.CFSResultContainer
            Extracted CFSResultData object.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result_data = f.MultiStepData
        >>> result_data_extract = result_data[0:2]

        """
        result_data = CFSResultContainer(
            analysis_type=self.AnalysisType, multi_step_id=self.MultiStepID, verbosity=self._Verbosity
        )

        # if isinstance(index, slice):
        for data_array in self.Data:
            result_data.add_data_array(data_array[index, ...], step_values=data_array.StepValues[index])

        return result_data

    def __add__(self, other: CFSResultContainer) -> CFSResultContainer:
        return self.combine_with(other, resolve_match="add")

    def __eq__(self, other) -> bool:
        if not isinstance(other, CFSResultContainer):
            return False

        data_equality = len(self.Data) == len(other.Data)
        for i in range(len(self.Data)):
            if data_equality:
                if self.ResultInfo[i] in other.ResultInfo:
                    idx_other = other.ResultInfo.index(self.ResultInfo[i])
                    data_equality = np.array_equal(self.Data[i], other.Data[idx_other])
                else:
                    return False
            else:
                return False

        return all(
            [
                data_equality,
                self.AnalysisType == other.AnalysisType,
                self.MultiStepID == other.MultiStepID,
            ]
        )

    @property
    def MultiStepID(self) -> int:
        """
        MultiStep ID (CFSResultContainer can contain data from only one MultiStep currently!)
        """
        return self._MultiStepID
        # if self.ResultInfo:
        #     id_collection = [r_info.MultiStepID for r_info in self.ResultInfo]
        #     return set(id_collection)

    @MultiStepID.setter
    def MultiStepID(self, multi_step_id: int):
        self._MultiStepID = multi_step_id
        for r_array in self.Data:
            r_array.MultiStepID = multi_step_id

    @property
    def AnalysisType(self) -> cfs_analysis_type:
        """
        Analysis type of MultiStepData (CFSResultContainer can contain data from only one MultiStep currently!)
        """
        return self._AnalysisType
        # if self.ResultInfo:
        #     analysis_type_collection = [r_info.AnalysisType for r_info in self.ResultInfo]
        #     return set(analysis_type_collection)

    @AnalysisType.setter
    def AnalysisType(self, analysis_type: cfs_analysis_type):
        self._AnalysisType = analysis_type
        for r_info in self.ResultInfo:
            r_info.AnalysisType = analysis_type

    @property
    def ResultInfo(self) -> List[CFSResultInfo]:
        """
        Structure containing information about the corresponding CFSResultArray object in self.Data

        Returns
        -------
        list[CFSResultInfo]
            List of CFSResultInfo objects corresponding to list of CFSResultArray objects in self.Data
        """
        if self.Data:
            return [r_array.ResultInfo for r_array in self.Data]
        else:
            return []

    @property
    def Regions(self) -> List[str | None]:
        """
        List of regions of all data arrays
        """
        return list(set([item.Region for item in self.Data]))

    @property
    def Quantities(self) -> List[str | None]:
        """
        List of quantities of all data arrays
        """
        return list(set([item.Quantity for item in self.Data]))

    @property
    def StepValues(self) -> np.ndarray:
        """
        Step Values of MultiStep property. All data sets of one MultiStep must have the same
        step values currently!
        """
        return self.get_multi_step_step_values(multi_step_id=self.MultiStepID)

    @StepValues.setter
    def StepValues(self, step_values: np.ndarray | List[float]):
        self.set_multi_step_step_values(step_values)

    def get_multi_step_step_values(self, multi_step_id=1) -> np.ndarray:
        for item in self.Data:
            if item.MultiStepID == multi_step_id:
                return item.StepValues
        return np.empty(0)

    def set_multi_step_step_values(self, step_values: np.ndarray | List[float], multi_step_id=1):
        for item in self.Data:
            if item.MultiStepID == multi_step_id:
                item.StepValues = np.array(step_values)

    def set_multi_step_analysis_type(self, analysis_type: cfs_analysis_type, multi_step_id=1):
        vprint(
            f"Setting AnalysisType {self.AnalysisType} -> {analysis_type}",
            verbose=self._Verbosity >= v_def.debug,
        )
        self.AnalysisType = analysis_type
        for item in self.Data:
            if item.MultiStepID == multi_step_id:
                item.AnalysisType = analysis_type

    def extract_quantity_region(
        self,
        quantity: str | Sequence[str] | None = None,
        region: str | CFSRegData | Sequence[str | CFSRegData] | None = None,
        restype: cfs_result_type | Sequence[cfs_result_type] | None = None,
    ) -> CFSResultContainer:
        """
        Return CFSResult of extracted quantity and region.

        Parameters
        ----------
        quantity : str
            Name of the result quantity.
        region : str
            Name of the region on which the result is defined.
        restype : pyCFS.data.io.cfs_types.cfs_result_type, optional
            Type of the result data. The default is ``None`` in which case the result type is identified automatically.
            Only works, if there are not multiple result types specified.

        Returns
        -------
        pyCFS.data.io.CFSResultContainer
            Extracted CFSResultData object.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result_data = f.MultiStepData
        >>> result_data_extract = result_data.extract_quantity_region(quantity='quantity', region='region')

        """

        if type(quantity) is str:
            quantity_lst = [quantity]
        else:
            quantity_lst = quantity  # type: ignore[assignment]
        if type(region) is str or type(region) is CFSRegData:
            region_lst = [region]
        else:
            region_lst = region  # type: ignore[assignment]
        if type(restype) is cfs_result_type:
            restype_lst = [restype]
        else:
            restype_lst = restype  # type: ignore[assignment]

        data_arrays = self.get_data_arrays(quantities=quantity_lst, regions=region_lst, restypes=restype_lst)

        return CFSResultContainer(
            data=data_arrays, analysis_type=self.AnalysisType, multi_step_id=self.MultiStepID, verbosity=self._Verbosity
        )

    def get_data_array(
        self, quantity: str, region: str | CFSRegData, restype: cfs_result_type | None = None
    ) -> CFSResultArray:
        """
        Return CFSResultArray for certain quantity and region.

        Parameters
        ----------
        quantity : str
            Name of the result quantity.
        region : str
            Name of the region on which the result is defined.
        restype : pyCFS.data.io.cfs_types.cfs_result_type, optional
            Type of the result data. The default is ``None`` in which case the result type is identified automatically.
            Only works, if there are not multiple result types specified.

        Returns
        -------
        pyCFS.data.io.CFSResultArray
            Extracted result data arrays.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result_data = f.MultiStepData
        >>> result_array = result_data.get_data_array(quantity='quantity', region='region')

        """
        for item in progressbar(self.Data, "Get data array: ", verbose=self._Verbosity >= v_def.debug):
            if quantity == item.Quantity and region == item.Region:
                if restype is None or restype == item.ResType:
                    return item
        raise LookupError(f"Could not find result data array for ({quantity}, {region})")

    def get_data_arrays(
        self,
        quantities: Sequence[str] | None = None,
        regions: Sequence[str | CFSRegData] | None = None,
        restypes: Sequence[cfs_result_type] | None = None,
    ) -> List[CFSResultArray]:
        """
        Return list of CFSResultArrays for certain quantities and regions.

        Parameters
        ----------
        quantities : list[str], optional
            List of result quantities. If None, all quantities are considered.
        regions : list[str], optional
            List of regions. If None, all regions are considered.

        Returns
        -------
        list[CFSResultArray]
            List of extracted result data arrays.

        Examples
        --------
        >>> from pyCFS.data.io import CFSReader
        >>> with CFSReader('file.cfs') as f:
        >>>     result_data = f.MultiStepData
        >>> result_arrays = result_data.get_data_arrays(quantities=['quantity1', 'quantity2'], regions=['region1'])
        """
        result_arrays = [
            item
            for item in progressbar(self.Data, "Get data arrays: ", verbose=self._Verbosity >= v_def.debug)
            if (regions is None or item.Region in regions)
            and (quantities is None or item.Quantity in quantities)
            and (restypes is None or item.ResType in restypes)
        ]
        return result_arrays

    def combine_with(self, other: CFSResultContainer, resolve_match="exception") -> CFSResultContainer:
        """
        Merges result data structures

        Parameters
        ----------
        other : CFSResultContainer
        resolve_match : str, optional
            'exception' (Default) raises exception on matching datasets, 'add' adds datasets on matching datasets

        Returns
        -------
        CFSResultContainer
        """
        for array_idx, r_data in enumerate(other.Data):
            if r_data.Quantity is None or r_data.Region is None:
                raise ValueError(f"MetaData {r_data.MetaData} of result not properly defined!")
            # Check if dataset alread exists
            try:
                r_data_match = self.get_data_array(
                    quantity=r_data.Quantity, region=r_data.Region, restype=r_data.ResType
                )
            except LookupError:
                self.add_data_array(data=r_data)
            else:
                if resolve_match == "add":
                    r_data_match += r_data  # type: ignore[misc]
                else:
                    raise Exception("Region already exists")
        return self

    def add_data_array(
        self,
        data: CFSResultArray | np.ndarray,
        *,
        step_values: np.ndarray = np.empty(0),
        quantity: str | None = None,
        region: str | None = None,
        res_type: cfs_result_type | None = None,
        dim_names: List[str] | None = None,
        is_complex: bool | None = None,
        multi_step_id: int | None = None,
        analysis_type: cfs_analysis_type | None = None,
        meta_data: Dict | None = None,
    ):
        """
        Add data using CFSResultArray or np.ndarray in combination with meta_data

        Parameters
        ----------
        data : np.ndarray | CFSResultArray
            data to be added. Supported shapes: (n, m, d) or (n,m) with n steps, m DOFs and d dimensions
        step_values : np.ndarray | list[float], optional, kwarg
            step values to overwrite from MetaData
        quantity : str, optional, kwarg
            name of data quantity to overwrite from MetaData
        region : str, optional, kwarg
            region on which data is added to overwrite from MetaData
        res_type : cfs_result_type, optional, kwarg
            result type based on cfs_result_type to overwrite from MetaData
        dim_names : list[str], optional, kwarg
            list of DIM labels to overwrite from MetaData
        is_complex : bool, optional, kwarg
            flag wheter added data is real or complex, to overwrite from MetaData
        multi_step_id : int, optional, kwarg
            MultiStep ID to overwrite from MetaData
        analysis_type : cfs_types.cfs_analysis_type, optional, kwarg
            AnalyisType to overwrite from MetaData
        meta_data : dict , optional, kwarg
            meta_data dictionary. Must contain keys:
            'Quantity','Region','StepValues','DimNames','ResType','IsComplex','MultiStepID','AnalysisType'

        Examples
        ---
        >>> import numpy as np
        >>> from pyCFS.data.io import CFSResultContainer
        >>> from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
        >>> result = CFSResultContainer()
        >>> data = CFSResultArray(np.ones((5,3,1)))
        >>> data.set_meta_data(quantity='Quantity', region='Region', step_values=np.array([0,1,2,3,4],dtype=float),
        >>>              dim_names=['-'], res_type=cfs_result_type.NODE, is_complex=False,
        >>>              multi_step_id=1, analysis_type=cfs_analysis_type.TRANSIENT)
        >>> result.add_data_array(data)

        """
        if not isinstance(data, CFSResultArray):
            if isinstance(data, np.ndarray):
                if meta_data is None:
                    raise ValueError(
                        "Provide either a CFSResultArray object or meta_data dict in combination with numpy.ndarray"
                    )
                else:
                    data = CFSResultArray(data)
            else:
                raise TypeError("Provide either a CFSResultArray object or numpy.ndarray.")
        if meta_data is not None:
            data.MetaData = meta_data
        if step_values.size != 0:
            data.StepValues = step_values
        if quantity is not None:
            data.Quantity = quantity
        if region is not None:
            data.Region = region
        if res_type is not None:
            data.ResType = res_type
        if dim_names is not None:
            data.DimNames = dim_names
        if is_complex is not None:
            data.IsComplex = is_complex
        else:
            data.IsComplex = data.IsComplex or bool(np.any(np.iscomplex(data)))
        if multi_step_id is not None:
            data.MultiStepID = multi_step_id
        if analysis_type is not None:
            data.AnalysisType = analysis_type
        elif self.AnalysisType == cfs_analysis_type.NO_ANALYSIS:
            self.AnalysisType = data.AnalysisType

        data = data.require_shape(verbose=self._Verbosity >= v_def.debug)
        data.check_result_array()

        # Check if result info already exists
        if self._get_result_info(
            multi_step_id=data.MultiStepID, quantity=data.Quantity, region=data.Region, res_type=data.ResType
        ):
            raise Exception("Result already exists. Overwriting result currently not supported!")

        # Check if result info is consistent
        if self._get_result_info(multi_step_id=data.MultiStepID):
            vprint(
                f"Adding data to existing MultiStep {data.MultiStepID}",
                verbose=self._Verbosity >= v_def.debug,
            )

            # Check StepValues
            if not np.array_equal(data.StepValues, self.get_multi_step_step_values(data.MultiStepID)):
                raise Exception("Step values of added data do not match step values of existing multi step data.")

        self.Data.append(data)

    # noinspection PyPep8Naming
    def add_data(
        self,
        data: np.ndarray,
        *,
        step_values: np.ndarray,
        quantity: str,
        region: str | CFSRegData,
        restype: cfs_result_type,
        dim_names: List[str] | None = None,
        is_complex: bool | None = None,
        multi_step_id: int | None = None,
        analysis_type: cfs_analysis_type | None = None,
    ):
        """
        Add data to CFSResultData object

        Parameters
        ----------
        data : np.ndarray
            data to be added. Supported shapes: (n, m, d) or (n,m) with n steps, m DOFs and d dimensions
        step_values : np.ndarray, kwarg
            step values (needs to match old data)
        quantity : str, kwarg
            name of data quantity
        region : str or CFSRegData, kwarg
            region on which data is added
        restype : cfs_result_type, kwarg
            result type based on cfs_result_type
        dim_names : list[str], optional, kwarg
            list of DIM labels
        is_complex : bool, optional, kwarg
            flag wheter added data is real or complex, determine automatically if None (can yield real results if
            complex numpy array has zero imaginary part)
        multi_step_id : int, optional, kwarg
            MultiStep ID, if not specified retrieve from CFSResultData parent object
        analysis_type : cfs_types.cfs_analysis_type, optional, kwarg
            AnalyisType, if not specified retrieve from CFSResultData parent object

        Examples
        ---
        >>> import numpy as np
        >>> from pyCFS.data.io import CFSResultContainer
        >>> from pyCFS.data.io.cfs_types import cfs_result_type, cfs_analysis_type
        >>> result = CFSResultContainer()
        >>> data = np.ones((5,3,1))
        >>> result.add_data(data, step_values=np.array([0,1,2,3,4],dtype=float), quantity='Quantity', region='Region',
        >>>                 dim_names=['-'], res_type=cfs_result_type.NODE, is_complex=False, multi_step_id=1,
        >>>                 analysis_type=cfs_analysis_type.TRANSIENT)

        """
        if isinstance(region, CFSRegData):
            region = region.Name

        # Check MultiStepID
        if multi_step_id is None:
            multi_step_id = self.MultiStepID

        # Check analysis type
        if analysis_type is None:
            analysis_type = self.AnalysisType
        elif analysis_type != self.AnalysisType:
            self.set_multi_step_analysis_type(analysis_type=analysis_type, multi_step_id=multi_step_id)

        self.add_data_array(
            data=CFSResultArray(
                data,
                quantity=quantity,
                region=region,
                step_values=step_values,
                dim_names=dim_names,
                res_type=restype,
                is_complex=is_complex,
                multi_step_id=multi_step_id,
                analysis_type=analysis_type,
            )
        )

    def sort_steps(self, return_idx=False) -> None | np.ndarray:
        """
        Sort data arrays by increasing step values.

        Returns
        -------
        np.ndarray
            index array used for sorting.
        """
        idx_sort = np.argsort(self.StepValues)
        for item in self.Data:
            item.sort_steps(idx_sort=idx_sort)

        if return_idx:
            return idx_sort
        else:
            return None

    def _get_result_info(
        self,
        multi_step_id=1,
        quantity: str | None = None,
        region: str | None = None,
        res_type: cfs_result_type | None = None,
    ) -> List[CFSResultInfo]:
        result_info_list = []
        for r_data in self.Data:
            if r_data.MultiStepID == multi_step_id:
                if quantity is None or r_data.Quantity == quantity:
                    if region is None or r_data.Region == region:
                        if res_type is None or r_data.ResType == res_type:
                            result_info_list.append(r_data.ResultInfo)

        return result_info_list

    def check_result(self: CFSResultContainer, mesh: Optional[CFSMeshData] = None) -> bool:
        """
        Check result data for consistency and validity.

        Parameters
        ----------
        self: CFSResultContainer
            Result data object to be checked.
        mesh: CFSMeshData, optional
            Mesh data object to check result data array shapes against.

        Returns
        -------
        bool
            True if result data is valid, raises AssertionError otherwise.

        """
        vprint("Checking result", verbose=self._Verbosity >= v_def.debug)
        # Check analysis type
        possible_types = [atype.value for atype in cfs_analysis_type]

        assert self.AnalysisType in possible_types, "Invalid analysis type."

        # StepValues
        for item in self.Data:
            np.testing.assert_array_equal(item.StepValues, self.StepValues, err_msg="StepValues mismatch.")

        # Sanity check for static analysis
        if self.AnalysisType == cfs_analysis_type.STATIC:
            if self.StepValues.size > 1:
                raise ValueError(
                    "Static analysis should only have one step value. "
                    f"Found {self.StepValues.size} step values: {self.StepValues}"
                )
        # Sanity check for complex data
        if any(item.IsComplex for item in self.Data):
            if self.AnalysisType in [
                cfs_analysis_type.STATIC,
                cfs_analysis_type.TRANSIENT,
            ]:
                raise ValueError(f"Complex data is not supported for static or transient analysis. \n{self}")

        # Data arrays
        for item in self.Data:
            assert (
                item.shape[0] == self.StepValues.size
            ), f"Data array {item.ResultInfo} mismatch with number of steps. ({item.shape[0]} != {self.StepValues.size})"

            item.check_result_array(mesh=mesh)

            if check_history(item.ResType):
                ndim = 2
            else:
                ndim = 3

            assert (
                item.ndim == ndim
            ), f"Data array {item.ResultInfo} has invalid number of dimensions ({item.ndim} != {ndim})."
            assert item.shape[-1] == len(
                item.DimNames
            ), f"Data array {item.ResultInfo} dimension labels ({len(item.DimNames)}) mismatch with number of data dimensions ({item.shape[-1]})."

        if mesh is None:
            vprint("Data array shapes not checked due to missing mesh data.", verbose=self._Verbosity >= v_def.debug)

        return True

    @staticmethod
    def require_container(
        result: CFSResultContainer | Sequence[CFSResultArray] | None = None, verbosity=v_def.release
    ) -> CFSResultContainer:
        if type(result) is CFSResultContainer:
            result_data = result
        elif isinstance(result, collections.abc.Sequence):
            result_data = CFSResultContainer(data=result, verbosity=verbosity)
        else:
            raise ValueError("Result data must be of type CFSResultContainer or Sequence[CFSResultArray]")

        return result_data
