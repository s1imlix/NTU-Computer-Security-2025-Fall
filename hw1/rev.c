#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

// Global array of dumped rand() values
unsigned int dumped_rand_values[] = {
    925546193, 112971749, 894331345, 550606490, 612670572, 1984253156,
    817333697, 1167418030, 200844547, 1559357924, 23570935, 1386030510,
    1718236449, 15324003, 1422046595, 194577446, 2099689618, 1639611688,
    1940125404, 594757870, 2080102868, 422936716, 2081226504, 661342256,
    1824932548, 2037670935, 941806690, 1534866686, 912695896, 816424631,
    1071806849, 1838242089, 929396380, 1966138194, 241364931, 1542066953,
    1802907702, 1058698629, 562001335, 2003752250, 470572905, 585572270,
    1242299112, 41325706, 600896274, 516862059, 235903153, 553102244,
    8990099, 28544909, 1147860114, 2089092967, 451481625, 1081602970,
    602951576, 128930526, 971790257, 1544758266, 1663797212, 1884486153,
    213699249, 588120413, 1575244595, 1143095629, 406774960, 1816609526,
    537678934, 62199014, 727824507, 1099680270, 2065951264, 1198397413,
    1685252540, 1160766728, 1239723119, 138665166, 1677628787, 1475626272,
    691767410, 1686618887, 1504171181, 1839627525, 1628228206, 1955652807,
    773746847, 83696134, 2084583333, 1745537105, 1628454400, 1600896897,
    1482539610, 1842153649, 41533662, 910300557, 837765631, 448308622,
    579426436, 1375444565, 510507637, 1307250943
};

size_t dumped_index = 0;

// Replacement for rand() that uses dumped values
unsigned int next_rand() {
    unsigned int val = dumped_rand_values[dumped_index];
    dumped_index++;
    if (dumped_index >= sizeof(dumped_rand_values)/sizeof(dumped_rand_values[0])) {
        dumped_index = 0; // wrap around if needed
    }
    return val;
}

// Rotate right for 8-bit value
unsigned char rotr(unsigned char value, unsigned int n) {
    const unsigned int bits = 8;
    n %= bits;
    return (value >> n) | (value << (bits - n));
}

// sub_1500 using next_rand()
uint64_t sub_1500(const unsigned char *a1, uint64_t a2, const unsigned char *a3) {
    unsigned char *v5 = calloc(a2, sizeof(unsigned char));
    unsigned char *v7 = calloc(a2, sizeof(unsigned char));
    uint64_t i, j;

    if (!a1 || !a2) {
        free(v5);
        free(v7);
        return 0;
    }

    // Fill arrays
    for (i = 0; i < a2; ++i) {
        v5[i] = (unsigned char)i;
        v7[i] = (unsigned char)next_rand();
    }

    // Shuffle v5
    for (j = i; j != 1;) {
        int r = next_rand();
        unsigned char tmp = v5[j - 1];
        unsigned char *ptr = &v5[r % j];
        v5[--j] = *ptr;
        *ptr = tmp;
    }

    // Transform
    uint64_t v14 = 0;
    for (uint64_t v13 = 0; v13 < i; ++v13) {
        unsigned char x = v5[v14];
        unsigned char v15 = (37 * x) >> 8;
        unsigned char shift = x - 7 * (((x - v15) >> 1) + v15) / 4 + 1;
        unsigned char val = v7[x] ^ rotr(a3[v14] + (unsigned char)v14, shift);
        printf("%c", val);
        v14 = v13 + 1;
    }

    free(v5);
    free(v7);
    return i;
}

int main() {
    unsigned char input[] = "ExampleInputString";
    unsigned char key[32] = {
        0x0B, 0x41, 0xDD, 0xD4, 0x7E, 0x7B, 0x33, 0xCD,
        0xDA, 0x6B, 0x51, 0x8E, 0x22, 0xFE, 0x57, 0x10,
        0x0E, 0xC7, 0x7C, 0xB2, 0x35, 0x61, 0x28, 0x4F,
        0x87, 0x06, 0x9A, 0x90, 0xF9, 0x45, 0x19, 0xAA
    };

    sub_1500(input, strlen((char*)input), key);

    return 0;
}

