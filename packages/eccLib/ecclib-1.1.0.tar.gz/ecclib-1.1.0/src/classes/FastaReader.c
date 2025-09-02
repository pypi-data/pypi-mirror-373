/*!
 @file FastaReader.c
 @brief Implementation for the FastaReader and FastaFile classes
*/

#include "FastaReader.h"

#include "../formats/fasta.h"
#include "FastaBuff.h"
#include "unicodeobject.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

/*!
 @brief Saves the provided filename and checks if it exists
 @param self
 @param args standard python argument tuple
 @param kwds unsupported!
 @return -1 on error
 @ingroup FastaFile_class
*/
static int FastaFile_init(FastaFile *self, PyObject *args, PyObject *kwds) {
    self->binary = true;
    static const char *keywords[] = {"filename", "binary", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|b", (char **)keywords,
                                     &self->base.filename, &self->binary)) {
        return -1;
    }
    self->base.file = NULL;
    return 0;
}

/*!
 @brief Creates a FastaReader object from the FastaFile
 @param self
 @return a FastaReader object or NULL on error
 @ingroup FastaFile_class
*/
static PyObject *FastaFile_iter(FastaFile *self) {
    FastaReader *reader = PyObject_New(FastaReader, &FastaReaderType);
    if (reader == NULL) {
        return NULL;
    }
    if (!initialize_reader(&self->base, &reader->base)) {
        return NULL;
    }
    reader->binary = self->binary;
    reader->title = NULL;
    return (PyObject *)reader;
}

/*!
 @brief Methods for the FastaFile class
*/
static PyMethodDef FastaFile_methods[] = {
    {"__enter__", (PyCFunction)file_enter, METH_NOARGS, ""},
    {"__exit__", (PyCFunction)file_exit, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyTypeObject FastaFileType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "eccLib.FastaFile",
    .tp_basicsize = sizeof(FastaFile),
    .tp_doc = PyDoc_STR("Just a FastaReader factory"),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)FastaFile_init,
    .tp_iter = (getiterfunc)FastaFile_iter,
    .tp_methods = FastaFile_methods,
};

/*!
 @brief Initialize a FastaReader object.
 @param self The FastaReader object to initialize.
 @param args The positional arguments passed to the constructor.
 @param kwds The keyword arguments passed to the constructor.
 @return 0 on success, -1 on failure.
 @ingroup FastaReader_class
*/
static int FastaReader_init(FastaReader *self, PyObject *args, PyObject *kwds) {
    self->binary = true;
    static const char *keywords[] = {"file", "binary", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|b", (char **)keywords,
                                     &self->base.fileObj, &self->binary)) {
        return -1;
    }
    Py_INCREF(self->base.fileObj);
    self->base.buff = NULL;
    self->title = NULL;
    return 0;
}

#define BUFFER_GROWTH 2

