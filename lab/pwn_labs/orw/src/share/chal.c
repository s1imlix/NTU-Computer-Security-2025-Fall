#include <error.h>
#include <seccomp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

__attribute__((constructor)) static void initproc() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}

static void setup_seccomp() {
  scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ALLOW);
  int ret = 0;
  if (ctx != NULL) {
    ret |= seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(write), 1,
                            SCMP_A0(SCMP_CMP_NE, STDOUT_FILENO));
    ret |= seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(sendfile), 1,
                            SCMP_A0(SCMP_CMP_GT, STDOUT_FILENO));
    ret |= seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(execve), 0);
    ret |= seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(execveat), 0);
    ret |= seccomp_load(ctx);
    seccomp_release(ctx);
  }
  if (ctx == NULL || ret)
    error(EXIT_FAILURE, ret, "seccomp");
}

typedef void (*fn)();

int main() {
  if (access("/flag.txt", F_OK) == -1)
    return perror("flag"), -1;

  fn addr = mmap(0, 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
                 MAP_PRIVATE | MAP_ANON, -1, 0);
  if (addr == MAP_FAILED)
    return perror("mmap"), -1;

  printf("> ");
  read(0, addr, 4096);

  close(STDOUT_FILENO);
  setup_seccomp();
  addr();

  return 0;
}
