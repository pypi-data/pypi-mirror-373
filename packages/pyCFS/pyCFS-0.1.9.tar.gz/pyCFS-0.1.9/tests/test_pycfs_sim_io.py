from pyCFS import pyCFS
from .pycfs_fixtures import sensor_array_result_file, hdf_result_file_real, hdf_result_file_imag
import numpy as np
import os
import h5py


def test_write_read_contents():
    contents = "secret test message"
    file = "./tests/data/sim_io/temp_file.txt"

    pyCFS.write_file_contents(file, contents)
    read_contents = pyCFS.read_file_contents(file)

    assert read_contents == contents


def test_find_and_remove_files():
    wildcards = ["./tests/data/sim_io/*file.txt"]
    pyCFS._find_and_remove_files(wildcards)

    assert os.path.exists("./tests/data/sim_io/temp_file.txt") == False
