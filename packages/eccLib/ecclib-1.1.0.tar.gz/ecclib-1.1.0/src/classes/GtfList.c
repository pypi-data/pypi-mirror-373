/*!
 @file GtfList.c
 @brief Contains the implementation of the GtfList object
*/
#include "GtfList.h"

#include <stdbool.h>
#include <stdlib.h>

#include <Python.h>

#include "../common.h"
#include "GtfDict.h"

/*!
 @brief Initializes a new GtfList object
 @param self
 @param args the arguments tuple, either a tuple of values for a new list, or a
 tuple with a iterable inside to convert
 @param kwds must be NULL or else error
 @ingroup GtfList_class
*/
static int GtfList_init(GtfList *restrict self, PyObject *args,
                        PyObject *restrict kwds) {
    if (kwds != NULL) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return -1;
    }
    Py_ssize_t argsLen = 0;
    PyObject *first = NULL;
    bool newArgs = false;
    bool newFirst = false;
    argsLen = PyTuple_GET_SIZE(args);
    if (argsLen > 0) {
        Py_ssize_t firstLen = argsLen;
        // borrowed reference
        first = PyTuple_GetItem(args, 0);
        if (first != NULL) {
            // if the first argument was an iterable, then use it to generate a
            // new arg list
            if (PyIter_Check(first)) {
                PyObject *firstList = PyList_New(0); // new reference
                PyObject *o;                         // new reference
                while ((o = PyIter_Next(first)) != NULL) {
                    if (!GtfDict_check(o)) {
                        PyErr_SetString(PyExc_TypeError,
                                        "Provided iterator produced an object "
                                        "that isn't a GtfDict");
                        return -1;
                    }
                    // append doesnt steal
                    PyList_Append(firstList, o);
                    // so we decrement the reference count
                    Py_DECREF(o);
                }
                // stolen reference to firstList
                PyTuple_SetItem(args, 0, firstList);
            } else { // else two cases
                if (argsLen == 1 &&
                    PySequence_Check(first)) { // if the first argument is a
                                               // list then we just set firstLen
                    firstLen = PySequence_Fast_GET_SIZE(first);
                } else {
                    // if we want to create a new list we need to swap args to
                    // be inside of an empty args tuple
                    first = args;
                    newArgs = true;
                    args = PyTuple_New(1); // args is now a new reference
                    // first is borrowed, so we need to incref
                    Py_INCREF(first);
                    PyTuple_SetItem(args, 0, first);
                }
                // Type checking of the first argument
                for (Py_ssize_t i = 0; i < firstLen; i++) {
                    // new reference
                    PyObject *el = PySequence_GetItem(first, i);
                    bool check = GtfDict_check(el);
                    Py_DECREF(el);
                    if (!check) {
                        PyErr_SetString(PyExc_TypeError,
                                        "Provided object isn't a GtfDict");
                        return -1;
                    }
                }
            }
        }
    }
    int res = PyList_Type.tp_init((PyObject *)self, args, NULL);
    // Free args and first should it be necessary
    if (newArgs) {
        Py_DECREF(args);
    }
    if (newFirst) {
        Py_DECREF(first);
    }
    return res;
}

/*!
 @brief Calculates the hausdorf distance between two GtfDicts
 @details The Hausdorf distance is the maximum distance between two points in
    two sets. In this case, it is the maximum distance between the start and end
    of two GtfDicts
 @param a the first GtfDict
 @param b the second GtfDict
 @return the Hausdorf distance between the two GtfDicts
*/
static long hausdorf_distance(GtfDict *restrict a, GtfDict *restrict b) {
    long aStart = PyLong_AsLong(a->start);
    long aEnd = PyLong_AsLong(a->end);
    long bStart = PyLong_AsLong(b->start);
    long bEnd = PyLong_AsLong(b->end);
    long start_diff = aStart - bStart;
    long end_diff = aEnd - bEnd;
    if (start_diff < 0) {
        start_diff = -start_diff;
    }
    if (end_diff < 0) {
        end_diff = -end_diff;
    }
    if (start_diff > end_diff) {
        return start_diff;
    } else {
        return end_diff;
    }
}

