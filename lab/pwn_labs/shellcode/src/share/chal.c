#include <stdio.h>
#include <unistd.h>

typedef void (*f)(const char *);

int main(void) {
  char sc[] = {0x31, 0xd2, 0xb2, 0xd,  0x48, 0x89, 0xfe, 0x31, 0xc0,
               0xb0, 0x1,  0x48, 0x89, 0xc7, 0xf,  0x5,  0xc3};

  ((f)(&sc))("Hello World!\n");

  int n = read(0, sc, 0x100);
  for (int i = 0; i < n; i++)
    if (sc[i] == 0xf || sc[i] == 0x5)
      sc[i] = 0xcc;

  ((f)(&sc))("Goodbye!\n");

  return 0;
}
