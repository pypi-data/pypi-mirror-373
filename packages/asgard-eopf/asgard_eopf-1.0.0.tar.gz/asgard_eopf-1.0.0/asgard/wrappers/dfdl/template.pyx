# Copyright 2022 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import os
import os.path as osp

cimport cython
cimport errors as dfdl_err
cimport infoset as dfdl_is
from cpython.ref cimport PyObject
from libc.stdint cimport (
    int8_t,
    int16_t,
    int32_t,
    int64_t,
    uint8_t,
    uint16_t,
    uint32_t,
    uint64_t,
)
from libc.stdio cimport FILE, fclose, feof, fopen

DFDL_LOGGER_NAME = "dfdl"

# --------------------------------------------------------------------------------------------------
cdef void print_error(const dfdl_err.Error *error):
    """
    Print an Error object to a Python logger

    :param error: pointer to error object
    """
    cdef const dfdl_err.ErrorLookup *lookup = dfdl_err.cli_error_lookup(error.code)

    assert lookup is not NULL

    msg = lookup.message.decode(encoding='utf-8')
    if lookup.field == dfdl_err.FIELD_C:
        logging.getLogger(DFDL_LOGGER_NAME).error( msg % error.arg.c)
    elif lookup.field == dfdl_err.FIELD_D64:
        logging.getLogger(DFDL_LOGGER_NAME).error( msg % error.arg.d64)
    elif lookup.field == dfdl_err.FIELD_S:
        arg_str = error.arg.s.decode(encoding='utf-8')
        logging.getLogger(DFDL_LOGGER_NAME).error( msg % arg_str)
    elif lookup.field == dfdl_err.FIELD_S_ON_STDOUT:
        arg_str = error.arg.s.decode(encoding='utf-8')
        logging.getLogger(DFDL_LOGGER_NAME).info( msg % arg_str)
    else:
        logging.getLogger(DFDL_LOGGER_NAME).error( msg )

# --------------------------------------------------------------------------------------------------
cdef void print_diagnostics(const dfdl_err.Diagnostics *diagnostics):
    """
    Print diagnostics to a Python logger

    :param diagnostics: diagnostics struct (or NULL if empty)
    """
    cdef dfdl_err.Error *error = NULL
    if diagnostics is not NULL:
        for index in range(diagnostics.length):
            print_error( &(diagnostics.array[index]) )

# --------------------------------------------------------------------------------------------------
"""
Writer to unparse an Infoset and write it to a Python dictionary

The prefixes should allow to descend to the current node being filled in the output dict tree.
"""
cdef struct PyDictWriter:
    dfdl_is.VisitEventHandler handler # C-style inherited struct
    PyObject *output                  # Underlying object should be a Python list with the root
                                      # dict and the dict from child objects

cdef const dfdl_err.Error * pythonStartDocument(PyDictWriter *writer):
    """
    Callback when starting the Infoset unparsing

    :param writer: pointer to the unparser struct
    """
    return NULL

cdef const dfdl_err.Error * pythonEndDocument(PyDictWriter *writer):
    """
    Callback when ending the Infoset unparsing

    :param writer: pointer to the unparsing struct
    """
    return NULL

cdef const dfdl_err.Error * pythonStartComplex(PyDictWriter *writer, dfdl_is.InfosetBase *base):
    """
    Callback when entering a ComplexElement

    :param writer: pointer to the unparsing struct
    :param base: pointer to the "ComplexElement" infoset node
    """
    # get name of complex element
    name_bytes = dfdl_is.get_erd_name(base.erd)
    name = name_bytes.decode(encoding='utf-8')
    # get dict of parent node
    target_dict = (<list>(writer.output))[-1]
    # handle several occurences of the same element
    next_node = dict()
    old_value = target_dict.get(name)
    if old_value is None:
        target_dict[name] = next_node
    elif isinstance(old_value, list):
        old_value.append(next_node)
    else:
        target_dict[name] = [old_value, next_node]
    # record current complex node
    (<list>(writer.output)).append(next_node)
    return NULL

