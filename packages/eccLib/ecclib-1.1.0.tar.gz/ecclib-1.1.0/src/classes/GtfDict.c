/*!
 @file GtfDict.c
 @brief Implementation of the GtfDict class
*/

#include "GtfDict.h"

#include <stdbool.h>
#include <stdlib.h>

#include "../formats/gtf.h"
#include <Python.h>

/*!
 @brief Returns the string representation of a Python string, with restricted
 characters percent encoded
 @param unicode the string to encode
 @param size the size of the string
 @return a newly allocated string with percent encoded characters
*/
static inline char *PyUnicode_AsEncodedUTF8AndSize(PyObject *unicode,
                                                   size_t *size) {
    Py_ssize_t len;
    const char *utf8 = PyUnicode_AsUTF8AndSize(unicode, &len);
    if (utf8 == NULL) {
        return NULL;
    }
    return gtf_percent_encode(utf8, len, size);
}

/*!
 @brief GtfDict.__init__()
 @param self the GtfDict instance being instantiated
 @param args the passed argument tuple
 @param kwargs the passed keywords argument as a dict
 @return -1 on error
 @ingroup GtfDict_class
*/
static int GtfDict_init(GtfDict *restrict self, PyObject *restrict args,
                        PyObject *restrict kwargs) {
    Py_ssize_t argsLen = PyTuple_GET_SIZE(args);
    // Input arg check
    if (argsLen > CORE_FIELD_COUNT) {
        PyErr_SetString(PyExc_ValueError,
                        "More than " STR(CORE_FIELD_COUNT) " arguments");
        return -1;
    }
    if (hashmap_create_xh(DEFAULT_ATTR_SIZE, &self->attributes) < 0) {
        PyErr_SetString(PyExc_Exception, "Failed to create hashmap");
        return -1;
    }
    if (kwargs == NULL) {
        if (argsLen == 1) { // conversion case
            PyObject *first = PyTuple_GET_ITEM(args, 0);
            if (PyMapping_Check(first)) {
                kwargs = first;
                argsLen = 0; // this will make the later code ignore the first
                             // argument
            }
        }
    } else {
        // might as well check...
        if (!PyArg_ValidateKeywordArguments(kwargs)) {
            return -1;
        }
    }
    // my own arg parsing because we can't combine PyArg_ParseTupleAndKeywords
    // with variable number of arguments
    const PyTypeObject *types[] = {
        &PyUnicode_Type, &PyUnicode_Type, &PyUnicode_Type, &PyLong_Type,
        &PyLong_Type,    &PyFloat_Type,   &PyBool_Type,    &PyLong_Type};
    for (unsigned char i = 0; i < CORE_FIELD_COUNT; i++) {
        PyObject *val;
        if (i >= argsLen) { // if args doesn't have i-th arg then try to find it
                            // in kwargs
            if (kwargs == NULL) {
                val = Py_None;
            } else {
                val = PyMapping_GetItemString(kwargs, keywords[i]);
                if (val == NULL) {
                    PyErr_Clear(); // shutup its fine
                    val = Py_None;
                } else {
                    Py_DECREF(val);
                }
            }
        } else { // else just get it from args
            val = PyTuple_GetItem(args, i);
            if (val == NULL) {
                return -1;
            }
        }
        // do type check
        if (!Py_IsNone(val) && !Py_IS_TYPE(val, (PyTypeObject *)types[i])) {
            PyErr_BadArgument();
            return -1;
        }
        Py_INCREF(val);
        // and update vals
        self->core[i] = val;
    }
    // basic validity checking
    if (self->end != Py_None && self->start != Py_None) {
        if (PyLong_AsLong(self->end) - PyLong_AsLong(self->start) < 0) {
            PyErr_SetString(PyExc_ValueError, "Negative gene length");
            return -1;
        }
    }
    if (self->frame != Py_None) {
        long frameLong = PyLong_AsLong(self->frame);
        if (frameLong > 2 || frameLong < 0) {
            PyErr_SetString(PyExc_ValueError, "Invalid frame value");
            return -1;
        }
    }
    if (kwargs != NULL) {
        PyObject *keys = PyMapping_Keys(kwargs);
        if (keys == NULL) {
            return -1;
        }
        Py_ssize_t keysLen = PySequence_Fast_GET_SIZE(keys);
        for (Py_ssize_t i = 0; i < keysLen; i++) {
            PyObject *key = PyList_GetItem(keys, i);
            if (key == NULL) {
                Py_DECREF(keys);
                return -1;
            }
            Py_ssize_t keyLen;
            const char *keyStr = PyUnicode_AsUTF8AndSize(key, &keyLen);
            if (keyStr == NULL) {
                Py_DECREF(keys);
                return -1;
            }
            // we skip the 7 keys
            bool found = false;
            for (unsigned char j = 0; j < CORE_FIELD_COUNT; j++) {
                if (keyLen == keyword_sizes[i] &&
                    strncmp(keyStr, keywords[j], keyLen) == 0) {
                    found = true;
                    break;
                }
            }
            if (found) {
                continue;
            }
            // and then insert
            PyObject *keyVal = PyMapping_GetItemString(kwargs, keyStr);
            if (keyVal == NULL) {
                PyErr_Clear();
                Py_DECREF(keys);
                return -1;
            } else {
                Py_DECREF(keyVal);
            }
            if (hashmap_put_tuple(&self->attributes, keyStr, keyLen, key,
                                  keyVal) < 0) {
                Py_DECREF(keys);
                return -1;
            }
        }
        Py_DECREF(keys);
    }
    return 0;
}

