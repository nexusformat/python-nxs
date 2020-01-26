================
Nexus Python API
================


Overview
========

NeXus Python Api binds the NeXus libraries to Python. It brings functionality
of the NeXus API to Python for reading, writing and modifying NeXus Files.
Python NeXus API imitates the functionality NeXus API though with a more object
oriented flavour.

* Information on NeXus Dataformat: http://www.nexusformat.org/

Installation
============

Requirements
~~~~~~~~~~~~

The following software has to be installed on your system in order to 
successfully install and use the Python bindings for NAPI

* Python 2.5 or higher
* ``setuptools`` (replaces the old ``distutils`` code)
* ``sphinx`` to build the documentation
* a working installation of the runtime binaries of ``libNeXus``
* ``numpy``-package

Supported operating systems are: Windows, OS X and Linux.

The bindings should be easily modified for any version of Python which supports 
ctypes and numpy. In order to build the documentation `sphinx` is required.

Building and Installing
~~~~~~~~~~~~~~~~~~~~~~~

This package uses the standard distutils installer for python

.. code-block:: bash

    $ python setup.py install

You will also need to make sure that `libNeXus` can be found.  
In order to build the documentation use 

.. code-block:: bash

    $ python setup.py build_sphinx

To run the tests use 

.. code-block:: bash

    $ python setup.py test 



Using API from Python
=====================

Test Files
~~~~~~~~~~

The Python NeXus-API includes nxstest.py, which provides similar tests to the
original C api file napi_test.c.

After installing, you can run the test using:

.. code-block:: bash
    
    $ python [options] [formats]

where options are ``-q`` for quiet and ``-x`` for external, and formats are
``hdf4``, ``hdf5`` and ``xml``.  The default is to test ``hdf5`` format
read/write.

Using The API And An Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The API's functions aim to reproduce the funtionality of the C API closely.
Some low level functionality has been hidden from the user. Memory allocation
functions NXmalloc and NXfree are done automatically in the API when needed.
The file handle is an object with methods rather than a parameter to functions.
Instead of checking status codes, errors raise exceptions.

The input and returned values match the format of the data in the files.  On
return, python creates values of the correct type.  However on input, numeric
types must be created correctly using ``numpy.array(...,dtype='type')``. The
matching datatypes are:

==============     ===============
NeXus datatype     Python Datatype
==============     ===============
NX_CHAR            char
NX_FLOAT32         float32
NX_FLOAT64         float64
NX_UINT8           uint8
NX_INT16           int16
NX_UINT16          uint16
NX_INT32           int32
NX_UINT32          uint32
==============     ===============


Here is simple example program that demonstrates the basic functions and most
important differences between the C Nexus Api and the Python Nexus API.

* Creates a NeXus file with access method HDF5
* adds datagroups
* makes a data array of data type NX_INT32
* puts data to the array
* reads the data and attributes
* prints data and attribute value<
* closes the groups and the file.


.. code-block:: python

    import nxs,numpy

    # Access method accepts strings or integer (e.g., nxs.ACC_CREATE5)
    f = nxs.open("test.h5", 'w5')
    f.makegroup("testgroup", "NXentry")
    f.opengroup("testgroup", "NXentry")
    f.makegroup("anothergroup", "NXentry")

    # Some data to store in the file, this of type int16
    data = numpy.array([[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15] ],'int16')

    # Make a data set for the array. Note that this could also
    # be done as f.makedata('data1','int16',[4,4])
    f.makedata('data1', dtype=data.dtype, shape=data.shape)
    f.opendata("data1")
    f.putdata(data)

    # Attribute type can be inferred from the data or specified.  If inferred, it
    # must match the type of the data.  Attributes are scalars or strings, with
    # string length inferred from value.
    f.putattr('integer-attribute', 42, 'int16')
    f.putattr('double-attribute', 3.14159)
    f.closedata() 
    # NeXus returns arrays from getattr/getdata/getslab
    f.opendata("data1")
    print 'data :',f.getdata()

    # getnext functions return tuples
    attrname,length,type = f.getnextattr ()
    value = f.getattr(attrname, length, type)
    print 'first attribute: ', value

    # ... or you can use iterators for attrs and entries
    print 'all attributes'
    for attr,value in f.attrs(): 
        print "  %s: %s"%(attr,value)

    f.closedata()
    f.closegroup()
    f.close()


NeXus API Routines
~~~~~~~~~~~~~~~~~~

Documentation for the individual methods, and how they differ from the basic
NAPI methods is available from the Python command line.  Rather than duplicate
it here, use the following in Python:

.. code-block:: python
    
    import nxs
    help(nxs)
