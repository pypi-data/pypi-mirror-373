## A first simulation

### Example : 3D Capacitor

The following tutorial builds upon [this](https://opencfs.gitlab.io/userdocu/Tutorials/Electrostatics_Capacitor/) `openCFS` tutorial. In the case that you are not familiar with `openCFS` it would be good to check it out first.

The main goal is to have the ability to execute the given simulation from a python file without having to manually change any of the simulation files. In this example with the capacitor simulation, we will go file by file and demonstrate how to set up the individual files and how to link everything together in the python file.
 
Let's say that for the investigation we are interested in three parameters are introduced. These are : 

- `V_TOP` and `V_BOTTOM` : which are the electric potentials on the upper and lower plates of the capacitor
- `PLATE_DIST` : which is the distance between the plates of the capacitor

:::{note}
To make it simple : just place the parameter names instead of the actual values in the simulation files. In this example we show also how to define a variable in the `openCFS` *xml* schema but it is not necessary.
:::

To reflect this we need to adapt the template files such that the parameters we have defined are also used. 

```xml
<variableList>
    <var name="V_top" value="V_TOP"/>
    <var name="V_bottom" value="V_BOTTOM"/>
</variableList>
```

This means also changing the journal file accordingly.

```
#{ d = PLATE_DIST }
```

#### Controlling the simulation

Now, what remains is to link our template files with the Python code. To show what a python simulation file looks like and how to set our parameters as well as the type of simulation, we will go line by line through the code to show what the final version of the python simulation file should look like.

First, we need to import the following libraries :

```python
import numpy as np
from pyCFS import pyCFS
```

Next, we need to configure `pyCFS` for the current simulation.

We do this by defining the simulation name and the path to the executable cfs file:

```python
project_name = "capacitor"
# path to the cfs bin directory : 
cfs_path = "/home/mypc/Public/CFS/build_opt/bin/"
# path to the coreform/trelis executable : 
trelis_path = "/home/share/coreform-cubit"
```

:::{important}
The `project_name` needs to be the same name as the template *xml* and *jou* file without the *_init* part.
:::

Now we can bridge the gap between the template files and the python file by introducing the parameter names. 
First, we have the `cfs_params` list, which contains the names of the parameters to be changed in the *capacitor_init.xml* file. Then we have the `trelis_params` list, which contains parameters whose values will be changed in the *capacitor.jou* file.

```python
# Set simulation parameter names :
cfs_params = ["V_TOP", "V_BOTTOM"]
trelis_params = ["PLATE_DIST"]
```

:::{important}
The names of the parameters being changed (`V_TOP`, `V_BOTTOM`, and `PLATE_DIST`) must match the parameter names in the *xml* and *jou* files.
:::

To run the simulation, we need to create a simulation object, which is an instance of the `pyCFS` class. 

```python
cap_sim = pyCFS(
    project_name,
    cfs_path,
    trelis_version=trelis_path,
    cfs_params_names=cfs_params,
    trelis_params_names=trelis_params,
)
```

Next, we want to run the simulation. To do so, we need parameters to pass to the simulation. If we are passing just one parameter set we need to pass a vector of size $(1 \times 3)$ or more generally $(1 \times N_p)$. Where $N_p$ is the number of parameters in total. If we want we can also combine our parameter vectors into a matrix of shape $(N_s \times N_p)$ ($N_s$ is the number of parameter sets) and pass it to the simulation object.

Here we define just a $(2 \times 3)$ matrix of parameters. 

```python
params = np.array([[20, 0.0, 2e-3],
                   [20, 10.0, 2e-3]], 
                   dtype=np.float32)
```

Finally we can execute the simulation for the given parameters by running : 

```python
cap_sim(params)
```

For the given parameters `pyCFS` will first run the meshing to generate the mesh needed by `openCFS` and then perform the simulation.

To obtain the results of our simulations we can just execute the following line of code which will return all of the results entries for the given result name. 

```Python
res = cap_sim.get_all_results_for("elecFieldIntensity")
```

More information about the result handling can be found [here](./result_handling.md).