/*!
 @brief A wrapper over the dict getattro that also acts as a getter for the 7
 key GTF keys
 @param self
 @param attr PyUnicode encoded attribute name string
 @return the gotten attr value
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_getattro(GtfDict *restrict self,
                                  PyObject *restrict attr) {
    Py_ssize_t len;
    const char *restrict attrName = PyUnicode_AsUTF8AndSize(attr, &len);
    if (attrName == NULL) {
        return NULL;
    }
    if (len == 0) {
        return NULL;
    }
    for (unsigned char i = 0; i < CORE_FIELD_COUNT; i++) {
        if (len == keyword_sizes[i] &&
            strncmp(attrName, keywords[i], len) == 0) {
            Py_INCREF(self->core[i]);
            return self->core[i];
        }
    }
    return PyDict_Type.tp_getattro((PyObject *)self, attr);
}

/*!
 @brief A wrapper over the dict setattro that also acts as a setter for the 7
 key GTF keys
 @param self
 @param attr PyUnicode encoded attribute name string
 @param value the value that the attribute should be set to. Doesn't steal the
 reference. Hopefully that's the expected behaviour
 @return -1 on error
 @ingroup GtfDict_class
*/
static int GtfDict_setattro(GtfDict *restrict self, PyObject *restrict attr,
                            PyObject *restrict value) {
    Py_ssize_t len;
    const char *restrict attrName = PyUnicode_AsUTF8AndSize(attr, &len);
    if (attrName == NULL) {
        return -1;
    }
    if (len == 0) {
        return -1;
    }
    for (unsigned char i = 0; i < CORE_FIELD_COUNT; i++) {
        if (len == keyword_sizes[i] &&
            strncmp(attrName, keywords[i], len) == 0) {
            if (value == NULL) {
                PyErr_SetString(PyExc_Exception,
                                "You cannot delete a core key");
                return -1;
            }
            Py_INCREF(value);
            Py_DECREF(self->core[i]);
            self->core[i] = value;
            return 0;
        }
    }
    return PyDict_Type.tp_setattro((PyObject *)self, attr, value);
}

