## Result handling

### Results

The main results are the results which are obtained from the *hdf* file produced by `openCFS` after a successful simulation. These results are stored internally into the `results` field and are of type `List[nestedResultDict]`. To allow an easier acquisition of the tracked results there are a few functions which provide useful options. 

### History results

History results from `openCFS` which are usually written to *.hist* files (just normal *txt* files) can also be written to the main *hdf* results file. 

:::{important}
`pyCFS` only handles history results which are saved to the main *hdf* results file.
:::

To set this up in your *xml* simulation file you just have to do the following. At the beginning of the file we need to add an output identifier for *hdf* files. 

```xml
<fileFormats>
    <!-- ... -->
    <output>
        <hdf5 id="hdf"/>
    </output>
    <!-- ... -->
</fileFormats>
```

Then we can define the history results as usual with the only difference being that we also specify `outputIds="hdf"`. 

```xml
<!-- Example calculating electrical energy in all regions -->
<regionResult type="elecEnergy">
    <allRegions outputIds="hdf"/>
</regionResult>
```

This way the history results will be written to the main *hdf* results file instead of the *.hist* files. 

The read history results are internally saved into `hist_results` which is a list of nested dictionaries `List[nestedResultDict]`.

### Sensor Arrays (not `CFS` sensor array)

:::{important}
`pyCFS` does not support the usage of `CFS` sensor arrays anymore! If you need a replacement please look below.
:::

Sensor Arrays in `pyCFS` allow you to specify a list of points in form of a *csv* file (`delimiter = ','`) at which to evaluate CFS results and save these results to the results *hdf* file. Using the actual `CFS` sensor array is problematic due to it, at 
this moment (20.1.2025), not being able to be written into the *hdf* result file, which complicates the handling of the data unnecessarily. 

:::{note}
Please note that using `pyCFS` sensor arrays is using the `CFS` feature for defining `nodeList`s and `elemList`s and therefore in contrast to the `CFS` sensor arrays, the `nodeResult`s will get mapped to the closest nodes in the mesh and the `elemResult`s will get mapped to the element in which the given node falls.
:::

To use `pyCFS` sensor arrays you need to add two things in your simulation setup : 
1. Define the `pyCFS` sensor arrays by constructing an information dictionary for each sensor array you want to use and pass these as a list of dictionaries to the `pyCFS` constructor.
    - `file_path` defining the path to the sensor array with name `result_name`
```python
# definition of two sensor arrays 
sensor_arrays = [{
                  "result_name": "SENSPOS1",
                  "file_path": "./input-data/sensor_positions.csv"}, 
                 {
                  "result_name": "SENSPOS2",
                  "file_path": "./input-data/sensor_positions_z.csv", 
                  },
                ]
```
2. Then you just need to specify which result quantity you want to evaluate at which sensor array. This is done by adding the sensor array identifier in your template *xml* simulation file. 
    - For example, we will use the snippet below if we want to evaluate the `elecPotential` quantity on sensor array `SENSPOS1` and to evaluate the quantity `elecFieldIntensity` at both `SENSPOS1` and `SENSPOS2`. Note, we can chain how many we want of the defined sensor arrays for a given quantity. It is important to use the `NODELIST` for `nodeResult`s and the `ELEMLIST` for `elemResult`s.
```xml
<nodeResult type="elecPotential">
    <allRegions/>
    SENSPOS1_NODELIST
</nodeResult>
<elemResult type="elecFieldIntensity">
    <allRegions/>
    SENSPOS1_SENSPOS2_ELEMLIST
</elemResult>
```  