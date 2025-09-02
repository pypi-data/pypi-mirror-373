/*!
 @file FastaBuff.c
 @brief Implementations for the FastaBuff object
*/

#include "FastaBuff.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include <Python.h>

#include "../common.h"
#include "../formats/fasta.h"
#include "GtfDict.h"

/*!
 @brief Initializes a FastaBuff object
 @param self the FastaBuff to initialize
 @param args the arguments to initialize the FastaBuff with
 @param kwds the keyword arguments to initialize the FastaBuff with. Should
 always be NULL
 @ingroup FastaBuff_class
*/
static int FastaBuff_init(FastaBuff *self, PyObject *restrict args,
                          PyObject *restrict kwds) {
    self->RNA = false;
    PyObject *restrict firstArg;
    const char *restrict kwlist[] = {"seq", "RNA", NULL};
    if (PyArg_ParseTupleAndKeywords(args, kwds, "O|p", (char **)kwlist,
                                    &firstArg, &self->RNA) != true) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return -1;
    }
    if (PyBytes_Check(firstArg)) {
        self->buffSize = PyBytes_GET_SIZE(firstArg);
        self->buffLen = self->buffSize * 2;
        self->buff = malloc(self->buffSize);
        memcpy(self->buff, PyBytes_AS_STRING(firstArg), self->buffSize);
        return 0;
    }
    PyObject *restrict string = NULL;
    const char *restrict seq;
    if (PyUnicode_Check(firstArg)) {
        Py_ssize_t size;
        seq = PyUnicode_AsUTF8AndSize(firstArg, &size);
        self->buffLen = (size_t)size;
        self->buffSize = (size_t)ceilf(size / 2.0);
    } else {
        string = PyObject_CallMethod(firstArg, "read", "i", -1);
        if (string == NULL) {
            return -1;
        }
        self->buffLen = (size_t)PySequence_Size(string);
        self->buffSize = self->buffLen / 2;
        seq = PyUnicode_AsUTF8(string);
    }
    self->buff = malloc(PACKING_ROUND(self->buffSize));

    uint8_t buffer[PACKING_WIDTH];
    uint8_t b_i = 0;

    size_t buff_i = 0;

    for (size_t i = 0; i < self->buffLen; i++) {
        const uint8_t val = fasta_binary_mapping[(uint8_t)seq[i]];
        if (val == i_Index) {
            PyErr_SetString(PyExc_ValueError, "Invalid character in sequence");
            return -1;
        }
        buffer[b_i++] = val;
        if (b_i == PACKING_WIDTH) {
            pack(buffer, (packing_t *)self->buff + buff_i++);
            b_i = 0;
        }
    }
    if (b_i != 0) {
        pack(buffer, (packing_t *)self->buff + buff_i++);
    }
    Py_XDECREF(string);
    return 0;
}

/*!
 @brief Returns the length of the FastaBuff
 @param self the FastaBuff to get the length of
 @return the length of the FastaBuff
 @ingroup FastaBuff_class
*/
static Py_ssize_t FastaBuff_len(FastaBuff *self) { return self->buffLen; }

/*!
 @brief Converts the FastaBuff to a string
 @param self the FastaBuff to convert
 @return the string representation of the FastaBuff
 @ingroup FastaBuff_class
*/
static PyObject *FastaBuff_str(FastaBuff *self) {
    PyObject *restrict res = PyUnicode_New(self->buffLen, 0x0F);
    if (res == NULL) {
        PyErr_SetString(PyExc_Exception, "Failed to create string");
        return NULL;
    }
    size_t i = 0;
    for (size_t j = 0; j < self->buffSize; j++) {
        const uint8_t b = self->buff[j];
        if (i >= self->buffLen)
            break;
        PyUnicode_WriteChar(res, i++, getIUPACchar(firstEl(b), self->RNA));
        if (i >= self->buffLen)
            break;
        PyUnicode_WriteChar(res, i++, getIUPACchar(secondEl(b), self->RNA));
    }
    return res;
}

