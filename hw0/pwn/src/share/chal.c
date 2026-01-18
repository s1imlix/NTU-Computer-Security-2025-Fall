#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#define SIZE 8
#define BACKDOOR 0xdeadbeef

uint64_t readint(const char *prompt) {
  printf("%s > ", prompt);
  uint64_t x = 0;
  scanf("%" PRIu64, &x);
  return x;
}

int comp_asc(const void *el1, const void *el2) {
  uint64_t f = *(uint64_t *)el1;
  uint64_t s = *(uint64_t *)el2;
  if (f > s)
    return 1;
  if (f < s)
    return -1;
  return 0;
}

int comp_dec(const void *el1, const void *el2) { return comp_asc(el2, el1); }

typedef int (*COMPAR)(const void *, const void *);

void edit(uint64_t *array) {
  uint64_t idx = readint("index");
  if (idx >= SIZE) {
    puts("nono");
  } else {
    array[idx] = readint("value");
  }
}

void sorting(uint64_t *array) {
  uint64_t base = readint("base");
  uint64_t len = readint("len");
  COMPAR compar = readint("asc(0) / dec(1)") ? comp_dec : comp_asc;
  qsort(array + base, len, sizeof(array[0]), compar);
}

int main(void) {
  srand(time(0));
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);

  uint64_t array[SIZE] = {};
  uint64_t meow = rand();

  for (int i = 0; i < SIZE; i++)
    array[i] = i;

  for (;;) {
    printf("array = [");
    for (int i = 0; i < SIZE; i++) {
      if (i)
        printf(", ");
      printf("%" PRIu64, array[i]);
    }
    printf("]\n");

    printf("1. change value\n");
    printf("2. sort array\n");
    printf("3. exit\n");

    switch (readint("")) {
    case 1:
      edit(array);
      break;
    case 2:
      sorting(array);
      break;
    default:
      goto exit;
    }
  }

exit:
  if (meow == BACKDOOR) {
    system("sh");
  }

  return 0;
}
