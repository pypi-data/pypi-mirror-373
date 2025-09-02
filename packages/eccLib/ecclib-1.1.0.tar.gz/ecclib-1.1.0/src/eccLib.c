/*!
 @file eccLib.c
 @brief Main library file
 @details This file initializes all the features according to the Python ABI.
*/

#include <stdlib.h>

/*!
 @brief The minor version of the Python ABI that is required
 @details This used to be, because of Py_SET_TYPE, now we don't use it. Thus we
 could theoretically support older versions, but I haven't personally tested it.
*/
#define REQUIRED_MINOR_VERSION 10
/*!
 @brief The major version of the Python ABI that is required
 @details Well it's not like we even want to support Python 2, so this is just a
 sanity check
*/
#define REQUIRED_MAJOR_VERSION 3

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#if PY_MINOR_VERSION < REQUIRED_MINOR_VERSION &&                               \
    PY_MAJOR_VERSION <= REQUIRED_MAJOR_VERSION
#error "Unsupported ABI version. Oldest supported version is " REQUIRED_MAJOR_VERSION "." REQUIRED_MINOR_VERSION
#endif

#include "classes/FastaBuff.h"
#include "classes/FastaReader.h"
#include "classes/GtfDict.h"
#include "classes/GtfList.h"
#include "classes/GtfReader.h"
#include "formats/fasta.h"
#include "functions.h"

// this documentation is only visible from the help() function

PyDoc_STRVAR(parseFASTAdoc, "parseFASTA(file: str | TextIO, echo:TextIO | None "
                            "= None) -> dict[str, FastaBuff]\n\n"
                            "Returns a dict containing FASTA data, with each "
                            "sequence under their associated title.");

PyDoc_STRVAR(
    parseGTFdoc,
    "parseGTF(file: str | TextIO, echo:TextIO | None = None) -> GtfList"
    "Parses raw GTF data and returns a list containing parsed GtfDicts");

PyDoc_STRVAR(
    moduledoc,
    "A Python module written in C for fast parsing of genomic files and "
    "genomic context analysis. Provides multiple objects for holding and "
    "analyzing genomic data. Though the main purpose of this module is to "
    "provide fast parsing of genomic data. Additionally provides a GtfReader "
    "class for iterative parsing of GTF files.");

static PyMethodDef eccLibMethods[] = {
    {"parseFASTA", (PyCFunction)parseFasta, METH_KEYWORDS | METH_VARARGS,
     parseFASTAdoc},
    {"parseGTF", (PyCFunction)parseGTF, METH_KEYWORDS | METH_VARARGS,
     parseGTFdoc},
    {NULL} /* Sentinel */
};

static struct PyModuleDef eccLibModule = {
    PyModuleDef_HEAD_INIT,
    "eccLib",  /* name of module */
    moduledoc, /* module documentation, may be NULL */
    -1,
    eccLibMethods,
    .m_slots = NULL};

/*!
 @brief small convenience function that instantiates the object within module
 @param module the module to which the object should be added to
 @param type the type of the object that should be added
 @param objName the name of the object
 @return -1 on error
*/
static inline int initObject(PyObject *module, PyTypeObject *type,
                             const char *objName) {
    if (PyType_Ready(type) < 0) {
        return -1;
    }
    if (PyModule_AddObject(module, objName, (PyObject *)type) < 0) {
        Py_DECREF(type);
        return -1;
    }
    return 0;
}

/*!
 @brief Hashes a string
 @param str the string to hash
 @param len the length of the string
 @return the hash
*/
static inline Py_hash_t PyHashString(const char *str, size_t len) {
    PyObject *obj = PyUnicode_DecodeUTF8(str, len, NULL);
    Py_hash_t hash = PyObject_Hash(obj);
    Py_DECREF(obj);
    return hash;
}

/*!
 @brief Initializes the eccLib module
 @return the module object
*/
PyMODINIT_FUNC PyInit_eccLib(void) {
    PyObject *m = PyModule_Create(&eccLibModule);
    // Init GtfReader
    if (initObject(m, &GtfReaderType, "GtfReader") < 0) {
        return NULL;
    }
    if (initObject(m, &GtfFileType, "GtfFile") < 0) {
        return NULL;
    }
    // init GtfDict
    if (initObject(m, &GtfDictType, "GtfDict") < 0) {
        return NULL;
    }
    // init GtfList
    GtfListType.tp_base = &PyList_Type;
    if (initObject(m, &GtfListType, "GtfList") < 0) {
        return NULL;
    }
    // init FastaBuff
    if (initObject(m, &FastaBuffType, "FastaBuff") < 0) {
        return NULL;
    }
    // init FastaReader
    if (initObject(m, &FastaReaderType, "FastaReader") < 0) {
        return NULL;
    }
    // init FastaFile
    if (initObject(m, &FastaFileType, "FastaFile") < 0) {
        return NULL;
    }
    initialize_fasta_binary_mapping();
    return m;
}

/*!
 @brief Main function that initializes the Python interpreter and imports the
 eccLib module
 @param argc the number of arguments
 @param argv the arguments
 @return 0 on success
*/
int main(int argc, char *argv[]) {
    if (argc < 1) {
        fprintf(stderr, "Error: no arguments provided\n");
        exit(1);
    }
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    /* Add a built-in module, before Py_Initialize */
    if (PyImport_AppendInittab("eccLib", PyInit_eccLib) == -1) {
        fprintf(stderr, "Error: could not extend in-built modules table\n");
        exit(1);
    }

    /* Pass argv[0] to the Python interpreter */
    // Py_SetProgramName(program);

    /* Initialize the Python interpreter.  Required.
       If this step fails, it will be a fatal error. */
    Py_Initialize();

    /* Optionally import the module; alternatively,
       import can be deferred until the embedded script
       imports it. */
    PyObject *pmodule = PyImport_ImportModule("eccLib");
    if (!pmodule) {
        PyErr_Print();
        fprintf(stderr, "Error: could not import module 'eccLib'\n");
    }

    free(program);
    return 0;
}