/*!
 @brief Gets a part of the sequence
 @param self the FastaBuff to get the part from
 @param index the index to get the part from
 @return the part of the sequence
*/
static PyObject *FastaBuff_getItem(FastaBuff *self, Py_ssize_t index) {
    if (index < 0) {
        index += self->buffLen;
    }
    if (index >= (Py_ssize_t)self->buffLen) {
        PyErr_SetString(PyExc_IndexError, "Index out of range");
        return NULL;
    }
    const uint8_t b = self->buff[index / 2];
    PyObject *restrict res = PyUnicode_New(1, 0x0F);
    uint8_t byte;
    if (index % 2 == 0) {
        byte = firstEl(b);
    } else {
        byte = secondEl(b);
    }
    if (PyUnicode_WriteChar(res, 0, getIUPACchar(byte, self->RNA))) {
        PyErr_SetString(PyExc_Exception, "Failed to write character");
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

/*!
 @brief Sets a part of the sequence
 @param self the FastaBuff to set the part in
 @param index the index to set the part at
 @param value the value to set
 @return 0 on success, -1 on error
 @ingroup FastaBuff_class
*/
static int FastaBuff_setItem(FastaBuff *self, Py_ssize_t index,
                             PyObject *value) {
    if (index < 0 || index >= (Py_ssize_t)self->buffLen) {
        PyErr_SetString(PyExc_IndexError, "Index out of range");
        return -1;
    }
    if (value == NULL) {
        PyErr_SetString(PyExc_NotImplementedError,
                        "Element deletion is unsupported");
        return -1;
    }
    if (!PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Value must be a character");
        return -1;
    }
    if (PyUnicode_GetLength(value) != 1) {
        PyErr_SetString(PyExc_ValueError, "Value must be a single character");
        return -1;
    }
    uint8_t val = fasta_binary_mapping[(uint8_t)PyUnicode_ReadChar(value, 0)];
    if (val == i_Index) {
        PyErr_SetString(PyExc_ValueError, "Invalid character");
        return -1;
    }
    if (index % 2 == 0) {
        self->buff[index / 2] = toByte(val, secondEl(self->buff[index / 2]));
    } else {
        self->buff[index / 2] = toByte(firstEl(self->buff[index / 2]), val);
    }
    return 0;
}

/*!
 @brief Returns the index of the first occurrence of the specified sequence in
 this FastaBuff, or -1 if this FastaBuff does not contain the sequence.
 @param self the FastaBuff to search in
 @param offset the offset to start searching from
 @param value substring
 @param len length of substring
 @return The index of the first occurrence of the specified sequence, or -1 on
 error.
*/
static int FastaBuff_strindex(FastaBuff *self, size_t offset, const char *value,
                              size_t len) {
    if (self->buffLen - offset < len) {
        return -1;
    }
    for (size_t i = offset; i < self->buffLen - len + 1; i++) {
        for (size_t j = 0; j < len; j++) {
            const Py_ssize_t k = i + j;
            uint8_t el;
            if (k % 2 == 0) {
                el = firstEl(self->buff[k / 2]);
            } else {
                el = secondEl(self->buff[k / 2]);
            }
            if (el != fasta_binary_mapping[(uint8_t)value[j]]) {
                break;
            }
            if (j == len - 1) {
                return (int)i;
            }
        }
    }
    return -1;
}

/*!
 @brief Returns the index of the first occurrence of the specified sequence in
 this FastaBuff
 @param self the FastaBuff to search in
 @param offset the offset to start searching from
 @param other the other FastaBuff to search for
 @return The index of the first occurrence of the specified sequence, or -1 on
 error.
*/
static int FastaBuff_buffindex(FastaBuff *self, size_t offset,
                               FastaBuff *restrict other) {
    if (self->buffLen - offset < other->buffLen) {
        return -1;
    }
    for (size_t i = offset; i < self->buffLen - other->buffLen + 1; i++) {
        for (size_t j = 0; j < other->buffLen; j++) {
            const Py_ssize_t k = i + j;
            uint8_t el;
            if (k % 2 == 0) {
                el = firstEl(self->buff[k / 2]);
            } else {
                el = secondEl(self->buff[k / 2]);
            }
            uint8_t otherEl;
            if (j % 2 == 0) {
                otherEl = firstEl(other->buff[j / 2]);
            } else {
                otherEl = secondEl(other->buff[j / 2]);
            }
            if (el != otherEl) {
                break;
            }
            if (j == other->buffLen - 1) {
                return (int)i;
            }
        }
    }
    return -1;
}

/*!
 @brief Checks if the FastaBuff contains the specified value
 @param self the FastaBuff to search in
 @param value the value to search for
 @return 1 if the FastaBuff contains the value, 0 if it does not, -1 on error
 @ingroup FastaBuff_class
*/
static int FastaBuff_contains(FastaBuff *restrict self,
                              PyObject *restrict value) {
    if (PyUnicode_Check(value)) {
        Py_ssize_t len = PyUnicode_GET_LENGTH(value);
        return FastaBuff_strindex(self, 0, PyUnicode_AsUTF8(value), len) != -1;
    } else if (FastaBuff_Check(value)) {
        FastaBuff *restrict other = (FastaBuff *)value;
        return FastaBuff_buffindex(self, 0, other) != -1;
    } else {
        PyErr_SetString(PyExc_TypeError, "Unsupported comparison");
        return -1;
    }
}

/*!
 @brief Returns the index of the first occurrence of the specified value in this
 FastaBuff
 @param self the FastaBuff to search in
 @param args the arguments to search for
 @return the index of the first occurrence of the specified value, or -1 on
 error
 @ingroup FastaBuff_class
*/
static PyObject *FastaBuff_index(FastaBuff *restrict self,
                                 PyObject *restrict args) {
    PyObject *restrict value;
    long start = 0;
    if (!PyArg_ParseTuple(args, "O|l", &value, &start)) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return NULL;
    }
    if (start < 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid start");
        return NULL;
    }
    int index;
    if (PyUnicode_Check(value)) {
        Py_ssize_t len = PyUnicode_GET_LENGTH(value);
        index = FastaBuff_strindex(self, start, PyUnicode_AsUTF8(value), len);
    } else if (FastaBuff_Check(value)) {
        FastaBuff *restrict other = (FastaBuff *)value;
        index = FastaBuff_buffindex(self, start, other);
    } else {
        PyErr_SetString(PyExc_TypeError, "Unsupported type");
        return NULL;
    }
    if (index < 0) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return PyLong_FromLong((long)index);
}

/*!
 @brief Counts the number of occurrences of the specified value in this
 FastaBuff
 @param self the FastaBuff to search in
 @param args the arguments to search for
 @return the number of occurrences of the specified value
 @ingroup FastaBuff_class
*/
static PyObject *FastaBuff_count(FastaBuff *restrict self,
                                 PyObject *restrict args) {
    PyObject *restrict value;
    if (!PyArg_ParseTuple(args, "O", &value)) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return NULL;
    }
    int count = 0;
    if (PyUnicode_Check(value)) {
        Py_ssize_t len;
        const char *restrict val = PyUnicode_AsUTF8AndSize(value, &len);
        int occ = FastaBuff_strindex(self, 0, val, len);
        while (occ >= 0) {
            count++;
            occ = FastaBuff_strindex(self, occ + 1, val, len);
        }
    } else if (FastaBuff_Check(value)) {
        FastaBuff *restrict other = (FastaBuff *)value;
        int occ = FastaBuff_buffindex(self, 0, other);
        while (occ >= 0) {
            count++;
            occ = FastaBuff_buffindex(self, occ + 1, other);
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "Unsupported type");
        return NULL;
    }
    return PyLong_FromLong((long)count);
}

