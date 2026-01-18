#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

long pool[0x100];

int main(void) {
  srand(time(NULL));

  long index = rand() % 0x100;
  long value = rand();
  long mask = rand();
  char buf[0100];

  printf("> ");
  scanf("%100s", buf);
  pool[index] = (pool[index] & mask) | value;
  printf("Go %lx\n", pool[index]);

  return 0;
}

__attribute__((constructor)) static void initproc() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}
