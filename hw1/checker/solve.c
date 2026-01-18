#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

// Global array of dumped rand() values
unsigned int dumped_rand_values[] = {
    0x372ab6d1, 0x6bbcfe5, 894331345, 550606490, 612670572, 1984253156,
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
    printf("Using dumped rand value: %u\n", val);
    dumped_index++;
    if (dumped_index >= sizeof(dumped_rand_values)/sizeof(dumped_rand_values[0])) {
        dumped_index = 0; // wrap around if needed
    }
    return val;
}

unsigned char rol(unsigned char value, unsigned int n) {
    const unsigned int bits = 8;
    n %= bits;
    return (value << n) | (value >> (bits - n));
} 

// Rotate right for 8-bit value
unsigned char rotr(unsigned char value, unsigned int n) {
    const unsigned int bits = 8;
    n %= bits;
    return (value >> n) | (value << (bits - n));
}

// sub_1500 using next_rand()
uint64_t sub_1500(unsigned char *a1, uint64_t a2, const unsigned char *a3) {
    unsigned char *v5 = calloc(0x100, sizeof(unsigned char));
    unsigned char *v7 = calloc(0x100, sizeof(unsigned char));
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
    for (size_t k = 0; k < a2; k++) {
	printf("%d ", v5[k]);
    }
    printf("\n");

    // Transform
    for (uint64_t v13 = 0; v13 < i; v13++) {
        uint8_t x = v5[v13];
        uint16_t v15 = (37 * x) >> 8;
        unsigned int shift = x - 7 * ((uint8_t)(((uint8_t)(x - v15) >> 1) + v15) >> 2) + 1;
        unsigned char val = v7[x] ^ rotr(a3[v13], shift);
        a1[x] = val;
        // printf("v5[%d]=%d->%c\n", v13, x, val);
    }
    a1[i] = 0;
    
    free(v5);
    free(v7);
    return i;
}

// Forward transform
uint64_t sub_1500_forward(const unsigned char *input, uint64_t len, unsigned char *outbuf) {
    uint8_t *v5 = calloc(len, sizeof(uint8_t));
    unsigned char *v7 = calloc(len, sizeof(unsigned char));
    uint64_t i, j;

    if (!input || !len) {
        free(v5);
        free(v7);
        return 0;
    }

    // Fill arrays
    for (i = 0; i < len; ++i) {
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
    for (size_t k = 0; k < len; k++) {
	printf("%d ", v5[k]);
    }
    printf("\n");

    // Transform
    for (uint64_t v13 = 0; v13 < i; v13++) {
        uint8_t x = v5[v13];
        uint16_t v15 = (37 * x) >> 8;
        unsigned int shift = x - 7 * ((uint8_t)(((uint8_t)(x - v15) >> 1) + v15) >> 2) + 1;
        outbuf[v13] = rol(v7[x] ^ input[x], shift);
    }

    free(v5);
    free(v7);
    return i;
}

int main() {
    unsigned char input[] = "flag{Th1s_1s_4_t3st_fl4g}";
    int n = strlen((char*)input);
    unsigned char output[256] = {0};
    unsigned char key[34] = {
    	0x03, 0x71, 0xE5, 0x2F, 0xE2, 0x18, 0xB5, 0xA6,
    	0xDD, 0x3C, 0xB3, 0xE7, 0x47, 0xDD, 0x1D, 0xB4,
    	0xA4, 0x9A, 0x51, 0x94, 0x0F, 0xA9, 0x69, 0x70,
    	0xF8, 0x84, 0x12, 0x56, 0x23, 0xCB, 0x77, 0xEC, 0xD8, 0xA2
    };

    sub_1500_forward(input, n, output);
    printf("Transformed: ");
    for (size_t i = 0; i < n; i++) {
	printf("%02X ", output[i]);
    }
    printf("\n");
    dumped_index = 0; // Reset index to reuse dumped values
    input[0] = 0; // Clear input
    sub_1500(input, n, output);
    printf("TEST Recovered: %s\n", input);

    dumped_index = 0; // Reset index to reuse dumped values
    printf("Recovering Key...\n");
    sub_1500(input, strlen((char*)key), key);
    printf("Key Recovered: %s\n", input);
    return 0;
}

