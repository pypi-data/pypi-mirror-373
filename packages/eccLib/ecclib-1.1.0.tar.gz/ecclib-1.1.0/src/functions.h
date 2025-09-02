/*!
 @file functions.h
 @brief Contains the declarations of the functions used in the eccLib module
*/

#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include <Python.h>

/*!
 @defgroup functions Functions
 @brief Functions used in the eccLib module
 @details Contains the declarations of the functions used in the eccLib module,
 these are directly called from Python
*/

/*!
 @brief Python function that parses provided raw FASTA content
 @param self the eccLib library object. Unused here
 @param args the passed argument tuple. Doesn't steal reference.
 @param kwargs the passed keyword arguments. Doesn't steal reference.
 @return a Python list of tuples with the first element being the title and the
 second being a FastaBuff object
 @ingroup functions
 @see FastaBuff
*/
PyObject *parseFasta(PyObject *self, PyObject *args, PyObject *restrict kwargs);

/*!
 @brief Python function for parsing raw GTF file contents
 @param self the eccLib library object. Unused entirely
 @param args the passed arguments tuple. Doesn't steal reference
 @param kwargs the passed keyword arguments. Doesn't steal reference
 @return a list of GtfDicts
 @ingroup functions
 @see GtfList
 @see GtfDict
 @see GtfFile
*/
PyObject *parseGTF(PyObject *restrict self, PyObject *restrict args,
                   PyObject *restrict kwargs);

#endif