/*!
 @brief A custom GtfDict richcompare
 @param self
 @param other the object that should be compared with self. Mapping or GtfDict
 @param op what operation is being performed
 @return PyBool describing the result
 @note Here the operator overrides are defined
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_richcompare(GtfDict *restrict self,
                                     PyObject *restrict other, const int op) {
    // If guard to prevent undefined behaviour with restrict using keyCompare
    if ((PyObject *)self == other) {
        // This should be effective enough given that Python shouldn't do
        // aliasing
        return Py_True;
    }
    PyObject *restrict otherStart;
    PyObject *restrict otherEnd;
    PyObject *restrict otherSeqname;
    PyObject *restrict otherFeature;
    PyObject *restrict otherReverse;
    if (PyMapping_Check(other)) {
        otherStart = PyMapping_GetItemString(other, keywords[START]);
        Py_XDECREF(otherStart);
        otherEnd = PyMapping_GetItemString(other, keywords[END]);
        Py_XDECREF(otherEnd);
        otherSeqname = PyMapping_GetItemString(other, keywords[SEQNAME]);
        Py_XDECREF(otherSeqname);
        otherFeature = PyMapping_GetItemString(other, keywords[FEATURE]);
        Py_XDECREF(otherFeature);
        otherReverse = PyMapping_GetItemString(other, keywords[REVERSE]);
        Py_XDECREF(otherReverse);
        if (otherStart == NULL || otherEnd == NULL || otherSeqname == NULL ||
            otherFeature == NULL || otherReverse == NULL) {
            PyErr_Clear(); // we don't care about the error this is fine
            return PyBool_FromLong(false || op == Py_NE);
        }
    } else if (Py_IS_TYPE(other, &GtfDictType)) {
        otherStart = ((GtfDict *)other)->start;
        otherEnd = ((GtfDict *)other)->end;
        otherSeqname = ((GtfDict *)other)->seqname;
        otherFeature = ((GtfDict *)other)->feature;
        otherReverse = ((GtfDict *)other)->reverse;
    } else {
        PyErr_SetString(PyExc_TypeError, "Invalid type");
        return NULL;
    }

    bool result = false;
    switch (op) {
    case Py_EQ: {
        result = PyObject_RichCompareBool(self->start, otherStart, op) &&
                 PyObject_RichCompareBool(self->end, otherEnd, op) &&
                 PyObject_RichCompareBool(self->seqname, otherSeqname, op) &&
                 PyObject_RichCompareBool(self->feature, otherFeature, op) &&
                 PyObject_RichCompareBool(self->reverse, otherReverse, op);
        break;
    }
    case Py_NE: {
        result = PyObject_RichCompareBool(self->start, otherStart, op) ||
                 PyObject_RichCompareBool(self->end, otherEnd, op) ||
                 PyObject_RichCompareBool(self->seqname, otherSeqname, op) ||
                 PyObject_RichCompareBool(self->feature, otherFeature, op) ||
                 PyObject_RichCompareBool(self->reverse, otherReverse, op);
        break;
    }
    case Py_LE: { // True if self.end <= other.end -> so if sequence is before
                  // with permissible overlap
        result = PyObject_RichCompareBool(self->seqname, otherSeqname, Py_EQ) &&
                 PyObject_RichCompareBool(self->reverse, otherReverse, Py_EQ) &&
                 PyObject_RichCompareBool(self->end, otherEnd, Py_LE);
        break;
    }
    case Py_LT: { // True if self.end < other.start
        result = PyObject_RichCompareBool(self->seqname, otherSeqname, Py_EQ) &&
                 PyObject_RichCompareBool(self->reverse, otherReverse, Py_EQ) &&
                 PyObject_RichCompareBool(self->end, otherStart, Py_LT);
        break;
    }
    case Py_GE: { // True if self.start >= other.start
        result = PyObject_RichCompareBool(self->seqname, otherSeqname, Py_EQ) &&
                 PyObject_RichCompareBool(self->reverse, otherReverse, Py_EQ) &&
                 PyObject_RichCompareBool(self->start, otherStart, Py_GE);
        break;
    }
    case Py_GT: { // True if self.start > other.end
        result = PyObject_RichCompareBool(self->seqname, otherSeqname, Py_EQ) &&
                 PyObject_RichCompareBool(self->reverse, otherReverse, Py_EQ) &&
                 PyObject_RichCompareBool(self->start, otherEnd, Py_GT);
        break;
    }
    default: {
        PyErr_SetString(PyExc_NotImplementedError,
                        "Operation not implemented for this type");
        return NULL;
    }
    }
    return PyBool_FromLong((long)result);
}

/*!
 @brief A custom method that determines if self overlaps with a different
 GtfDict
 @param self
 @param args a python argument tuple
 @return PyBool
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_overlaps(GtfDict *restrict self,
                                  PyObject *restrict args) {
    PyObject *restrict other = PyTuple_GetItem(args, 0);
    if (other == NULL) {
        return NULL;
    }
    bool overlaps = false;
    PyObject *restrict startOther;
    PyObject *restrict endOther;
    PyObject *restrict seqnameOther;
    PyObject *restrict reverseOther;
    if (Py_IS_TYPE(other, &GtfDictType)) {
        startOther = ((GtfDict *)other)->start;
        endOther = ((GtfDict *)other)->end;
        seqnameOther = ((GtfDict *)other)->seqname;
        reverseOther = ((GtfDict *)other)->reverse;
    } else if (PyMapping_Check(other)) {
        startOther = PyMapping_GetItemString(other, keywords[START]);
        if (startOther == NULL) {
            return NULL;
        } else {
            Py_DECREF(startOther);
        }
        endOther = PyMapping_GetItemString(other, keywords[END]);
        if (endOther == NULL) {
            return NULL;
        } else {
            Py_DECREF(endOther);
        }
        seqnameOther = PyMapping_GetItemString(other, keywords[SEQNAME]);
        if (seqnameOther == NULL) {
            return NULL;
        } else {
            Py_DECREF(seqnameOther);
        }
        reverseOther = PyMapping_GetItemString(other, keywords[REVERSE]);
        if (reverseOther == NULL) {
            return NULL;
        } else {
            Py_DECREF(reverseOther);
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "Invalid type");
        return NULL;
    }
    if (PyObject_RichCompareBool(self->seqname, seqnameOther, Py_EQ) &&
        (PyObject_RichCompareBool(self->reverse, reverseOther, Py_EQ) ||
         Py_IsNone(self->reverse) || Py_IsNone(reverseOther))) {
        overlaps = (PyObject_RichCompareBool(endOther, self->start, Py_GE) &&
                    PyObject_RichCompareBool(startOther, self->end, Py_LE));
    }
    return PyBool_FromLong((long)overlaps);
}

int GtfDict_containsValue(GtfDict *restrict self, PyObject *restrict other) {
    if ((PyObject *)self == other) {
        return true;
    }
    bool contains = false;
    PyObject *restrict startOther;
    PyObject *restrict endOther;
    PyObject *restrict seqnameOther;
    PyObject *restrict reverseOther;
    if (Py_IS_TYPE(other, &GtfDictType)) {
        startOther = ((GtfDict *)other)->start;
        endOther = ((GtfDict *)other)->end;
        seqnameOther = ((GtfDict *)other)->seqname;
        reverseOther = ((GtfDict *)other)->reverse;
    } else if (PyMapping_Check(other)) {
        startOther = PyMapping_GetItemString(other, keywords[START]);
        if (startOther == NULL) {
            return -1;
        } else {
            Py_DECREF(startOther);
        }
        endOther = PyMapping_GetItemString(other, keywords[END]);
        if (endOther == NULL) {
            return -1;
        } else {
            Py_DECREF(endOther);
        }
        seqnameOther = PyMapping_GetItemString(other, keywords[SEQNAME]);
        if (seqnameOther == NULL) {
            return -1;
        } else {
            Py_DECREF(seqnameOther);
        }
        reverseOther = PyMapping_GetItemString(other, keywords[REVERSE]);
        if (reverseOther == NULL) {
            return -1;
        } else {
            Py_DECREF(reverseOther);
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "Invalid type");
        return -1;
    }
    if (PyObject_RichCompareBool(self->seqname, seqnameOther, Py_EQ) &&
        (PyObject_RichCompareBool(self->reverse, reverseOther, Py_EQ) ||
         Py_IsNone(self->reverse) || Py_IsNone(reverseOther))) {
        contains = PyObject_RichCompareBool(startOther, self->start, Py_GE) &&
                   PyObject_RichCompareBool(endOther, self->end, Py_LE);
    }
    return (int)contains;
}

/*!
 @brief Wrapper over GtfDict_containsValue() that allows for this method to be
 used as standalone
 @param self
 @param args the standard Python argument tuple
 @return PyBool result
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_contains(GtfDict *restrict self,
                                  PyObject *restrict args) {
    PyObject *restrict other = PyTuple_GetItem(args, 0);
    if (other == NULL) {
        return NULL;
    }
    return PyBool_FromLong((long)GtfDict_containsValue(self, other));
}

/*!
 @brief Comparison function for sorting ranges by start, then end
 @param a pointer to the first range (long[2])
 @param b pointer to the second range (long[2])
 @return negative if a < b, 0 if equal, positive if a > b
*/
static int gtf_range_compare(const void *a, const void *b) {
    const long *ra = (const long *)a;
    const long *rb = (const long *)b;
    if (ra[0] != rb[0]) {
        return (ra[0] > rb[0]) - (ra[0] < rb[0]);
    }
    return (ra[1] > rb[1]) - (ra[1] < rb[1]);
}

