## Introduction

In the following sections we will cover the basics of the `pyCFS` library. 

### General setup 

The `pyCFS` project directory needs to adhere to the structure given below.

```bash
simulation_root
|
|    templates
     |   capacitor_init.xml
     |   mat_init.xml
     |   capacitor_init.jou
|     
|    sim_control.py
```

The example above shows the minimal and most likely setup when using `pyCFS`. It includes a *templates* directory and a control python file. The *templates* directory contains the template files needed to perform the simulation. These files are used to parametrize the simulation : 

* CFS simulations parameters (*capacitor_init.xml* and *mat_init.xml*)
* Cubit (Trelis) geometric parameters (*capacitor_init.jou*)

Finally from the python file we can control the simulation and manipulate the results as will be shown in the introductory example. 
