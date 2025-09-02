/*!
 @file functions.c
 @brief Functions for parsing files. Core of the library
*/

#include "functions.h"

#include <ctype.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <Python.h>
#include <string.h>

#include "classes/FastaBuff.h"
#include "classes/GtfDict.h"
#include "classes/GtfList.h"
#include "common.h"
#include "formats/fasta.h"
#include "formats/gtf.h"
#include "pyport.h"

#if __unix__
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

/*!
 @brief Struct for storing input data for parsing functions
*/
typedef struct {
    /*!
     @brief The string to parse
     @warning This should not be modified
    */
    const char *str;
    /*!
     @brief The length of the string
    */
    Py_ssize_t len;
    /*!
     @brief The PyUnicode object that holds the string
     @warning MAY BE NULL
    */
    PyObject *parent;
} input_t;

/*!
 @brief Checks if the input_t object is NULL
 @param input the input_t object to check
 @return true or false depending on if the input_t object is NULL
*/
#define input_t_is_NULL(input) (input.str == NULL)

/*!
 @brief NULL input_t object
 @return an input_t object with all fields set to NULL
*/
#define NULL_input_t                                                           \
    (input_t) { NULL, 0, NULL }

/*!
 @brief Frees the input_t object
 @param input the input_t object to free
 @warning MUST BE CALLED WITH input_t_is_NULL(input) == false
 @note on *nix systems munmap() is used to free the memory mapped file
*/
static void free_input_t(input_t input) {
    if (input.parent != NULL) {
        Py_DECREF(input.parent);
    }
#ifdef __unix__
    else {
        munmap((void *)input.str, input.len);
    }
#endif
}

/*!
 @brief Gets file contents object for parsing from python function arguments
 @details For performance reasons this function will attempt to get the file
 size using seek() and tell() if the object has those methods and then load the
 entire file using mmap(). If the object doesn't have seek() then it will just
 call read(-1).
 @param first the first argument
 @return a input_t object containing the file contents
 @note first needs to be either a string or have a read method
*/
static input_t getFileContentsFromArgs(PyObject *restrict first) {
    input_t result;
    if (PyUnicode_Check(first)) {
        Py_INCREF(first);
        result.parent = first;
    } else {
#ifdef __unix__
        { // exclusive to systems that have read() and fstat() so POSIX afaik
            int fd = PyObject_AsFileDescriptor(first);
            if (fd >= 0) {
                // If the object can be converted to a file descriptor
                { // first get the file size
                    struct stat sb;
                    if (fstat(fd, &sb) != 0) {
                        PyErr_SetFromErrno(PyExc_OSError);
                        return NULL_input_t;
                    }
                    result.len = sb.st_size;
                }

                { // then we mmap
                    char *restrict mmap_buff =
                        mmap(NULL, result.len, PROT_READ, MAP_SHARED, fd, 0);
                    if (mmap_buff == MAP_FAILED) {
                        PyErr_SetFromErrno(PyExc_OSError);
                        return NULL_input_t;
                    }
                    result.str = mmap_buff;
                }

                result.parent = NULL;
                return result;
            } else {
                PyErr_Clear();
            }
        }
#endif
        if (PyObject_HasAttrString(first, "seek") == false) {
            result.parent = PyObject_CallMethod(first, "read", "i", -1);
        } else {
            PyObject *seek = PyObject_CallMethod(first, "seek", "ii", 0, 2);
            if (seek == NULL) {
                return NULL_input_t;
            }
            Py_DECREF(seek);
            PyObject *size = PyObject_CallMethod(first, "tell", NULL);
            if (size == NULL) {
                return NULL_input_t;
            }
            seek = PyObject_CallMethod(first, "seek", "ii", 0, 0);
            if (seek == NULL) {
                Py_DECREF(size);
                return NULL_input_t;
            }
            Py_DECREF(seek);
            result.parent = PyObject_CallMethod(first, "read", "O", size);
            Py_DECREF(size);
        }
        if (result.parent == NULL) {
            return NULL_input_t;
        }
        if (!PyUnicode_Check(result.parent)) {
            PyErr_SetString(PyExc_Exception, "File contents must be a string");
            Py_DECREF(result.parent);
            return NULL_input_t;
        }
    }
    result.str = PyUnicode_AsUTF8AndSize(result.parent, &result.len);
    return result;
}

/*!
 @brief Adds an entry to the FASTA tuple
 @param list the list to add the entry to
 @param title the title of the entry
 @param titleLen the length of the title
 @param seq the sequence of the entry
 @return the result of PyList_Append
 @see FastaBuff
*/
static inline int addFasta(PyObject *list, const char *restrict title,
                           size_t titleLen, PyObject *seq) {
    PyObject *key = PyUnicode_DecodeUTF8(title, titleLen, NULL);
    if (key == NULL) {
        return -1;
    }
    PyObject *value;
    int res;
    if (seq != NULL) {
        value = seq;
    } else {
        value = Py_None;
        Py_INCREF(value);
    }
    PyObject *entry = PyTuple_Pack(2, key, value);
    Py_DECREF(value);
    Py_DECREF(key);
    if (entry == NULL) {
        return -1;
    }
    res = PyList_Append(list, entry);
    Py_DECREF(entry);
    return res;
}