/*!
 @brief A custom method that returns the percentage of the gene that is
 covered by the other GtfDict or iterable of GtfDicts
 @param self
 @param args a python argument tuple
 @return PyFloat representing the coverage percentage
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_coverage(GtfDict *restrict self,
                                  PyObject *restrict args) {
    PyObject *restrict other = PyTuple_GetItem(args, 0);
    if (other == NULL) {
        return NULL;
    }
    if (Py_IS_TYPE(other, &GtfDictType)) {
        // if other is a GtfDict then the job is fairly easy
        GtfDict *restrict otherGtf = (GtfDict *)other;
        if (self->seqname != otherGtf->seqname ||
            self->reverse != otherGtf->reverse) {
            PyErr_SetString(PyExc_ValueError,
                            "Cannot calculate coverage for different "
                            "sequences or strands");
            return NULL;
        }
        long selfStart = PyLong_AsLong(self->start);
        long selfEnd = PyLong_AsLong(self->end);
        long otherStart = PyLong_AsLong(otherGtf->start);
        long otherEnd = PyLong_AsLong(otherGtf->end);

        long max_start = selfStart > otherStart ? selfStart : otherStart;
        long min_end = selfEnd < otherEnd ? selfEnd : otherEnd;
        if (max_start >= min_end) {
            // no overlap
            return PyFloat_FromDouble(0.0);
        }
        double coverage =
            (double)(min_end - max_start) / (double)(selfEnd - selfStart);

        return PyFloat_FromDouble(coverage);
    } else {
        PyObject *restrict iter = PyObject_GetIter(other); // new reference
        if (iter == NULL) {
            PyErr_SetString(PyExc_TypeError,
                            "Argument must be a GtfDict or an iterable of "
                            "GtfDicts");
            return NULL;
        }
        size_t iterSize = 0;
        long (*restrict ranges)[2] = malloc(sizeof(long[2]));
        PyObject *restrict item = PyIter_Next(iter); // new reference
        while (item != NULL) {
            if (!Py_IS_TYPE(item, &GtfDictType)) {
                PyErr_SetString(PyExc_TypeError,
                                "Argument must be a GtfDict or an iterable "
                                "of GtfDicts");
                Py_DECREF(item);
                Py_DECREF(iter);
                return NULL;
            }

            GtfDict *restrict otherGtf = (GtfDict *)item;
            if (self->seqname == otherGtf->seqname ||
                self->reverse == otherGtf->reverse) {

                long selfStart = PyLong_AsLong(self->start);
                long selfEnd = PyLong_AsLong(self->end);
                long otherStart = PyLong_AsLong(otherGtf->start);
                long otherEnd = PyLong_AsLong(otherGtf->end);
                long max_start =
                    selfStart > otherStart ? selfStart : otherStart;
                long min_end = selfEnd < otherEnd ? selfEnd : otherEnd;
                if (max_start < min_end) {
                    // overlap found, add to the ranges
                    ranges = realloc(ranges, sizeof(long[2]) * (iterSize + 1));
                    ranges[iterSize][0] = max_start;
                    ranges[iterSize][1] = min_end;
                    iterSize++;
                }
            }

            Py_DECREF(item);
            item = PyIter_Next(iter);
        }
        Py_DECREF(iter);
        qsort(ranges, iterSize, sizeof(long[2]),
              (int (*)(const void *, const void *))gtf_range_compare);
        // now we have the ranges sorted, we can merge them
        long (*mergedRanges)[2] = malloc(sizeof(long[2]) * iterSize);
        size_t mergedSize = 0;
        for (size_t i = 0; i < iterSize; i++) {
            if (mergedSize == 0 ||
                ranges[i][0] > mergedRanges[mergedSize - 1][1]) {
                // no overlap with the last range, add a new one
                mergedRanges[mergedSize][0] = ranges[i][0];
                mergedRanges[mergedSize][1] = ranges[i][1];
                mergedSize++;
            } else {
                // overlap with the last range, merge them
                if (ranges[i][1] > mergedRanges[mergedSize - 1][1]) {
                    mergedRanges[mergedSize - 1][1] = ranges[i][1];
                }
            }
        }
        free(ranges);
        if (mergedSize == 0) {
            // no overlap found
            free(mergedRanges);
            return PyFloat_FromDouble(0.0);
        }
        long selfStart = PyLong_AsLong(self->start);
        long selfEnd = PyLong_AsLong(self->end);
        long totalCovered = 0;
        for (size_t i = 0; i < mergedSize; i++) {
            totalCovered += mergedRanges[i][1] - mergedRanges[i][0];
        }
        free(mergedRanges);
        double coverage = (double)totalCovered / (double)(selfEnd - selfStart);
        return PyFloat_FromDouble(coverage);
    }
}

/*!
 @brief Custom __len__ method that returns actually the result of subtracting
 start from end
 @param self
 @return the gene length
 @ingroup GtfDict_class
*/
static Py_ssize_t GtfDict_len(GtfDict *restrict self) {
    long start = PyLong_AsLong(self->start);
    long end = PyLong_AsLong(self->end);
    return (Py_ssize_t)(end - start);
}

