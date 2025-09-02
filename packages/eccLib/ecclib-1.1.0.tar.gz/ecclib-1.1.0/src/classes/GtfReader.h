/*!
 @file GtfReader.h
 @brief This file defines the GtfReader and GtfFile object interface
*/

#ifndef GTFREADER_H
#define GTFREADER_H

#include <Python.h>

#include "../hashmap_ext.h"
#include "../reader.h"

/*!
 @defgroup GtfReader_class GtfReader
 @brief A module providing a reader for GTF files
*/

/*!
 @defgroup GtfFile_class GtfFile
 @brief A module providing a file object for GTF files
*/

/*!
 @struct GtfReader
 @brief A reader that reads GTF files
 @ingroup GtfReader_class
 @see GtfFile
 @see GtfDict
 @see parseGTF
*/
typedef struct {
    struct reader base;
    /*!
        @brief The hashmap key cache
        @details This hashmap is used to store the attribute keys that are found
       in the GTF file. This is used to optimize memory usage
    */
    hashmap_t attr_keys;
    /*!
     @brief The hashmap value cache
     @details This hashmap is used to store the values that are found
        in the GTF file. This is used to optimize memory usage
    */
    hashmap_t attr_vals;
    /*!
     @brief Mapping from attribute key to converter callable for the value, or
     None
    */
    PyObject *attr_tp;
} GtfReader;

/*!
 @struct GtfFile
 @brief A file that holds GTF data
 @ingroup GtfFile_class
 @see GtfReader
*/
typedef struct {
    struct file base;
    /*!
     @brief Mapping from attribute key to converter callable for the value, or
     None
    */
    PyObject *attr_tp;
} GtfFile;

/*!
 @brief The Python type definition for the GtfFile object
 @ingroup GtfFile_class
*/
extern PyTypeObject GtfFileType;

/*!
 @brief The Python type definition for the GtfReader object
 @ingroup GtfReader_class
*/
extern PyTypeObject GtfReaderType;

#endif