/*!
 @brief Echoes progress to a file
 @details Echoes the progress of lineIndex/total to the file
 @param echo the file to echo to
 @param lineIndex the current line index
 @param total the total amount of lines
*/
static inline void echoProgress(PyObject *restrict echo, unsigned int lineIndex,
                                unsigned int total) {
    float progress;
    if (total == 0) { // well we can't divide by zero so this
        progress = 100.0;
    } else {
        progress = ((float)lineIndex / (float)total) * 100;
    }
    char echoStr[100]; // i really doubt we can exceed this limit, even so it
                       // won't crash just not print out the entire number, yes
                       // i know I can use math.h to figure out the needed size
    snprintf(echoStr, sizeof(echoStr), "%d/%d(%.2f%%)\r", lineIndex, total,
             progress);
    PyFile_WriteString(echoStr, echo);
}

/*!
 @brief Processes a chunk of FASTA text data
 @param chunk the chunk of data to process
 @param chunk_size the size of the chunk
 @param out the output object, may be NULL
 @return true if ok, false if error
*/
static bool processTextData(const char *restrict chunk, Py_ssize_t chunk_size,
                            PyObject **out) {

    PyObject *seq = PyUnicode_New(chunk_size, CHAR_MAX);
    if (seq == NULL) {
        return false;
    }
    void *restrict data = PyUnicode_DATA(seq);
    size_t j = 0;
    for (size_t i = 0; i < (size_t)chunk_size; i++) {
        if (isalpha(chunk[i])) {
            PyUnicode_WRITE(PyUnicode_1BYTE_KIND, data, j, chunk[i]);
            j++;
        }
    }
    // standard break, probably bad
    ((PyASCIIObject *)seq)->length = j;
    if (j == 0) {
        Py_DECREF(seq);
        *out = NULL;
    } else {
        *out = seq;
    }
    return true;
}

/*!
 @brief Processes a chunk of binary FASTA data
 @param chunk the chunk of data to process
 @param chunk_size the size of the chunk
 @param out the output buffer
 @return true if ok, false if error
*/
static bool processBinaryData(const char *restrict chunk, Py_ssize_t chunk_size,
                              PyObject **out) {
    // the number of allocated bytes for sequence
    size_t sequenceBufferSize = PACKING_ROUND(chunk_size / 2);
    // here we overallocate, but it's better than reallocating
    packing_t *sequenceBuffer = malloc(sequenceBufferSize);
    if (sequenceBuffer == NULL) {
        PyErr_SetFromErrno(PyExc_MemoryError);
        return false;
    }
    bool RNA = false; // if we have a U in the sequence
    // number of CHARACTERS, so usually 2x the number of bytes
    size_t seq_i = 0;
    size_t buff_i = 0;

    uint8_t buffer[PACKING_WIDTH];
    uint8_t b_i = 0;

    // this loop over here is very hot performance-wise.
    for (Py_ssize_t i = 0; i < chunk_size; i++) {
        uint8_t c = chunk[i]; // this op can have a 8% overhead, crazy
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
    if (seq_i == 0) {
        *out = Py_None;
        free(sequenceBuffer);
    } else {
        if (b_i != 0) {
            pack(buffer, sequenceBuffer + buff_i++);
        }
        *out = (PyObject *)FastaBuff_new((uint8_t *)sequenceBuffer,
                                         sequenceBufferSize, seq_i, RNA);
    }
    return true;
}

PyObject *parseFasta(PyObject *self, PyObject *args,
                     PyObject *restrict kwargs) {
    UNUSED(self);
    static const char *keywords[] = {"file", "binary", "echo", NULL};
    PyObject *restrict first;
    PyObject *restrict binary = Py_True;
    PyObject *restrict echo = Py_None;
    if (PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", (char **)keywords,
                                    &first, &binary, &echo) != true) {
        return NULL;
    }

    input_t input = getFileContentsFromArgs(first);
    if (input_t_is_NULL(input)) {
        return NULL;
    }
    const char *end = input.str + input.len;

    uint32_t seq_count = 0; // technically we don't need to have anything
                            // assigned to this, but it's good to have it
    if (!Py_IsNone(echo)) {
        seq_count = strncount(input.str, '>', input.len);
    }

    PyObject *result = PyList_New(0);
    if (result == NULL) {
        free_input_t(input);
        return NULL;
    }
    uint32_t seq_index = 1;

    const char *ptr = memchr(input.str, '>', input.len);

    bool (*processor)(const char *restrict, Py_ssize_t, PyObject **) =
        binary == Py_True ? processBinaryData : processTextData;

    while (ptr < end) {
        if (!Py_IsNone(echo)) {
            echoProgress(echo, seq_index, seq_count);
        }
        // we have found a new sequence
        const char *title_start = ++ptr;

        // find the end of the title
        const char *title_end = memchr(title_start, '\n', end - ptr);
        if (title_end == NULL) {
            if (addFasta(result, title_start, end - ptr, NULL) < 0) {
                free_input_t(input);
                Py_DECREF(result);
                return NULL;
            }
            break;
        }

        const size_t titleLen = title_end - title_start;
        ptr = title_end + 1;

        // we have found the start of the sequence; end of the title

        const char *chunk_start = ptr;

        // find the end of the sequence
        const char *next_sequence = memchr(chunk_start, '>', end - ptr);
        if (next_sequence != NULL) {
            ptr = next_sequence;
        } else {
            ptr = end;
        }

        // process what we have found

        Py_ssize_t chunkLen = ptr - chunk_start + 1;
        PyObject *obj;
        if (chunkLen > 0) {
            if (!processor(title_end, chunkLen, &obj)) {
                free_input_t(input);
                Py_DECREF(result);
                return NULL;
            }
        } else {
            obj = NULL;
        }

        if (addFasta(result, title_start, titleLen, obj) < 0) {
            free_input_t(input);
            Py_DECREF(result);
            return NULL;
        }

        if (PyErr_CheckSignals() < 0) {
            free_input_t(input);
            Py_DECREF(result);
            return NULL;
        }
        seq_index++;
    }

    free_input_t(input);
    if (!Py_IsNone(echo)) {
        PyFile_WriteString("\n", echo);
    }
    return result;
}

