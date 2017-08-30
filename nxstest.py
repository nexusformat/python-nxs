# This program is public domain

# Author: Paul Kienzle

"""
NeXus tests converted to python.
"""

from __future__ import print_function

import nxs,os,numpy,sys

def memfootprint():
    import gc
    objs = gc.get_objects()
    classes = set( c.__class__ for c in gc.get_objects() if hasattr(c,'__class__') )
    # print("\n".join([c.__name__ for c in classes]))
    print("#objects=",len(objs))
    print("#classes=",len(classes))

def leak_test1(n = 1000, mode='w5'):
#    import gc
#    gc.enable()
#    gc.set_debug(gc.DEBUG_LEAK)
    filename = "leak_test1.nxs"
    try: os.unlink(filename)
    except OSError: pass
    file = nxs.open(filename,mode)
    file.close()
    print("File should exist now")
    for i in range(n):
        if i%100 == 0: 
            print("loop count %d"%i)
            memfootprint()
        file.open()
        file.close()
#        gc.collect()
    os.unlink(filename)

def _show(file, indent=0):
    prefix = ' '*indent
    link = file.link()
    if link:
        print("%(prefix)s-> %(link)s" % locals())
        return
    for attr,value in file.attrs():
        print("%(prefix)s@%(attr)s: %(value)s" % locals())
    for name,nxclass in file.entries():
        if nxclass == "SDS":
            shape,dtype = file.getinfo()
            dims = "x".join([str(x) for x in shape])
            print("%(prefix)s%(name)s %(dtype)s %(dims)s" % locals())
            link = file.link()
            if link:
                print("  %(prefix)s-> %(link)s" % locals())
            else:
                for attr,value in file.attrs():
                    print("  %(prefix)s@%(attr)s: %(value)s" % locals())
                if numpy.prod(shape) < 8:
                    value = file.getdata()
                    print("  %s%s"%(prefix,str(value)))
        else:
            print("%(prefix)s%(name)s %(nxclass)s" % locals())
            _show(file, indent+2)

def show_structure(filename):
    file = nxs.open(filename)
    print("=== File",file.inquirefile())
    _show(file)
    

def populate(filename,mode):
    c1 = numpy.array(['abcd','efgh','ijkl','mnop','qrst'])
    i1 = numpy.arange(4,dtype='uint8')
    i2 = numpy.arange(4,dtype='int16')*1000
    i4 = numpy.arange(4,dtype='int32')*1000000
    i8 = numpy.arange(4,dtype='int64')*1000000000000
    r4 = numpy.arange(20,dtype='float32').reshape((5,4))
    r8 = numpy.arange(20,dtype='float64').reshape((5,4))
    comp_array=numpy.ones((100,20),dtype='int32')
    for i in range(100): comp_array[i,:] *= i

    file = nxs.open(filename,mode)
    file.setnumberformat('float32','%9.3g')
    file.makegroup("entry","NXentry")
    file.opengroup("entry","NXentry")
    file.putattr("hugo","namenlos")
    file.putattr("cucumber","passion")
    #file.putattr("embedded_null","embedded\000null")

    # Write character data
    file.makedata("ch_data",'char',[10])
    file.opendata("ch_data")
    file.putdata("NeXus data")
    file.closedata()
    file.makedata("c1_data",'char',[5,4])
    file.opendata("c1_data")
    file.putdata(c1)
    file.closedata()
    
    # Write numeric data
    for var in ['i1','i2','i4','i8','r4']:
        if mode == 'w4' and var == 'i8': continue
        name = var+'_data'
        val = locals()[var]
        file.makedata(name,val.dtype,val.shape)
        file.opendata(name)
        file.putdata(val)
        file.closedata()
    
    # Write r8_data
    file.makedata('r8_data','float64',[5,4])
    file.opendata('r8_data')
    file.putslab(r8[4,:],[4,0],[1,4])
    file.putslab(r8[0:4,:],[0,0],[4,4])
    file.putattr("ch_attribute","NeXus")
    file.putattr("i4_attribute",42,dtype='int32')
    file.putattr("r4_attribute",3.14159265,dtype='float32')
    ## Oops... NAPI doesn't support array attributes
    #file.putattr("i4_array",[3,2],dtype='int32')
    #file.putattr("r4_array",[3.14159265,2.718281828],dtype='float32')
    dataID = file.getdataID()
    file.closedata()

    # Create the NXdata group
    file.makegroup("data","NXdata")
    file.opengroup("data","NXdata")
    
    # .. demonstrate linking
    file.makelink(dataID)

    # .. demonstrate compressed data
    file.compmakedata("comp_data",'int32',[100,20],'lzw',[20,20])
    file.opendata('comp_data')
    file.putdata(comp_array)
    file.closedata()
    file.flush()

    # .. demonstrate extensible data
    file.makedata('flush_data','int32',[nxs.UNLIMITED])
    file.opendata('flush_data')
    for i in range(7):
        file.putslab(i,[i],[1])
    file.closedata()
    file.flush()
    file.closegroup()

    # Create NXsample group
    file.makegroup('sample','NXsample')
    file.opengroup('sample','NXsample')
    file.makedata('ch_data','char',[20])
    file.opendata('ch_data')
    file.putdata('NeXus sample')
    file.closedata()
    sampleID = file.getgroupID()
    file.closegroup()
    file.closegroup()

    # Demonstrate named links
    file.makegroup('link','NXentry')
    file.opengroup('link','NXentry')
    file.makelink(sampleID)
    file.makenamedlink('renLinkGroup',sampleID)
    file.makenamedlink('renLinkData',dataID)
    file.closegroup()
    
    file.close()
    return filename

