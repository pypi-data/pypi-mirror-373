/*!
 @file FastaBuff.h
 @brief Contains the definition of the FastaBuff object
*/

#ifndef FASTABUFF_H
#define FASTABUFF_H

#include <Python.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

/*!
 @defgroup FastaBuff_class FastaBuff
 @brief All methods and objects related to the FastaBuff object
 @details The FastaBuff object is a memory efficient buffer for FASTA data. It
 stores the data in a packed format, with each byte containing two 4 bit values.
 This allows for a 50% reduction in memory usage compared to a regular byte
 array. The object also provides methods for easy manipulation of the data.
*/

/*!
 @struct FastaBuff
 @brief A buffer that holds packed uint4 FASTA data
 @see getFastaIndex
 @see parseFasta
 @ingroup FastaBuff_class
*/
typedef struct {
    PyObject_HEAD
        /*!
            @brief The buffer that holds the packed FASTA data
        */
        uint8_t *buff;
    /*!
        @var buffSize
        @brief The size of the buffer in bytes
    */
    size_t buffSize;
    /*!
        @var buffLen
        @brief The length of the sequence
    */
    size_t buffLen;
    /*!
        @var RNA
        @brief If true, T will be converted to U
    */
    bool RNA;
} FastaBuff;

/*!
 @brief Creates a new FastaBuff object
 @param buff the buffer to use, this will be owned by the FastaBuff object
 @param buffSize the size of the buffer
 @param buffLen the length of the sequence
 @param RNA if true, T will be converted to U
*/
FastaBuff *FastaBuff_new(uint8_t *restrict buff, size_t buffSize,
                         size_t buffLen, bool RNA);

/*!
 @brief The Python type definition for the FastaBuff object
 @ingroup FastaBuff_class
*/
extern PyTypeObject FastaBuffType;

/*!
 @brief Checks if the object is an instance of the FastaBuff type
 @param op the object to check
 @return 1 if the object is an instance of the FastaBuff type, 0 otherwise
*/
#define FastaBuff_Check(op) PyObject_TypeCheck(op, &FastaBuffType)

#endif
