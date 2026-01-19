#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

__attribute__((constructor)) static void initproc() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}

int main() {
  char buf[0x60];
  read(0, buf, 0x80);

  return 0;
}