/*!
 @brief Read the next sequence from the FastaReader object.
 @param self The FastaReader object to read from.
 @return The next sequence as a tuple (title, sequence), or NULL on error.
 @ingroup FastaReader_class
*/
static PyObject *FastaReader_next(FastaReader *restrict self) {
    if (self->base.file == NULL) {
        PyErr_SetString(PyExc_IOError, "File has been closed");
        return NULL;
    }
    // first find the title; title can be inherited from the prev iter
    if (self->title == NULL) {
        line_out title = next_line(&self->base, is_valid_title);
        if (title.line.token == NULL) {
            Py_XDECREF(title.obj);
            return NULL;
        }
        self->title_len = title.line.len - 1;
        if (title.line.token[self->title_len] == '\n') {
            self->title_len--;
        }
        self->title = malloc(self->title_len + 1);
        if (self->title == NULL) {
            Py_XDECREF(title.obj);
            PyErr_SetFromErrno(PyExc_MemoryError);
            return NULL;
        }
        memcpy(self->title, title.line.token + 1, self->title_len);
        Py_XDECREF(title.obj);
    }

    size_t sequenceSize = 0;
    size_t seq_i = 0;

    line_out line = next_line(&self->base, NULL);

    PyObject *result;
    if (self->binary) { // binary processing
        packing_t *sequenceBuffer = NULL;

        bool RNA = false;
        size_t buff_i = 0;

        uint8_t buffer[PACKING_WIDTH];
        uint8_t b_i = 0;

        // while no error and we havent found the next title
        while (line.line.token != NULL && *line.line.token != '>') {
            // adjust the size to the nearest multiple of PACKING_WIDTH
            if ((line.line.len / 2) + (buff_i * sizeof(packing_t)) >
                sequenceSize) {
                sequenceSize = PACKING_ROUND(
                    (sequenceSize + line.line.len + 1) * BUFFER_GROWTH);
                sequenceBuffer = realloc(sequenceBuffer, sequenceSize);
                if (sequenceBuffer == NULL) {
                    PyErr_SetFromErrno(PyExc_MemoryError);
                    return NULL;
                }
            }

            // ok sequence ready, we can process it

            for (size_t i = 0; i < line.line.len; i++) {
                uint8_t c = line.line.token[i];
                uint8_t b = fasta_binary_mapping[c];
                if (b == i_Index) {
                    continue;
                }
                if (c == 'U') {
                    RNA = true;
                }
                buffer[b_i++] = b;
                seq_i++;
                if (b_i == PACKING_WIDTH) {
                    pack(buffer, sequenceBuffer + buff_i++);
                    b_i = 0;
                }
            }

            // iteration
            Py_XDECREF(line.obj);
            line = next_line(&self->base, NULL);
        }

        // cleanup
        if (seq_i == 0) { // oh oh we added nothing
            free(sequenceBuffer);
            if (PyErr_ExceptionMatches(PyExc_StopIteration)) {
                // we added nothing AND stop iteration? exit out
                return NULL;
            }
            result = Py_None;
            Py_INCREF(result);
        } else {
            sequenceSize = seq_i;
            sequenceBuffer = realloc(sequenceBuffer, PACKING_ROUND(seq_i));
            if (b_i > 0) {
                pack(buffer, sequenceBuffer + buff_i++);
            }
            if (sequenceBuffer == NULL) {
                PyErr_SetFromErrno(PyExc_MemoryError);
                Py_XDECREF(line.obj);
                return NULL;
            }
            result = (PyObject *)FastaBuff_new((uint8_t *)sequenceBuffer,
                                               sequenceSize, seq_i, RNA);
        }
    } else { // the trick here, is that we use Resize as realloc
        if (line.line.token == NULL) {
            return NULL;
        }

        if (line.line.token[line.line.len - 1] == '\n') {
            line.line.len--;
        }
        // we initialize result as the first line of the sequence
        sequenceSize = line.line.len;
        seq_i = line.line.len;
        result = PyUnicode_DecodeASCII(line.line.token, sequenceSize, NULL);
        Py_XDECREF(line.obj);

        line = next_line(&self->base, NULL);
        // while no error and we havent found the next title
        while (line.line.token != NULL && *line.line.token != '>') {
            // we treat PyUnicode_Resize as realloc
            if (seq_i + line.line.len > sequenceSize) {
                sequenceSize = (sequenceSize + line.line.len) * BUFFER_GROWTH;
                if (PyUnicode_Resize(&result, sequenceSize) < 0) {
                    Py_XDECREF(line.obj);
                    Py_DECREF(result);
                    return NULL;
                }
            }

            // having allocated enough memory, we can safely write to the data
            // to result
            char *data = PyUnicode_DATA(result);
            for (size_t i = 0; i < line.line.len; i++) {
                if (!isalpha(line.line.token[i])) {
                    continue;
                }
                PyUnicode_WRITE(PyUnicode_1BYTE_KIND, data, seq_i++,
                                line.line.token[i]);
            }

            Py_XDECREF(line.obj);
            line = next_line(&self->base, NULL);
        }

        // finish up
        if (seq_i == 0) {
            Py_DECREF(result);
            if (PyErr_ExceptionMatches(PyExc_StopIteration)) {
                // we added nothing AND stop iteration? exit out
                return NULL;
            }
            result = Py_None;
            Py_INCREF(result);
        }
        // we overallocated earlier, we probs should now reallocate down
        if (PyUnicode_Resize(&result, seq_i) < 0) {
            Py_DECREF(result);
            return NULL;
        }
    }

    // convert title to Python3 String
    PyObject *key = PyUnicode_DecodeUTF8(self->title, self->title_len, NULL);
    if (key == NULL) {
        Py_XDECREF(result);
        return NULL;
    }

    // ok so we got *something* out, if eof then ignore it, else update title
    if (PyErr_ExceptionMatches(PyExc_StopIteration)) {
        PyErr_Clear();
    } else {
        self->title_len = line.line.len - 1;
        if (line.line.token[self->title_len] == '\n') {
            self->title_len--;
        }
        self->title = realloc(self->title, self->title_len);
        if (self->title == NULL) {
            PyErr_SetFromErrno(PyExc_MemoryError);
            Py_DECREF(key);
            Py_XDECREF(result);
            return NULL;
        }
        memcpy(self->title, line.line.token + 1, self->title_len);
    }
    Py_XDECREF(line.obj);

    PyObject *entry = PyTuple_Pack(2, key, result);
    Py_DECREF(result);
    Py_DECREF(key);
    if (entry == NULL) {
        return NULL;
    }

    return entry;
}

/*!
 @brief Deallocate the FastaReader object.
 @param self The FastaReader object to deallocate.
 @ingroup FastaReader_class
*/
static void FastaReader_dealloc(FastaReader *restrict self) {
    free(self->title);
    free_reader(&self->base);
}

PyTypeObject FastaReaderType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "eccLib.FastaReader",
    .tp_basicsize = sizeof(FastaReader),
    .tp_doc = PyDoc_STR("A iterable reader of Fasta entries"),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)FastaReader_init,
    .tp_iternext = (iternextfunc)FastaReader_next,
    .tp_dealloc = (destructor)FastaReader_dealloc,
};
