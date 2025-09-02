/*!
 @file FastaReader.h
 @brief Header file for the FastaReader and FastaFile objects
*/

#ifndef FASTAREADER_H
#define FASTAREADER_H

#include "../reader.h"
#include <Python.h>

/*!
 @defgroup FastaReader_class FastaReader
 @brief A module providing a reader for Fasta files
*/

/*!
 @defgroup FastaFile_class FastaFile
 @brief A module providing a file object for Fasta files
*/

/*!
 @struct FastaReader
 @brief A reader that reads Fasta files
 @ingroup FastaReader_class
 @see FastaFile
 @see FastaBuff
 @see parseFASTA
*/
typedef struct {
    struct reader base;
    bool binary;
    char *title;
    size_t title_len;
} FastaReader;

/*!
 @struct FastaFile
 @brief A file that holds Fasta data
 @ingroup FastaFile_class
 @see FastaReader
*/
typedef struct {
    struct file base;
    bool binary;
} FastaFile;

/*!
 @brief The Python type definition for the FastaFile object
 @ingroup FastaFile_class
*/
extern PyTypeObject FastaFileType;

/*!
 @brief The Python type definition for the FastaReader object
 @ingroup FastaReader_class
*/
extern PyTypeObject FastaReaderType;

#endif