/*!
 @brief Converts the FastaBuff to a bytes object
 @param self the FastaBuff to convert
 @param args unused
 @return the bytes representation of the FastaBuff
 @ingroup FastaBuff_class
*/
static PyObject *FastaBuff_dump(FastaBuff *restrict self, PyObject *args) {
    UNUSED(args);
    PyObject *restrict res =
        PyBytes_FromStringAndSize((char *)self->buff, self->buffSize);
    if (res == NULL) {
        PyErr_SetString(PyExc_Exception, "Failed to create bytes");
        return NULL;
    }
    return res;
}

/*!
 @brief Returns the annotated sequence
 @param self the FastaBuff to get the annotated sequence from
 @param args the arguments to get the annotated sequence with
 @return the annotated sequence
 @ingroup FastaBuff_class
*/
static PyObject *FastaBuff_get_annotated(FastaBuff *restrict self,
                                         PyObject *restrict args) {
    PyObject *restrict first;
    if (!PyArg_ParseTuple(args, "O", &first)) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return NULL;
    }
    long start;
    long end;
    if (Py_IS_TYPE(first, &GtfDictType)) {
        GtfDict *restrict gtf = (GtfDict *)first;
        start = PyLong_AsLong(gtf->start);
        end = PyLong_AsLong(gtf->end);
    } else if (PyMapping_Check(first)) {
        PyObject *restrict startObj = PyMapping_GetItemString(first, "start");
        if (startObj == NULL) {
            return NULL;
        }
        start = PyLong_AsLong(startObj);
        Py_DECREF(startObj);
        PyObject *restrict endObj = PyMapping_GetItemString(first, "end");
        if (endObj == NULL) {
            return NULL;
        }
        end = PyLong_AsLong(endObj);
        Py_DECREF(endObj);
    } else {
        PyErr_SetString(PyExc_TypeError, "Invalid type");
        return NULL;
    }
    if (start < 0) {
        PyErr_SetString(PyExc_ValueError, "Start out of range");
        return NULL;
    }
    if ((unsigned long)end >= self->buffLen) {
        PyErr_SetString(PyExc_ValueError, "End out of range");
        return NULL;
    }
    PyObject *restrict res = PyUnicode_New(end - start, 0x0F);
    if (res == NULL) {
        return NULL;
    }
    for (Py_ssize_t i = start; i < end; i++) {
        char c =
            getIUPACchar(self->buff[i / 2] >> (4 * (i % 2)) & 0x0F, self->RNA);
        if (PyUnicode_WriteChar(res, i - start, (Py_UCS4)c) < 0) {
            Py_DECREF(res);
            return NULL;
        }
    }
    return res;
}

