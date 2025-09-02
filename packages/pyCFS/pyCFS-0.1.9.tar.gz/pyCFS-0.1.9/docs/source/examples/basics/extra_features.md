## Extra features

### Exporting system matrices

For more information regarding this topic and what is exactly exported please first read [this](https://opencfs.gitlab.io/userdocu/Tutorials/SystemMatrixExport/SystemMatrix/#extracting-system-matrices) entry in the `CFS` documentation.

To enable system matrices export in `pyCFS` we need to pass an additional argument (`export_matrices = True`) when executing a simulation with `pyCFS`. Assume we have set up a simulation like in the 3D capacitor example and we have our instance of the `pyCFS` object called `cap_sim`. To execute the simulation for a set of parameters and export the system matrices we would run 
```python
cap_sim(params, export_matrices = True)
``` 
The results are then to be found in `cap_sim.matrix_exports` which is a list of dictionaries. The length of the list is equal to the number of parameter sets in `params`. Each dictionary contains three exports : 
- `sol` : solution vector
- `rhs` : right hand side vector
- `sys` : system matrix

:::{important}
This mode is currently only available for serial execution. Running in parallel mode will also pass with a warning but the results wont be stored!
:::
