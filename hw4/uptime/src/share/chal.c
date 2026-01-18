#include <fcntl.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/sendfile.h>
#include <sys/wait.h>
#include <unistd.h>

#define MAGIC 0xdeadbeef01337331LL

void magic() {
  int fd = open("/proc/uptime", O_RDONLY);
  if (sendfile(STDOUT_FILENO, fd, NULL, 0x20) < 0)
    perror("sendfile");
  close(fd);
}

struct user {
  char *username;
  char *password;
  char *prompt;
  uint64_t cnt;
};

unsigned readint() {
  unsigned x;
  scanf("%u", &x);
  return x;
}

char *readstr(const char *name) {
  printf("%s length > ", name);
  unsigned len = readint();
  char *s = malloc(len);
  printf("%s > ", name);
  scanf("%s", s);
  return s;
}

int main(void) {
  struct user *user = NULL;

  for (;;) {
    printf("\nWelcome to the uptime helper!\n");
    printf("1. register a new user\n");
    printf("2. login\n");
    printf("3. reset password\n");
    printf("select an option > ");
    int op = readint();

    switch (op) {
    case 1: {
      if (user) {
        free(user->prompt);
        free(user->username);
        free(user->password);
      }

      user = malloc(sizeof(struct user));
      user->username = readstr("username");
      user->password = readstr("password");

      if (strchr(user->username, '%'))
        exit(-1);

      char buf[0x40];
      snprintf(buf, sizeof(buf), "Hi %s! Glad you're here.\n", user->username);
      strcat(buf, "Welcome back %s!\nThis is login #%d.\n");
      user->prompt = strdup(buf);
      user->cnt = 0;
      printf("Account for '%s' saved. Use option 2 to sign in.\n",
             user->username);
      break;
    }
    case 2: {
      char u[16], p[16];
      printf("Enter username and password separated by a space.\n");
      scanf("%16s %16s", u, p);
      if (!strcmp(u, user->username) && !strcmp(p, user->password)) {
        printf(user->prompt, user->username, ++user->cnt);

        if (user->cnt == MAGIC)
          magic();
      } else {
        printf("Invalid credentials. Please try again.\n");
      }
      break;
    }
    case 3: {
      if (!user) {
        printf("No account found. Please register first.\n");
      } else {
        printf("old password: %s\n", user->password);
        user->password = readstr("new password");
        user->cnt = 0;
        printf("Password updated. Login counter reset.\n");
      }
      break;
    }
    default:
      exit(-1);
    }
  }

  return 0;
}

__attribute__((constructor)) static void initproc() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}