/*!
 @brief Finds the host gene of the gene in args assuming this object contains
 the correct host gene
 @param self
 @param args standard python argument tuple
 @return None or a new GtfDict reference
 @ingroup GtfList_class
*/
static PyObject *GtfList_findHost(GtfList *restrict self,
                                  PyObject *restrict args) {
    GtfDict *gene = (GtfDict *)PyTuple_GetItem(args, 0); // borrowed reference
    if (gene == NULL) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return NULL;
    }
    if (!GtfDict_check(gene)) {
        PyErr_SetString(PyExc_TypeError, "Provided object isn't a GtfDict");
        return NULL;
    }
    PyObject *closest = Py_None; // whatever happens in the loop, it's always a
                                 // borrowed reference
    long smallest_dist = LONG_MAX;
    Py_ssize_t ourLen =
        PySequence_Length((PyObject *)self); // foreach value in GtfList
    for (Py_ssize_t i = 0; i < ourLen; i++) {
        GtfDict *value = (GtfDict *)PySequence_GetItem((PyObject *)self, i);
        // if the value contains our gene and isn't equal and is actually a gene
        if (GtfDict_containsValue(value, (PyObject *)gene) &&
            PyObject_RichCompareBool((PyObject *)value, (PyObject *)gene,
                                     Py_NE)) {
            // we do the actual check
            long dist = hausdorf_distance(gene, value);
            if (dist < smallest_dist) {
                smallest_dist = dist;
                closest = (PyObject *)value;
            }
        }
    }
    Py_INCREF(closest);
    return closest;
}

/*!
 @brief Wrapper over the default __setitem__ that performs a type check
 @param self
 @param key int or slice
 @param value GtfDict or iterable of GtfDicts
 @return -1 on error
 @ingroup GtfList_class
*/
static int GtfList_mp_ass_subscript(GtfList *restrict self,
                                    PyObject *restrict key,
                                    PyObject *restrict value) {
    PyTypeObject *type = (PyTypeObject *)PyObject_Type(key);
    if (type == &PyLong_Type) { // singular assignment
        if (!GtfDict_check(value)) {
            Py_DECREF(type);
            PyErr_SetString(PyExc_TypeError, "Provided object isn't a GtfDict");
            return -1;
        }
    } else if (type == &PySlice_Type) { // slice assignment
        Py_ssize_t iterSize = PySequence_Fast_GET_SIZE(value);
        for (int i = 0; i < iterSize; i++) {
            PyObject *val = PySequence_GetItem(value, i);
            bool check = GtfDict_check(val);
            Py_DECREF(val);
            if (!check) {
                Py_DECREF(type);
                PyErr_SetString(PyExc_TypeError,
                                "Provided object isn't a GtfDict");
                return -1;
            }
        }
    }
    Py_DECREF(type);
    return PyList_Type.tp_as_mapping->mp_ass_subscript((PyObject *)self, key,
                                                       value);
}

