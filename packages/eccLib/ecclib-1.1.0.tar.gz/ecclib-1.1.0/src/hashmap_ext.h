/*!
 @file hashmap_ext.h
 @brief Contains the declarations for our extension of the hashmap module
 @details This file includes the declarations from hashmap.h, which should be
 located in hashmap dir in project root. By default that's a git submodule.
 This means, that in this project you should ideally include this file.
*/

#include <Python.h>

#ifndef HASHMAP_EXT_H
#define HASHMAP_EXT_H

#include "../hashmap/hashmap.h"

// compile flags that should improve performance

#define XXH_INLINE_ALL          // slight pefrormance improvement
#define XXH_NO_STREAM           // compile size optimization
#define XXH_STATIC_LINKING_ONLY // why not if indeed we are statically linking
#define XXH_NO_STDLIB           // we don't use streaming nor states

// supposedly a faster hash function
#include "../xxHash/xxhash.h"

/*!
 @defgroup hashmap_ext hashmap.h extension
 @brief Our extension of the hashmap module
 @details Since the Python dict object proved far too hermetic for our
 shenanigans we had to use a third-part hashmap library. We settled on
 https://github.com/sheredom/hashmap.h, and this module extends that library
*/

/*!
 @brief A struct to store a key-value pair
 @details This is used to store the two values needed for a Python dict. The
 functions within this module will allocate memory for these structs and store
 them in the hashmap
 @ingroup hashmap_ext
*/
struct map_tuple {
    /*!
     @brief The Python object containing the key
     @warning This object should be a held reference, and the key used in the
     hashmap itself should originate from this object
    */
    PyObject *key;
    /*!
     @brief The Python object containing the value
     @warning This object should be a held reference
    */
    PyObject *value;
};

/*!
 @brief Put a key-value pair into the hashmap
 @param m the hashmap to put the pair into
 @param key the key to put
 @param len the length of the key
 @param py_key the Python key object
 @param value the value to put
 @return 0 on success, 1 on failure
 @note This funciton will increment the reference count of the key and value
 @ingroup hashmap_ext
*/
int hashmap_put_tuple(struct hashmap_s *const m, const char *const key,
                      const hashmap_uint32_t len, PyObject *py_key,
                      PyObject *value);

/*!
 @brief Remove a value from the hashmap
 @param m the hashmap to remove the value from
 @param key the key to remove the value for
 @param len the length of the key
 @return the removed value or NULL if not found
 @warning You must free the returned value, and decrement the reference count of
 the key and value
 @ingroup hashmap_ext
*/
struct map_tuple *hashmap_pop_tuple(struct hashmap_s *const m,
                                    const char *const key,
                                    const hashmap_uint32_t len);

/*!
 @brief Destroy a hashmap, assuming the values are map_tuples
 @param m the hashmap to destroy
 @ingroup hashmap_ext
*/
void hashmap_destroy_tuple(struct hashmap_s *m);

/*!
 @brief Destroy a hashmap, assuming the values are PyObjects
 @param m the hashmap to destroy
 @ingroup hashmap_ext
*/
void hashmap_destroy_py(struct hashmap_s *m);

/*!
 @brief Create a hashmap with a custom hash function
 @param initial_capacity the initial capacity of the hashmap
 @param out_hashmap the hashmap to create
 @return 0 on success, 1 on failure
*/
int hashmap_create_xh(const hashmap_uint32_t initial_capacity,
                      struct hashmap_s *const out_hashmap);

#endif
