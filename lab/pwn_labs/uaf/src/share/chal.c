#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void default_handle(char *event) {
  printf("EVENT: get event named \"%s\"!\n", event);
}

struct entity {
  char *name;
  char *event;
  void (*event_handle)(char *);
};

struct entity *entities[0x2];

int read_int() {
  char buf[0x20];
  read(0, buf, 0x1f);
  return atoi(buf);
}

int get_idx() {
  int idx = read_int();
  if (idx >= 0x2 || idx < 0)
    exit(0);
  return idx;
}

void memu() {
  puts("1. register entity");
  puts("2. delete entity");
  puts("3. trigger event");
  printf("choice: ");
}

void register_entity() {
  int idx;
  int len;
  printf("Index: ");
  idx = get_idx();
  entities[idx] = malloc(sizeof(struct entity));
  entities[idx]->event_handle = default_handle;
  entities[idx]->event = "Default Event";
  printf("Nmae Length: ");
  len = read_int();
  if (len == 0 || len > 0x430)
    exit(0);
  entities[idx]->name = malloc(len);
  printf("Name: ");
  read(0, entities[idx]->name, len - 1);
}

void delete_entity() {
  int idx;
  printf("Index: ");
  idx = get_idx();
  if (entities[idx]) {
    free(entities[idx]->name);
    free(entities[idx]);
  } else
    puts("Invalid index");
}

void trigger_event() {
  int idx;
  printf("Index: ");
  idx = get_idx();
  if (entities[idx]) {
    printf("Name: %s\n", entities[idx]->name);
    entities[idx]->event_handle(entities[idx]->event);
  }
}

int main(void) {
  setvbuf(stdin, 0, 2, 0);
  setvbuf(stdout, 0, 2, 0);
  for (;;) {
    memu();
    int choice = read_int();
    switch (choice) {
    case 1:
      register_entity();
      break;
    case 2:
      delete_entity();
      break;
    case 3:
      trigger_event();
    default:
      puts("Invalid command");
    }
  }
  return 0;
}