cdef const dfdl_err.Error * pythonEndComplex(PyDictWriter *writer, dfdl_is.InfosetBase *base):
    """
    Callback when leaving a ComplexElement

    :param writer: pointer to the unparsing struct
    :param base: pointer to the "ComplexElement" infoset node
    """
    (<list>(writer.output)).pop()
    return NULL

cdef const dfdl_err.Error * pythonSimpleElem(PyDictWriter *writer, const dfdl_is.ERD *erd, const void *valueptr):
    """
    Callback when processing a SimpleElement

    :param writer: pointer to the unparsing struct
    :param erd: pointer to the "SimpleElement" ERD node
    :param valueptr: pointer to the stored value
    """
    # get name of simple element
    name_bytes = dfdl_is.get_erd_name(erd)
    name = name_bytes.decode(encoding='utf-8')
    # get dict of parent node
    target_dict = (<list>(writer.output))[-1]
    # parse valueptr
    cdef:
        dfdl_is.TypeCode kind = erd.typeCode
        bint val_bint
        double val_double
        float val_float
        int8_t val_int8
        int16_t val_int16
        int32_t val_int32
        int64_t val_int64
        uint8_t val_uint8
        uint16_t val_uint16
        uint32_t val_uint32
        uint64_t val_uint64
        size_t index
        dfdl_is.HexBinary *val_hex
    if kind == dfdl_is.PRIMITIVE_BOOLEAN:
        val_bint = (<bint*>valueptr)[0]
        val = True if val_bint else False
    elif kind == dfdl_is.PRIMITIVE_DOUBLE:
        val_double = (<double*>valueptr)[0]
        val = val_double
    elif kind == dfdl_is.PRIMITIVE_FLOAT:
        val_float = (<float*>valueptr)[0]
        val = val_float
    elif kind == dfdl_is.PRIMITIVE_HEXBINARY:
        val_hex = <dfdl_is.HexBinary *>valueptr
        val_bytes = bytearray( <int>(val_hex[0].lengthInBytes) )
        for index in range(val_hex[0].lengthInBytes):
            val_bytes[index] = val_hex[0].array[index]
        val = val_bytes.hex()
    elif kind == dfdl_is.PRIMITIVE_INT16:
        val_int16 = (<int16_t*>valueptr)[0]
        val = val_int16
    elif kind == dfdl_is.PRIMITIVE_INT32:
        val_int32 = (<int32_t*>valueptr)[0]
        val = val_int32
    elif kind == dfdl_is.PRIMITIVE_INT64:
        val_int64 = (<int64_t*>valueptr)[0]
        val = val_int64
    elif kind == dfdl_is.PRIMITIVE_INT8:
        val_int8 = (<int8_t*>valueptr)[0]
        val = val_int8
    elif kind == dfdl_is.PRIMITIVE_UINT16:
        val_uint16 = (<uint16_t*>valueptr)[0]
        val = val_uint16
    elif kind == dfdl_is.PRIMITIVE_UINT32:
        val_uint32 = (<uint32_t*>valueptr)[0]
        val = val_uint32
    elif kind == dfdl_is.PRIMITIVE_UINT64:
        val_uint64 = (<uint64_t*>valueptr)[0]
        val = val_uint64
    elif kind == dfdl_is.PRIMITIVE_UINT8:
        val_uint8 = (<uint8_t*>valueptr)[0]
        val = val_uint8
    else:
        logging.getLogger(DFDL_LOGGER_NAME).warning("Unknown primitive type!")
    # record simple element
    old_value = target_dict.get(name)
    if old_value is None:
        target_dict[name] = val
    elif isinstance(old_value, list):
        old_value.append(val)
    else:
        target_dict[name] = [old_value, val]
    return NULL