failures = 0
def fail(msg):
    global failures
    print("FAIL:",msg)
    failures += 1

def dicteq(a,b):
    """
    Compare two dictionaries printing how they differ.
    """
    for k,v in a.iteritems():
        if k not in b:
            print(k,"not in",b)
            return False
        if v != b[k]: 
            print(v,"not equal",b[k])
            return False
    for k,v in b.iteritems():
        if k not in a: 
            print(k,"not in",a)
            return False
    return True

def check(filename, mode):
    global failures
    failures = 0
    file = nxs.open(filename,'rw')
    if filename != file.inquirefile(): fail("Files don't match")

    # check headers
    num_attrs = file.getattrinfo()
    wxattrs = ['xmlns','xmlns:xsi','xsi:schemaLocation', 'XML_version']
    w4attrs = ['HDF_version']
    w5attrs = ['HDF5_Version']
    extras = dict(wx=wxattrs,w4=w4attrs,w5=w5attrs)
    expected_attrs = ['NeXus_version','file_name','file_time']+extras[mode]
    for i in range(num_attrs):
        name,dims,type = file.getnextattr()
        if name not in expected_attrs:
            fail("attribute %s unexpected"%(name))
    if num_attrs != len(expected_attrs): 
        fail("Expected %d root attributes but got %d"
             % (len(expected_attrs),num_attrs))
    
    file.opengroup('entry','NXentry')
    
    expect = dict(hugo='namenlos',cucumber='passion')
    #expect['embedded_null'] = "embedded\000null"
    get = dict((k,v) for k,v in file.attrs())
    same = dicteq(get,expect)
    if not same: fail("/entry attributes are %s"%(get))

    # Check that the numbers are written correctly
    for name,dtype,shape,scale in \
        [('i1','int8',(4),1),
         ('i2','int16',(4),1000),
         ('i4','int32',(4),1000000),
         ('i8','int64',(4),1000000000000),
         ('r4','float32',(5,4),1),
         ('r8','float64',(5,4),1)
         ]:
        if mode == 'w4' and name == 'i8': continue
        n = numpy.prod(shape)
        expected = numpy.arange(n,dtype=dtype).reshape(shape)*scale
        file.opendata(name+'_data')
        get = file.getdata()
        file.closedata()
        if not (get == expected).all(): 
            fail("%s retrieved %s"%(dtype,get))


    # Check attribute types
    file.opendata('r8_data')
    get = file.getattr("ch_attribute",5,'char')
    if not get == "NeXus": fail("ch_attribute retrieved %s"%(get))
    get = file.getattr("i4_attribute",1,'int32')
    if not get == numpy.int32(42): fail("i4_attribute retrieved %s"%(get))
    get = file.getattr("r4_attribute",1,'float32')
    if ((mode=='wx' and not abs(get-3.14159265) < 1e-6) or
        (mode!='wx' and not get == numpy.float32(3.14159265))):
        fail("r4_attribute retrieved %s"%(get))
    ## Oops... NAPI doesn't support array attributes
    #expect = numpy.array([3,2],dtype='int32')
    #get = file.getattr("i4_array",2,'int32')
    #if not (get==expect).all(): fail('i4_array retrieved %s'%(get))
    #expect = numpy.array([3.14159265,2.718281828],dtype='float32')
    #get = file.getattr("r4_array",2,dtype='float32')
    #if not (get==expect).all(): fail("r4_array retrieved %s"%(get))
    file.closedata()

    file.opendata('c1_data')
    rawshape,rawdtype = file.getrawinfo()
    shape,dtype = file.getinfo()
    get = file.getdata()
    file.closedata()
    if not (shape[0]==5 and shape[1]==4 and dtype=='char'):
        fail("returned string array info is incorrect")
    if not (rawshape[0]==5 and rawshape[1]==4 and rawdtype=='char'):
        fail("returned string array storage info is incorrect")
        print(rawshape,dtype)
    if not (get[0]=="abcd" and get[4]=="qrst"):
        fail("returned string is incorrect")
        print(shape,dtype)


    # Check reading from compressed datasets
    comp_array=numpy.ones((100,20),dtype='int32')
    for i in range(100): comp_array[i,:] *= i
    expected = comp_array
    file.opengroup('data','NXdata') #/entry/data
    file.opendata('comp_data')      #/entry/data/comp_data
    get = file.getdata()
    file.closedata()                #/entry/data/comp_data
    file.closegroup()               #/entry/data
    if not (get == expected).all():
        fail("compressed data differs")
        print(get)
        
    # Check strings
    file.opengroup('sample','NXsample') #/entry/sample
    file.opendata('ch_data')            #/entry/sample/ch_data
    rawshape,rawdtype = file.getrawinfo()
    shape,dtype = file.getinfo()
    get = file.getdata()
    file.closedata()                    #/entry/sample/ch_data
    file.closegroup()                   #/entry/sample
    if not (shape[0]==12 and dtype=='char'):
        fail("returned string info is incorrect")
        print(shape,dtype)
    if not (rawshape[0]==20 and rawdtype=='char'):
        fail("returned string storage info is incorrect")
        print(shape,dtype)
    if not (get == "NeXus sample"):
        fail("returned string is incorrect")
        print(shape,dtype)

    file.closegroup() #/entry

    # Check read slab (e.g., from extensible)

    # Check links
    file.opengroup('entry','NXentry')
    file.opengroup('sample','NXsample')
    sampleid = file.getgroupID()
    file.closegroup() #/entry/sample
    file.opengroup('data','NXdata') #/entry/data
    file.opendata('r8_data') #/entry/data/r8_data
    dataid = file.getdataID()
    file.closedata() #/entry/data/r8_data
    file.closegroup() #/entry/data
    file.opendata('r8_data')
    data2id = file.getdataID()
    file.closedata()
    file.closegroup() #/entry
    if not (file.sameID(dataid,data2id)):
        fail("/entry/data/r8_data not linked to /entry/r8_data")
    
    # Check openpath and getslab
    file.openpath('/entry/data/comp_data')
    get = file.getslab([4,4],[5,3])
    expected = comp_array[4:(4+5),4:(4+3)]
    if not (get == expected).all():
        fail("retrieved compressed slabs differ")
        print(get)
    file.openpath('/entry/data/comp_data')
    get = file.getslab([4,4],[5,3])
    expected = comp_array[4:(4+5),4:(4+3)]
    if not (get == expected).all():
        fail("after reopen: retrieved compressed slabs differ")
        print(get)
    file.openpath('../r8_data')
    for k,v in file.attrs():
        if k == 'target' and v != '/entry/r8_data':
            fail("relative openpath was not successful")

    return failures == 0

