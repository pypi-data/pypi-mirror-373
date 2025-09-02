/*!
 @file GtfDict.h
 @brief Defines the GtfDict object interface
*/

#ifndef GTFDICT_H
#define GTFDICT_H

#include <Python.h>

// The third-party hashmap library is used to store the attributes
#include "../hashmap_ext.h"

/*!
 @defgroup GtfDict_class GtfDict
 @brief All methods and objects related to the GtfDict object
*/

/*!
 @struct GtfDict
 @brief A dict that holds GTF data
 @details An object meant to hold a single GTF line. The core GTF fields are
 stored within the object itself, while the attributes are stored in a separate
 dict. This object is meant to be used as a dict, but also provides a method to
 convert itself to a valid GTF line
 @note This object is NOT a subclass of the Python dict object, but it behaves
 like one
 @ingroup GtfDict_class
*/
typedef struct {
    PyObject_HEAD union { // note the two ways of accessing the same data
        /*!
         @brief The core GTF fields accessible as an array for iteration
         @see gtfFields
        */
        PyObject *core[8];
        /*!
         @brief The core GTF fields accessible as named fields
        */
        struct {
            PyObject *seqname;
            PyObject *source;
            PyObject *feature;
            PyObject *start;
            PyObject *end;
            PyObject *score;
            PyObject *reverse;
            PyObject *frame;
        };
    };
    /*!
     @var attributes
     @brief The attributes of the GTF line
    */
    struct hashmap_s attributes;
} GtfDict;

/*!
 @brief The Python type definition for the GtfDict object
 @ingroup GtfDict_class
*/
extern PyTypeObject GtfDictType;

/*!
 @def GtfDict_check(o)
 @brief Checks if the object can be interpreted as a GtfDict
 @param o the object to check
 @return true if the object can be interpreted as a GtfDict, false otherwise
*/
#define GtfDict_check(o) PyType_IsSubtype(Py_TYPE(o), &GtfDictType)

/*!
 @brief Internal function for checking if the other dict is contained within
 self. Linked as __contains__ and contains()
 @param self
 @param other the other object that might be contained
 @return C bool describing
 @see GtfDict_contains
*/
int GtfDict_containsValue(GtfDict *self, PyObject *other);

/*!
 @brief Generates a valid GTF line based on the GtfDict
 @param self
 @param len NULL or pointer to result length output
 @result valid GTF line string
 @see GtfDict_str
*/
char *GtfDictToGTF(GtfDict *self, size_t *len);

/*!
 @brief GtfDict.keys()
 @param self
 @return a list of keys
 @ingroup GtfDict_class
*/
PyObject *GtfDict_keys(GtfDict *restrict self);

/*!
 @brief A custom getitem that also checks the core attributes
 @param self
 @param key the key to get
 @return new reference to the gotten value
 @ingroup GtfDict_class
*/
PyObject *GtfDict_getitem(GtfDict *restrict self, PyObject *restrict key);

#endif
