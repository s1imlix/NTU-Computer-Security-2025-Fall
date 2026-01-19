#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

char users[][8] = {
    "admin",
    "guest",
};

int main(void) {
  setvbuf(stdout, NULL, _IONBF, 0);

  int i;

  for (;;) {
    printf("idx: ");
    scanf("%d", &i);
    puts(users[i]);

    printf("idx: ");
    scanf("%d", &i);
    printf("data: ");
    scanf("%s", users[i]);
  }

  return 0;
}
