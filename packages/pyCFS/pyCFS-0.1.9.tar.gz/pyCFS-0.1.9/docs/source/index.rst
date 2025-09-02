.. pyCFS documentation master file, created by
   sphinx-quickstart on Wed Feb 29 12:44:06 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyCFS's documentation!
=================================

.. note::

   This project is under active development.


pyCFS is an automation and data processing library for the `openCFS <https://opencfs.org/>`_ software. It enables the user to build an abstraction
layer around the openCFS simulation which means that the user can execute simulations directly from a python script or notebook without worrying 
about the individual simulation files.

Furthermore, the data processing submodule implements the most frequently needed data processing building
blocks and pipelines which are employed in data pre and postprocessing steps.

.. raw:: html

   <iframe src="./embedded/presentation_overview/export/index.html" width="100%" height="600px"></iframe>

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   getting_started
   dev_notes
   pycfs_data
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`