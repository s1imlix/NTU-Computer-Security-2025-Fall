#include <fcntl.h>
#include <inttypes.h>
#include <seccomp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

void win() { execve("/bin/sh", NULL, NULL); }

void child(void *addr) {
  if (mprotect(addr, 0x1000, PROT_EXEC | PROT_WRITE) < 0)
    perror("mprotect"), exit(-1);

  scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
  seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
  if (seccomp_load(ctx) < 0)
    perror("seccomp_load"), exit(-1);
  seccomp_release(ctx);

  ((void (*)())addr)();

  exit(0);
}

int main(void) {
  srand(time(0));
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);

  void *addr = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE,
                    MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  if ((unsigned long)addr == -1)
    perror("mmap"), exit(-1);

  for (;;) {
    printf("write code > ");
    read(0, addr, 0x1000);
    pid_t pid = fork();
    if (pid < 0)
      perror("fork"), exit(-1);
    if (pid == 0)
      child(addr);
    int wstatus;
    if (waitpid(pid, &wstatus, 0) < 0)
      perror("waitpid"), exit(-1);
    printf("child exit %d\n", WEXITSTATUS(wstatus));
    printf("continue > ");
    char c;
    scanf("%c", &c);
    if (c == 'N')
      break;
  }

  char buf[0x10];
  printf("gets > ");
  gets(buf);

  return 0;
}
