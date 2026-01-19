#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

__attribute__((constructor)) static void initproc() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}

int main() {
  char s[0x30];
  int run = 1;

  while (run) {
    scanf("%s", s);
    strcat(s, "\n");
    printf(s, s);
  }

  return 0;
}