def populate_external(filename,mode):
    ext = dict(w5='.h5',w4='.hdf',wx='.xml')[mode]
    file = nxs.open(filename,mode)
    file.makegroup('entry1','NXentry')
    file.linkexternal('entry1','NXentry','nxfile://data/dmc01'+ext)
    file.makegroup('entry2','NXentry')
    file.linkexternal('entry2','NXentry','nxfile://data/dmc02'+ext)
    file.makegroup('entry3','NXentry')
    file.close()

def check_external(filename,mode):
    ext = dict(w5='.h5',w4='.hdf',wx='.xml')[mode]
    file = nxs.open(filename,'rw')
    
    file.openpath('/entry1/start_time')
    time = file.getdata()
    
    get = file.inquirefile()
    expected = 'nxfile://data/dmc01'+ext
    if expected != get: fail("first external file returned %s"%(get))
    
    file.openpath('/entry2/sample/sample_name')
    sample = file.getdata()

    get = file.inquirefile()
    expected = 'nxfile://data/dmc02'+ext
    if expected != get: fail("second external file returned %s"%(get))

    file.openpath('/')
    remote = file.isexternalgroup('entry1','NXentry')
    if remote is None:
        fail("failed to identify /entry1 as external")
    remote = file.isexternalgroup('entry3','NXentry')
    if remote is not None: 
        fail('incorrectly identified /entry3 as external')
    
    file.close()

def test_external(mode,quiet=True):
    ext = dict(w5='.h5',w4='.hdf',wx='.xml')[mode]
    filename = 'nxext'+ext
    populate_external(external,mode)
    if not quiet:
        show_structure(external)
    failures = check_external(filename,mode)
    return failures

def test_mode(mode,quiet=True,external=False):
    ext = dict(w5='.h5',w4='.hdf',wx='.xml')[mode]
    filename = 'NXtest'+ext
    populate(filename,mode=mode)
    if not quiet and 'NX_LOAD_PATH' in os.environ:
        show_structure('dmc01'+ext)
    if not quiet:
        show_structure(filename)
    failures = check(filename,mode)
    if external: failures += test_external(mode,quiet)
    return failures

def test():
    tests = 0
    if '-q' in sys.argv:
        quiet = True
    else:
        quiet = False
    if '-x' in sys.argv:
        external = True
        
    else:
        external = False
    if 'hdf4' in sys.argv: 
        test_mode('w4',quiet,external)
        tests += 1
    if 'xml' in sys.argv:
        test_mode('wx',quiet,external)
        tests += 1
    if 'hdf5' in sys.argv: 
        test_mode('w5',quiet,external)
        tests += 1
    if tests == 0: test_mode('w5',quiet,external)

if __name__ == "__main__":
    test()
    #leak_test1(n=10000)
    
