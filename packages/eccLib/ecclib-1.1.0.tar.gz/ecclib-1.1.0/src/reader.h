/*!
 @file reader.h
 @brief header for the reader module
*/

#ifndef READER_H
#define READER_H

#include "common.h"
#include <Python.h>
#include <stdbool.h>

/*!
 @defgroup reader_module reader
 @brief A module providing a C "base classes" for FastaReader, GtfReader and
 GtfFile, FastaFile
 @details For maintainability and to avoid duplicating code, plenty of
 similar functionality was generalized from GtfReader into this module.
 Through the magic of pointers, basic polymorphism is achieved. For example:
 both FastaReader and GtfReader are derived from the reader struct. They both
 have that struct as the first field, meaning functions taking in reader*
 as arguments can use them.
*/

/*!
 @brief Reader base struct
 @details This struct holds either a Python file object, or a C FILE pointer.
 Which is actually used depends on whether buff is NULL. Regardless of that,
 both use cases allow for iterative line-by-line reading.
 @see reader_next_line
 @ingroup reader_module
*/
struct reader {
    PyObject_HEAD union {
        /*!
            @brief The FILE that is being read
            @details During iteration this object is used to access file
            contents via fgets(). buff is used to store the line read, and
            buffSize is used to store the size of the buffer.
            @note This is used if buff is NULL
        */
        FILE *file;
        /*!
            @brief The file object that is being read using PyFile_GetLine
            @note This is used if buff is not NULL
        */
        PyObject *fileObj;
    };
    /*!
     @brief The buffer for getline to write to
     @note if NULL, indicates fileObj should be used
    */
    char *buff;
    /*!
     @brief The size of the buff, garbage if buff is NULL
    */
    size_t buffSize;
};

/*!
 @brief Free the reader object
 @param self the reader object
 @ingroup reader_module
*/
void free_reader(struct reader *self);

/*!
 @brief File base struct
 @ingroup reader_module
*/
struct file {
    PyObject_HEAD
        /*!
         @brief The name of the file
        */
        const char *filename;
    /*!
     @brief The FILE object
     @details This is used to access the file contents
     @warning may be NULL
    */
    FILE *file;
};

/*!
 @brief __enter__ method for file objects
 @details This function opens the file and ensures the file is ready for reader
 creation.
 @param self the file object
 @param args arguments passed to __enter__
 @ingroup reader_module
*/
PyObject *file_enter(struct file *self, PyObject *args);

/*!
 @brief __exit__ method for file objects
 @param self the file object
 @param args arguments passed to __exit__
 @param kwds keyword arguments passed to __exit__
 @ingroup reader_module
*/
PyObject *file_exit(struct file *self, PyObject *args, PyObject *kwds);

/*!
 @brief how big should the line buffer be?
*/
#define BUFFSIZE (1024)

/*!
 @brief Initialize the reader object based on the file object
 @details This function does all the sanity checks, resets the FILE object, and
 initializes the reader object
 @param self the file object
 @param reader the allocated reader object
 @return true on success, false on failure
 @ingroup reader_module
*/
bool initialize_reader(const struct file *self, struct reader *reader);

/*!
 @brief A simple that hold a string, and potentially it's Python parent object
 @ingroup reader_module
 @see next_line
*/
typedef struct {
    /*!
     @brief The string token
     @warning May be null to indicate error
     @note May be owned by the reader object
    */
    occurrence_t line;
    /*!
     @brief The Python object owning the token buffer
     @note May be null to indicate token is owned by the reader object
    */
    PyObject *obj;
} line_out;

/*!
 @brief Fetches the next line from the reader object
 @details This function returns a line_out structure containing the next line
 from the reader object. Unfortunately, the line *may* contain the '\n'
 character. Use Py_XDECREF to release the returned structure.
 @param self the reader object
 @return the next line from the reader object
 @ingroup reader_module
 @warning the returned line token buffer may be owned by the reader object
*/
line_out next_line(struct reader *restrict self,
                   bool (*valid)(const char *, size_t));

#endif
