/*!
 @file GtfList.h
 @brief Contains the definition of the GtfList object
*/

#ifndef GtfList_H
#define GtfList_H

#include <Python.h>

/*!
 @defgroup GtfList_class GtfList
 @brief All methods and objects related to the GtfList object
 @details The GtfList object is a list that holds geneDicts. It is used to
 store the parsed GTF data. It exists to provide type checking and to allow for
 easy processing method implementation
*/

/*!
 @struct GtfList
 @brief A list that holds geneDicts
 @details The GtfList object is a list that holds geneDicts. It is used to
 store the parsed GTF data. It exists to provide type checking and to allow for
 easy processing method implementation
 @note This object is a subclass of the Python list object
 @see GtfDict
 @ingroup GtfList_class
*/
typedef struct {
    /*!
     @var list
     @brief The underlying list object
    */
    PyListObject list;
} GtfList;

/*!
 @brief The Python type definition for the GtfList object
 @ingroup GtfList_class
*/
extern PyTypeObject GtfListType;

/*!
 @brief Creates a new GtfList object
 @param len the length of the list
 @return a new GtfList object
*/
PyObject *GtfList_new(Py_ssize_t len);

/*!
 @brief Checks if the object is an instance of the GtfList type
 @param op the object to check
 @return 1 if the object is an instance of the GtfList type, 0 otherwise
*/
#define GtfList_Check(op) PyObject_TypeCheck(op, &GtfListType)

#endif