PyObject *parseGTF(PyObject *restrict self, PyObject *restrict args,
                   PyObject *restrict kwargs) {
    UNUSED(self);
    static const char *keywords[] = {"file", "echo", "attr_tp", NULL};
    PyObject *restrict first;
    PyObject *restrict echo = Py_None;
    PyObject *restrict attr_tp = Py_None;
    if (PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", (char **)keywords,
                                    &first, &echo, &attr_tp) != true) {
        return NULL;
    }
    if (!Py_IsNone(attr_tp) && !PyMapping_Check(attr_tp)) {
        PyErr_SetString(PyExc_TypeError, "attr_tp must be a mapping");
        return NULL;
    }
    input_t input = getFileContentsFromArgs(first);
    if (input_t_is_NULL(input)) {
        return NULL;
    }
    unsigned int lineCount = 0;
    if (!Py_IsNone(echo)) {
        lineCount = strncount(input.str, '\n', input.len);
    }
    // NOTE from my testing it seems that finding the accurate size is not worth
    // it. Seems like Python Lists are built for appending and it doesn't care
    // if no size is given Now naturally it would be nice to give it a size,
    // appending is still worse than simply writing, but the cost of processing
    // the entire file to get an accurate final size is simply too high
    PyObject *restrict result = GtfList_new(0);
    if (result == NULL) {
        free_input_t(input);
        return NULL;
    }

    hashmap_t attr_keys, attr_vals;
    if (hashmap_create_xh(DEFAULT_ATTR_SIZE, &attr_keys) < 0) {
        PyErr_SetString(PyExc_Exception, "Failed to create hashmap");
        free_input_t(input);
        Py_DECREF(result);
        return NULL;
    }
    if (hashmap_create_xh(DEFAULT_ATTR_SIZE, &attr_vals) < 0) {
        PyErr_SetString(PyExc_Exception, "Failed to create hashmap");
        free_input_t(input);
        Py_DECREF(result);
        hashmap_destroy_py(&attr_keys);
        return NULL;
    }

    unsigned int lineIndex = 1;
    occurrence_t lastoccurrence;
    strtok_ri(input.str, '\n', &input.len, &lastoccurrence);
    do {
        if (!Py_IsNone(echo)) {
            echoProgress(echo, lineIndex, lineCount);
        }
        lineIndex++;

        if (!validGTFLineToParse(lastoccurrence.token, lastoccurrence.len)) {
            if (strncmp(lastoccurrence.token, GFF3_FASTA_HEADER,
                        sizeof(GFF3_FASTA_HEADER)) != 0) {
                continue;
            } else {
                // GFFv3 files CAN have FASTA sequences at the end, so
                // we need to check for that
                break;
            }
        }

        GtfDict *dict =
            createGTFdict(&lastoccurrence, attr_tp, &attr_keys, &attr_vals);
        if (dict != NULL) {
            int res = PyList_Append(result, (PyObject *)dict);
            Py_DECREF(dict);
            if (res != 0) {
                free_input_t(input);
                Py_DECREF(result);
                hashmap_destroy_py(&attr_keys);
                hashmap_destroy_py(&attr_vals);
                return NULL;
            }
        } else {
            free_input_t(input);
            Py_DECREF(result);
            hashmap_destroy_py(&attr_keys);
            hashmap_destroy_py(&attr_vals);
            return NULL;
        }

        if (PyErr_CheckSignals() < 0) {
            free_input_t(input);
            Py_DECREF(result);
            hashmap_destroy_py(&attr_keys);
            hashmap_destroy_py(&attr_vals);
            return NULL;
        }
    } while (strtok_ri(NULL, '\n', &input.len, &lastoccurrence) > 0);

    free_input_t(input);
    if (!Py_IsNone(echo)) {
        PyFile_WriteString("\n", echo);
    }
    hashmap_destroy_py(&attr_keys);
    hashmap_destroy_py(&attr_vals);
    return result;
}
