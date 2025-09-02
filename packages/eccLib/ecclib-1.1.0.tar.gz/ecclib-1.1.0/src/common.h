/*!
 @file common.h
 @brief Contains common functions and structs used by the other modules
*/

#ifndef COMMON_H
#define COMMON_H

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include <Python.h>

/*!
 @defgroup common Common
 @brief Commonly used functions
 @details Mainly contains functions for string manipulation (very much a core of
 the library). Also here is where percent encoding handling lives
*/

/*!
 @struct occurrence_t
 @brief An occurrence of a token in a string
 @details A struct that holds the last occurrence of a token in a string and
 it's size
 @ingroup common
 @see strtok_ri
*/
typedef struct {
    /*!
        @var token
        @brief The token that was found
    */
    const char *token;
    /*!
        @var len
        @brief The length of the token
    */
    size_t len;
} occurrence_t;

/*!
 @brief Version of strtok_r that doesn't modify the original string
 @details A reentrant inplace string tokenizer. A custom type is used to store
 the last occurrence of the token. Both strLen and lastoccurrence are modified
 by this function
 @param str the string to tokenize, may be NULL in which case the last
 occurrence is used
 @param delim the delimiter to use
 @param strLen the length of the string to tokenize, will be decremented by the
 length of the token found. So it will reflect the remaining length of the
 string after the token
 @param lastoccurrence a struct that holds the last occurrence of the token.
 Cannot be NULL
 @return -1 on error, 0 on break, 1 on success
 @ingroup common
*/
int strtok_ri(const char *restrict str, char delim, Py_ssize_t *restrict strLen,
              occurrence_t *restrict lastoccurrence);

/*!
 @brief Writes a percent encoded character to a buffer
 @details Creates a percent encoded character in the form %xx and writes it to
 out
 @param out the buffer to write to
 @param c the character to encode
 @ingroup common
*/
void percent_encode_char(char *restrict out, char c);

/*!
 @brief Counts the number of occurrences of c in str
 @param str the string to search in
 @param c the character to search for
 @param len the length of the string to search in
 @return the number of occurrences of c in str
 @ingroup common
*/
uint32_t strncount(const char *restrict str, char c, size_t len);

/*!
 @brief Supresses unused variable warnings
 @param x the variable to suppress the warning for
 @ingroup common
 @details In C++11 you can just not provide a name for the parameter to suppress
    the warning, but in C you have to use this macro
*/
#define UNUSED(x) (void)(x)

#define STR_HELPER(x) #x
/*!
 @brief Converts a macro to a string
 @param x the macro to convert
 @ingroup common
*/
#define STR(x) STR_HELPER(x)

/*!
 @brief Finds the first occurrence of either c1 or c2 in buf
 @param buf the buffer to search in
 @param c1 the first character to search for
 @param c2 the second character to search for
 @param len the length of the buffer to search in
 @return a pointer to the first occurrence of either c1 or c2 in buf, or NULL if
 not found
 @ingroup common
*/
void *memchr2(const void *buf, int c1, int c2, size_t len);

#endif
