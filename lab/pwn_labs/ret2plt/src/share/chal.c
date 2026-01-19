#include <error.h>
#include <seccomp.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

__attribute__((constructor)) static void initproc() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}

__attribute__((constructor)) static void setup_seccomp() {
  scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ALLOW);
  int ret = 0;
  if (ctx != NULL) {
    ret |= seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(execve), 0);
    ret |= seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(execveat), 0);
    ret |= seccomp_load(ctx);
    seccomp_release(ctx);
  }
  if (ctx == NULL || ret)
    error(EXIT_FAILURE, ret, "seccomp");
}

int main() {
  puts("meow");

  char buf[0x60];
  read(0, buf, 0x80);

  return 0;
}
