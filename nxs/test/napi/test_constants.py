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

class test_constants(unittest.TestCase):
    """
    Testing constants exported by nxs. 
    """
    
    
    def test_scalar_constants(self):
        self.assertEqual(napi.NOSTRIP,128)
        self.assertEqual(napi.UNLIMITED,-1)
        self.assertEqual(napi.MAXRANK,32)
        self.assertEqual(napi.MAXNAMELEN,64)
        self.assertEqual(napi.MAXPATHLEN,1024)
        
    def test_type_codes(self):
        d_expected = {"char":4,"float32":5,"float64":6,
                      "int8":20,"uint8":21,"int16":22,"uint16":23,
                      "int32":24,"uint32":25,"int64":26,"uint64":27}
        self.assertDictEqual(napi._nxtype_code,d_expected)

    def test_open_modes(self):
        dr = {"r":1,"rw":2,"w":3,"w4":4,"w5":5,"wx":6}
        self.assertDictEqual(napi._nxopen_mode,dr)
        
    def test_compression_code(self):
        d_expected = {"none":100,"lzw":200,"rle":300,"huffman":400}
        self.assertDictEqual(napi._compression_code,d_expected)
        
    def test_h4skip(self):
        l_expected = ['CDF0.0','_HDF_CHK_TBL_','Attr0.0','RIG0.0','RI0.0',
                'RIATTR0.0N','RIATTR0.0C']
        self.assertListEqual(napi.H4SKIP,l_expected)
        
