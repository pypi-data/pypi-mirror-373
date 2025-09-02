# Installation

## Environment setup

This section covers the setup of the environment used for running the library. Please make sure that you follow the
instructions in the given order.

:::{important}
If you are a developer just set up the conda/virtual environment as below (step 1) and follow with
the [developer install](#developer-install).
:::

1. Install python version  >= 3.10.
    1. (Recommended) Install [anaconda](https://www.anaconda.com/download)
       or [miniconda](https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html). After doing so, open
       the command prompt and follow the next steps.
        - Create a new environment with :
       ```bash
        conda create --name pycfs python=3.12
        ```
        - Switch to new environment with :
        ```bash
        conda activate pycfs
        ```
    2. (Alternatively) Create a virtual environment in your project root directory (`~`) with :
       - Create a new environment with :
            ```bash
            python3.10 -m venv ~/.venv/pycfs
            ```
            (requires locally installed python>=3.10)
        - Switch to new environment with :
        
            - Linux bash: 
                ```bash
                source ~/.venv/pycfs/bin/activate
                ```

            - Windows PowerShell
                ```powershell
                ~\.venv\pycfs\Scripts\Activate.ps1
                ```
2. Install *pyCFS*
    - Install via pip :
        ```bash
        python -m pip install --upgrade pycfs
        ```
    - If you want to install a specific branch (e.g. `main`), this can be done with
        ```bash
        python -m pip install --upgrade git+https://gitlab.com/opencfs/pycfs@main
        ```
3. Install *openCFS* and *coreform cubit* :
    - Follow [this tutorial](https://opencfs.gitlab.io/userdocu/Installation/)

## Developer install

First you will need to clone the repository and `cd` into the repository root. As a developer you will need to install
a few dependencies more than what is needed to just use the package.

1. Setup up your python environment using anaconda or virtual environment.

2. Install the requirements by running :
   ```bash
   python -m pip install -r requirements/dev.txt
   ```
3. To install the package make sure you're in the root directory. Make sure you have activated your
   conda environment or virtual environment, and then run:

   ```bash
   python -m pip install -e .
   ```

   the `-e` flag (editable install) applies the changes you make while developing directly to the package so that you can
   easily test it while developing in this source directory.

This will install the required packages and then the `pyCFS` package itself. You can test your installation by running :

```bash
pytest
```