/*!
 @brief Wrapper over list.append that throws a type error if the provided arg is
 not a GtfDict
 @param self
 @param args standard python arg tuple
 @return None or NULL on error
 @ingroup GtfList_class
*/
static PyObject *GtfList_append(GtfList *restrict self,
                                PyObject *restrict args) {
    // borrowed reference
    PyObject *new = PyTuple_GetItem(args, 0);
    if (!GtfDict_check(new)) {
        PyErr_SetString(PyExc_TypeError, "Provided object isn't a GtfDict");
        return NULL;
    }
    // doesn't steal reference
    if (PyList_Append((PyObject *)self, new) < 0) {
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

/*!
 @brief concatenates o to self
 @param self
 @param o the object to concatenate to self
 @return self as a new reference
 @ingroup GtfList_class
*/
static PyObject *GtfList_inplace_concat(GtfList *restrict self,
                                        PyObject *restrict o) {
    if (!PySequence_Check(o)) {
        PyErr_SetString(PyExc_TypeError, "Provided object isn't a sequence");
        return NULL;
    }
    if (GtfList_Check(o)) { // if we are inplace concatenating another GtfList
        return PyList_Type.tp_as_sequence->sq_inplace_concat((PyObject *)self,
                                                             o);
    } else { // else we check each element and append it
        Py_ssize_t sz = PySequence_Fast_GET_SIZE(o);
        for (Py_ssize_t i = 0; i < sz; i++) {
            PyObject *value = PySequence_Fast_GET_ITEM(o, i);
            if (!GtfDict_check(value)) {
                PyErr_SetString(PyExc_TypeError,
                                "Provided object isn't a GtfDict");
                return NULL;
            }
            PyList_Append((PyObject *)self, value);
        }
        Py_INCREF(self);
        return (PyObject *)self;
    }
}

/*!
 @brief Custom list extend that does a type check
 @param self
 @param args tuple with a single iterable
 @return None or NULL on error
 @ingroup GtfList_class
*/
static PyObject *GtfList_extend(GtfList *restrict self,
                                PyObject *restrict args) {
    if (args == NULL) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return NULL;
    }
    // Faster to do my own extend than call it after iterating over everything
    // already
    PyObject *iterable = PyTuple_GetItem(args, 0);
    PyObject *res = GtfList_inplace_concat(self, iterable);
    if (res == NULL) {
        return NULL;
    }
    Py_DECREF(res);
    Py_INCREF(Py_None);
    return Py_None;
}

/*!
 @brief A wrapper over the default list insert that does a type check
 @param self
 @param args tuple with (index, value)
 @return None or NULL on error
 @ingroup GtfList_class
*/
static PyObject *GtfList_insert(GtfList *restrict self,
                                PyObject *restrict args) {
    if (args == NULL) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return NULL;
    }
    PyObject *indexObj = PyTuple_GetItem(args, 0);
    long index = PyLong_AsLong(indexObj);
    PyObject *value = PyTuple_GetItem(args, 1);
    if (!GtfDict_check(value)) {
        PyErr_SetString(PyExc_TypeError, "Provided object isn't a GtfDict");
        return NULL;
    }
    if (PyList_Insert((PyObject *)self, (Py_ssize_t)index, value) < 0) {
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

/*!
 @brief non discriminatory implementation of __add__. Does no checks and returns
 a LIST
 @param self
 @param other an iterable to be concatenated
 @return a new list object
 @ingroup GtfList_class
*/
static PyObject *GtfList_concat(GtfList *restrict self,
                                PyObject *restrict other) {
    Py_ssize_t selfSize = PySequence_Fast_GET_SIZE((PyObject *)self);
    Py_ssize_t otherSize = PySequence_Fast_GET_SIZE(other);
    PyObject *list = PyList_New(selfSize + otherSize);
    for (Py_ssize_t i = 0; i < selfSize; i++) {
        PyObject *value = PySequence_GetItem((PyObject *)self, i);
        PyList_SetItem(list, i, value);
    }
    for (Py_ssize_t i = 0; i < otherSize; i++) {
        PyObject *value = PySequence_GetItem(other, i);
        PyList_SetItem(list, i + selfSize, value);
    }
    if (GtfList_Check(other)) {
        Py_SET_TYPE(list, &GtfListType);
    }
    return list;
}

/*!
 @brief Generates a complete GTF file
 @param self
 @return Str PyObject or NULL on error
 @ingroup GtfList_class
*/
static PyObject *GtfList_str(GtfList *restrict self) {
    char *result = NULL;
    size_t resSize = 0;
    Py_ssize_t selfSize = PySequence_Fast_GET_SIZE((PyObject *)self);
    for (Py_ssize_t i = 0; i < selfSize; i++) {
        GtfDict *value =
            (GtfDict *)PySequence_Fast_GET_ITEM((PyObject *)self, i);
        size_t thisSz; // doesn't include \0
        char *line = GtfDictToGTF(value, &thisSz);
        result = realloc(result, resSize + thisSz + 1);
        memcpy(result + resSize, line, thisSz);
        free(line);
        resSize += thisSz + 1;
        *(result + resSize - 1) = '\n';
    }
    PyObject *string = PyUnicode_DecodeUTF8(result, resSize, NULL);
    free(result);
    return string;
}

/*!
 @brief Generates a representation of the GtfList object
 @param self
 @return a string representation of the object
 @ingroup GtfList_class
*/
static PyObject *GtfList_repr(GtfList *restrict self) {
    UNUSED(self);
    return PyList_Type.tp_repr((PyObject *)self);
}

/*!
 @brief Splits the gene list into a dict of GtfLists with each GtfList having
 only one seqname
 @param self
 @return A dict seqname->GtfList
 @ingroup GtfList_class
*/
static PyObject *GtfList_sq_split(GtfList *restrict self) {
    PyObject *result = PyDict_New();
    Py_ssize_t selfSize = PySequence_Fast_GET_SIZE(self);
    for (Py_ssize_t i = 0; i < selfSize; i++) {
        GtfDict *object = (GtfDict *)PySequence_Fast_GET_ITEM(self, i);
        PyObject *list;
        if (!PyDict_Contains(result, object->seqname)) {
            list = GtfList_new(0);
            PyDict_SetItem(result, object->seqname,
                           list); // doesn't steal reference
            Py_DECREF(list);
        } else {
            list = PyDict_GetItem(result, object->seqname); // borrowed
                                                            // reference
        }
        // so here in both cases we need to have a NOT strong reference to the
        // object
        PyList_Append(list, (PyObject *)object);
    }
    return result;
}

/*!
 @brief Gets the values of a column in the GtfList
 @param self
 @param args tuple with a single str
 @param kwargs optional pad argument
 @return a list of values
 @ingroup GtfList_class
*/
static PyObject *GtfList_column(GtfList *restrict self, PyObject *restrict args,
                                PyObject *restrict kwargs) {
    PyObject *key;
    bool pad = true;
    if (!PyArg_ParseTuple(args, "O", &key)) {
        PyErr_SetString(PyExc_Exception, "Invalid arguments");
        return NULL;
    }
    if (kwargs != NULL) {
        PyObject *padObj = PyDict_GetItemString(kwargs, "pad");
        if (padObj == NULL) {
            PyErr_Clear();
        } else {
            pad = PyObject_IsTrue(padObj);
        }
    }
    if (!PyUnicode_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "Key must be a string");
        return NULL;
    }
    Py_ssize_t len = PySequence_Fast_GET_SIZE((PyObject *)self);
    if (pad) {
        PyObject *result = PyList_New(len);
        for (Py_ssize_t i = 0; i < len; i++) {
            GtfDict *obj = (GtfDict *)PyList_GetItem((PyObject *)self, i);
            if (obj == NULL) {
                Py_DECREF(result);
                return NULL;
            }
            PyObject *value = GtfDict_getitem(obj, key);
            if (value == NULL) {
                // Get item returns a new reference
                Py_INCREF(Py_None);
                value = Py_None;
                PyErr_Clear();
            }
            PyList_SetItem(result, i, value);
        }
        return result;
    } else {
        PyObject *result = PyList_New(0);
        for (Py_ssize_t i = 0; i < len; i++) {
            GtfDict *obj = (GtfDict *)PyList_GetItem((PyObject *)self, i);
            if (obj == NULL) {
                Py_DECREF(result);
                return NULL;
            }
            PyObject *value = PyObject_GetItem((PyObject *)obj, key);
            if (value == NULL) {
                Py_DECREF(result);
                return NULL;
            } else {
                PyList_Append(result, value);
                Py_DECREF(value);
            }
        }
        return result;
    }
}

/*!
 @brief Finds a sequence within the GtfList
 @param self
 @param args A list of functions to check the objects against
 @param kwargs A dict of key -> value | function to check the value under the
 key
 @return a list of matching objects
 @ingroup GtfList_class
*/
static PyObject *GtfList_find(GtfList *restrict self, PyObject *restrict args,
                              PyObject *restrict kwargs) {
    Py_ssize_t argLen = PySequence_Fast_GET_SIZE(args);
    // arg type check
    for (Py_ssize_t i = 0; i < argLen; i++) {
        // we do this here to avoid doing this check multiple times
        PyObject *function = PyTuple_GetItem(args, i);
        if (!PyCallable_Check(function)) {
            PyErr_SetString(PyExc_TypeError, "All args must be a function");
            return NULL;
        }
    }
    // sanity check
    if (kwargs != NULL && !PyArg_ValidateKeywordArguments(kwargs)) {
        return NULL;
    }
    PyObject *keys = NULL;
    Py_ssize_t keysLen;
    if (kwargs != NULL) { // get the kwargs
        keys = PyDict_Keys(kwargs);
        if (keys == NULL) {
            return NULL;
        }
        keysLen = PySequence_Fast_GET_SIZE(keys);
    }
    PyObject *result = GtfList_new(0);
    if (result == NULL) {
        Py_XDECREF(keys);
        return NULL;
    }
    Py_ssize_t selfLen = PyList_Size((PyObject *)self);
    for (Py_ssize_t i = 0; i < selfLen; i++) {
        GtfDict *obj = (GtfDict *)PyList_GetItem((PyObject *)self, i);
        // this is so much better with goto
        if (kwargs != NULL) {
            PyObject *obj_keys = GtfDict_keys(obj);
            // foreach key
            for (Py_ssize_t n = 0; n < keysLen; n++) {
                // new reference
                PyObject *key = PySequence_GetItem(keys, n);
                if (key == NULL) {
                    Py_DECREF(obj_keys);
                    return NULL;
                }
                if (PySequence_Contains(obj_keys, key)) {
                    // borrowed reference
                    PyObject *kwargsValue =
                        PyDict_GetItemWithError(kwargs, key);
                    if (kwargsValue == NULL) {
                        Py_DECREF(obj_keys);
                        Py_DECREF(key);
                        return NULL;
                    }
                    // new reference
                    PyObject *dictValue =
                        PyObject_GetItem((PyObject *)obj, key);
                    if (dictValue == NULL) {
                        Py_DECREF(obj_keys);
                        Py_DECREF(key);
                        return NULL;
                    }
                    // if it's a function call it
                    if (PyCallable_Check(kwargsValue)) {
                        PyObject *fRes =
                            PyObject_CallOneArg(kwargsValue, dictValue);
                        Py_DECREF(dictValue);
                        if (fRes == NULL) {
                            Py_DECREF(obj_keys);
                            Py_DECREF(key);
                            return NULL;
                        } else if (!PyObject_IsTrue(fRes)) {
                            Py_DECREF(fRes);
                            Py_DECREF(obj_keys);
                            Py_DECREF(key);
                            goto failed;
                        }
                        Py_DECREF(fRes);
                        // if it's a value check it
                    } else {
                        bool check = PyObject_RichCompareBool(kwargsValue,
                                                              dictValue, Py_EQ);
                        Py_DECREF(dictValue);
                        if (!check) {
                            Py_DECREF(key);
                            Py_DECREF(obj_keys);
                            goto failed;
                        }
                    }
                } else {
                    Py_DECREF(key);
                    Py_DECREF(obj_keys);
                    goto failed;
                }
                Py_DECREF(key);
            }
            Py_DECREF(obj_keys);
        }
        // foreach check function
        for (Py_ssize_t f = 0; f < argLen; f++) {
            PyObject *function = PyTuple_GetItem(args, f);
            if (function == NULL) {
                return NULL;
            }
            PyObject *res = PyObject_CallOneArg(function, (PyObject *)obj);
            if (res == NULL) {
                return NULL;
            } else if (!PyObject_IsTrue(res)) {
                Py_DECREF(res);
                goto failed;
            }
            Py_DECREF(res);
        }
        PyList_Append(result, (PyObject *)obj);
    failed:; // if at any point we failed the checks, we jump here
    }
    Py_XDECREF(keys);
    return result;
}

PyObject *GtfList_new(Py_ssize_t len) {
    PyObject *list = PyList_New(len);
    if (list == NULL) {
        return NULL;
    }
    Py_SET_TYPE(list, &GtfListType);
    return list;
}

/*!
 @brief The methods of the GtfList object
*/
static PyMethodDef GtfList_methods[] = {
    {"find_closest_bound", (PyCFunction)GtfList_findHost, METH_VARARGS,
     "Returns None or the approximate host gene of the provided GtfDict"},
    {"append", (PyCFunction)GtfList_append, METH_VARARGS,
     "Appends the provided element to the GtfList"},
    {"extend", (PyCFunction)GtfList_extend, METH_VARARGS,
     "Extends the gene list with the provided iterable"},
    {"insert", (PyCFunction)GtfList_insert, METH_VARARGS,
     "Inserts the provided object at the provided position"},
    {"sq_split", (PyCFunction)GtfList_sq_split, METH_NOARGS,
     "Splits this gene list by the seqnames"},
    {"find", (PyCFunction)GtfList_find, METH_VARARGS | METH_KEYWORDS,
     "Splits this gene list by the seqnames"},
    {"column", (PyCFunction)GtfList_column, METH_VARARGS | METH_KEYWORDS,
     "Returns a list of the values of the provided key"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

/*!
 @brief The sequence methods of the GtfList object
*/
static PySequenceMethods GtfListSq = {.sq_inplace_concat =
                                          (binaryfunc)GtfList_inplace_concat,
                                      .sq_concat = (binaryfunc)GtfList_concat};

/*!
 @brief The mapping methods of the GtfList object
*/
static PyMappingMethods GtfListMap = {
    .mp_ass_subscript = (objobjargproc)GtfList_mp_ass_subscript};

PyTypeObject GtfListType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "eccLib.GtfList",
    .tp_basicsize = sizeof(GtfList),
    .tp_doc = PyDoc_STR("A list of GtfDicts"),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_init = (initproc)GtfList_init,
    .tp_as_mapping = &GtfListMap,
    .tp_methods = GtfList_methods,
    .tp_as_sequence = &GtfListSq,
    .tp_str = (reprfunc)GtfList_str,
    .tp_repr = (reprfunc)GtfList_repr};
