#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct Todo {
  char data[0x10];
  struct Todo *prev, *next;
};

struct User {
  char username[8];
  char password[8];
  struct Todo *todo;
  struct User *prev, *next;
};

static struct User *users = NULL;
static struct User *current = NULL;

static void free_todos(struct Todo *t) {
  while (t) {
    struct Todo *n = t->next;
    free(t);
    t = n;
  }
}

static void show_menu(void) {
  puts("1. register");
  puts("2. login");
  puts("3. logout");
  puts("4. add todo");
  puts("5. show todos");
  puts("6. remove todo");
  puts("7. clear todos");
  puts("8. destroy user");
  puts("9. exit");
  printf("> ");
}

static void register_user(void) {
  struct User *u = malloc(sizeof(struct User));
  if (!u) {
    puts("alloc failed");
    exit(-1);
  }

  memset(u, 0, sizeof(*u));

  printf("username > ");
  scanf("%7s", u->username);
  printf("password > ");
  scanf("%7s", u->password);

  /* insert at head */
  u->next = users;
  if (users)
    users->prev = u;
  users = u;

  puts("registered");
}

static void login_user(void) {
  if (current) {
    puts("already logged in");
    return;
  }

  char username[8], password[8];
  printf("username > ");
  scanf("%7s", username);
  printf("password > ");
  scanf("%7s", password);

  for (struct User *u = users; u; u = u->next) {
    if (!strcmp(u->username, username) && !strcmp(u->password, password)) {
      current = u;
      printf("hello %s\n", username);
      return;
    }
  }

  puts("invalid credential");
}

static void logout_user(void) {
  if (!current) {
    puts("not logged in");
    return;
  }

  puts("bye");
  current = NULL;
}

static void add_todo(void) {
  if (!current) {
    puts("login first");
    return;
  }

  struct Todo *t = malloc(sizeof(struct Todo));
  if (!t) {
    puts("alloc failed");
    exit(-1);
  }

  memset(t, 0, sizeof(*t));
  printf("todo > ");
  scanf("%15s", t->data);

  t->prev = NULL;
  t->next = current->todo;
  if (current->todo)
    current->todo->prev = t;
  current->todo = t;
  puts("added");
}

static void show_todos(void) {
  if (!current) {
    puts("login first");
    return;
  }

  struct Todo *t = current->todo;
  int idx = 0;
  while (t) {
    printf("%d. %s\n", idx, t->data);
    t = t->next;
    ++idx;
  }

  if (!idx)
    puts("(empty)");
}

static void remove_todo(void) {
  if (!current) {
    puts("login first");
    return;
  }

  int idx = 0;
  printf("id > ");
  if (scanf("%d", &idx) != 1 || idx < 0) {
    puts("invalid id");
    return;
  }

  struct Todo *t = current->todo;
  while (t && idx--)
    t = t->next;

  if (!t) {
    puts("not found");
    return;
  }

  if (t->prev)
    t->prev->next = t->next;
  else
    current->todo = t->next;
  if (t->next)
    t->next->prev = t->prev;

  free(t);
  puts("removed");
}

static void clear_todo_list(void) {
  if (!current) {
    puts("login first");
    return;
  }

  free_todos(current->todo);
  puts("cleared");
}

static void clear_all(void) {
  struct User *u = users;
  while (u) {
    struct User *n = u->next;
    free_todos(u->todo);
    free(u);
    u = n;
  }
  users = NULL;
  current = NULL;
}

static void destroy_user(void) {
  char username[8], password[8];
  printf("username > ");
  scanf("%7s", username);
  printf("password > ");
  scanf("%7s", password);

  struct User *u = users;
  while (u) {
    if (!strcmp(u->username, username) && !strcmp(u->password, password)) {
      if (u->prev)
        u->prev->next = u->next;
      else
        users = u->next;
      if (u->next)
        u->next->prev = u->prev;
      if (current == u)
        current = NULL;
      free_todos(u->todo);
      free(u);
      puts("destroyed");
      return;
    }
    u = u->next;
  }

  puts("not found");
}

int main(void) {
  for (;;) {
    show_menu();
    int op;
    if (scanf("%d", &op) != 1)
      break;

    switch (op) {
    case 1:
      register_user();
      break;
    case 2:
      login_user();
      break;
    case 3:
      logout_user();
      break;
    case 4:
      add_todo();
      break;
    case 5:
      show_todos();
      break;
    case 6:
      remove_todo();
      break;
    case 7:
      clear_todo_list();
      break;
    case 8:
      destroy_user();
      break;
    case 9:
      clear_all();
      return 0;
    default:
      puts("?");
      break;
    }
  }

  return 0;
}

__attribute__((constructor)) static void initproc() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}
