/*!
 @file common.c
 @brief Contains implementations for common functions and structs used by the
 other modules
*/

#include "common.h"

#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#ifdef __SSE2__
#include <emmintrin.h>
#endif

int strtok_ri(const char *restrict str, char delim, Py_ssize_t *restrict strLen,
              occurrence_t *restrict lastoccurrence) {
    if (*strLen <= 0) {
        return 0;
    }
    if (str == NULL) {
        str = lastoccurrence->token + lastoccurrence->len + 1;
    }
    const char *end = memchr(str, delim, *strLen);
    if (end == NULL) {
        end = str + *strLen;
    }
    *strLen -= end - str;

    // Update the last occurrence structure
    lastoccurrence->token = str;
    lastoccurrence->len = end - str;

    // Skip the delimiter if found
    if (*strLen > 0 && *end == delim) {
        (*strLen)--; // Account for the delimiter
    }
    return 1;
}

void percent_encode_char(char *restrict out, char c) {
    out[0] = '%';
    out[1] = "0123456789ABCDEF"[c >> 4];
    out[2] = "0123456789ABCDEF"[c & 0x0F];
}

uint32_t strncount(const char *restrict str, char c, size_t len) {
    uint32_t count = 0;
    const char *p;
    while ((p = memchr(str, c, len)) != NULL) {
        count++;
        len -= p - str;
        str = p + 1;
    }
    return count;
}

void *memchr2(const void *buf, int c1, int c2, size_t len) {
    const unsigned char *p = buf;
    size_t i = 0;
#ifdef __SSE2__
    {
        __m128i v1 = _mm_set1_epi8((char)c1);
        __m128i v2 = _mm_set1_epi8((char)c2);

        for (; i + 16 <= len; i += 16) {
            __m128i chunk = _mm_loadu_si128((const __m128i *)(p + i));
            __m128i cmp1 = _mm_cmpeq_epi8(chunk, v1);
            __m128i cmp2 = _mm_cmpeq_epi8(chunk, v2);
            __m128i cmp = _mm_or_si128(cmp1, cmp2);
            int mask = _mm_movemask_epi8(cmp);
            if (mask) {
                int offset = __builtin_ctz(mask);
                return (void *)(p + i + offset);
            }
        }
    }
#endif
    // Fallback for remaining bytes and systems without SSE2
    for (; i < len; ++i) {
        if (p[i] == c1 || p[i] == c2)
            return (void *)(p + i);
    }
    return NULL;
}