/*!
 @brief FastaBuff comparison function
 @param self the FastaBuff to compare
 @param other the other object to compare
 @param op the operation to perform
 @return the result of the comparison
 @ingroup FastaBuff_class
*/
static PyObject *FastaBuff_richcompare(FastaBuff *restrict self,
                                       PyObject *restrict other, const int op) {
    if (op != Py_EQ && op != Py_NE) {
        PyErr_SetString(PyExc_TypeError, "Unsupported comparison");
        return NULL;
    }
    if (Py_IS_TYPE(other, &FastaBuffType)) {
        FastaBuff *restrict otherBuff = (FastaBuff *)other;
        bool res = (otherBuff->buffSize == self->buffSize) &&
                   (memcmp(self->buff, otherBuff->buff, self->buffSize) == 0) &&
                   (self->RNA == otherBuff->RNA);
        return PyBool_FromLong(res || op == Py_NE);
    } else if (PyUnicode_Check(other)) {
        Py_ssize_t len;
        const char *restrict str = PyUnicode_AsUTF8AndSize(other, &len);
        if (len != (Py_ssize_t)self->buffLen) {
            return PyBool_FromLong(op == Py_NE);
        }
        for (Py_ssize_t i = 0; i < len; i++) {
            if (str[i] != getIUPACchar(i % 2 == 0 ? firstEl(self->buff[i / 2])
                                                  : secondEl(self->buff[i / 2]),
                                       self->RNA)) {
                return PyBool_FromLong(op == Py_NE);
            }
        }
        return PyBool_FromLong(op == Py_EQ);
    } else {
        PyErr_SetString(PyExc_TypeError, "Unsupported comparison");
        return NULL;
    }
}

/*!
 @brief Gets a subsequence of the FastaBuff
 @param self the FastaBuff to get the subsequence from
 @param key the key to get the subsequence with
 @return the subsequence
 @ingroup FastaBuff_class
*/
static PyObject *FastaBuff_getSubscript(FastaBuff *restrict self,
                                        PyObject *restrict key) {
    if (PyLong_Check(key)) {
        return FastaBuff_getItem(self, PyLong_AsSsize_t(key));
    } else if (PySlice_Check(key)) {
        Py_ssize_t start, stop, step, slicelength;
        if (PySlice_GetIndicesEx(key, self->buffLen, &start, &stop, &step,
                                 &slicelength) < 0) {
            return NULL;
        }
        PyObject *restrict res = PyUnicode_New(slicelength, 0x0F);
        if (res == NULL) {
            return NULL;
        }
        for (Py_ssize_t i = start; i < stop; i++) {
            char c = getIUPACchar(self->buff[i / 2] >> (4 * (i % 2)) & 0x0F,
                                  self->RNA);
            if (PyUnicode_WriteChar(res, i - start, c) < 0) {
                Py_DECREF(res);
                return NULL;
            }
        }
        return res;
    } else {
        PyErr_SetString(PyExc_TypeError, "Invalid key type");
        return NULL;
    }
}

