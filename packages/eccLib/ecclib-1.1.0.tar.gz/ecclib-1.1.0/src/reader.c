/*!
 @file reader.c
 @brief Implementation for the reader module
*/

#include "reader.h"

#include "common.h"
#include "object.h"

PyObject *file_enter(struct file *self, PyObject *args) {
    UNUSED(args);
    if (self->file != NULL) {
        PyErr_SetString(PyExc_IOError, "File is already open");
        return NULL;
    }
    self->file = fopen(self->filename, "r");
    if (self->file == NULL) {
        PyErr_SetFromErrno(PyExc_IOError);
        return NULL;
    }
    Py_INCREF(self);
    return (PyObject *)self;
}

PyObject *file_exit(struct file *self, PyObject *args, PyObject *kwds) {
    UNUSED(args);
    UNUSED(kwds);
    if (self->file == NULL) {
        PyErr_SetString(PyExc_IOError, "File is not open");
        return NULL;
    }
    if (fclose(self->file) != 0) {
        PyErr_SetFromErrno(PyExc_IOError);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

void free_reader(struct reader *self) {
    if (self->buff != NULL) {
        free(self->buff);
    } else {
        Py_DECREF(self->fileObj);
    }
    PyObject_Free(self);
}

bool initialize_reader(const struct file *self, struct reader *reader) {
    if (self->file == NULL) {
        PyErr_SetString(PyExc_IOError, "File is not open");
        return false;
    }
    if (fseek(self->file, 0, SEEK_SET) != 0) { // reset the file
        PyErr_SetFromErrno(PyExc_IOError);
        return false;
    }
    reader->file = self->file;
    reader->buff = malloc(BUFFSIZE);
    if (reader->buff == NULL) {
        PyErr_SetFromErrno(PyExc_MemoryError);
        return false;
    }
    reader->buffSize = BUFFSIZE;
    return true;
}

static inline bool fetch_py(struct reader *restrict self, line_out *out) {
    PyObject *lineObj = PyFile_GetLine(self->fileObj, -1);
    if (lineObj == NULL) {
        if (PyErr_ExceptionMatches(PyExc_EOFError)) {
            PyErr_SetNone(PyExc_StopIteration);
        }
        return false;
    }
    out->line.token =
        PyUnicode_AsUTF8AndSize(lineObj, (Py_ssize_t *)&out->line.len);
    out->obj = lineObj;
    return true;
}

line_out next_line(struct reader *restrict self,
                   bool (*valid)(const char *, size_t)) {
    line_out line = (line_out){{NULL, 0}, NULL};
    if (self->buff != NULL) {
        do {
            // MAYBE if there was an fgets like function, that would read till
            // >, it would be more efficient. However while we can roll our own,
            // there is no equivalent Python API
            char *result = fgets(self->buff, self->buffSize, self->file);
            if (result != NULL) {
                line.line.token = self->buff;
                line.line.len = strlen(self->buff);
            } else {
                if (feof(self->file)) {
                    PyErr_SetNone(PyExc_StopIteration);
                } else {
                    PyErr_SetString(PyExc_IOError, "Failed to read line");
                }
            }
        } while (valid != NULL && !valid(self->buff, self->buffSize));
    } else {
        do {
            Py_XDECREF(line.obj);
            if (!fetch_py(self, &line)) {
                return line;
            }
        } while (valid != NULL && !valid(line.line.token, line.line.len));
    }
    return line;
}
