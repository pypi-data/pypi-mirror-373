## CLI tool

Included in the `pyCFS` installation is a CLI tool. It is meant as a means to execute commands directly from the terminal outside of a python runtime. It offers different possibilities which can be also shown from the man page by running : 

```bash
pycfs --help
```

Here we will show examples of how to use the CLI tool.

### Generating a simulation setup

It is possible to generate an example simulation project which just needs to be filled out by the user. 

To do so just run : 

```bash
pycfs --setup_type newsim --simulation_name capacitor_2d
```

This will generate a *capacitor_2d* project directory and inside of it a *templates* directory containing the essential template files and finally two python files as seen below.

```bash
capacitor_2d
|
|    templates
     |   capacitor_2d_init.xml
     |   capacitor_2d_init.jou
     |   mat_init.xml
|     
|    run_sim.py
|    sim_setup.py
```

The idea of the two python files is to introduce some sort of best practice when working with the library. This way we can define a `get_setup()` function in the *sim_setup.py* file. This function will do the whole setup of the simulation as shown in the introductory example. 

Finally we can import the `get_setup()` function in the *run_sim.py* file.
