import nxs.napi as napi
import unittest

class test_field_creation_hdf5(unittest.TestCase):
    mode = "w5"
    filename = "test_file_creation_hdf5.nxs"
    
    def setUp(self):
        self._file = napi.NeXus(self.filename,self.mode)
        self._file.makegroup("entry","NXentry")
        self._file.opengroup("entry")
        
    def tearDown(self):
        self._file.close()
        
        
    def test_field_without_compression(self):
        self._file.makedata("data1",'uint32',(3,4))
        self._file.opendata("data1")
        
