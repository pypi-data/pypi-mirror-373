/*!
 @file fasta.c
 @brief Implementations for the FASTA module
*/

#include "fasta.h"

#include <limits.h> // For CHAR_MAX
#include <stdbool.h>
#include <stdint.h>

uint8_t fasta_binary_mapping[CHAR_MAX + 1];

void initialize_fasta_binary_mapping() {
    for (int i = 0; i <= CHAR_MAX; i++) {
        fasta_binary_mapping[i] = i_Index; // Invalid character
    }
    // the idea, is that indexing into the array will return i_Index for invalid
    // characters. Yes this is faster than a switch... somehow

    // Then add the actual mapping
    fasta_binary_mapping['-'] = 0x00;
    fasta_binary_mapping['.'] = 0x00;
    fasta_binary_mapping['U'] = 0x01;
    fasta_binary_mapping['T'] = 0x01;
    fasta_binary_mapping['G'] = 0x02;
    fasta_binary_mapping['K'] = 0x03;
    fasta_binary_mapping['C'] = 0x04;
    fasta_binary_mapping['Y'] = 0x05;
    fasta_binary_mapping['S'] = 0x06;
    fasta_binary_mapping['B'] = 0x07;
    fasta_binary_mapping['A'] = 0x08;
    fasta_binary_mapping['W'] = 0x09;
    fasta_binary_mapping['R'] = 0x0A;
    fasta_binary_mapping['D'] = 0x0B;
    fasta_binary_mapping['M'] = 0x0C;
    fasta_binary_mapping['H'] = 0x0D;
    fasta_binary_mapping['V'] = 0x0E;
    fasta_binary_mapping['N'] = 0x0F;
}

char getIUPACchar(uint8_t index, bool rna) {
    char res = ".TGKCYSBAWRDMHVN"[index];
    if (res == 'T' && rna) {
        return 'U';
    }
    return res;
}

bool is_valid_title(const char *title, size_t len) {
    if (len == 0)
        return false;
    if (title[0] != '>')
        return false;
    return true;
}
