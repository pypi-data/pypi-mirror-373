/*!
 @file gtf.h
 @brief Header file for the GTF module
*/

#ifndef GTF_H
#define GTF_H

#include <Python.h>
#include <stdlib.h>

#include "../classes/GtfDict.h"
#include "../common.h"

/*!
 @defgroup gtf Gtf
 @brief Module providing functions for handling GTF data
 @see
 https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md
*/

/*!
 @brief How many attributes should be allocated by default
 @ingroup gtf
 @see GtfDict
*/
#define DEFAULT_ATTR_SIZE                                                      \
    64 // well how often do you see a GTF line with more than 64 attributes?

/*!
 @brief Parses a singular GTF line into a Python dict
 @param token the GTF line to parse. It should contain a minimum of 7 \\t, else
 it will throw an error
 @param attr_tp a mapping containing the callable to use to convert the
 attribute values to the correct type, or None
 @param attr_keys a hashmap containing the keys of the attributes
 @param attr_vals a hashmap containing the values of the attributes
 @return a PyObject* pointing to an object of type dict, or NULL on error
 @ingroup gtf
 @see occurrence_t
 @see GtfDict
*/
GtfDict *createGTFdict(const occurrence_t *restrict token, PyObject *attr_tp,
                       hashmap_t *restrict attr_keys,
                       hashmap_t *restrict attr_vals);

/*!
 @brief Determines if the provided line is a valid GTF line that can be parsed
 safely
 @details A line is considered valid if it doesn't start with a # and contains
 at least one \\t
 @param line the line to check
 @param len the length of the line
 @return true or false depending on line validity
 @ingroup gtf
*/
bool validGTFLineToParse(const char *line, size_t len);

/*!
 @brief Percent encodes restricted GTF characters
 @param str the string to percent encode
 @param len the length of the string
 @param outLen the length of the output string
 @return a newly allocated string with percent encoded characters
*/
char *gtf_percent_encode(const char *restrict str, size_t len,
                         size_t *restrict outLen);

/*!
 @brief Enum containing the fields that a GTF line can contain
 @ingroup gtf
 @see GtfDict
 @see keywords
*/
enum gtfFields {
    SEQNAME = 0,
    SOURCE = 1,
    FEATURE = 2,
    START = 3,
    END = 4,
    SCORE = 5,
    REVERSE = 6,
    FRAME = 7,
    ATTRIBUTES = 8
};

/*!
 @brief The number of core fields in a GTF line
 @ingroup gtf
 @details This is better than using ATTRIBUTES, as it's more descriptive
*/
#define CORE_FIELD_COUNT 8

/*!
 @brief Array containing the keywords of the GTF fields
 @ingroup gtf
*/
extern const char *keywords[CORE_FIELD_COUNT];

/*!
 @brief Array containing the sizes of the keywords
 @ingroup gtf
*/
extern const uint8_t keyword_sizes[CORE_FIELD_COUNT];

#define GFF3_FASTA_HEADER "##FASTA"

#endif
