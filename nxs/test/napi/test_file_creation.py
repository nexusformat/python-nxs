"""@package nxs
Python NeXus interface.

NeXus_ is a common data format for neutron, Xray and muon science.
The files contain multidimensional data elements grouped into a
hierarchical structure.  The data sets are self-describing, with
a description of the instrument configuration including the units
used as well as the data measured.

The NeXus file interface requires compiled libraries to read the
underlying HDF_ files.  Binary packages are available for some
platforms from the NeXus site.  Details of where the nxs package
searches for the libraries are recorded in `nxs.napi`.
"""

import unittest 
import nxs.napi as napi
import os

class test_file_creation(unittest.TestCase):

    def test_hdf5(self):
        f = napi.open("test_hdf5.nxs","w5")
        os.remove("test_hdf5.nxs")
        
    def test_hdf4(self):
        f = napi.open("test_hdf4.nxs","w4")
        os.remove("test_hdf4.nxs")
        
    def test_mxml(self):
        f = napi.open("test_mxml.nxs","wx")
        
