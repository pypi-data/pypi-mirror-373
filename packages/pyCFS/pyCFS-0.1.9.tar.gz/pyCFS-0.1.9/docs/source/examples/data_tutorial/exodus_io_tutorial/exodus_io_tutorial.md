# Tutorial

Tutorial for using the Exodus I/O functionality of pyCFS.

1. Run journal file to get exodus file (download journal file [here](./beam2D.jou))

```bash
cubit -nographics -batch beam2D.jou
```

2. Convert exodus file to opencfs hdf5 file (download script [here](./exodus_io_tutorial.py))

```bash
python exodus_io_tutorial.py
```

```python
# %% Import Exodus reader and CFS writer
from pyCFS.data.extras.exodus_io import read_exodus
from pyCFS.data import io

# %% Read mesh from Exodus file and convert it to cfs mesh
file_read = "beam2D.e"
cfs_mesh = read_exodus(file_read)

# %% Write mesh to cfs file
file_write = "beam2D.cfs"

io.write_file(file_write, mesh=cfs_mesh)
```

3. Run openCFS simulation (download input file [here](./BucklingBeam2D.xml) and material file [here](./mat.xml))

```bash
cfs BucklingBeam2D
```

