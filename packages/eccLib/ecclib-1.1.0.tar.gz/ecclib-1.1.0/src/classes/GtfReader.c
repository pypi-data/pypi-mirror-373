/*!
 @file GtfReader.c
 @brief Contains the implementation of the iterative GTF reader
*/

#include "GtfReader.h"

#include <Python.h>
#include <stdbool.h>

#include "../formats/gtf.h"
#include "object.h"

// GTF file class definition

/*!
 @brief Saves the provided filename and checks if it exists
 @param self
 @param args standard python argument tuple
 @param kwds unsupported!
 @return -1 on error
 @ingroup GtfFile_class
*/
static int GtfFile_init(GtfFile *self, PyObject *args, PyObject *kwds) {
    self->attr_tp = Py_None;
    static const char *keywords[] = {"filename", "attr_tp", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|O", (char **)keywords,
                                     &self->base.filename, &self->attr_tp)) {
        return -1;
    }
    Py_INCREF(self->attr_tp);
    if (!Py_IsNone(self->attr_tp) && !PyMapping_Check(self->attr_tp)) {
        PyErr_SetString(PyExc_TypeError, "attr_tp must be a mapping");
        return -1;
    }
    self->base.file = NULL;
    return 0;
}

/*!
 @brief Creates a GtfReader object from the GtfFile
 @param self
 @return a GtfReader object or NULL on error
 @ingroup GtfFile_class
*/
static PyObject *GtfFile_iter(GtfFile *self) {
    GtfReader *reader = PyObject_New(GtfReader, &GtfReaderType);
    if (reader == NULL) {
        return NULL;
    }
    if (!initialize_reader(&self->base, &reader->base)) {
        return NULL;
    }
    // initialize the reader
    if (hashmap_create_xh(DEFAULT_ATTR_SIZE, &reader->attr_keys) < 0) {
        PyErr_SetString(PyExc_Exception, "Failed to create hashmap");
        return NULL;
    }
    if (hashmap_create_xh(DEFAULT_ATTR_SIZE, &reader->attr_vals) < 0) {
        PyErr_SetString(PyExc_Exception, "Failed to create hashmap");
        hashmap_destroy_py(&reader->attr_keys);
        return NULL;
    }
    Py_INCREF(self->attr_tp);
    reader->attr_tp = self->attr_tp;
    return (PyObject *)reader;
}

static void GtfFile_dealloc(GtfFile *self) {
    Py_DECREF(self->attr_tp);
    PyObject_Free(self);
}

/*!
 @brief Methods for the GtfFile class
*/
static PyMethodDef GtfFile_methods[] = {
    {"__enter__", (PyCFunction)file_enter, METH_NOARGS, ""},
    {"__exit__", (PyCFunction)file_exit, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyTypeObject GtfFileType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "eccLib.GtfFile",
    .tp_basicsize = sizeof(GtfFile),
    .tp_doc = PyDoc_STR("Just a GtfReader factory"),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)GtfFile_init,
    .tp_iter = (getiterfunc)GtfFile_iter,
    .tp_methods = GtfFile_methods,
    .tp_dealloc = (destructor)GtfFile_dealloc,
};

// GTF reader class definition

/*!
 @brief Initializes the GtfReader
 @param self
 @param args standard python argument tuple
 @param kwds unsupported!
*/
static int GtfReader_init(GtfReader *self, PyObject *args, PyObject *kwds) {
    self->attr_tp = Py_None;
    static const char *keywords[] = {"file", "attr_tp", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", (char **)keywords,
                                     &self->base.fileObj, &self->attr_tp)) {
        return -1;
    }
    if (!Py_IsNone(self->attr_tp) && !PyMapping_Check(self->attr_tp)) {
        PyErr_SetString(PyExc_TypeError, "attr_tp must be a mapping");
        return -1;
    }
    Py_INCREF(self->base.fileObj);
    Py_INCREF(self->attr_tp);
    if (hashmap_create_xh(DEFAULT_ATTR_SIZE, &self->attr_keys) < 0) {
        PyErr_SetString(PyExc_Exception, "Failed to create hashmap");
        return -1;
    }
    if (hashmap_create_xh(DEFAULT_ATTR_SIZE, &self->attr_vals) < 0) {
        PyErr_SetString(PyExc_Exception, "Failed to create hashmap");
        hashmap_destroy_py(&self->attr_keys);
        return -1;
    }
    self->base.buff = NULL;
    return 0;
}

/*!
 @brief Retrieves the next line of the opened file and tries parsing it
 @param self
 @return NULL on error or GtfDict
 @ingroup GtfReader_class
*/
static PyObject *GtfReader_next(GtfReader *restrict self) {
    if (self->base.file == NULL) {
        PyErr_SetString(PyExc_IOError, "GTF file has been closed");
        return NULL;
    }
    line_out line = next_line((struct reader *)self, validGTFLineToParse);
    if (line.line.token == NULL) {
        return NULL;
    }
    PyObject *res = (PyObject *)createGTFdict(
        &line.line, self->attr_tp, &self->attr_keys, &self->attr_vals);
    Py_XDECREF(line.obj);
    return (PyObject *)res;
}

/*!
 @brief Deallocates the GtfReader
 @param self
 @ingroup GtfReader_class
*/
static void GtfReader_dealloc(GtfReader *restrict self) {
    Py_DECREF(self->attr_tp);
    hashmap_destroy_py(&self->attr_keys);
    hashmap_destroy_py(&self->attr_vals);
    free_reader(&self->base);
}

PyTypeObject GtfReaderType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "eccLib.GtfReader",
    .tp_basicsize = sizeof(GtfReader),
    .tp_doc = PyDoc_STR("A iterable reader of GTF dicts from a GTF file"),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)GtfReader_init,
    .tp_iternext = (iternextfunc)GtfReader_next,
    .tp_dealloc = (destructor)GtfReader_dealloc,
};
