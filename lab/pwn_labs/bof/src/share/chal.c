#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void win() { execve("/bin/sh", NULL, NULL); }

int main(void) {
  setvbuf(stdout, NULL, _IONBF, 0);

  struct Course {
    char name[8];
    char desc[8];
    long score;
  } course;

  printf("Gift: ");
  write(1, &course, 0x20);
  printf("\n");

  gets(course.desc);

  return 0;
}
