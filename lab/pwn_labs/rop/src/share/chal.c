#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void) {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);

  puts("/bin/date");

  char buf[8];
  gets(buf);

  return 0;
}