# --------------------------------------------------------------------------------------------------
cdef class PacketIterator:
    """
    Navatt iterator, parse 1 ISP paquet at each round
    """

    cdef:
        dfdl_is.InfosetBase *_root
        dfdl_is.PState _pstate
        PyDictWriter _writer
        size_t _size  # total file size in bits

    def __cinit__(self, dat_file: str, size: int):
        """
        Constructor

        :param dat_file: path to .dat file
        :param size: file size in bytes
        """
        self._size = size * 8

        # try to instanciate the iterator
        self._root = dfdl_is.get_infoset(True)
        dat_file_bytes = dat_file.encode()
        self._pstate.pu.stream = fopen(dat_file_bytes, b"r")
        self._pstate.pu.bitPos0b = 0
        self._pstate.pu.diagnostics = NULL
        self._pstate.pu.error = NULL
        self._pstate.unreadBits = 0
        self._pstate.numUnreadBits = 0

        # WARNING: due to https://github.com/cython/cython/issues/4939, we had to remove the const
        # qualifier on VisitEventHandler visiter methods 
        self._writer.handler.visitStartDocument = <dfdl_is.VisitStartDocument>&pythonStartDocument
        self._writer.handler.visitEndDocument = <dfdl_is.VisitEndDocument>&pythonEndDocument
        self._writer.handler.visitStartComplex = <dfdl_is.VisitStartComplex>&pythonStartComplex
        self._writer.handler.visitEndComplex = <dfdl_is.VisitEndComplex>&pythonEndComplex
        self._writer.handler.visitSimpleElem = <dfdl_is.VisitSimpleElem>&pythonSimpleElem

    def __dealloc__(self):
        """
        Free allocated resources
        """
        # free resources
        cdef int status
        if self._pstate.pu.stream is not NULL:
            status = fclose(self._pstate.pu.stream)
            if status != 0:
                logging.getLogger(DFDL_LOGGER_NAME).error("Failed to close .dat file")


    def __iter__(self):
        """
        Get iterator (i.e. self)
        """
        return self

    def __next__(self):
        """
        Move to next ISP paquet
        """
        if self._pstate.pu.bitPos0b >= self._size:
            raise StopIteration
        # parse one paquet
        self._root.erd.parseSelf(self._root, &self._pstate)
        print_diagnostics(self._pstate.pu.diagnostics)
        if self._pstate.pu.error is not NULL:
            print_error(self._pstate.pu.error)
            raise RuntimeError("Error during paquet parsing")
  
        # fill output
        output = [dict()]
        self._writer.output = <PyObject*>output
        cdef const dfdl_err.Error *err = dfdl_is.walk_infoset(<dfdl_is.VisitEventHandler *>&self._writer, self._root)
        if err is not NULL:
            print_error(err)
            raise RuntimeError("Error during output filling")
  
        self._writer.output = NULL
        return output[0]


class File:
    """
    NavattFile, wraps the decoding of a NAVATT .dat file
    """

    def __init__(self, dat_file: str):
        """
        Constructor, check the input file path and size
        """
        # check file
        if not osp.isfile(dat_file):
            raise RuntimeError(
                f"Can't instanciate NavattFile with path '{dat_file}', unknown file"
            )
        # detect size
        self.file_size = os.stat(dat_file).st_size
        pkt_size = dfdl_is.packet_size
        if pkt_size > 0 and self.file_size % pkt_size != 0:
            raise RuntimeError(
                f"File size ({self.file_size}) is not a multiple of the Navatt paquet size "
                f"({pkt_size})"
            )
        # register valid file
        self.path = dat_file
        if pkt_size > 0:
            self.paquet_count = self.file_size // pkt_size
        else:
            # TODO: compute number of paquets
            self.paquet_count = 0

    def __iter__(self):
        """
        Get an iterator on this file
        """
        return PacketIterator(self.path, self.file_size)

    def __len__(self) -> int:
        """
        Return the length of this file (in paquets)
        """
        return self.paquet_count