/*!
 @def getGTFValue(dict, key)
 @brief A macro that creates a string representation of a key in the GTF line
 @details bit of a hack to avoid code duplication
 @param dict the GtfDict instance
 @param key the key to get
 @note Creates keyStr, keySize and key variables
*/
#define getGTFValue(dict, key)                                                 \
    PyObject *key##Str = NULL;                                                 \
    size_t key##Size;                                                          \
    char *restrict key;                                                        \
    if (Py_IsNone(dict->key)) {                                                \
        key = malloc(2);                                                       \
        key[0] = '.';                                                          \
        key[1] = '\0';                                                         \
        key##Size = 1;                                                         \
    } else {                                                                   \
        key##Str = PyObject_Str(dict->key);                                    \
        key = PyUnicode_AsEncodedUTF8AndSize(key##Str, &key##Size);            \
        Py_DECREF(key##Str);                                                   \
    }

/*!
 @brief A struct to use during iteration over the attributes
*/
struct iterateContext {
    char *restrict *result;
    size_t *resSize;
};

/*!
 @brief Function to iterate over the attributes and append them to the result
 @param context the iterateContext
 @param e the current element
 @return 0
*/
static int iterate_to_str(void *const context,
                          struct hashmap_element_s *const e) {
    struct iterateContext *restrict ctx = (struct iterateContext *)context;
    struct map_tuple *tuple = (struct map_tuple *)e->data;
    PyObject *value = PyObject_Str(tuple->value);
    size_t valueSz;
    char *valueStr = PyUnicode_AsEncodedUTF8AndSize(value, &valueSz);
    Py_DECREF(value);
    size_t partSize = valueSz + e->key_len + 5;
    *ctx->result = realloc(*ctx->result, *ctx->resSize + partSize + 1);
    sprintf(*ctx->result + *ctx->resSize, "%s \"%s\"; ", (char *)e->key,
            valueStr);
    free(valueStr);
    *ctx->resSize += partSize - 1;
    return 0;
}

char *GtfDictToGTF(GtfDict *restrict self, size_t *restrict len) {
    // first get the keyless values
    getGTFValue(self, seqname);
    getGTFValue(self, source);
    getGTFValue(self, feature);
    getGTFValue(self, start);
    getGTFValue(self, end);
    getGTFValue(self, score);
    char reverse[] = ".";
    if (!Py_IsNone(self->reverse)) {
        if (PyLong_AsLong(self->reverse)) {
            reverse[0] = '-';
        } else {
            reverse[0] = '+';
        }
    }
    getGTFValue(self, frame);
    size_t resSize = seqnameSize + sourceSize + featureSize + startSize +
                     endSize + scoreSize + frameSize + 9;
    char *restrict result = calloc(resSize + 1, sizeof(char));
    sprintf(result, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t", seqname, source,
            feature, start, end, score, reverse, frame);
    free(seqname);
    free(source);
    free(feature);
    free(start);
    free(end);
    free(score);
    free(frame);
    {
        struct iterateContext context = {&result, &resSize};
        if (hashmap_iterate_pairs(&self->attributes, iterate_to_str, &context) <
            0) {
            PyErr_SetString(PyExc_Exception,
                            "Failed to iterate over attributes");
            free(result);
            return NULL;
        }
    }
    if (len != NULL) {
        *len = resSize;
    }
    return result;
}

/*!
 @brief returns the GTF representation of the GtfDict
 @param self
 @return PyUnicode GTF representation
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_str(GtfDict *restrict self) {
    size_t resSize;
    char *restrict result = GtfDictToGTF(self, &resSize);
    PyObject *res = PyUnicode_DecodeUTF8(result, resSize, NULL);
    free(result);
    return res;
}

PyObject *GtfDict_getitem(GtfDict *restrict self, PyObject *restrict key) {
    Py_ssize_t len;
    const char *keyStrC = PyUnicode_AsUTF8AndSize(key, &len);
    if (keyStrC == NULL) {
        return NULL;
    }
    for (int i = 0; i < CORE_FIELD_COUNT; i++) {
        if (len == keyword_sizes[i] &&
            strncmp(keyStrC, keywords[i], keyword_sizes[i]) == 0) {
            Py_INCREF(self->core[i]);
            return self->core[i];
        }
    }
    struct map_tuple *tuple = hashmap_get(&self->attributes, keyStrC, len);
    if (tuple == NULL) {
        PyErr_SetString(PyExc_KeyError, "Key not found");
        return NULL;
    }
    PyObject *res = tuple->value;
    Py_INCREF(res);
    return res;
}

/*!
 @brief A custom setitem that also checks the core attributes
 @param self
 @param key the key to set
 @param value borrowed value to set
 @return -1 on error
 @ingroup GtfDict_class
*/
static int GtfDict_setitem(GtfDict *restrict self, PyObject *restrict key,
                           PyObject *restrict value) {
    Py_ssize_t len;
    const char *keyStrC = PyUnicode_AsUTF8AndSize(key, &len);
    if (keyStrC == NULL) {
        return -1;
    }
    for (int i = 0; i < CORE_FIELD_COUNT; i++) {
        if (len == keyword_sizes[i] &&
            strncmp(keyStrC, keywords[i], keyword_sizes[i]) == 0) {
            if (value == NULL) {
                PyErr_SetString(PyExc_Exception,
                                "You cannot delete a core key");
                return -1;
            }
            Py_DECREF(self->core[i]);
            Py_INCREF(value);
            self->core[i] = value;
            return 0;
        }
    }
    if (value == NULL) {
        struct map_tuple *res =
            hashmap_pop_tuple(&self->attributes, keyStrC, len);
        if (res == NULL) {
            PyErr_SetString(PyExc_KeyError, "Key not found");
            return -1;
        }
        Py_DECREF(res->key);
        Py_DECREF(res->value);
        free(res);
        return 0;
    }
    int res = hashmap_put_tuple(&self->attributes, keyStrC, len, key, value);
    if (res == -1) {
        PyErr_SetString(PyExc_Exception, "Failed to set item");
    }
    return res;
}

/*!
 @brief A function to iterate over the keys of the GtfDict
 @param context the list to append the keys to
 @param e the current element
 @return 1 on success
*/
static int iterate_keys(void *const context, void *const e) {
    struct map_tuple *tuple = (struct map_tuple *)e;
    if (PyList_Append((PyObject *)context, tuple->key) < 0) {
        return -1;
    }
    return 1;
}

PyObject *GtfDict_keys(GtfDict *restrict self) {
    PyObject *keys = PyList_New(CORE_FIELD_COUNT);
    if (keys == NULL) {
        return NULL;
    }
    for (int i = 0; i < CORE_FIELD_COUNT; i++) {
        PyObject *key =
            PyUnicode_DecodeUTF8(keywords[i], keyword_sizes[i], NULL);
        if (key == NULL) {
            Py_DECREF(keys);
            return NULL;
        }
        if (PyList_SetItem(keys, i, key) < 0) {
            Py_DECREF(keys);
            return NULL;
        }
    }
    if (hashmap_iterate(&self->attributes, iterate_keys, keys) != 0) {
        Py_DECREF(keys);
        return NULL;
    }
    return keys;
}

/*!
 @brief A function to iterate over the values of the GtfDict
 @param context the list to append the values to
 @param held the current element
 @return 1 on success
*/
static int iterate_values(void *const context, void *const held) {
    struct map_tuple *tuple = (struct map_tuple *)held;
    if (PyList_Append((PyObject *)context, tuple->value) < 0) {
        return 0;
    }
    return 1;
}

/*!
 @brief A function that returns the values of the GtfDict
 @param self
 @return a list of the values
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_values(GtfDict *restrict self) {
    PyObject *values = PyList_New(CORE_FIELD_COUNT);
    if (values == NULL) {
        return NULL;
    }
    for (int i = 0; i < CORE_FIELD_COUNT; i++) {
        Py_INCREF(self->core[i]);
        PyList_SetItem(values, i, self->core[i]);
    }
    if (hashmap_iterate(&self->attributes, iterate_values, values) != 0) {
        Py_DECREF(values);
        return NULL;
    }
    return values;
}

/*!
 @brief Returns the iterator for the GtfDict
 @param self
 @return the iterator
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_iter(GtfDict *restrict self) {
    PyObject *keys = GtfDict_keys(self);
    if (keys == NULL) {
        return NULL;
    }
    PyObject *iter = PyObject_GetIter(keys);
    Py_DECREF(keys);
    return iter;
}

/*!
 @brief A custom pop method that also checks the core attributes
 @param self
 @param args the argument tuple
 @return new reference to the popped value
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_pop(GtfDict *restrict self, PyObject *restrict args) {
    PyObject *key = PyTuple_GetItem(args, 0);
    if (key == NULL) {
        return NULL;
    }
    Py_ssize_t len;
    const char *keyStrC = PyUnicode_AsUTF8AndSize(key, &len);
    if (keyStrC == NULL) {
        return NULL;
    }
    for (int i = 0; i < CORE_FIELD_COUNT; i++) {
        if (len == keyword_sizes[i] &&
            strncmp(keyStrC, keywords[i], keyword_sizes[i]) == 0) {
            PyErr_SetString(PyExc_Exception, "You cannot delete a core key");
            return NULL;
        }
    }
    struct map_tuple *res = hashmap_pop_tuple(&self->attributes, keyStrC, len);
    if (res == NULL) {
        PyErr_SetString(PyExc_KeyError, "Key not found");
        return NULL;
    }
    PyObject *val = res->value;
    Py_DECREF(res->key);
    free(res);
    return val;
}

/*!
 @brief A custom get method that also allows for a default value to be provided
 @param self
 @param args the argument tuple
 @return new reference to the gotten value
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_get(GtfDict *restrict self, PyObject *restrict args) {
    PyObject *key = PyTuple_GetItem(args, 0);
    if (key == NULL) {
        return NULL;
    }
    PyObject *defaultVal = PyTuple_GetItem(args, 1);
    if (defaultVal == NULL) {
        PyErr_Clear();
        defaultVal = Py_None;
    }
    PyObject *res = GtfDict_getitem(self, key);
    if (res == NULL) {
        PyErr_Clear();
        Py_INCREF(defaultVal);
        return defaultVal;
    }
    return res;
}

/*!
 @brief A custom items method that also checks the core attributes
 @param self
 @return a list of tuples containing the key-value pairs
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_items(GtfDict *restrict self) {
    PyObject *keys = GtfDict_keys(self);
    if (keys == NULL) {
        return NULL;
    }
    PyObject *items = PyList_New(PyList_Size(keys));
    if (items == NULL) {
        Py_DECREF(keys);
        return NULL;
    }
    for (Py_ssize_t i = 0; i < PyList_Size(keys); i++) {
        PyObject *key = PyList_GetItem(keys, i);
        if (key == NULL) {
            Py_DECREF(keys);
            Py_DECREF(items);
            return NULL;
        }
        PyObject *value = GtfDict_getitem(self, key);
        if (value == NULL) {
            Py_DECREF(keys);
            Py_DECREF(items);
            return NULL;
        }
        Py_DECREF(value);
        PyObject *tuple = PyTuple_Pack(2, key, value);
        if (tuple == NULL) {
            Py_DECREF(keys);
            Py_DECREF(items);
            return NULL;
        }
        PyList_SetItem(items, i, tuple);
    }
    Py_DECREF(keys);
    return items;
}

/*!
 @brief A custom update method that also checks the core attributes
 @param self
 @param args the argument tuple
 @return None
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_update(GtfDict *restrict self,
                                PyObject *restrict args) {
    PyObject *other = PyTuple_GetItem(args, 0);
    if (other == NULL) {
        return NULL;
    }
    if (!PyMapping_Check(other)) {
        PyErr_SetString(PyExc_TypeError, "Invalid type");
        return NULL;
    }
    if (!PyArg_ValidateKeywordArguments(other)) {
        PyErr_SetString(PyExc_TypeError, "Provided map has non string keys");
        return NULL;
    }
    PyObject *keys = PyMapping_Keys(other);
    if (keys == NULL) {
        return NULL;
    }
    Py_ssize_t keysSize = PyList_Size(keys);
    for (Py_ssize_t i = 0; i < keysSize; i++) {
        PyObject *key = PyList_GetItem(keys, i);
        PyObject *value = PyObject_GetItem(other, key);
        if (value == NULL) {
            Py_DECREF(keys);
            return NULL;
        }
        if (GtfDict_setitem(self, key, value) < 0) {
            Py_DECREF(keys);
            return NULL;
        }
    }
    Py_DECREF(keys);
    Py_INCREF(Py_None);
    return Py_None;
}

/*!
 @brief Custom deallocator that deallocates all the core attributes
 @param self
 @ingroup GtfDict_class
*/
static void GtfDict_dealloc(GtfDict *restrict self) {
    Py_XDECREF(self->seqname);
    Py_XDECREF(self->source);
    Py_XDECREF(self->feature);
    Py_XDECREF(self->start);
    Py_XDECREF(self->end);
    Py_XDECREF(self->score);
    Py_XDECREF(self->reverse);
    Py_XDECREF(self->frame);
    hashmap_destroy_tuple(&self->attributes);
    // Deallocators also need to call the parent deallocator
    PyObject_Free(self);
}

/*!
 @brief A custom hash function that XORs the hashes of the core attributes and
 the attributes
 @param context the context to store the hash in
 @param value the current value
 @return 1 on success
*/
static int iterate_hash(void *const context, void *const value) {
    struct map_tuple *tuple = (struct map_tuple *)value;
    *(hashmap_uint32_t *)context ^= PyObject_Hash(tuple->key);
    Py_hash_t hash = PyObject_Hash(tuple->value);
    if (hash == -1) {
        return 0;
    }
    *(hashmap_uint32_t *)context ^= hash;
    return 1;
}

/*!
 @brief A GtfDict hash function that XORs the hashes of the core attributes and
 the attributes
 @param self
 @return the hash
 @ingroup GtfDict_class
*/
static Py_hash_t GtfDict_hash(GtfDict *restrict self) {
    Py_hash_t hash = PyObject_Hash(self->core[0]);
    for (int i = 1; i < CORE_FIELD_COUNT; i++) {
        Py_hash_t coreHash = PyObject_Hash(self->core[i]);
        if (coreHash == -1) {
            return -1;
        }
        hash ^= coreHash;
    }
    hashmap_uint32_t attrHash = 0;
    if (hashmap_iterate(&self->attributes, iterate_hash, &attrHash) != 0) {
        return -1;
    }
    hash ^= attrHash;
    return hash;
}

/*!
 @brief A custom __repr__ method that returns a dict representation of the
 GtfDict
 @param self
 @return the dict representation
 @ingroup GtfDict_class
*/
static PyObject *GtfDict_repr(PyObject *restrict self) {
    PyObject *args = PyTuple_New(1);
    Py_INCREF(self);
    PyTuple_SetItem(args, 0, (PyObject *)self);
    PyObject *dict = PyObject_CallObject((PyObject *)&PyDict_Type, args);
    Py_DECREF(args);
    if (dict == NULL) {
        return NULL;
    }
    PyObject *repr = PyObject_Repr(dict);
    Py_DECREF(dict);
    return repr;
}

/*!
 @brief All the methods of the GtfDict class
*/
static PyMethodDef GtfDict_methods[] = {
    {"overlaps", (PyCFunction)GtfDict_overlaps, METH_VARARGS,
     "Returns true if the provided GtfDict overlaps with this GtfDict"},
    {"contains", (PyCFunction)GtfDict_contains, METH_VARARGS,
     "Returns true if the provided GtfDict can be considered to be entirely "
     "contained within the range of this GtfDict"},
    {"keys", (PyCFunction)GtfDict_keys, METH_NOARGS, "Returns a list of keys"},
    {"values", (PyCFunction)GtfDict_values, METH_NOARGS,
     "Returns a list of values"},
    {"pop", (PyCFunction)GtfDict_pop, METH_VARARGS,
     "Pops the value of the provided key"},
    {"get", (PyCFunction)GtfDict_get, METH_VARARGS,
     "Gets the value of the provided key, or the default value if the key is "
     "not found"},
    {"items", (PyCFunction)GtfDict_items, METH_NOARGS,
     "Returns a list of tuples containing the key-value pairs"},
    {"update", (PyCFunction)GtfDict_update, METH_VARARGS,
     "Updates the GtfDict with the provided dict"},
    {"coverage", (PyCFunction)GtfDict_coverage, METH_VARARGS,
     "Returns the percentage of the gene that is covered by the other GtfDict "
     "or iterable of GtfDicts"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

/*!
 @brief The sequence methods of the GtfDict class
*/
static PySequenceMethods GtfDictSeq = {.sq_contains =
                                           (objobjproc)GtfDict_containsValue,
                                       .sq_length = (lenfunc)GtfDict_len};

/*!
 @brief The mapping methods of the GtfDict class
*/
static PyMappingMethods GtfDictMap = {
    .mp_subscript = (binaryfunc)GtfDict_getitem,
    .mp_ass_subscript = (objobjargproc)GtfDict_setitem};

PyTypeObject GtfDictType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "eccLib.GtfDict",
    .tp_basicsize = sizeof(GtfDict),
    .tp_doc = PyDoc_STR("A dict that has all the necessary keys to be "
                        "compliant with GTF specification"),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_dealloc = (destructor)GtfDict_dealloc,
    .tp_init = (initproc)GtfDict_init,
    .tp_richcompare = (richcmpfunc)GtfDict_richcompare,
    .tp_repr = (reprfunc)GtfDict_repr,
    .tp_str = (reprfunc)GtfDict_str,
    .tp_iter = (getiterfunc)GtfDict_iter,
    .tp_getattro = (getattrofunc)GtfDict_getattro,
    .tp_setattro = (setattrofunc)GtfDict_setattro,
    .tp_hash = (hashfunc)GtfDict_hash,
    .tp_methods = GtfDict_methods,
    .tp_as_sequence = &GtfDictSeq,
    .tp_as_mapping = &GtfDictMap};
