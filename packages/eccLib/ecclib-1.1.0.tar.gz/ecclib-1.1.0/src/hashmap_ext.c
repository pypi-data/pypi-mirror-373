/*!
 @file hashmap_ext.c
 @brief Implementation of the hashmap_ext module
*/

#include "hashmap_ext.h"

#include "common.h"

static hashmap_uint32_t xxhash_hasher(hashmap_uint32_t seed, const void *key,
                                      hashmap_uint32_t key_len) {
    // collisions caused from casting 64 bit to 32 bit are worse than the speed
    // difference between XXH32 and XXH3
    return XXH3_64bits_withSeed(key, key_len, seed);
}

int hashmap_create_xh(const hashmap_uint32_t initial_capacity,
                      struct hashmap_s *const out_hashmap) {
    struct hashmap_create_options_s options;
    options.initial_capacity = initial_capacity;
    options.hasher = &xxhash_hasher;
    options.comparer = NULL;
    options._ = 0;

    return hashmap_create_ex(options, out_hashmap);
}

hashmap_uint32_t hashmap_new_hash(struct hashmap_s *const m,
                                  const char *const key,
                                  const hashmap_uint32_t len) {
    hashmap_uint32_t index;
    while (!hashmap_hash_helper(m, key, len, &index)) {
        if (hashmap_rehash_helper(m)) {
            return 1;
        }
    }
    return index;
}

int hashmap_put_tuple(struct hashmap_s *const m, const char *const key,
                      const hashmap_uint32_t len, PyObject *restrict py_key,
                      PyObject *restrict value) {
    hashmap_uint32_t hash = hashmap_new_hash(m, key, len);
    struct map_tuple *new;
    /* If the hashmap element was not already in use, set that it is being used
     * and bump our size. */
    if (0 == m->data[hash].in_use) {
        m->data[hash].in_use = 1;
        m->size++;
        new = (struct map_tuple *)malloc(sizeof(struct map_tuple));
        if (new == NULL) {
            return -1;
        }
        m->data[hash].data = new;
    } else {
        new = m->data[hash].data;
        Py_DECREF(new->key);
        Py_DECREF(new->value);
    }
    Py_INCREF(py_key);
    Py_INCREF(value);
    new->key = py_key;
    new->value = value;

    m->data[hash].key = key;
    m->data[hash].key_len = len;
    return 0;
}

struct map_tuple *hashmap_pop_tuple(struct hashmap_s *const m,
                                    const char *const key,
                                    const hashmap_uint32_t len) {

    hashmap_uint32_t hash = hashmap_new_hash(m, key, len);

    hashmap_uint32_t i;

    /* Linear probing, if necessary */
    for (i = 0; i < HASHMAP_LINEAR_PROBE_LENGTH; i++) {
        const hashmap_uint32_t index = hash + i;

        if (m->data[index].in_use) {
            if (m->comparer(m->data[index].key, m->data[index].key_len, key,
                            len)) {
                struct map_tuple *data = m->data[index].data;

                /* Blank out the fields including in_use */
                memset(&m->data[index], 0, sizeof(struct hashmap_element_s));

                /* Reduce the size */
                m->size--;

                return data;
            }
        }
    }

    /* Not found */
    return HASHMAP_NULL;
}

static int free_iter(void *const context, void *const held) {
    UNUSED(context);
    struct map_tuple *tuple = (struct map_tuple *)held;
    Py_DECREF(tuple->key);
    Py_DECREF(tuple->value);
    free(tuple);
    return 1;
}

void hashmap_destroy_tuple(struct hashmap_s *m) {
    hashmap_iterate(m, free_iter, NULL);
    hashmap_destroy(m);
}

static int free_iter_py(void *const context, void *const held) {
    UNUSED(context);
    Py_DECREF((PyObject *)held);
    return 1;
}

void hashmap_destroy_py(struct hashmap_s *m) {
    hashmap_iterate(m, free_iter_py, NULL);
    hashmap_destroy(m);
}
