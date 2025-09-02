## Data handling 

OpenCFS results are stored as `hdf5` files. So all of the results that one wants to track need to be written out to the `hdf5` results file of OpenCFS. This way pyCFS can access these results in a coherent manner (Previously it was also possible to use history files but this is deprecated in favour of simpler data handling). 

### Data flow

Lets look at a simple example where one parameter combination is passed to the pyCFS simulation and observe how the data is extracted and stored. 

1. Run the simulation with parameters $\mathbf{x}$
2. After `OpenCFS` finishes there will be a new results file : 
   - Located in : 'results_hdf5/sim.cfs'
3. In the next step after successful `OpenCFS` run : 
   1. The `hdf5` results file is read
   2. The previously defined results are extracted 
   3. These are then added to the current results (in RAM, therefore one should not store the whole simulation here but just some values which are crucial for the computations which follow)
4. If the `OpenCFS` run was not successful : 
   1. The data for the current run will just be a nan or None
5. The user needs to specify in the setup file which results need to be tracked (one can also select to extract the whole `hdf5` file)
   1. Extracting the whole `hdf5` file is usually not necessary as it can be stored on the drive if needed (`save_hdf_results = True`)

### Data structure

Here the structure of the results is described. 

The results are in general stored internally in the `pyCFS` object as a `List[pyCFSResultDict]`. It is a list of result dictionaries because we can execute the simulation by passing a number of different parameter combinations. Due to this each parameter combination has an appropriate result dictionary. The index of the parameter combination is also the index of the result for this parameter combination.

The `pyCFSResultDict` has the following structure : 

1. *MultiStep_i* 
2. *Step_j*
3. *resultName*
4. *regionName*
5. data

It can be described by the following type : 

```python
#                           multistep_i  step_j    result   region
pyCFSResultDict : TypeAlias = Dict[str, Dict[str, Dict[str, Dict[str, resultArr]]]]
```