/*!
 @brief Finds occurrences of the specified sequence in this FastaBuff
 @param self the FastaBuff to search in
 @param args the arguments to search for
 @return a list of the indices of the first occurrence of the specified sequence
 in this FastaBuff.
 @ingroup FastaBuff_class
*/
static PyObject *FastaBuff_find(FastaBuff *restrict self,
                                PyObject *restrict args) {
    PyObject *restrict firstArg;
    if (!PyArg_ParseTuple(args, "O", &firstArg)) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return NULL;
    }
    PyObject *restrict listResult = PyList_New(0);
    if (listResult == NULL) {
        return NULL;
    }
    if (PyUnicode_Check(firstArg)) {
        Py_ssize_t len;
        const char *restrict str = PyUnicode_AsUTF8AndSize(firstArg, &len);
        int occ = FastaBuff_strindex(self, 0, str, len);
        while (occ >= 0) {
            PyObject *restrict i = PyLong_FromLong((long)occ);
            if (i == NULL) {
                Py_DECREF(listResult);
                return NULL;
            }
            if (PyList_Append(listResult, i) < 0) {
                Py_DECREF(i);
                Py_DECREF(listResult);
                return NULL;
            }
            Py_DECREF(i);
            occ = FastaBuff_strindex(self, occ + 1, str, len);
        }
    } else if (FastaBuff_Check(firstArg)) {
        FastaBuff *restrict other = (FastaBuff *)firstArg;
        int occ = FastaBuff_buffindex(self, 0, other);
        while (occ >= 0) {
            PyObject *restrict i = PyLong_FromLong((long)occ);
            if (i == NULL) {
                Py_DECREF(listResult);
                return NULL;
            }
            if (PyList_Append(listResult, i) < 0) {
                Py_DECREF(i);
                Py_DECREF(listResult);
                return NULL;
            }
            Py_DECREF(i);
            occ = FastaBuff_buffindex(self, occ + 1, other);
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "Unsupported type");
        Py_DECREF(listResult);
        return NULL;
    }
    return listResult;
}

/*!
 @brief Deallocates the FastaBuff
 @param self the FastaBuff to deallocate
 @ingroup FastaBuff_class
*/
static void FastaBuff_dealloc(FastaBuff *self) {
    free(self->buff);
    PyObject_Free(self);
}

FastaBuff *FastaBuff_new(uint8_t *restrict buff, size_t buffSize,
                         size_t buffLen, bool RNA) {
    FastaBuff *restrict self = PyObject_New(FastaBuff, &FastaBuffType);
    if (self == NULL) {
        PyErr_SetString(PyExc_Exception, "Failed to create FastaBuff");
        return NULL;
    }
    self->buff = buff;
    self->buffSize = buffSize;
    self->buffLen = buffLen;
    self->RNA = RNA;
    return self;
}

/*!
 @brief The FastaBuff methods
*/
static PyMethodDef FastaBuffMethods[] = {
    {"dump", (PyCFunction)FastaBuff_dump, METH_NOARGS,
     "Dumps the buffer as bytes"},
    {"index", (PyCFunction)FastaBuff_index, METH_VARARGS,
     "Returns the index of the first occurrence of the specified sequence in "
     "this FastaBuff."},
    {"get_annotated", (PyCFunction)FastaBuff_get_annotated, METH_VARARGS,
     "Returns the annotated sequence based on the GtfDict"},
    {"count", (PyCFunction)FastaBuff_count, METH_VARARGS,
     "Returns the number of occurrences of the specified sequence in this "
     "FastaBuff."},
    {"find", (PyCFunction)FastaBuff_find, METH_VARARGS,
     "Returns the indices of the first occurrence of the specified sequence in "
     "this FastaBuff."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

/*!
 @brief The FastaBuff mapping methods
*/
static PyMappingMethods FastaBuffMap = {.mp_subscript =
                                            (binaryfunc)FastaBuff_getSubscript};

/*!
 @brief The FastaBuff sequence methods
*/
static PySequenceMethods FastaBuffSeq = {
    .sq_length = (lenfunc)FastaBuff_len,
    .sq_ass_item = (ssizeobjargproc)FastaBuff_setItem,
    .sq_contains = (objobjproc)FastaBuff_contains,
};

PyTypeObject FastaBuffType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "eccLib.FastaBuff",
    .tp_basicsize = sizeof(FastaBuff),
    .tp_doc = PyDoc_STR("A buffer for storing a FASTA sequence"),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)FastaBuff_init,
    .tp_str = (reprfunc)FastaBuff_str,
    .tp_repr = (reprfunc)FastaBuff_str,
    .tp_richcompare = (richcmpfunc)FastaBuff_richcompare,
    .tp_methods = FastaBuffMethods,
    .tp_as_sequence = &FastaBuffSeq,
    .tp_as_mapping = &FastaBuffMap,
    .tp_dealloc = (destructor)FastaBuff_dealloc};
